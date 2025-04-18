import os
import pandas as pd
from google.cloud import vision

# Initialize Google Vision client
client = vision.ImageAnnotatorClient()

def process_image(image_path):
    with open(image_path, "rb") as f:
        content = f.read()

    image = vision.Image(content=content)
    image_context = vision.ImageContext(language_hints=["en"])  #Hint for English

    response = client.text_detection(image=image, image_context=image_context)
    texts = response.text_annotations

    return texts[0].description.strip() if texts else ""


def run_ocr_on_table(table_path, csv_output_folder, month, data_type, table_number):
    data = []

    # Process all row folders
    for row_folder in sorted(os.listdir(table_path), key=lambda x: int(x.split('_')[-1])):
        row_path = os.path.join(table_path, row_folder)
        if not os.path.isdir(row_path):
            continue

        row_data = []
        for col_file in sorted(os.listdir(row_path), key=lambda x: int(x.split('_')[-1].split('.')[0])):
            col_path = os.path.join(row_path, col_file)
            if col_file.lower().endswith(".png"):
                extracted_text = process_image(col_path)
                row_data.append(extracted_text)

        data.append(row_data)

    # Save CSV
    os.makedirs(csv_output_folder, exist_ok=True)
    csv_filename = f"{month}_{data_type}_{table_number}.csv"
    csv_path = os.path.join(csv_output_folder, csv_filename)
    pd.DataFrame(data).to_csv(csv_path, index=False, header=False)

    print(f"✅ OCR finished and saved: {csv_path}")
