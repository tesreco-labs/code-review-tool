import pandas as pd
import os
import glob

INPUT_FOLDER = "data/raw"
OUTPUT_FOLDER = "data/categorized"

os.makedirs(OUTPUT_FOLDER, exist_ok=True)


def categorize(comment):

    comment = str(comment).lower()

    if any(word in comment for word in [
        "bug","incorrect","wrong","fix","error","fails","failure"
    ]):
        return "Bug"

    elif any(word in comment for word in [
        "performance","slow","efficient","optimize","faster","memory"
    ]):
        return "Performance"

    elif any(word in comment for word in [
        "doc","docs","documentation","docstring","comment"
    ]):
        return "Documentation"

    elif any(word in comment for word in [
        "test","pytest","unit test","integration test","coverage"
    ]):
        return "Testing"

    elif any(word in comment for word in [
        "style","pep8","format","formatting","spacing","indent"
    ]):
        return "Code Style"

    elif any(word in comment for word in [
        "rename","naming","variable name","method name"
    ]):
        return "Naming"

    elif any(word in comment for word in [
        "refactor","cleanup","simplify","split","extract"
    ]):
        return "Refactoring"

    elif any(word in comment for word in [
        "security","unsafe","vulnerability","inject"
    ]):
        return "Security"

    elif any(word in comment for word in [
        "architecture","design","structure"
    ]):
        return "Architecture"

    elif any(word in comment for word in [
        "api","interface","endpoint"
    ]):
        return "API Design"

    elif any(word in comment for word in [
        "best practice","pythonic","prefer","recommend","should use"
    ]):
        return "Best Practice"

    elif "?" in comment:
        return "Question/Discussion"

    else:
        return "Other"


files = glob.glob(os.path.join(INPUT_FOLDER, "*.csv"))

for file in files:

    print(f"Processing {file}")

    df = pd.read_csv(file)

    df["category"] = df["review_comment"].apply(categorize)

    output_file = os.path.join(
        OUTPUT_FOLDER,
        os.path.basename(file)
    )

    df.to_csv(output_file, index=False)

    print(f"Saved -> {output_file}")

print("\nAll datasets categorized successfully.")