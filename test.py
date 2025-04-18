import tkinter as tk
import tkinter.font as tkFont

def is_invalid(value):
    value = value.strip().lower()
    if value in {"", "x", "nan"}:
        return True
    try:
        val = float(value)
        return not (-50 <= val <= 99)
    except:
        return True

root = tk.Tk()
text = tk.Text(root, height=10, width=80, wrap="none", font=("Courier", 11))
text.pack()

text.tag_configure("flagged", foreground="red")

rows = [
    ["2020", "25", "nan", "x", "80"],
    ["1888", "-60", "20", "45", "102"],
    ["2021", "30", "15", "x", "bad"],
]

for r, row in enumerate(rows):
    text.insert("end", f"Row {r + 1}: ")
    for c, val in enumerate(row):
        start = text.index("end")
        text.insert("end", val)
        end = text.index("end")
        if is_invalid(val):
            text.tag_add("flagged", start, end)
        if c < len(row) - 1:
            text.insert("end", "\t")
    text.insert("end", "\n")

root.mainloop()

