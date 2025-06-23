import cv2
import os
import math
import numpy as np

for filename in os.listdir(os.path.join(os.path.dirname(__file__), "key")):
    if filename.endswith(".json"):
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.path.join(os.path.dirname(__file__), "key", filename)
        break

def start_segmentation(image_path, output_dir):
    img = cv2.imread(image_path)
    if img is None:
        print(f"❌ Could not load image: {image_path}")
        return

    img_original = img.copy()
    img_copy = img.copy()
    row_lines = []
    col_lines = []
    drawing_mode = ["row"]  # Can be "row", "col", or "rotate"
    rotation_angle = [0.0]  # float for precise angle control

    def redraw_lines():
        nonlocal img_copy
        center = (img.shape[1] // 2, img.shape[0] // 2)
        rot_matrix = cv2.getRotationMatrix2D(center, rotation_angle[0], 1.0)
        rotated = cv2.warpAffine(img, rot_matrix, (img.shape[1], img.shape[0]))
        img_copy = rotated.copy()
        for y in row_lines:
            cv2.line(img_copy, (0, y), (img.shape[1], y), (0, 255, 0), 2)
        for x in col_lines:
            cv2.line(img_copy, (x, 0), (x, img.shape[0]), (255, 0, 0), 2)
        if drawing_mode[0] == "rotate":
            cv2.putText(img_copy, f"Rotation: {rotation_angle[0]:.2f}", (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)


    def draw_line(event, x, y, flags, param):
        if drawing_mode[0] in ["row", "col"]:
            if event == cv2.EVENT_LBUTTONDOWN:
                if drawing_mode[0] == "row":
                    row_lines.append(y)
                elif drawing_mode[0] == "col":
                    col_lines.append(x)
                redraw_lines()
                cv2.imshow("Draw Grid", img_copy)
            elif event == cv2.EVENT_RBUTTONDOWN:
                if drawing_mode[0] == "row" and row_lines:
                    row_lines.pop()
                elif drawing_mode[0] == "col" and col_lines:
                    col_lines.pop()
                redraw_lines()
                cv2.imshow("Draw Grid", img_copy)
        

    def handle_rotate_mode():
        print("🔄 Rotate mode: Press 'l' to rotate left, 'r' to rotate right, or 'Enter' to exit rotate mode.")
        while True:
            key = cv2.waitKey(0)
            if key == 27:
                cv2.destroyAllWindows()
                print("🛑 Segmentation canceled.")
                exit()
            elif key == 13:
                print("✅ Exited rotate mode.")
                break
            elif key == ord('l'):
                rotation_angle[0] -= 0.25
                redraw_lines()
                cv2.imshow("Draw Grid", img_copy)
            elif key == ord('r'):
                rotation_angle[0] += 0.25
                redraw_lines()
                cv2.imshow("Draw Grid", img_copy)

    cv2.namedWindow("Draw Grid", cv2.WINDOW_NORMAL)
    cv2.resizeWindow("Draw Grid", 1600, 800)
    cv2.setMouseCallback("Draw Grid", draw_line)

    print("📏 Draw ROW lines (left click to add, right click to undo). Press 'r' to rotate. Press any key to continue to columns.")
    drawing_mode[0] = "row"
    redraw_lines()
    cv2.imshow("Draw Grid", img_copy)

    while True:
        key = cv2.waitKey(0)
        if key == 27:
            cv2.destroyAllWindows()
            print("🛑 Segmentation canceled.")
            return
        elif key == ord('r'):
            drawing_mode[0] = "rotate"
            redraw_lines()
            cv2.imshow("Draw Grid", img_copy)
            handle_rotate_mode()
            drawing_mode[0] = "row"
            redraw_lines()
            cv2.imshow("Draw Grid", img_copy)
        else:
            break

    print("📐 Now drawing COLUMNS. Press 'r' to rotate. Press any key when done.")
    drawing_mode[0] = "col"
    redraw_lines()
    cv2.imshow("Draw Grid", img_copy)

    while True:
        key = cv2.waitKey(0)
        if key == 27:
            cv2.destroyAllWindows()
            print("🛑 Segmentation canceled.")
            return
        elif key == ord('r'):
            drawing_mode[0] = "rotate"
            redraw_lines()
            cv2.imshow("Draw Grid", img_copy)
            handle_rotate_mode()
            drawing_mode[0] = "col"
            redraw_lines()
            cv2.imshow("Draw Grid", img_copy)
        else:
            break

    cv2.destroyAllWindows()

    row_lines = sorted(set(row_lines))
    col_lines = sorted(set(col_lines))
    row_lines.insert(0, 0)
    row_lines.append(img.shape[0])
    col_lines.insert(0, 0)
    col_lines.append(img.shape[1])

    center = (img.shape[1] // 2, img.shape[0] // 2)
    rot_matrix = cv2.getRotationMatrix2D(center, rotation_angle[0], 1.0)
    rotated_img = cv2.warpAffine(img, rot_matrix, (img.shape[1], img.shape[0]))

    for i in range(len(row_lines) - 1):
        row_folder = os.path.join(output_dir, f"row_{i+1}")
        os.makedirs(row_folder, exist_ok=True)
        for j in range(len(col_lines) - 1):
            cell_crop = rotated_img[row_lines[i]:row_lines[i+1], col_lines[j]:col_lines[j+1]]
            cell_path = os.path.join(row_folder, f"col_{j+1}.png")
            cv2.imwrite(cell_path, cell_crop)

    print(f"✅ Saved {len(row_lines)-1} rows and {len(col_lines)-1} columns to {output_dir}")
