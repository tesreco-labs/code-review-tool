from github_api import get_all_prs
import pandas as pd

prs = get_all_prs(state="open")

data = []

for pr in prs:
    data.append({
        "PR Number": pr["number"],
        "Title": pr["title"],
        "Author": pr["user"]["login"],
        "State": pr["state"],
        "Created At": pr["created_at"],
        "PR URL": pr["html_url"]
    })

df = pd.DataFrame(data)

df.to_excel(
    "pull_requests.xlsx",
    index=False
)

print("Excel file created successfully!")
print(f"Total PRs saved: {len(df)}")