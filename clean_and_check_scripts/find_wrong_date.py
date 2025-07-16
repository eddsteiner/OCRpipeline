import os
from glob import glob
import pandas as pd

# === CONFIG ===
ROOT_DIR = 'output'  # Adjust as needed
TARGET_YEAR = 1952   # Change this to find other years

# === SCAN FUNCTION ===
def find_files_with_year(root_dir, target_year):
    matches = []

    for dirpath, _, _ in os.walk(root_dir):
        for file in glob(os.path.join(dirpath, '*.csv')):
            try:
                df = pd.read_csv(file, header=None)

                # Check if the first column is likely a year column
                first_col = df.iloc[:, 0]

                # Clean up values and convert to numeric
                years = pd.to_numeric(first_col, errors='coerce')

                # Check if the target year exists
                if (years > target_year).any():
                    matches.append(file)
            except Exception as e:
                print(f"Error reading {file}: {e}")

    return matches

# === RUN ===
if __name__ == '__main__':
    results = find_files_with_year(ROOT_DIR, TARGET_YEAR)

    if results:
        print(f"Found {len(results)} file(s) containing the year {TARGET_YEAR}:")
        for path in results:
            print(" -", path)
    else:
        print(f"No files found with year {TARGET_YEAR}.")
