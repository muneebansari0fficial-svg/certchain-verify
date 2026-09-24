import sys
import joblib
import numpy as np
from pathlib import Path

sys.path.append(str(Path(__file__).parent))
from extract_features import extract_features, FEATURE_NAMES


MODEL_PATH = "ai/models/certificate_forgery_model.joblib"


def predict(image_path):

    model = joblib.load(MODEL_PATH)

    features = extract_features(image_path)
    vector = [features[k] for k in FEATURE_NAMES]

    X = np.array([vector])

    proba = model.predict_proba(X)[0]
    forged_proba = proba[1]

    risk_score = int(round(forged_proba * 100))

    if risk_score >= 70:
        category = "HIGH_FORGERY_RISK"
    elif risk_score >= 40:
        category = "MEDIUM_FORGERY_RISK"
    else:
        category = "LOW_FORGERY_RISK"

    return {
        "risk_score": risk_score,
        "risk_category": category,
        "forged_probability": float(forged_proba)
    }


if __name__ == "__main__":

    if len(sys.argv) < 2:
        print("Usage: python predict.py <image_path>")
        sys.exit(1)

    image_path = sys.argv[1]

    try:
        result = predict(image_path)

        print(f"AI_RISK_SCORE={result['risk_score']}")
        print(f"AI_CATEGORY={result['risk_category']}")
        print(f"AI_FORGED_PROBABILITY={result['forged_probability']}")

    except Exception as e:
        print(f"ERROR: {str(e)}", file=sys.stderr)
        sys.exit(1)