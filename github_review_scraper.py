"""
github_review_scraper.py

Automates scraping of PR review comments + matching code patches
across MANY GitHub repositories, with:
  - pagination handling (PRs, comments, files)
  - rate-limit aware throttling + auto-wait on exhaustion
  - resumable output (appends, skips repos already fully done)
  - CSV + JSON export
  - retry on transient network errors

Usage:
    1. Put your GitHub token in an environment variable:
         export GITHUB_TOKEN=ghp_xxxxxxxxxxxxxxxxxxxx        (Linux/Mac)
         setx GITHUB_TOKEN "ghp_xxxxxxxxxxxxxxxxxxxx"         (Windows, new shell after)

    2. Create a text file `repos.txt` with one repo per line, e.g.:
         pallets/flask
         psf/requests
         https://github.com/django/django

    3. Run:
         python github_review_scraper.py --repos repos.txt --out dataset

    Outputs:
        dataset.csv   -> flat table, one row per review comment
        dataset.json  -> same data as JSON records
        progress.log  -> which repos/PRs have been completed (for resuming)
"""

import argparse
import csv
import json
import os
import re
import sys
import time
from pathlib import Path

import requests

API_ROOT = "https://api.github.com"


# --------------------------------------------------------------------------
# Helpers
# --------------------------------------------------------------------------

def parse_repo_string(raw: str):
    """Accepts 'owner/repo' or a full GitHub URL, returns (owner, repo)."""
    raw = raw.strip()
    if not raw or raw.startswith("#"):
        return None
    raw = raw.rstrip("/")
    match = re.search(r"(?:github\.com/)?([^/\s]+)/([^/\s]+?)(?:\.git)?$", raw)
    if not match:
        raise ValueError(f"Could not parse repo string: {raw!r}")
    return match.group(1), match.group(2)


def load_repo_list(path: str):
    repos = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            parsed = parse_repo_string(line)
            if parsed:
                repos.append(parsed)
    return repos


