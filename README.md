# OCRpipeline
This project is a user-guided OCR pipeline designed for extracting structured data from scanned, handwritten tables. It is especially effective for digitizing legacy documents such as agricultural logs, historical field notebooks, or other analog forms where automated OCR tools typically fail.

## Features

- **Manual Table Segmentation** – Visually define rows and columns on scanned images using an interactive drawing tool.
- **OCR with Google Cloud Vision** – Automatically extracts text from each segmented cell using the Google Cloud Vision API.
- **Correction & Validation Interface** – Review OCR results cell-by-cell alongside the image snippet; confirm or correct in real time.
- **Outlier Detection** – Highlights statistically unusual entries for manual review.
- **CSV Export** – Outputs clean, structured data ready for analysis or database ingestion.

## How to Run

### 1. Add Google Cloud Vision API Key

Place your `.json` key file from google cloud console in the `key/` folder. The application will automatically find and use it.

### 2. Launch the Application

```bash
python app.py
```

## Dependencies

- **Python 3.x**
- **OpenCV**
- **TKinter**
- **Pandas**
- **Pillow**
- **Google Cloud Vision API Client**

## Why Manual Segmentation?

Fully automatic OCR solutions often fail on poorly scanned, handwritten, or skewed tables. This tool allows users to guide the segmentation process, ensuring accurate structure detection and higher OCR reliability.
