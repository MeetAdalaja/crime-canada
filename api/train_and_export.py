# api/train_and_export.py
import json, os, joblib
import numpy as np
import pandas as pd
from pathlib import Path
from sklearn.linear_model import Ridge
from sklearn.ensemble import ExtraTreesRegressor
from xgboost import XGBRegressor
from sklearn.metrics import r2_score, mean_absolute_error, mean_squared_error

DATA_PATH = Path(__file__).parent / "data" / "Merged_Unemployment_Data.csv"
MODELS_DIR = Path(__file__).parent / "models"
MODELS_DIR.mkdir(parents=True, exist_ok=True)

ONTARIO_CODE = "Ontario [35]"

# 9 violations (exact display strings as in your notebook/paper)
VIOLATIONS = [
    "Total robbery [160]",
    "Total property crime violations [200]",
    "Total theft under $5,000 (non-motor vehicle) [240]",
    "Total theft of motor vehicle [220]",
    "Total mischief [250]",
    "Total drug violations [401]",
    "Sexual assault, level 3, aggravated [1310]",
    "Abduction under age 14, by parent or guardian [1560]",
    "Criminal harassment [1625]",
]

# Auto model choice: robust defaults aligned with your findings
AUTO_MODEL = {
    "Total robbery [160]": ExtraTreesRegressor(n_estimators=600, random_state=42),
    "Total property crime violations [200]": XGBRegressor(
        n_estimators=800, max_depth=5, learning_rate=0.05, subsample=0.9,
        colsample_bytree=0.9, random_state=42
    ),
    "Total theft under $5,000 (non-motor vehicle) [240]": XGBRegressor(
        n_estimators=800, max_depth=5, learning_rate=0.05, subsample=0.9,
        colsample_bytree=0.9, random_state=42
    ),
    "Total theft of motor vehicle [220]": ExtraTreesRegressor(n_estimators=700, random_state=42),
    "Total mischief [250]": ExtraTreesRegressor(n_estimators=700, random_state=42),
    "Total drug violations [401]": XGBRegressor(
        n_estimators=600, max_depth=4, learning_rate=0.05, subsample=0.9,
        colsample_bytree=0.9, random_state=42
    ),
    # Low-frequency → linear tends to behave well
    "Sexual assault, level 3, aggravated [1310]": Ridge(alpha=1.0),
    "Abduction under age 14, by parent or guardian [1560]": Ridge(alpha=1.0),
    "Criminal harassment [1625]": Ridge(alpha=1.0),
}

def build_lag_frame(df_violation, target_col="Actual_incidents", lags=(1,2)):
    df = df_violation[["REF_DATE", target_col]].dropna().sort_values("REF_DATE").copy()
    for L in lags:
        df[f"{target_col}_lag{L}"] = df[target_col].shift(L)
    df = df.dropna().reset_index(drop=True)
    return df

def train_eval_save(df_ON):
    meta_summary = {}
    for v in VIOLATIONS:
        sub = df_ON[df_ON["Violations"] == v].copy()
        if sub.empty:
            print(f"[WARN] No rows for {v}")
            continue

        # Build lag dataset
        lagdf = build_lag_frame(sub, target_col="Actual_incidents", lags=(1,2))
        # Train/test split by year boundary: train <= 2019, test 2020-2023 (if available)
        train_df = lagdf[lagdf["REF_DATE"] <= 2019]
        test_df  = lagdf[lagdf["REF_DATE"] >  2019]

        X_train = train_df[["Actual_incidents_lag1", "Actual_incidents_lag2"]].values
        y_train = train_df["Actual_incidents"].values

        model = AUTO_MODEL[v]
        model.fit(X_train, y_train)

        # Evaluate on test (if any)
        metrics = {}
        if not test_df.empty:
            X_test = test_df[["Actual_incidents_lag1", "Actual_incidents_lag2"]].values
            y_test = test_df["Actual_incidents"].values
            y_pred = model.predict(X_test)
            metrics = {
                "r2": float(r2_score(y_test, y_pred)) if len(np.unique(y_test))>1 else None,
                "mae": float(mean_absolute_error(y_test, y_pred)),
                "rmse": float(mean_squared_error(y_test, y_pred, squared=False)),
                "test_years": test_df["REF_DATE"].tolist(),
            }

        # Save model
        slug = v.replace(" ", "_").replace("/", "_").replace("[","").replace("]","")
        joblib.dump(model, MODELS_DIR / f"model_{slug}.joblib")

        # Save per-violation metadata
        meta = {
            "violation": v,
            "place": ONTARIO_CODE,
            "train_years": train_df["REF_DATE"].tolist(),
            "last_observed_year": int(lagdf["REF_DATE"].max()) if not lagdf.empty else None,
            "auto_model": type(model).__name__,
            "metrics": metrics,
        }
        with open(MODELS_DIR / f"meta_{slug}.json", "w") as f:
            json.dump(meta, f, indent=2)

        meta_summary[v] = meta
        print(f"[OK] Trained & saved: {v} → {meta['auto_model']}")

    with open(MODELS_DIR / "summary.json", "w") as f:
        json.dump(meta_summary, f, indent=2)

def main():
    df = pd.read_csv(DATA_PATH)
    # Ontario filter (exact match)
    df_ON = df[df["GEO"] == ONTARIO_CODE].copy()
    # Keep only required columns
    need_cols = {"REF_DATE","GEO","Violations","Actual_incidents"}
    missing = need_cols - set(df_ON.columns)
    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    # Cast REF_DATE to int if needed
    df_ON["REF_DATE"] = pd.to_numeric(df_ON["REF_DATE"], errors="coerce").astype("Int64")
    df_ON = df_ON.dropna(subset=["REF_DATE","Actual_incidents"])
    df_ON["REF_DATE"] = df_ON["REF_DATE"].astype(int)

    train_eval_save(df_ON)

if __name__ == "__main__":
    main()
