import pandas as pd
import os
from glob import glob

# === CONFIG ===
ROOT_DIR = 'output'  # <-- Root folder for months (adjust this path if needed)
OUTPUT_FILE = 'master_temperature_data.csv'

# === HELPERS ===
month_to_number = {
    'january': '01', 'february': '02', 'march': '03', 'april': '04',
    'may': '05', 'june': '06', 'july': '07', 'august': '08',
    'september': '09', 'october': '10', 'november': '11', 'december': '12'
}

def load_and_melt(file_path, value_name):
    df = pd.read_csv(file_path, header=None)
   # Only keep first 32 columns (year + 31 days)
    df = df.iloc[:, :32]  # 0 = year, 1-31 = days

    df = df.rename(columns={0: 'year'})
    df_melted = df.melt(id_vars=['year'], var_name='day', value_name=value_name)

    # Correct day index (since day columns start at index 1 in df)
    df_melted['day'] = df_melted['day']  # already correct after iloc slicing
    df_melted['day'] = df_melted['day'].astype(int)

    return df_melted

# === PROCESS ===
all_data = []

# Iterate over months
for month in month_to_number.keys():
    month_dir = os.path.join(ROOT_DIR, month)
    if not os.path.exists(month_dir):
        continue  # skip non-existent months

    month_num = month_to_number[month]
    month_data = None

    for var_type in ['max', 'min', 'precipitation']:
        csv_output_dir = os.path.join(month_dir, var_type, 'csv_output')
        if not os.path.isdir(csv_output_dir):
            continue  # skip if folder missing
        
        files = glob(os.path.join(csv_output_dir, f'{month}_{var_type}_*.csv'))
        if not files:
            continue  # skip if no files for this type
        
        # Process all files of this var_type
        var_dataframes = []
        for file_path in files:
            df_melted = load_and_melt(file_path, var_type)
            df_melted['month'] = month_num
            # Convert to numeric, coerce bad values to NaN
            df_melted['year'] = pd.to_numeric(df_melted['year'], errors='coerce')

            # Drop NaNs after coercion
            df_melted = df_melted[df_melted['year'].notna()]

            # Convert float years like 2003.0 -> 2003 safely
            df_melted['year'] = df_melted['year'].astype(int)

            # Drop implausible years (e.g., <1800, >2025)
            df_melted = df_melted[df_melted['year'].between(1800, 2025)]



            df_melted['date'] = df_melted.apply(lambda row: f"{int(row['day']):02d}-{row['month']}-{int(row['year'])}"if pd.notnull(row['year']) and pd.notnull(row['day']) else None,axis=1)

            var_dataframes.append(df_melted[['date', var_type]])
        
        if var_dataframes:
            var_df = pd.concat(var_dataframes, ignore_index=True)
            if month_data is None:
                month_data = var_df
            else:
                month_data = month_data.merge(var_df, on='date', how='outer')

    if month_data is not None:
        all_data.append(month_data)

# === MERGE ALL MONTHS ===
if all_data:
    final_df = pd.concat(all_data, ignore_index=True)
    final_df = final_df[['date', 'max', 'min', 'precipitation']]

    # --- SORT PROPERLY ---
    # Split date into day, month, year as integers
    final_df[['day', 'month', 'year']] = final_df['date'].str.split('-', expand=True).astype(int)

    # Sort by year, month, day
    final_df = final_df.sort_values(by=['year', 'month', 'day'])

    # Rebuild date column
    final_df['date'] = final_df.apply(lambda row: f"{row['day']:02d}-{row['month']:02d}-{row['year']}", axis=1)

    # Drop helper columns
    final_df = final_df[['date', 'max', 'min', 'precipitation']]

    # Output final CSV
    final_df.to_csv(OUTPUT_FILE, index=False)
    print(f"Done! Output saved to {OUTPUT_FILE}")
else:
    print("No data found to process.")


