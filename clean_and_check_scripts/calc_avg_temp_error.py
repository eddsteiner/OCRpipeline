import os
import pandas as pd
from glob import glob

# CONFIG
DATA_ROOT = 'collected_csvs'
MONTHS = [
    'january', 'february', 'march', 'april', 'may', 'june',
    'july', 'august', 'september', 'october', 'november', 'december'
]

total_error = 0
total_count = 0
errors_by_file = []

def compute_file_error(file_path):
    global total_error, total_count
    df = pd.read_csv(file_path, header=None)

    if df.shape[1] < 2:
        print(f"⏭️ Skipping {file_path} (not enough columns)")
        return

    # Compare second-to-last column vs last column
    left_col = df.shape[1] - 2
    right_col = df.shape[1] - 1

    try:
        base = df[left_col]
        change = df[right_col]
        percent_error = abs(change - base) / base.abs()

        valid_errors = percent_error[base != 0].dropna()

        total_error += valid_errors.sum()
        total_count += valid_errors.count()
        errors_by_file.append(file_path)
    except Exception as e:
        print(f"❌ Error comparing cols {left_col} and {right_col} in {file_path}: {e}")



# Walk through all months and filter only min and max files
for month in MONTHS:
    folder = os.path.join(DATA_ROOT, month)
    if not os.path.isdir(folder):
        continue

    # Only include files containing '_min_' or '_max_'
    for file_path in glob(os.path.join(folder, '*_min_*.csv')) + glob(os.path.join(folder, '*_max_*.csv')):
        compute_file_error(file_path)

# Final result
if total_count > 0:
    avg_error = total_error / total_count
    print(f"\n✅ Average percentage error across all min/max files: {avg_error:.3f}%")
    print(f"Files processed: {len(errors_by_file)}")
    print(f"Total cells compared: {total_count}")
else:
    print("❌ No valid temperature comparisons found.")
