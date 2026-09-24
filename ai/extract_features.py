import cv2
import numpy as np


def extract_features(image_path: str) -> dict:
    """
    Extract 16 forensic features from a certificate image.
    """

    img = cv2.imread(image_path)

    if img is None:
        raise Exception(f"Could not read image: {image_path}")

    # Resize for consistency
    img = cv2.resize(img, (800, 600))

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    features = {}

    # ============================================
    # 1-2: ELA (Error Level Analysis)
    # ============================================

    _, encoded = cv2.imencode(
        ".jpg", img, [cv2.IMWRITE_JPEG_QUALITY, 90]
    )

    recompressed = cv2.imdecode(encoded, cv2.IMREAD_COLOR)

    ela = cv2.absdiff(img, recompressed)

    ela_gray = cv2.cvtColor(ela, cv2.COLOR_BGR2GRAY)

    features["ela_mean"] = float(np.mean(ela_gray))
    features["ela_std"] = float(np.std(ela_gray))

    # ============================================
    # 3-4: Noise features
    # ============================================

    blur = cv2.GaussianBlur(gray, (5, 5), 0)

    noise = cv2.absdiff(gray, blur)

    features["noise_mean"] = float(np.mean(noise))
    features["noise_std"] = float(np.std(noise))

    # ============================================
    # 5-6: Laplacian
    # ============================================

    laplacian = cv2.Laplacian(gray, cv2.CV_64F)

    features["laplacian_mean"] = float(np.mean(np.abs(laplacian)))
    features["laplacian_var"] = float(np.var(laplacian))

    # ============================================
    # 7-8: DCT
    # ============================================

    dct = cv2.dct(np.float32(gray) / 255.0)

    features["dct_mean"] = float(np.mean(np.abs(dct)))
    features["dct_std"] = float(np.std(dct))

    # ============================================
    # 9-10: Edge density
    # ============================================

    edges = cv2.Canny(gray, 50, 150)

    features["edge_density"] = float(np.sum(edges > 0) / edges.size)
    features["edge_mean"] = float(np.mean(edges))

    # ============================================
    # 11-12: Saturation & Value
    # ============================================

    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    features["saturation_mean"] = float(np.mean(hsv[:, :, 1]))
    features["value_mean"] = float(np.mean(hsv[:, :, 2]))

    # ============================================
    # 13-14: Sobel
    # ============================================

    sobel_x = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
    sobel_y = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)

    features["sobel_x_mean"] = float(np.mean(np.abs(sobel_x)))
    features["sobel_y_mean"] = float(np.mean(np.abs(sobel_y)))

    # ============================================
    # 15-16: Histogram stats
    # ============================================

    hist = cv2.calcHist([gray], [0], None, [256], [0, 256])

    hist = hist.flatten() / hist.sum()

    features["hist_entropy"] = float(
        -np.sum(hist * np.log2(hist + 1e-10))
    )

    features["hist_peak"] = float(np.max(hist))

    return features


FEATURE_NAMES = [
    "ela_mean", "ela_std",
    "noise_mean", "noise_std",
    "laplacian_mean", "laplacian_var",
    "dct_mean", "dct_std",
    "edge_density", "edge_mean",
    "saturation_mean", "value_mean",
    "sobel_x_mean", "sobel_y_mean",
    "hist_entropy", "hist_peak"
]


def features_to_vector(features: dict) -> list:
    return [features[k] for k in FEATURE_NAMES]


# ============================================
# CLI TEST
# ============================================

if __name__ == "__main__":

    import sys
    import json

    if len(sys.argv) < 2:
        print("Usage: python extract_features.py <image_path>")
        sys.exit(1)

    image_path = sys.argv[1]

    try:
        feats = extract_features(image_path)
        print(json.dumps(feats, indent=2))

    except Exception as e:
        print(f"ERROR: {str(e)}", file=sys.stderr)
        sys.exit(1)