import os
from dotenv import load_dotenv

load_dotenv()

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
OWNER = "python"
REPO = "peps"

BASE_URL = "https://api.github.com"

HEADERS = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github+json"
}
print("Token:", GITHUB_TOKEN)
print("Owner:", OWNER)
print("Repo:", REPO)

import requests

response = requests.get(
    "https://api.github.com/user",
    headers=HEADERS
)

print("Status Code:", response.status_code)
print(response.json())