import os
import requests

def fetch_issues(username: str, repo: str):
    """
    Fetch GitHub issues for a repository.
    Returns list of issues or empty list if request fails.
    """
    token = os.getenv("GITHUB_TOKEN")
    url = f"https://api.github.com/repos/{username}/{repo}/issues"
    headers = {}
    
    if token:
        headers["Authorization"] = f"token {token}"
    
    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        return []

    return response.json()  # <-- Returns parsed JSON objects, not strings
