import cv2
import numpy as np
import random
from pathlib import Path


# ============================================
# AUGMENTATION FUNCTIONS
# ============================================

def aug_rotate(img, angle=None):
    if angle is None:
        angle = random.choice([-10, -5, 5, 10])

    h, w = img.shape[:2]
    center = (w // 2, h // 2)

    M = cv2.getRotationMatrix2D(center, angle, 1.0)

    return cv2.warpAffine(
        img, M, (w, h),
        borderMode=cv2.BORDER_REPLICATE
    )


def aug_brightness(img, factor=None):
    if factor is None:
        factor = random.uniform(0.85, 1.15)

    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV).astype(np.float32)

    hsv[:, :, 2] = np.clip(hsv[:, :, 2] * factor, 0, 255)

    return cv2.cvtColor(hsv.astype(np.uint8), cv2.COLOR_HSV2BGR)


def aug_contrast(img, alpha=None):
    if alpha is None:
        alpha = random.uniform(0.8, 1.2)

    return cv2.convertScaleAbs(img, alpha=alpha, beta=0)


def aug_blur(img, ksize=None):
    if ksize is None:
        ksize = random.choice([3, 5])

    return cv2.GaussianBlur(img, (ksize, ksize), 0)


def aug_noise(img, intensity=None):
    if intensity is None:
        intensity = random.uniform(5, 15)

    noise = np.random.normal(0, intensity, img.shape).astype(np.float32)

    noisy = img.astype(np.float32) + noise

    return np.clip(noisy, 0, 255).astype(np.uint8)


def aug_scale(img, scale=None):
    if scale is None:
        scale = random.choice([0.95, 1.05])

    h, w = img.shape[:2]

    new_w = int(w * scale)
    new_h = int(h * scale)

    resized = cv2.resize(img, (new_w, new_h))

    if scale < 1:
        # Pad
        pad_w = (w - new_w) // 2
        pad_h = (h - new_h) // 2

        return cv2.copyMakeBorder(
            resized,
            pad_h, h - new_h - pad_h,
            pad_w, w - new_w - pad_w,
            cv2.BORDER_REPLICATE
        )
    else:
        # Crop
        x = (new_w - w) // 2
        y = (new_h - h) // 2

        return resized[y:y + h, x:x + w]


def aug_flip(img):
    return cv2.flip(img, 1)


def aug_jpeg(img, quality=None):
    if quality is None:
        quality = random.choice([70, 80, 90])

    _, encoded = cv2.imencode(
        ".jpg", img, [cv2.IMWRITE_JPEG_QUALITY, quality]
    )

    return cv2.imdecode(encoded, cv2.IMREAD_COLOR)


# ============================================
# AUGMENTATION PIPELINE
# ============================================

AUGMENTATIONS = [
    ("rot1", lambda im: aug_rotate(im, -10)),
    ("rot2", lambda im: aug_rotate(im, 10)),
    ("bright1", lambda im: aug_brightness(im, 0.85)),
    ("bright2", lambda im: aug_brightness(im, 1.15)),
    ("contrast1", lambda im: aug_contrast(im, 0.85)),
    ("contrast2", lambda im: aug_contrast(im, 1.15)),
    ("blur1", lambda im: aug_blur(im, 3)),
    ("blur2", lambda im: aug_blur(im, 5)),
    ("noise1", lambda im: aug_noise(im, 8)),
    ("noise2", lambda im: aug_noise(im, 12)),
    ("scale1", lambda im: aug_scale(im, 0.95)),
    ("scale2", lambda im: aug_scale(im, 1.05)),
    ("flip", lambda im: aug_flip(im)),
    ("jpeg1", lambda im: aug_jpeg(im, 70)),
    ("jpeg2", lambda im: aug_jpeg(im, 85)),
]


def augment_genuine_images(input_dir, output_dir):
    """
    Generate 15 augmented versions per genuine image.
    """

    input_dir = Path(input_dir)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    genuine_files = sorted(input_dir.glob("*.png"))

    if not genuine_files:
        raise Exception(f"No images in {input_dir}")

    print(f"Found {len(genuine_files)} genuine images")
    print(f"Applying {len(AUGMENTATIONS)} augmentations each")
    print(f"Expected total: {len(genuine_files) * (len(AUGMENTATIONS) + 1)}\n")

    counter = 1

    for g_file in genuine_files:

        img = cv2.imread(str(g_file))

        if img is None:
            continue

        # Save original
        out_name = f"g_{counter:04d}_orig.png"
        cv2.imwrite(str(output_dir / out_name), img)

        counter += 1

        print(f"  {g_file.name}:")

        for aug_name, aug_func in AUGMENTATIONS:

            try:
                aug_img = aug_func(img)

                out_name = f"g_{counter:04d}_{aug_name}.png"

                cv2.imwrite(str(output_dir / out_name), aug_img)

                counter += 1

            except Exception as e:
                print(f"    Skip {aug_name}: {e}")

        print(f"    → {len(AUGMENTATIONS) + 1} versions created")

    print(f"\nDone. Total genuine images: {counter - 1}")


# ============================================
# CLI
# ============================================

if __name__ == "__main__":

    random.seed(42)

    augment_genuine_images(
        input_dir="ai/dataset/genuine_original",
        output_dir="ai/dataset/genuine"
    )