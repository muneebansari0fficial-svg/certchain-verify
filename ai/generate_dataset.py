import cv2
import numpy as np
import os
import random
import csv
from pathlib import Path


def forge_splice(img):
    output = img.copy()
    h, w = output.shape[:2]
    x = random.randint(int(w * 0.3), int(w * 0.7))
    y = random.randint(int(h * 0.3), int(h * 0.7))
    patch_w = random.randint(80, 150)
    patch_h = random.randint(25, 45)
    cv2.rectangle(output, (x, y), (x + patch_w, y + patch_h), (255, 255, 255), -1)
    for i in range(random.randint(2, 4)):
        y_line = y + 8 + i * 8
        if y_line > y + patch_h - 5:
            break
        cv2.line(output, (x + 5, y_line), (x + patch_w - 5, y_line), (0, 0, 0), 1)
    return output


def forge_copy_move(img):
    output = img.copy()
    h, w = output.shape[:2]
    src_x = random.randint(10, w // 3)
    src_y = random.randint(10, h // 3)
    region_w = random.randint(50, 100)
    region_h = random.randint(30, 60)
    region = output[src_y:src_y + region_h, src_x:src_x + region_w].copy()
    dst_x = random.randint(w // 2, w - region_w - 10)
    dst_y = random.randint(h // 2, h - region_h - 10)
    output[dst_y:dst_y + region_h, dst_x:dst_x + region_w] = region
    return output


def forge_inpaint(img):
    output = img.copy()
    h, w = output.shape[:2]
    x = random.randint(int(w * 0.2), int(w * 0.7))
    y = random.randint(int(h * 0.2), int(h * 0.7))
    region_w = random.randint(60, 120)
    region_h = random.randint(20, 40)
    cv2.rectangle(output, (x, y), (x + region_w, y + region_h), (250, 250, 250), -1)
    noise = np.random.randint(0, 15, (region_h, region_w, 3), dtype=np.uint8)
    region = output[y:y + region_h, x:x + region_w]
    output[y:y + region_h, x:x + region_w] = cv2.add(region, noise)
    return output


def forge_double_compression(img):
    output = img.copy()
    for _ in range(3):
        _, encoded = cv2.imencode(".jpg", output, [cv2.IMWRITE_JPEG_QUALITY, 60])
        output = cv2.imdecode(encoded, cv2.IMREAD_COLOR)
    return output


FORGERY_FUNCS = {
    "splice": forge_splice,
    "copy_move": forge_copy_move,
    "inpaint": forge_inpaint,
    "double_compression": forge_double_compression
}


def generate_forgeries(genuine_dir, output_dir, labels_csv):

    genuine_dir = Path(genuine_dir)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    labels = []

    genuine_files = sorted(genuine_dir.glob("*.png"))

    if not genuine_files:
        raise Exception(f"No genuine images found in {genuine_dir}")

    print(f"Found {len(genuine_files)} genuine images\n")

    # Genuine entries
    for g_file in genuine_files:
        labels.append({
            "path": str(g_file),
            "label": 0,
            "attack": "none"
        })

    # Forgeries — source number track karo
    for g_file in genuine_files:

        img = cv2.imread(str(g_file))

        if img is None:
            continue

        # Source number nikaalo (g_0001_orig -> 0001)
        source_stem = g_file.stem
        parts = source_stem.split("_")

        if len(parts) >= 2:
            source_num = parts[1]
        else:
            source_num = "0000"

        for attack_name, attack_func in FORGERY_FUNCS.items():

            forged = attack_func(img)

            out_name = f"f_{source_num}_{attack_name}.png"
            out_path = output_dir / out_name

            cv2.imwrite(str(out_path), forged)

            labels.append({
                "path": str(out_path),
                "label": 1,
                "attack": attack_name
            })

            print(f"  Forged ({attack_name}): {out_name}")

    # Write CSV
    with open(labels_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["path", "label", "attack"])
        writer.writeheader()
        writer.writerows(labels)

    print(f"\nDone. Total samples: {len(labels)}")
    print(f"Labels saved: {labels_csv}")


if __name__ == "__main__":
    random.seed(42)

    generate_forgeries(
        genuine_dir="ai/dataset/genuine",
        output_dir="ai/dataset/forged",
        labels_csv="ai/dataset/certificate_dataset.csv"
    )