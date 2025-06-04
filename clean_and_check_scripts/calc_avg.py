import os
import pandas as pd
import shutil
from glob import glob
import csv

# === CONFIG ===
SOURCE_ROOT = 'output'
TARGET_ROOT = 'collected_csvs'
MONTHS_ORDER = [
    'january', 'february', 'march', 'april', 'may', 'june',
    'july', 'august', 'september', 'october', 'november', 'december'
]
ERROR_LOG = 'error_log.csv'
error_entries = []  # in-memory list of errors

# === STEP 1: Copy all CSVs to centralized folder grouped by month ===  USE ONLY TO COPY AND AGGREGATE ALL OUPUT CSVS INTO ONE FOLDER
for month in MONTHS_ORDER:
    month_path = os.path.join(SOURCE_ROOT, month)
    if not os.path.isdir(month_path):
        continue

    for root, dirs, files in os.walk(month_path):
        if 'csv_output' in root:
            csv_files = glob(os.path.join(root, '*.csv'))
            for csv_file in csv_files:
                os.makedirs(os.path.join(TARGET_ROOT, month), exist_ok=True)
                filename = os.path.basename(csv_file)
                dest_path = os.path.join(TARGET_ROOT, month, filename)
                shutil.copy2(csv_file, dest_path)
                print(f"Copied: {csv_file} -> {dest_path}")

def add_calc_avg(file_path):
    df = pd.read_csv(file_path, header=None)

    if df.shape[1] > 2:
        day_cols = df.columns[1:-1]

        # Track errors before coercion
        for col in day_cols:
            for idx, val in df[col].items():
                try:
                    float(val)
                except (ValueError, TypeError):
                    error_entries.append([file_path, idx + 1, col + 1, val])  # store row/col 1-based

        # Coerce values and compute average
        df[day_cols] = df[day_cols].apply(pd.to_numeric, errors='coerce')
        df['calc_avg'] = df[day_cols].mean(axis=1, skipna=True)
        df.to_csv(file_path, index=False, header=False)
        print(f"✅ Updated with calc_avg: {file_path}")
    else:
        print(f"⏭️ Skipped (not enough columns): {file_path}")

# Run calc_avg on new collected files
for month in MONTHS_ORDER:
    month_dir = os.path.join(TARGET_ROOT, month)
    if os.path.isdir(month_dir):
        csvs = glob(os.path.join(month_dir, '*.csv'))
        for csv_file in csvs:
            add_calc_avg(csv_file)

if error_entries:
    with open(ERROR_LOG, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['file', 'row', 'col', 'value'])
        writer.writerows(error_entries)
    print(f"\n⚠️ Error log saved to: {ERROR_LOG}")
else:
    print("\n✅ No errors detected.")

