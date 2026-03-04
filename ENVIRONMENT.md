# Environment Variables & Deployment Guide

## Environment Variables

| Variable | Required | Purpose | Where to get it |
|----------|----------|---------|-----------------|
| `GITHUB_TOKEN` | Optional | Increases GitHub API rate limits (60 → 5000 req/hr) | [github.com/settings/tokens](https://github.com/settings/tokens) |
| `OPENAI_API_KEY` | Optional | Enables real AI summaries | [platform.openai.com/api-keys](https://platform.openai.com/api-keys) |

---

## Local Development

```bash
# Copy and fill in your secrets
cp .env.example .env

# Run locally (without Docker)
uvicorn app.main:app --reload
```

---

## Docker — Local Testing

### Build
```bash
docker build -t ai-task-manager .
```

### Run (no secrets)
```bash
docker run -d -p 8000:8000 --name ai-task-manager ai-task-manager
```

### Run (with secrets)
```bash
docker run -d -p 8000:8000 \
  -e GITHUB_TOKEN=ghp_your_token_here \
  -e OPENAI_API_KEY=sk-your_key_here \
  --name ai-task-manager \
  ai-task-manager
```

### Verify
```
http://127.0.0.1:8000/               → API root
http://127.0.0.1:8000/health         → env + db status
http://127.0.0.1:8000/tasks          → list tasks
http://127.0.0.1:8000/frontend/index.html  → frontend UI
```

---

## Azure Deployment (App Service — Linux Container)

### Step 1: Push image to Docker Hub

```bash
# Tag the image
docker tag ai-task-manager <your_dockerhub_username>/ai-task-manager:latest

# Log in and push
docker login
docker push <your_dockerhub_username>/ai-task-manager:latest
```

### Step 2: Create Azure App Service

In [Azure Portal](https://portal.azure.com):

1. **Create a resource** → **Web App**
2. **Basics tab:**
   - Subscription: _your subscription_
   - Resource Group: `rg-ai-task-manager` (create new)
   - Name: `ai-task-manager` (must be globally unique)
   - Publish: **Docker Container**
   - OS: **Linux**
   - Region: _your nearest region_
3. **Docker tab:**
   - Options: **Single Container**
   - Image Source: **Docker Hub**
   - Access Type: **Public**
   - Image and tag: `<your_dockerhub_username>/ai-task-manager:latest`
4. Click **Review + Create** → **Create**

### Step 3: Set environment variables in Azure

In your App Service → **Configuration** → **Application settings** → add:

| Name | Value |
|------|-------|
| `GITHUB_TOKEN` | `ghp_your_token_here` |
| `OPENAI_API_KEY` | `sk-your_key_here` |
| `WEBSITES_PORT` | `8000` |

Click **Save** — the container will restart automatically.

### Step 4: Verify

```
https://<your-app-name>.azurewebsites.net/
https://<your-app-name>.azurewebsites.net/health
https://<your-app-name>.azurewebsites.net/tasks
https://<your-app-name>.azurewebsites.net/frontend/index.html
```

---

## Health Check Response

```json
{
  "status": "healthy",
  "environment": {
    "github_token_configured": true,
    "openai_api_key_configured": true
  },
  "database": "connected"
}
```

---

## What Happens Without Each Variable?

| Missing | Behaviour |
|---------|-----------|
| `GITHUB_TOKEN` | GitHub API limited to 60 requests/hour (unauthenticated) |
| `OPENAI_API_KEY` | Falls back to mock AI responses — app still works |
| Both missing | Fully functional with mock data and GitHub rate limits |

