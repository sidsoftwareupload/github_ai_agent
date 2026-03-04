import os
import re
from openai import OpenAI

api_key = os.getenv("OPENAI_API_KEY")
if api_key:
    client = OpenAI(api_key=api_key)
else:
    client = None

def summarise_text(text: str):
    """
    Smart mock AI layer that extracts task-like sentences from GitHub issues.
    Later this entire function can be replaced with real OpenAI without changing the app.
    """
    if client:
        # Use real OpenAI if API key is available
        prompt = f"""
        You are an engineering task assistant.
        Extract clear, actionable tasks from the following GitHub issues.
        Return them as concise bullet points.

        Issues:
        {text}
        """

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You extract engineering tasks."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3
        )

        return response.choices[0].message.content
    
    # Mock AI: Extract task-like sentences
    lines = text.split("\n")
    tasks = []

    for line in lines:
        line = line.strip()
        if not line:
            continue

        # Basic keyword detection for engineering tasks
        if re.search(r"(fix|add|update|implement|remove|refactor|improve|optimize|debug|test|deploy)", line, re.IGNORECASE):
            tasks.append(f"- {line}")

    # Fallback if no keywords found - take first few lines
    if not tasks:
        for line in lines[:5]:
            if line.strip():
                tasks.append(f"- {line.strip()}")

    return "\n".join(tasks)
