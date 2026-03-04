import requests
import json

# Test the /process-task endpoint
url = "http://127.0.0.1:8000/process-task"

# Test payload - replace with your actual GitHub credentials
payload = {
    "username": "torvalds",  # Example: Linux creator's public repo
    "repo": "linux",
    "token": "ghp_your_token_here"  # Replace with actual token
}

try:
    response = requests.post(url, json=payload)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
except Exception as e:
    print(f"Error: {e}")
