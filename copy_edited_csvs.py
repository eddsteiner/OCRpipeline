import os
import shutil
from glob import glob

# === CONFIG ===
SOURCE_ROOT = 'output'
DEST_ROOT = 'collected_csv_final'
MONTHS = [
    'january', 'february', 'march', 'april', 'may', 'june',
    'july', 'august', 'september', 'october', 'november', 'december'
]
TYPES = ['max', 'min']

# === MAIN COPY LOOP ===
for month in MONTHS:
    for dtype in TYPES:
        csv_dir = os.path.join(SOURCE_ROOT, month, dtype, 'csv_output')
        if not os.path.isdir(csv_dir):
            continue

        csv_files = glob(os.path.join(csv_dir, '*.csv'))
        if not csv_files:
            continue

        dest_month_dir = os.path.join(DEST_ROOT, month)
        os.makedirs(dest_month_dir, exist_ok=True)

        for csv_file in csv_files:
            filename = os.path.basename(csv_file)
            dest_path = os.path.join(dest_month_dir, filename)
            shutil.copy2(csv_file, dest_path)
            print(f"✅ Copied: {csv_file} -> {dest_path}")

print("\n✅ All edited CSVs copied to collected_csv_final.")
