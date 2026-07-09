import pandas as pd
import glob
import os

# Folder containing the CSV parts
folder_path = "data"

# Find all CSV files
csv_files = sorted(glob.glob(os.path.join(folder_path, "dataset_part*.csv")))

print("Files found:")
for file in csv_files:
    print(file)

# Read and combine all CSVs
df_list = [pd.read_csv(file) for file in csv_files]
merged_df = pd.concat(df_list, ignore_index=True)

# Save merged file
output_file = os.path.join(folder_path, "merged_dataset.csv")
merged_df.to_csv(output_file, index=False)

print(f"\n✅ Merged {len(csv_files)} files.")
print(f"Total Rows: {len(merged_df)}")
print(f"Saved as: {output_file}")