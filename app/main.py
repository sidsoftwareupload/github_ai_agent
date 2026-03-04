import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.github_api import fetch_issues
from app.ai_logic import summarise_text
from .database import engine, SessionLocal, init_db
from . import models

# Environment variables configuration
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

def validate_environment():
    """Log warnings for missing environment variables at startup"""
    if not GITHUB_TOKEN:
        print("⚠️  Warning: GITHUB_TOKEN not set - GitHub API rate limits will apply")
    if not OPENAI_API_KEY:
        print("⚠️  Warning: OPENAI_API_KEY not set - Using mock AI responses")
    return {
        "github_token": bool(GITHUB_TOKEN),
        "openai_api_key": bool(OPENAI_API_KEY)
    }

# Lifespan: runs once on startup (safe with multi-worker gunicorn)
@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()              # create tables if they don't exist
    validate_environment() # log env-var warnings
    yield                  # app runs here

app = FastAPI(lifespan=lifespan)

# Enable CORS for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # allow all for testing
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount frontend static files
app.mount("/frontend", StaticFiles(directory="frontend"), name="frontend")

class RepoRequest(BaseModel):
    username: str
    repo: str

@app.get("/")
def home():
    return {"message": "GitHub AI Task Agent running"}

@app.get("/health")
def health_check():
    """Health check endpoint showing environment status"""
    return {
        "status": "healthy",
        "environment": {
            "github_token_configured": bool(GITHUB_TOKEN),
            "openai_api_key_configured": bool(OPENAI_API_KEY)
        },
        "database": "connected"
    }

@app.post("/process-task")
def process_task(request: RepoRequest):
    # Step 1: fetch issues from GitHub
    issues = fetch_issues(request.username, request.repo)
    
    # Step 2: process each issue individually
    db = SessionLocal()
    new_tasks_count = 0
    
    for issue in issues:
        title = issue.get("title") or ""
        body = issue.get("body") or ""
        
        # Combine title and body for AI summarization
        issue_text = title + "\n" + body
        task_content = summarise_text(issue_text)
        
        # Check if task already exists (avoid duplicates)
        existing_task = db.query(models.Task).filter(
            models.Task.repo == request.repo,
            models.Task.content == task_content
        ).first()
        
        if existing_task:
            continue  # Skip if already in DB
        
        # Otherwise, add new task
        db_task = models.Task(
            repo=request.repo,
            content=task_content,
            status="pending"
        )
        db.add(db_task)
        new_tasks_count += 1
    
    db.commit()
    db.close()
    
    # Step 3: return JSON
    return {
        "repo": request.repo,
        "issues_processed": len(issues),
        "new_tasks_created": new_tasks_count,
        "message": f"Processed {len(issues)} issues, created {new_tasks_count} new tasks"
    }

@app.get("/tasks")
def get_tasks(repo: str = None):
    db = SessionLocal()

    if repo:
        tasks = db.query(models.Task).filter(models.Task.repo == repo).all()
    else:
        tasks = db.query(models.Task).all()

    results = [
        {
            "id": task.id,
            "repo": task.repo,
            "content": task.content,
            "status": task.status,
            "created_at": task.created_at,
            "updated_at": task.updated_at
        }
        for task in tasks
    ]

    db.close()

    return results

@app.patch("/tasks/{task_id}")
def update_task_status(task_id: int, new_status: str):
    db = SessionLocal()
    
    task = db.query(models.Task).filter(models.Task.id == task_id).first()
    if not task:
        db.close()
        raise HTTPException(status_code=404, detail="Task not found")

    task.status = new_status
    db.commit()
    db.refresh(task)
    
    result = {
        "id": task.id,
        "repo": task.repo,
        "status": task.status,
        "content": task.content
    }
    
    db.close()
    return result