def load_completed_prs(progress_path: str):
    """Returns a set of 'owner/repo#pr_number' strings already scraped."""
    done = set()
    if os.path.exists(progress_path):
        with open(progress_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    done.add(line)
    return done


def mark_pr_done(progress_path: str, key: str):
    with open(progress_path, "a", encoding="utf-8") as f:
        f.write(key + "\n")


# --------------------------------------------------------------------------
# GitHub API client with rate-limit + retry handling
# --------------------------------------------------------------------------

class GitHubClient:
    def __init__(self, token: str, max_retries: int = 5):
        if not token:
            raise ValueError(
                "No GitHub token found. Set the GITHUB_TOKEN environment variable."
            )
        self.session = requests.Session()
        self.session.headers.update(
            {
                "Authorization": f"Bearer {token}",
                "Accept": "application/vnd.github+json",
                "X-GitHub-Api-Version": "2022-11-28",
            }
        )
        self.max_retries = max_retries

    def _handle_rate_limit(self, resp):
        remaining = resp.headers.get("X-RateLimit-Remaining")
        reset = resp.headers.get("X-RateLimit-Reset")
        if remaining is not None and int(remaining) == 0 and reset:
            wait_seconds = max(int(reset) - int(time.time()), 0) + 2
            print(
                f"  [rate limit] exhausted, sleeping {wait_seconds}s until reset...",
                file=sys.stderr,
            )
            time.sleep(wait_seconds)
            return True
        return False

    def get(self, url: str, params: dict = None):
        """GET with retry, rate-limit wait, and secondary-rate-limit backoff."""
        attempt = 0
        while attempt < self.max_retries:
            resp = self.session.get(url, params=params, timeout=30)

            if resp.status_code == 403 and "rate limit" in resp.text.lower():
                if self._handle_rate_limit(resp):
                    attempt += 1
                    continue
                # secondary rate limit (abuse detection) -> backoff
                wait = 2 ** attempt * 5
                print(f"  [secondary limit] backing off {wait}s...", file=sys.stderr)
                time.sleep(wait)
                attempt += 1
                continue

            if resp.status_code == 404:
                return resp  # let caller decide (e.g. repo renamed/deleted)

            if resp.status_code >= 500:
                wait = 2 ** attempt * 3
                print(f"  [server error {resp.status_code}] retrying in {wait}s...", file=sys.stderr)
                time.sleep(wait)
                attempt += 1
                continue

            resp.raise_for_status()
            self._handle_rate_limit(resp)  # proactively wait if we just hit 0
            return resp

        raise RuntimeError(f"Exceeded max retries fetching {url}")

    def paginated_get(self, url: str, params: dict = None):
        """Yields items across all pages using the Link header."""
        params = dict(params or {})
        params.setdefault("per_page", 100)
        next_url = url
        while next_url:
            resp = self.get(next_url, params=params if next_url == url else None)
            if resp.status_code == 404:
                return
            data = resp.json()
            if isinstance(data, list):
                for item in data:
                    yield item
            else:
                yield data
                return
            next_url = resp.links.get("next", {}).get("url")


# --------------------------------------------------------------------------
# Core scraping logic
# --------------------------------------------------------------------------

def scrape_repo(client: GitHubClient, owner: str, repo: str, completed_prs: set,
                 progress_path: str, pr_state: str = "closed"):
    """Yields one dict per review comment, matched with its file patch."""
    full_name = f"{owner}/{repo}"
    print(f"\n=== Scraping {full_name} ===")

    prs_url = f"{API_ROOT}/repos/{owner}/{repo}/pulls"
    for pr in client.paginated_get(prs_url, params={"state": pr_state, "sort": "updated", "direction": "desc"}):
        pr_number = pr.get("number")
        pr_key = f"{full_name}#{pr_number}"
        if pr_key in completed_prs:
            continue  # already scraped in a previous run

        print(f"  PR #{pr_number}: {pr.get('title', '')[:70]}")

        # 1. Changed files -> map filename to patch
        files_url = f"{API_ROOT}/repos/{owner}/{repo}/pulls/{pr_number}/files"
        patch_by_file = {}
        for f in client.paginated_get(files_url):
            patch_by_file[f.get("filename")] = f.get("patch", "")

        # 2. Review comments (inline code comments)
        comments_url = f"{API_ROOT}/repos/{owner}/{repo}/pulls/{pr_number}/comments"
        any_comment = False
        for c in client.paginated_get(comments_url):
            any_comment = True
            path = c.get("path")
            yield {
                "repo": full_name,
                "pr_number": pr_number,
                "pr_title": pr.get("title", ""),
                "commit_sha": c.get("commit_id", ""),
                "file": path,
                "line": c.get("line") or c.get("original_line"),
                "side": c.get("side", ""),
                "diff_hunk": c.get("diff_hunk", ""),
                "patch": patch_by_file.get(path, ""),
                "review_comment": c.get("body", ""),
                "reviewer": (c.get("user") or {}).get("login", ""),
                "created_at": c.get("created_at", ""),
            }

        if not any_comment:
            # still record the PR as processed with no comment rows
            pass

        mark_pr_done(progress_path, pr_key)
        completed_prs.add(pr_key)

        # be polite even within the primary rate limit
        time.sleep(0.2)


# --------------------------------------------------------------------------
# Output writers
# --------------------------------------------------------------------------

FIELDNAMES = [
    "repo", "pr_number", "pr_title", "commit_sha", "file", "line", "side",
    "diff_hunk", "patch", "review_comment", "reviewer", "created_at",
]


def append_csv_row(csv_path: str, row: dict, write_header: bool):
    with open(csv_path, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        if write_header:
            writer.writeheader()
        writer.writerow(row)


def rewrite_json_from_csv(csv_path: str, json_path: str):
    """Regenerate the JSON file from the CSV so JSON always mirrors final state."""
    rows = []
    if os.path.exists(csv_path):
        with open(csv_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows = list(reader)
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(rows, f, indent=2, ensure_ascii=False)


# --------------------------------------------------------------------------
# Main
# --------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Scrape PR review comments + patches from many repos.")
    parser.add_argument("--repos", required=True, help="Path to text file with one owner/repo per line")
    parser.add_argument("--out", default="dataset", help="Output basename (produces <out>.csv and <out>.json)")
    parser.add_argument("--state", default="closed", choices=["open", "closed", "all"],
                         help="Which PRs to scrape (closed = merged+closed, usually what you want)")
    parser.add_argument("--token", default=os.environ.get("GITHUB_TOKEN"),
                         help="GitHub token (defaults to GITHUB_TOKEN env var)")
    args = parser.parse_args()

    csv_path = f"{args.out}.csv"
    json_path = f"{args.out}.json"
    progress_path = f"{args.out}.progress.log"

    client = GitHubClient(token=args.token)
    repos = load_repo_list(args.repos)
    if not repos:
        print("No repos found in the input file.", file=sys.stderr)
        sys.exit(1)

    completed_prs = load_completed_prs(progress_path)
    write_header = not os.path.exists(csv_path) or os.path.getsize(csv_path) == 0

    total_rows = 0
    for owner, repo in repos:
        try:
            for row in scrape_repo(client, owner, repo, completed_prs, progress_path, pr_state=args.state):
                append_csv_row(csv_path, row, write_header)
                write_header = False
                total_rows += 1
        except Exception as e:
            print(f"  !! Error scraping {owner}/{repo}: {e}", file=sys.stderr)
            continue

    rewrite_json_from_csv(csv_path, json_path)
    print(f"\nDone. {total_rows} new review-comment rows written this run.")
    print(f"CSV:  {csv_path}")
    print(f"JSON: {json_path}")
    print(f"Progress log (for resuming): {progress_path}")


if __name__ == "__main__":
    main()
