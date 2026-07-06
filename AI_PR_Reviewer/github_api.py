import requests
from config import BASE_URL, OWNER, REPO, HEADERS


def fetch_pull_requests(state="open", page=1, per_page=100):
    """
    Fetch pull requests.

    Args:
        state (str): open, closed, or all
        page (int): page number
        per_page (int): number of PRs per page (max 100)

    Returns:
        list: Pull requests
    """

    url = f"{BASE_URL}/repos/{OWNER}/{REPO}/pulls"

    params = {
        "state": state,
        "page": page,
        "per_page": per_page
    }

    response = requests.get(url, headers=HEADERS, params=params)
    response.raise_for_status()

    return response.json()


def fetch_pr_files(pr_number):
    """
    Fetch all changed files in a pull request.

    Args:
        pr_number (int): Pull Request number

    Returns:
        list: Changed files
    """

    url = f"{BASE_URL}/repos/{OWNER}/{REPO}/pulls/{pr_number}/files"

    response = requests.get(url, headers=HEADERS)
    response.raise_for_status()

    return response.json()


def fetch_review_comments(pr_number):
    """
    Fetch inline review comments on a pull request.

    These are comments attached to specific lines of code.

    Args:
        pr_number (int): Pull Request number

    Returns:
        list: Review comments
    """

    url = f"{BASE_URL}/repos/{OWNER}/{REPO}/pulls/{pr_number}/comments"

    response = requests.get(url, headers=HEADERS)
    response.raise_for_status()

    return response.json()


def fetch_reviews(pr_number):
    """
    Fetch review events for a pull request.

    These include:
    - APPROVED
    - CHANGES_REQUESTED
    - COMMENTED

    Args:
        pr_number (int): Pull Request number

    Returns:
        list: Reviews
    """

    url = f"{BASE_URL}/repos/{OWNER}/{REPO}/pulls/{pr_number}/reviews"

    response = requests.get(url, headers=HEADERS)
    response.raise_for_status()

    return response.json()


def fetch_issue_comments(pr_number):
    """
    Fetch conversation comments on a pull request.

    These are NOT attached to code lines.

    Args:
        pr_number (int): Pull Request number

    Returns:
        list: Issue comments
    """

    url = f"{BASE_URL}/repos/{OWNER}/{REPO}/issues/{pr_number}/comments"

    response = requests.get(url, headers=HEADERS)
    response.raise_for_status()

    return response.json()