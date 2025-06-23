# manual_input_gui.py

#NOT IN USE NEED TO REFINE LATER


import os
import sys
import tkinter as tk
from tkinter import messagebox
from tkinter import ttk

import pandas as pd
import cv2
from PIL import Image, ImageTk

# Validate CLI arguments
if len(sys.argv) != 4:
    print("Usage: python manual_input_gui.py <month> <type_folder> <table_number>")
    sys.exit(1)

month, dtype_folder, table_number = sys.argv[1:]

BASE_DIR = "output"
segment_path = os.path.join(BASE_DIR, month, dtype_folder, f"table_{table_number}")
csv_out_path = os.path.join(BASE_DIR, month, dtype_folder, "csv_output")

class ManualInputGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Manual Input")

        self.rows = 22
        self.cols = 33
        self.row_idx = 0
        self.col_idx = 0
        self.data = []
        self.selected_file = None

        self.images = self.collect_images(segment_path)
        self.setup_gui()
        self.load_or_prompt_csv()
        self.load_image()

    def collect_images(self, path):
        all_imgs = []
        for row_folder in sorted(os.listdir(path)):
            row_path = os.path.join(path, row_folder)
            if os.path.isdir(row_path) and row_folder.startswith("row_"):
                for col_file in sorted(os.listdir(row_path), key=lambda x: int(x.split('_')[1].split('.')[0])):
                    if col_file.lower().endswith(('.png', '.jpg', '.jpeg')):
                        all_imgs.append(os.path.join(row_path, col_file))
        return all_imgs

    def setup_gui(self):
        self.left = tk.Frame(self.root)
        self.left.pack(side="left", padx=10, pady=10)

        self.img_panel = tk.Label(self.left)
        self.img_panel.pack()

        self.input_text = tk.StringVar()
        self.entry = tk.Entry(self.left, textvariable=self.input_text)
        self.entry.pack(pady=(10, 0))
        self.entry.bind("<Return>", self.handle_enter_key)
        self.entry.bind("/", self.handle_slash_key)

        button_frame = tk.Frame(self.left)
        button_frame.pack(pady=5)
        tk.Button(button_frame, text="Confirm", command=self.save_and_next).pack(side="left", padx=5)
        tk.Button(button_frame, text="Save", command=self.save_csv).pack(side="left", padx=5)

        self.right = tk.Frame(self.root)
        self.right.pack(side="left", padx=10, pady=10)

        self.text_display = tk.Text(self.right, height=30, width=80)
        self.text_display.pack()

    def load_image(self):
        if self.row_idx >= self.rows:
            self.finish()
            return
        img_index = self.row_idx * self.cols + self.col_idx
        if img_index >= len(self.images):
            self.finish()
            return
        img_path = self.images[img_index]
        img = cv2.imread(img_path)
        if img is None:
            self.img_panel.config(text="(Could not load image)")
            return
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        img = cv2.resize(img, (300, 300))
        imgtk = ImageTk.PhotoImage(image=Image.fromarray(img))
        self.img_panel.config(image=imgtk)
        self.img_panel.image = imgtk

    def save_and_next(self):
        value = self.input_text.get().strip()
        if value == "":
            value = "NaN"
        else:
            value = value.replace("/", "\n")

        self.data[self.row_idx][self.col_idx] = value
        self.text_display.insert(tk.END, f"[{self.row_idx+1},{self.col_idx+1}]: {value}\n")
        self.input_text.set("")

        self.col_idx += 1
        if self.col_idx >= self.cols:
            self.col_idx = 0
            self.row_idx += 1

        self.load_image()

    def finish(self):
        df = pd.DataFrame(self.data)
        os.makedirs(csv_out_path, exist_ok=True)
        save_path = os.path.join(csv_out_path, self.selected_file or f"manual_input_table_{table_number}.csv")
        df.to_csv(save_path, index=False, header=False)
        messagebox.showinfo("Done", f"CSV saved to:\n{save_path}")
        self.root.quit()

    def handle_enter_key(self, event):
        self.save_and_next()
        return "break"

    def handle_slash_key(self, event):
        current = self.input_text.get()
        self.input_text.set(current + "\n")
        return "break"

    def save_csv(self):
        df = pd.DataFrame(self.data)
        os.makedirs(csv_out_path, exist_ok=True)
        save_path = os.path.join(csv_out_path, self.selected_file or f"manual_input_table_{table_number}.csv")
        df.to_csv(save_path, index=False, header=False)
        messagebox.showinfo("Saved", f"Progress saved to:\n{save_path}")

    def load_or_prompt_csv(self):
        os.makedirs(csv_out_path, exist_ok=True)
        existing_files = [f for f in os.listdir(csv_out_path) if f.endswith(".csv")]

        prompt = tk.Toplevel(self.root)
        prompt.title("Choose or Name Your CSV")

        tk.Label(prompt, text="Select an existing file or enter a new filename:").pack(pady=5)
        var = tk.StringVar()
        file_dropdown = ttk.Combobox(prompt, values=existing_files, textvariable=var)
        file_dropdown.pack()

        new_file_entry = tk.Entry(prompt)
        new_file_entry.pack(pady=5)
        new_file_entry.insert(0, f"manual_input_table_{table_number}.csv")

        def confirm():
            choice = new_file_entry.get().strip() or var.get().strip()
            if not choice.endswith(".csv"):
                choice += ".csv"
            self.selected_file = choice
            csv_path = os.path.join(csv_out_path, self.selected_file)

            if os.path.exists(csv_path):
                df = pd.read_csv(csv_path, header=None, dtype=str)
                df.fillna("NaN", inplace=True)
                self.data = df.values.tolist()
                self.rows = len(self.data)
                self.cols = len(self.data[0]) if self.rows > 0 else 33
                for r, row in enumerate(self.data):
                    for c, val in enumerate(row):
                        if val != "NaN":
                            self.text_display.insert(tk.END, f"[{r+1},{c+1}]: {val}\n")
                for r in range(self.rows):
                    for c in range(self.cols):
                        if self.data[r][c] == "NaN":
                            self.row_idx, self.col_idx = r, c
                            return
            else:
                self.data = [["NaN" for _ in range(self.cols)] for _ in range(self.rows)]
                self.row_idx, self.col_idx = 0, 0

            prompt.destroy()

        tk.Button(prompt, text="Continue", command=confirm).pack(pady=5)
        prompt.transient(self.root)
        prompt.grab_set()
        self.root.wait_window(prompt)


if __name__ == "__main__":
    root = tk.Tk()
    app = ManualInputGUI(root)
    root.mainloop()
