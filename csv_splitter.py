import csv
import os

# ==========================================
# Configuration
# ==========================================

INPUT_FILES = [
    "dataset.csv",
    "dataset2.csv"
]

MAX_FILE_SIZE_MB = 90      # Keep below GitHub's 100 MB limit
OUTPUT_DIR = "split_csv"

# ==========================================

MAX_SIZE = MAX_FILE_SIZE_MB * 1024 * 1024

os.makedirs(OUTPUT_DIR, exist_ok=True)


def split_csv(file_path):
    filename = os.path.splitext(os.path.basename(file_path))[0]

    with open(file_path, "r", encoding="utf-8", newline="") as infile:

        reader = csv.reader(infile)

        header = next(reader)

        part = 1

        output_path = os.path.join(
            OUTPUT_DIR,
            f"{filename}_part{part}.csv"
        )

        outfile = open(output_path, "w", encoding="utf-8", newline="")
        writer = csv.writer(outfile)

        writer.writerow(header)

        print(f"Creating {output_path}")

        for row in reader:

            writer.writerow(row)

            # Check actual file size
            if outfile.tell() >= MAX_SIZE:
                outfile.close()

                print(
                    f"Finished Part {part} "
                    f"({os.path.getsize(output_path)/(1024*1024):.2f} MB)"
                )

                part += 1

                output_path = os.path.join(
                    OUTPUT_DIR,
                    f"{filename}_part{part}.csv"
                )

                outfile = open(output_path, "w", encoding="utf-8", newline="")
                writer = csv.writer(outfile)

                writer.writerow(header)

                print(f"Creating {output_path}")

        outfile.close()

        print(
            f"Finished Part {part} "
            f"({os.path.getsize(output_path)/(1024*1024):.2f} MB)"
        )


# ==========================================

for file in INPUT_FILES:
    print(f"\nSplitting {file}")
    split_csv(file)

print("\nAll files split successfully!")