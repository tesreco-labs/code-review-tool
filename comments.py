import requests
from config import BASE_URL, HEADERS, OWNER, REPO


def get_review_comments(pr_number):
    url = f"{BASE_URL}/repos/{OWNER}/{REPO}/pulls/{pr_number}/comments"

    response = requests.get(url, headers=HEADERS)

    return response.json()