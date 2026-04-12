import os
import joblib
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.metrics import accuracy_score, classification_report
from sklearn.model_selection import GridSearchCV, train_test_split
from sklearn.naive_bayes import GaussianNB
from sklearn.neighbors import KNeighborsClassifier
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler, MinMaxScaler, RobustScaler
from sklearn.svm import SVC
from sklearn.tree import DecisionTreeClassifier

DEFAULT_DATASET_URL = "https://raw.githubusercontent.com/AngeloSouzaOliveira/API-Fuel-Insight-MVP/refs/heads/main/data/all_countries_combined.csv"
DATASET_PATH = os.getenv("ML_DATASET_PATH", DEFAULT_DATASET_URL)
MODEL_OUTPUT_PATH = os.getenv(
    "ML_MODEL_OUTPUT_PATH",
    os.path.join(os.path.dirname(__file__), "ml", "fuel_price_tier_model.pkl"),
)

FEATURES = [
    "year",
    "region",
    "subsidy_regime",
    "is_oil_producer",
    "crude_oil_usd_per_barrel",
    "tax_pct_of_pump_price",
    "gasoline_real_2024usd",
]
TARGET = "price_tier"


def _build_one_hot_encoder():
    try:
        return OneHotEncoder(handle_unknown="ignore", sparse_output=False)
    except TypeError:
        return OneHotEncoder(handle_unknown="ignore", sparse=False)


def train_and_export() -> dict:
    df = pd.read_csv(DATASET_PATH).dropna(subset=FEATURES + [TARGET]).copy()
    x = df[FEATURES]
    y = df[TARGET]

    x_train, x_test, y_train, y_test = train_test_split(
        x, y, test_size=0.2, random_state=42, stratify=y
    )

    num_features = [
        "year",
        "is_oil_producer",
        "crude_oil_usd_per_barrel",
        "tax_pct_of_pump_price",
        "gasoline_real_2024usd",
    ]
    cat_features = ["region", "subsidy_regime"]

    base_pre = ColumnTransformer(
        transformers=[
            ("num", Pipeline([("scaler", StandardScaler())]), num_features),
            ("cat", _build_one_hot_encoder(), cat_features),
        ]
    )

    candidates = {
        "KNN": (
            KNeighborsClassifier(),
            {"clf__n_neighbors": [3, 5, 7, 9]},
        ),
        "DecisionTree": (
            DecisionTreeClassifier(random_state=42),
            {"clf__max_depth": [3, 5, 8, None], "clf__min_samples_split": [2, 5, 10]},
        ),
        "NaiveBayes": (
            GaussianNB(),
            {},
        ),
        "SVM": (
            SVC(random_state=42),
            {
                "pre__num__scaler": [StandardScaler(), MinMaxScaler(), RobustScaler()],
                "clf__C": [0.5, 1, 5, 10],
                "clf__kernel": ["linear", "rbf"],
            },
        ),
    }

    best = {"name": None, "score": -1.0, "model": None}
    model_scores = {}

    for name, (clf, grid) in candidates.items():
        pipe = Pipeline([("pre", base_pre), ("clf", clf)])
        gs = GridSearchCV(pipe, grid, cv=5, scoring="accuracy", n_jobs=-1)
        gs.fit(x_train, y_train)
        preds = gs.best_estimator_.predict(x_test)
        acc = accuracy_score(y_test, preds)
        model_scores[name] = acc

        if acc > best["score"]:
            best = {"name": name, "score": acc, "model": gs.best_estimator_}

    out_path = MODEL_OUTPUT_PATH
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    joblib.dump(best["model"], out_path)

    final_preds = best["model"].predict(x_test)
    return {
        "best_model": best["name"],
        "best_accuracy": float(best["score"]),
        "all_scores": model_scores,
        "report": classification_report(y_test, final_preds, output_dict=True),
        "model_path": out_path,
    }


if __name__ == "__main__":
    result = train_and_export()
    print(result)
