import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import cv2
import numpy as np

from segmentation import start_segmentation
from ocr_processor import run_ocr_on_table

# === SETTINGS ===
INPUT_ROOT = "input_tables"
OUTPUT_ROOT = "output"

calendar_order = [
    "january", "february", "march", "april", "may", "june",
    "july", "august", "september", "october", "november", "december"
]

def get_output_folder(month: str, data_type: str, table_number: str):
    if not month or not data_type:
        base = os.path.join(OUTPUT_ROOT, "miscellaneous", f"table_{table_number}")
    else:
        base = os.path.join(OUTPUT_ROOT, month, data_type, f"table_{table_number}")
    os.makedirs(base, exist_ok=True)
    return base

def get_csv_output_folder(month: str, data_type: str):
    if not month or not data_type:
        base = os.path.join(OUTPUT_ROOT, "miscellaneous", "csv_output")
    else:
        base = os.path.join(OUTPUT_ROOT, month, data_type, "csv_output")
    os.makedirs(base, exist_ok=True)
    return base

def sharpen_image(img):
    kernel = np.array([[0, -1, 0],
                       [-1, 5, -1],
                       [0, -1, 0]])
    return cv2.filter2D(img, -1, kernel)

def sharpen_segmented_images(folder_path):
    for root, _, files in os.walk(folder_path):
        for file in files:
            if file.lower().endswith(('.png', '.jpg', '.jpeg')):
                img_path = os.path.join(root, file)
                img = cv2.imread(img_path)
                if img is not None:
                    sharpened = sharpen_image(img)
                    cv2.imwrite(img_path, sharpened)

class OCRAppGUI:
    def __init__(self, root):
        self.root = root
        root.title("OCR Table Pipeline")
        root.geometry("500x400")

        self.month = tk.StringVar()
        self.data_type = tk.StringVar()
        self.table_file = tk.StringVar()
        self.table_number = tk.StringVar(value="1")

        self.build_gui()

    def build_gui(self):
        tk.Label(self.root, text="Select Month:").pack(pady=5)
        month_options = [m for m in calendar_order if os.path.isdir(os.path.join(INPUT_ROOT, m))]
        self.month_menu = ttk.Combobox(self.root, textvariable=self.month, values=month_options)
        self.month_menu.pack()

        tk.Label(self.root, text="Select Type (max or min):").pack(pady=5)
        self.type_menu = ttk.Combobox(self.root, textvariable=self.data_type, values=["max", "min"])
        self.type_menu.pack()

        tk.Button(self.root, text="Choose Table Image", command=self.select_table_file).pack(pady=5)
        self.file_label = tk.Label(self.root, text="No file selected")
        self.file_label.pack()

        tk.Label(self.root, text="Enter Table Number:").pack(pady=5)
        self.num_entry = tk.Entry(self.root, textvariable=self.table_number)
        self.num_entry.pack()

        tk.Button(self.root, text="Start Segmentation", command=self.run_segmentation).pack(pady=8)
        tk.Button(self.root, text="Run OCR", command=self.run_ocr).pack(pady=4)
        tk.Button(self.root, text="Launch Error Checker", command=self.launch_checker).pack(pady=4)

    def select_table_file(self):
        init_dir = os.path.join(INPUT_ROOT, self.month.get(), self.data_type.get()) \
            if self.month.get() and self.data_type.get() else INPUT_ROOT

        filepath = filedialog.askopenfilename(
            initialdir=init_dir,
            title="Select Table Image",
            filetypes=(("Image Files", "*.png;*.jpg;*.jpeg"),)
        )
        if filepath:
            self.table_file.set(filepath)
            self.file_label.config(text=os.path.basename(filepath))

    def run_segmentation(self):
        if not self.table_file.get():
            messagebox.showerror("Missing info", "Please select a table image.")
            return

        out_dir = get_output_folder(self.month.get(), self.data_type.get(), self.table_number.get())

        if os.path.exists(out_dir) and os.listdir(out_dir):
            overwrite = messagebox.askyesno(
                "Overwrite Existing Segmentation?",
                f"A segmented output already exists for Table {self.table_number.get()}.",
            )
            if not overwrite:
                return

        start_segmentation(self.table_file.get(), out_dir)
        sharpen_segmented_images(out_dir)
        messagebox.showinfo("Segmentation Complete", f"Segmentation and sharpening saved to:\n{out_dir}")

    def run_ocr(self):
        if not self.table_number.get():
            messagebox.showerror("Missing info", "Please enter a table number.")
            return

        segment_path = get_output_folder(self.month.get(), self.data_type.get(), self.table_number.get())
        csv_out = get_csv_output_folder(self.month.get(), self.data_type.get())
        messagebox.showinfo("Running OCR", f"Hang Tight! This might take a couple minutes!")
        run_ocr_on_table(
            segment_path, csv_out,
            self.month.get() or "miscellaneous",
            self.data_type.get() or "miscellaneous",
            self.table_number.get()
        )

    def launch_checker(self):
        try:
            import subprocess
            subprocess.Popen(["python", "error_checker_gui.py"])
        except Exception as e:
            messagebox.showerror("Error", f"Could not launch error checker: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = OCRAppGUI(root)
    root.mainloop()
