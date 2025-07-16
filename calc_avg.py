import os
import pandas as pd
import shutil
from glob import glob
import csv

# === CONFIG ===
SOURCE_ROOT = 'output'
TARGET_ROOT = 'output'
MONTHS_ORDER = [
    'january', 'february', 'march', 'april', 'may', 'june',
    'july', 'august', 'september', 'october', 'november', 'december'
]
ERROR_LOG = 'error_log.csv'
error_entries = []  # in-memory list of errors



def add_calc_avg(file_path):
    df = pd.read_csv(file_path, header=None)

    if df.shape[1] > 2:
        day_cols = df.columns[1:-1]

        # Track errors before coercion
        # Track errors before coercion
        for col in day_cols:
            for idx, val in df[col].items():
                str_val = str(val).strip().lower()

                if str_val in {"nan", "x", ""}:
                    continue  # Acceptable placeholder values

                try:
                    float(val)
                except (ValueError, TypeError):
                    error_entries.append([file_path, idx + 1, col + 1, val])


        # Coerce values and compute average
        df[day_cols] = df[day_cols].apply(pd.to_numeric, errors='coerce')
        df['calc_avg'] = df[day_cols].mean(axis=1, skipna=True)
        df.to_csv(file_path, index=False, header=False)
        print(f"✅ Updated with calc_avg: {file_path}")
    else:
        print(f"⏭️ Skipped (not enough columns): {file_path}")

for month in MONTHS_ORDER:
    for dtype in ['max', 'min']:
        csv_dir = os.path.join(SOURCE_ROOT, month, dtype, 'csv_output')
        if not os.path.isdir(csv_dir):
            continue

        csv_files = glob(os.path.join(csv_dir, '*.csv'))
        for csv_file in csv_files:
            if 'precipitation' in csv_file.lower():
                continue  # skip any unexpected precipitation file
            print(f"Processing: {csv_file}")
            add_calc_avg(csv_file)





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

