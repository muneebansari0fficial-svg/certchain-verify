import pandas as pd
import numpy as np
import joblib
import sys
from pathlib import Path
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import GroupKFold, cross_val_score
from sklearn.metrics import (
    classification_report,
    confusion_matrix,
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score
)

sys.path.append(str(Path(__file__).parent))
from extract_features import extract_features, FEATURE_NAMES


DATASET_CSV = "ai/dataset/certificate_dataset.csv"
MODEL_PATH = "ai/models/certificate_forgery_model.joblib"


def load_dataset(csv_path):
    """Load dataset and extract features from each image."""

    df = pd.read_csv(csv_path)

    print(f"Loaded {len(df)} samples from CSV")

    X = []
    y = []
    groups = []

    for idx, row in df.iterrows():

        img_path = row["path"]

        try:
            features = extract_features(img_path)
            vector = [features[k] for k in FEATURE_NAMES]

            X.append(vector)
            y.append(row["label"])

            # Group = source image (without augmentation suffix)
            stem = Path(img_path).stem

            # Agar forged file hai (f_XXXX_attack.png), to source g_XXXX hai
            if stem.startswith("f_"):
                parts = stem.split("_")
                source_num = parts[1]
                base_name = f"g_{source_num}"
            else:
                # g_0001_orig -> g_0001
                parts = stem.split("_")
                if len(parts) >= 2:
                    base_name = f"{parts[0]}_{parts[1]}"
                else:
                    base_name = stem

            groups.append(base_name)

        except Exception as e:
            print(f"  Skip {img_path}: {e}")

    X = np.array(X)
    y = np.array(y)
    groups = np.array(groups)

    print(f"Extracted features: {X.shape}")
    print(f"Labels: {np.bincount(y)}")
    print(f"Groups: {len(np.unique(groups))} unique")

    return X, y, groups


def train_model(X, y, groups):
    """Train Random Forest with group-aware cross-validation."""

    print("\n" + "=" * 50)
    print("TRAINING RANDOM FOREST")
    print("=" * 50)

    n_groups = len(np.unique(groups))

    print(f"\nUnique groups: {n_groups}")

    if n_groups >= 3:
        n_splits = min(3, n_groups)

        gkf = GroupKFold(n_splits=n_splits)

        model = RandomForestClassifier(
            n_estimators=100,
            max_depth=8,
            random_state=42,
            class_weight="balanced"
        )

        cv_scores = cross_val_score(
            model, X, y,
            groups=groups,
            cv=gkf,
            scoring="accuracy"
        )

        print(f"\nCross-validation scores: {cv_scores}")
        print(f"Mean CV accuracy: {cv_scores.mean():.3f}")

    print("\nTraining final model on all data...")

    model = RandomForestClassifier(
        n_estimators=100,
        max_depth=8,
        random_state=42,
        class_weight="balanced"
    )

    model.fit(X, y)

    y_pred = model.predict(X)

    print("\n" + "=" * 50)
    print("TRAINING PERFORMANCE")
    print("=" * 50)

    print(f"Accuracy:  {accuracy_score(y, y_pred):.3f}")
    print(f"Precision: {precision_score(y, y_pred, zero_division=0):.3f}")
    print(f"Recall:    {recall_score(y, y_pred, zero_division=0):.3f}")
    print(f"F1-Score:  {f1_score(y, y_pred, zero_division=0):.3f}")

    try:
        y_proba = model.predict_proba(X)[:, 1]
        print(f"ROC-AUC:   {roc_auc_score(y, y_proba):.3f}")
    except Exception:
        pass

    print("\nConfusion Matrix:")
    print(confusion_matrix(y, y_pred))

    print("\nClassification Report:")
    print(classification_report(
        y, y_pred,
        target_names=["Genuine", "Forged"],
        zero_division=0
    ))

    print("\n" + "=" * 50)
    print("FEATURE IMPORTANCE")
    print("=" * 50)

    importances = model.feature_importances_
    indices = np.argsort(importances)[::-1]

    for i in range(len(FEATURE_NAMES)):
        idx = indices[i]
        print(f"  {i+1}. {FEATURE_NAMES[idx]:20s} {importances[idx]:.4f}")

    return model


def save_model(model):
    Path(MODEL_PATH).parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, MODEL_PATH)
    print(f"\nModel saved: {MODEL_PATH}")


if __name__ == "__main__":

    print("=" * 50)
    print("CERTCHAIN AI - MODEL TRAINING")
    print("=" * 50)
    print()

    X, y, groups = load_dataset(DATASET_CSV)

    if len(X) == 0:
        print("ERROR: No data loaded")
        sys.exit(1)

    model = train_model(X, y, groups)

    save_model(model)

    print("\n" + "=" * 50)
    print("DONE")
    print("=" * 50)