import pandas as pd
from github_api import get_all_prs
from comments import get_review_comments


def build_dataset():
    rows = []

    prs = get_all_prs(state="all")

    for pr in prs:

        pr_number = pr["number"]

        comments = get_review_comments(pr_number)

        for comment in comments:

            rows.append({
                "pr_number": pr_number,
                "file": comment.get("path"),
                "review_comment": comment.get("body")
            })

    df = pd.DataFrame(rows)

    df.to_csv("data/output.csv", index=False)

    print("Dataset saved successfully!")