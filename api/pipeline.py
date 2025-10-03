# api/pipeline.py
import json, joblib
from pathlib import Path
import pandas as pd
import numpy as np

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
        # In-sample fitted values (walk-forward style on test block 2020–2023)
        # We'll return None for fitted; Step 2 can add full backtesting if needed
        return {
            "years": years,
            "actual": actual,
            "last_observed_year": max(years) if years else None,
        }

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

        # Recursive: use last two observations, roll forward
        y = values.copy()
        yhat = []
        for yr in range(last_year+1, to_year+1):
            if len(y) < 2:
                break
            x = np.array([[y[-1], y[-2]]])
            pred = float(model.predict(x)[0])
            # guard against negative predictions
            pred = max(0.0, pred)
            y.append(pred)
            yhat.append({"year": yr, "yhat": pred})

        return {
            "forecast": yhat,
            "from_year": last_year+1,
            "to_year": to_year,
        }

store = ModelStore()
