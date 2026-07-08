import requests
from config import BASE_URL, HEADERS, OWNER, REPO

def get_all_prs(state="open"):
    url = f"{BASE_URL}/repos/{OWNER}/{REPO}/pulls"

    params = {
        "state": state,
        "page": 1,
        "per_page": 100
    }

    response = requests.get(
        url,
        headers=HEADERS,
        params=params
    )

    return response.json()