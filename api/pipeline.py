# api/pipeline.py
import json, joblib
from pathlib import Path
import pandas as pd
import numpy as np
from sklearn.linear_model import Ridge
from sklearn.ensemble import ExtraTreesRegressor
from xgboost import XGBRegressor

BASE = Path(__file__).parent
MODELS_DIR = BASE / "models"
DATA_PATH = BASE / "data" / "Merged_Unemployment_Data.csv"
ONTARIO_CODE = "Ontario [35]"

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
    "Sexual assault, level 3, aggravated [1310]": Ridge(alpha=1.0),
    "Abduction under age 14, by parent or guardian [1560]": Ridge(alpha=1.0),
    "Criminal harassment [1625]": Ridge(alpha=1.0),
}

class ModelStore:
    def __init__(self):
        self.models = {}
        self.meta = {}
        self.df_ON = None
        self._load_data()
        self._load_models()

    def _load_data(self):
        df = pd.read_csv(DATA_PATH)
        df = df[(df["GEO"] == ONTARIO_CODE) & (df["Violations"].isin(VIOLATIONS))].copy()
        df["REF_DATE"] = pd.to_numeric(df["REF_DATE"], errors="coerce").astype("Int64")
        df = df.dropna(subset=["REF_DATE","Actual_incidents"])
        df["REF_DATE"] = df["REF_DATE"].astype(int)
        self.df_ON = df

    def _slug(self, v):
        return v.replace(" ", "_").replace("/", "_").replace("[","").replace("]","")

    def _load_models(self):
        for v in VIOLATIONS:
            slug = self._slug(v)
            model_path = MODELS_DIR / f"model_{slug}.joblib"
            meta_path  = MODELS_DIR / f"meta_{slug}.json"
            if model_path.exists():
                self.models[v] = joblib.load(model_path)
            if meta_path.exists():
                with open(meta_path) as f:
                    self.meta[v] = json.load(f)

    def list_violations(self):
        return VIOLATIONS

    def historical_series(self, violation: str):
        sub = self.df_ON[self.df_ON["Violations"] == violation].copy()
        sub = sub[["REF_DATE","Actual_incidents"]].dropna().sort_values("REF_DATE")
        years  = sub["REF_DATE"].tolist()
        actual = sub["Actual_incidents"].tolist()
        return {
            "years": years,
            "actual": actual,
            "last_observed_year": max(years) if years else None,
        }

    def _build_lag(self, sub):
        df = sub[["REF_DATE","Actual_incidents"]].dropna().sort_values("REF_DATE").copy()
        df["y_lag1"] = df["Actual_incidents"].shift(1)
        df["y_lag2"] = df["Actual_incidents"].shift(2)
        df = df.dropna().reset_index(drop=True)
        return df

    def forecast_to_year(self, violation: str, to_year: int):
        sub = self.df_ON[self.df_ON["Violations"] == violation].copy()
        sub = sub[["REF_DATE","Actual_incidents"]].dropna().sort_values("REF_DATE")
        if sub.empty:
            return {"forecast": [], "from_year": None, "to_year": None}

        model = self.models.get(violation)
        if model is None:
            return {"forecast": [], "from_year": None, "to_year": None}

        years = sub["REF_DATE"].tolist()
        values = sub["Actual_incidents"].astype(float).tolist()

        last_year = years[-1]
        if to_year <= last_year:
            return {"forecast": [], "from_year": last_year+1, "to_year": to_year}

        y = values.copy()
        yhat = []
        for yr in range(last_year+1, to_year+1):
            if len(y) < 2: break
            x = np.array([[y[-1], y[-2]]])
            pred = float(model.predict(x)[0])
            pred = max(0.0, pred)
            y.append(pred)
            yhat.append({"year": yr, "yhat": pred})

        return {"forecast": yhat, "from_year": last_year+1, "to_year": to_year}

    def predict_specific_year(self, violation: str, year: int):
        """
        Backtest-style: train on data up to (year-1) and predict `year`.
        Return both predicted and actual (since we have it up to 2023).
        """
        sub = self.df_ON[self.df_ON["Violations"] == violation].copy()
        sub = sub[["REF_DATE","Actual_incidents"]].dropna().sort_values("REF_DATE")
        if sub.empty:
            return {"year": year, "yhat": None, "actual": None, "train_upto_year": None}

        min_year = int(sub["REF_DATE"].min())
        last_obs = int(sub["REF_DATE"].max())

        if year <= min_year or year > last_obs:
            # outside backtest range
            actual = float(sub[sub["REF_DATE"] == year]["Actual_incidents"].iloc[0]) if year <= last_obs and (sub["REF_DATE"] == year).any() else None
            return {"year": year, "yhat": None, "actual": actual, "train_upto_year": None}

        # Build lags and cut at year-1
        lagdf = self._build_lag(sub)
        train_df = lagdf[lagdf["REF_DATE"] <= (year - 1)]
        if train_df.empty:
            return {"year": year, "yhat": None, "actual": None, "train_upto_year": None}

        X_train = train_df[["y_lag1", "y_lag2"]].values
        y_train = train_df["Actual_incidents"].values

        # Use same auto-model class for this violation
        model = AUTO_MODEL[violation]
        model.fit(X_train, y_train)

        # Predict `year` using last two actuals available at (year-1)
        # Find (year-1) and (year-2) actuals
        s = sub.set_index("REF_DATE")["Actual_incidents"]
        if (year-1) not in s.index or (year-2) not in s.index:
            return {"year": year, "yhat": None, "actual": None, "train_upto_year": int(train_df["REF_DATE"].max())}

        x = np.array([[float(s[year-1]), float(s[year-2])]])
        yhat = float(model.predict(x)[0])
        yhat = max(0.0, yhat)
        actual = float(s[year]) if year in s.index else None

        return {
            "year": year,
            "yhat": yhat,
            "actual": actual,
            "train_upto_year": int(train_df["REF_DATE"].max()),
        }

store = ModelStore()
