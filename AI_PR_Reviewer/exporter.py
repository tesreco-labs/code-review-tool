import csv


def save_dataset(rows, filename="outputs/dataset.csv"):

    with open(filename, "w", newline="", encoding="utf-8") as file:

        writer = csv.writer(file)

        writer.writerow([
            "PR Number",
            "Title",
            "File",
            "Change Type",
            "Old Code",
            "New Code",
            "Review Comment"
        ])

        writer.writerows(rows)

    print(f"\nDataset saved to {filename}")