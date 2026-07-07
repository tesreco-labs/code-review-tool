from github_api import (
    fetch_pull_requests,
    fetch_pr_files,
    fetch_review_comments
)

from change_parser import extract_changes
from exporter import save_dataset


def main():

    dataset = []

    page = 1

    while True:

        prs = fetch_pull_requests("closed", page)

        if not prs:
            break

        print(f"\nProcessing Page {page}")

        for pr in prs:

            print(f"PR #{pr['number']}")

            comments = fetch_review_comments(pr["number"])

            if len(comments) == 0:
                continue

            files = fetch_pr_files(pr["number"])

            review_text = "\n".join(
                [comment["body"] for comment in comments]
            )

            for file in files:

                changes = extract_changes(file.get("patch", ""))

                for change in changes:

                    dataset.append([

                        pr["number"],

                        pr["title"],

                        file["filename"],

                        change["change_type"],

                        change["old_code"],

                        change["new_code"],

                        review_text

                    ])

        # ONLY FIRST PAGE FOR NOW
        break

    save_dataset(dataset)


if __name__ == "__main__":
    main()