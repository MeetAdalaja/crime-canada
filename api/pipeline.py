# # api/pipeline.py
# import json, re, joblib
# from pathlib import Path
# import pandas as pd
# import numpy as np
# from sklearn.linear_model import Ridge

# BASE = Path(__file__).parent
# MODELS_DIR = BASE / "models"
# DATA_PATH = BASE / "data" / "Merged_Unemployment_Data.csv"

# VIOLATIONS = [
#     "Total robbery [160]",
#     "Total property crime violations [200]",
#     "Total theft under $5,000 (non-motor vehicle) [240]",
#     "Total theft of motor vehicle [220]",
#     "Total mischief [250]",
#     "Total drug violations [401]",
#     "Sexual assault, level 3, aggravated [1310]",
#     "Abduction under age 14, by parent or guardian [1560]",
#     "Criminal harassment [1625]",
# ]

# def is_province_geo(name: str) -> bool:
#     m = re.search(r"\[(\d+)\]", str(name))
#     return bool(m and len(m.group(1)) == 2)

# def place_slug(place: str) -> str:
#     name = re.sub(r"\s*\[(\d+)\]\s*$", r"_\1", place.strip())
#     name = re.sub(r"[^\w\-]+", "_", name)
#     return name

# def vslug(v: str) -> str:
#     return re.sub(r"[^\w\-]+", "_", v)

# class ModelStore:
#     def __init__(self):
#         self.df_all = None
#         self.places = []     # provinces/territories only
#         self.models = {}     # key: (place, violation) -> estimator
#         self.meta = {}       # key: (place, violation) -> dict
#         self.backtests = {}  # dict[place][violation][yearstr] -> {year,yhat,actual,train_upto_year}
#         self._forecast_cache = {}  # key: (place, violation, to_year) -> dict
#         self._load_data()
#         self._load_models_from_disk()
#         self._load_backtests_from_disk()
#         # NEW: ensure any missing pairs are fit once at startup (fast) and have backtests
#         self._ensure_models_and_backtests()

#     # ---------- data ----------
#     def _load_data(self):
#         df = pd.read_csv(DATA_PATH)
#         need = {"REF_DATE","GEO","Violations","Actual_incidents"}
#         missing = need - set(df.columns)
#         if missing:
#             raise ValueError(f"Missing columns: {missing}")

#         df = df.dropna(subset=["REF_DATE","GEO","Violations","Actual_incidents"]).copy()
#         df["REF_DATE"] = pd.to_numeric(df["REF_DATE"], errors="coerce").astype("Int64")
#         df = df.dropna(subset=["REF_DATE"])
#         df["REF_DATE"] = df["REF_DATE"].astype(int)

#         # provinces/territories only (two-digit code like [35])
#         self.places = sorted({g for g in df["GEO"].unique() if is_province_geo(g)})
#         df = df[(df["GEO"].isin(self.places)) & (df["Violations"].isin(VIOLATIONS))]
#         self.df_all = df

#     # ---------- artifacts on disk ----------
#     def _load_models_from_disk(self):
#         if not MODELS_DIR.exists(): return
#         for pdir in MODELS_DIR.iterdir():
#             if not pdir.is_dir(): continue
#             # match folder to a known place
#             for place in self.places:
#                 if place_slug(place) == pdir.name:
#                     for v in VIOLATIONS:
#                         mp = pdir / f"model_{vslug(v)}.joblib"
#                         mt = pdir / f"meta_{vslug(v)}.json"
#                         if mp.exists():
#                             try:
#                                 self.models[(place, v)] = joblib.load(mp)
#                             except Exception:
#                                 pass
#                         if mt.exists():
#                             try:
#                                 with open(mt) as f:
#                                     self.meta[(place, v)] = json.load(f)
#                             except Exception:
#                                 pass
#                     break
#         # Backward-compatibility: if someone still has old Ontario-only flat files, map them
#         # to Ontario [35] once so we don't silently drop forecasts there.
#         flat_dir = MODELS_DIR
#         ont = "Ontario [35]"
#         if (ont in self.places) and not any(k[0] == ont for k in self.models.keys()):
#             # try to recover
#             for v in VIOLATIONS:
#                 mp = flat_dir / f"model_{vslug(v)}.joblib"
#                 mt = flat_dir / f"meta_{vslug(v)}.json"
#                 if mp.exists():
#                     try:
#                         self.models[(ont, v)] = joblib.load(mp)
#                     except Exception:
#                         pass
#                 if mt.exists():
#                     try:
#                         with open(mt) as f:
#                             self.meta[(ont, v)] = json.load(f)
#                     except Exception:
#                         pass

#     def _load_backtests_from_disk(self):
#         bt_path = MODELS_DIR / "backtests.json"
#         if bt_path.exists():
#             try:
#                 with open(bt_path) as f:
#                     self.backtests = json.load(f)
#             except Exception:
#                 self.backtests = {}
#         else:
#             self.backtests = {}

#     # ---------- startup fallback (NEW) ----------
#     def _ensure_models_and_backtests(self):
#         # fit a very fast AR(2) Ridge model for any missing (place, violation)
#         for place in self.places:
#             for v in VIOLATIONS:
#                 if (place, v) not in self.models:
#                     mdl = self._fit_startup_model(place, v)
#                     if mdl is not None:
#                         self.models[(place, v)] = mdl
#                         self.meta[(place, v)] = {
#                             "violation": v,
#                             "place": place,
#                             "auto_model": "Ridge(startup)",
#                             "train_upto_year": self._last_obs_year(place, v),
#                             "last_observed_year": self._last_obs_year(place, v),
#                         }
#         # ensure backtests exist for 2021–2023 (only compute for those missing)
#         for place in self.places:
#             for v in VIOLATIONS:
#                 for yr in (2021, 2022, 2023):
#                     if str(yr) in self.backtests.get(place, {}).get(v, {}):
#                         continue
#                     rec = self._compute_backtest(place, v, yr)
#                     if rec is None:
#                         continue
#                     self.backtests.setdefault(place, {}).setdefault(v, {})[str(yr)] = rec

#     def _last_obs_year(self, place: str, v: str):
#         sub = self.df_all[(self.df_all["GEO"] == place) & (self.df_all["Violations"] == v)]
#         if sub.empty: return None
#         return int(sub["REF_DATE"].max())

#     def _fit_startup_model(self, place: str, violation: str):
#         sub = self.df_all[(self.df_all["GEO"] == place) & (self.df_all["Violations"] == violation)].copy()
#         sub = sub[["REF_DATE","Actual_incidents"]].dropna().sort_values("REF_DATE")
#         if len(sub) < 3:
#             return None
#         df = sub.copy()
#         df["lag1"] = df["Actual_incidents"].shift(1)
#         df["lag2"] = df["Actual_incidents"].shift(2)
#         df = df.dropna()
#         if len(df) < 5:
#             return None
#         X = df[["lag1","lag2"]].values
#         y = df["Actual_incidents"].values
#         mdl = Ridge(alpha=1.0)
#         mdl.fit(X, y)
#         return mdl

#     def _compute_backtest(self, place: str, violation: str, year: int):
#         # rolling-origin: train ≤ (year-1) then predict year using actual lags
#         sub = self.df_all[(self.df_all["GEO"] == place) & (self.df_all["Violations"] == violation)].copy()
#         sub = sub[["REF_DATE","Actual_incidents"]].dropna().sort_values("REF_DATE")
#         if sub.empty: return None
#         s = sub.set_index("REF_DATE")["Actual_incidents"]
#         if not (year in s.index and (year-1) in s.index and (year-2) in s.index):
#             return None
#         df = sub.copy()
#         df["lag1"] = df["Actual_incidents"].shift(1)
#         df["lag2"] = df["Actual_incidents"].shift(2)
#         df = df.dropna()
#         train = df[df["REF_DATE"] <= (year - 1)]
#         if train.empty: return None
#         X = train[["lag1","lag2"]].values
#         y = train["Actual_incidents"].values
#         mdl = Ridge(alpha=1.0)
#         mdl.fit(X, y)
#         x = np.array([[float(s[year-1]), float(s[year-2])]])
#         yhat = float(mdl.predict(x)[0])
#         return {
#             "year": int(year),
#             "yhat": float(max(0.0, yhat)),
#             "actual": float(s[year]),
#             "train_upto_year": int(train["REF_DATE"].max()),
#         }

#     # ---------- public APIs ----------
#     def list_places(self):
#         return self.places

#     def list_violations(self):
#         return VIOLATIONS

#     def historical_series(self, place: str, violation: str):
#         sub = self.df_all[(self.df_all["GEO"] == place) & (self.df_all["Violations"] == violation)].copy()
#         sub = sub[["REF_DATE", "Actual_incidents"]].dropna().sort_values("REF_DATE")
#         years = sub["REF_DATE"].tolist()
#         actual = sub["Actual_incidents"].tolist()
#         return {
#             "years": years,
#             "actual": actual,
#             "last_observed_year": max(years) if years else None,
#         }

#     def forecast_to_year(self, place: str, violation: str, to_year: int):
#         key = (place, violation, int(to_year))
#         if key in self._forecast_cache:
#             return self._forecast_cache[key]

#         sub = self.df_all[(self.df_all["GEO"] == place) & (self.df_all["Violations"] == violation)].copy()
#         sub = sub[["REF_DATE","Actual_incidents"]].dropna().sort_values("REF_DATE")
#         if sub.empty:
#             res = {"forecast": [], "from_year": None, "to_year": None}
#             self._forecast_cache[key] = res
#             return res

#         model = self.models.get((place, violation))
#         years = sub["REF_DATE"].tolist()
#         values = sub["Actual_incidents"].astype(float).tolist()
#         if not years or model is None:
#             res = {"forecast": [], "from_year": None, "to_year": None}
#             self._forecast_cache[key] = res
#             return res

#         last_year = years[-1]
#         if to_year <= last_year:
#             res = {"forecast": [], "from_year": last_year + 1, "to_year": to_year}
#             self._forecast_cache[key] = res
#             return res

#         y = values.copy()
#         out = []
#         for yr in range(last_year + 1, to_year + 1):
#             if len(y) < 2: break
#             x = np.array([[y[-1], y[-2]]])
#             pred = float(model.predict(x)[0])
#             pred = max(0.0, pred)
#             y.append(pred)
#             out.append({"year": yr, "yhat": pred})

#         res = {"forecast": out, "from_year": last_year + 1, "to_year": to_year}
#         self._forecast_cache[key] = res
#         return res

#     def predict_specific_year(self, place: str, violation: str, year: int):
#         rec = self.backtests.get(place, {}).get(violation, {}).get(str(int(year)))
#         if rec:
#             return {
#                 "year": int(rec["year"]),
#                 "yhat": float(rec["yhat"]),
#                 "actual": float(rec["actual"]),
#                 "train_upto_year": int(rec["train_upto_year"]),
#             }
#         # fallback: return actual if exists
#         sub = self.df_all[(self.df_all["GEO"] == place) & (self.df_all["Violations"] == violation)]
#         s = sub.set_index("REF_DATE")["Actual_incidents"] if not sub.empty else None
#         actual = float(s.get(year)) if s is not None and year in s.index else None
#         return {"year": int(year), "yhat": None, "actual": actual, "train_upto_year": None}

# store = ModelStore()




# api/pipeline.py
import json, re, joblib
from pathlib import Path
import pandas as pd
import numpy as np
from sklearn.linear_model import Ridge

BASE = Path(__file__).parent
MODELS_DIR = BASE / "models"
DATA_PATH = BASE / "data" / "Merged_Unemployment_Data.csv"

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

def is_province_geo(name: str) -> bool:
    m = re.search(r"\[(\d+)\]", str(name))
    return bool(m and len(m.group(1)) == 2)

def place_slug(place: str) -> str:
    name = re.sub(r"\s*\[(\d+)\]\s*$", r"_\1", place.strip())
    name = re.sub(r"[^\w\-]+", "_", name)
    return name

def vslug(v: str) -> str:
    return re.sub(r"[^\w\-]+", "_", v)

class ModelStore:
    def __init__(self):
        self.df_all = None
        self.places = []     # provinces/territories only
        self.models = {}     # key: (place, violation) -> estimator
        self.meta = {}       # key: (place, violation) -> dict
        self.backtests = {}  # dict[place][violation][yearstr] -> {year,yhat,actual,train_upto_year}
        self._forecast_cache = {}  # key: (place, violation, to_year) -> dict
        self._load_data()
        self._load_models_from_disk()
        self._load_backtests_from_disk()
        self._ensure_models_and_backtests()  # fit fast fallback if artifacts missing

    # ---------- data ----------
    def _load_data(self):
        df = pd.read_csv(DATA_PATH)
        need = {"REF_DATE","GEO","Violations","Actual_incidents"}
        missing = need - set(df.columns)
        if missing:
            raise ValueError(f"Missing columns: {missing}")

        df = df.dropna(subset=["REF_DATE","GEO","Violations","Actual_incidents"]).copy()
        df["REF_DATE"] = pd.to_numeric(df["REF_DATE"], errors="coerce").astype("Int64")
        df = df.dropna(subset=["REF_DATE"])
        df["REF_DATE"] = df["REF_DATE"].astype(int)

        # provinces/territories only (two-digit code like [35]); exclude CMAs
        self.places = sorted({g for g in df["GEO"].unique() if is_province_geo(g)})
        df = df[(df["GEO"].isin(self.places)) & (df["Violations"].isin(VIOLATIONS))]
        self.df_all = df

    # ---------- artifacts on disk ----------
    def _load_models_from_disk(self):
        if not MODELS_DIR.exists(): return
        # load per-place folders
        for pdir in MODELS_DIR.iterdir():
            if not pdir.is_dir(): continue
            for place in self.places:
                if place_slug(place) == pdir.name:
                    for v in VIOLATIONS:
                        mp = pdir / f"model_{vslug(v)}.joblib"
                        mt = pdir / f"meta_{vslug(v)}.json"
                        if mp.exists():
                            try:
                                self.models[(place, v)] = joblib.load(mp)
                            except Exception:
                                pass
                        if mt.exists():
                            try:
                                with open(mt) as f:
                                    self.meta[(place, v)] = json.load(f)
                            except Exception:
                                pass
                    break
        # backward-compat: flat Ontario-only models
        ont = "Ontario [35]"
        if (ont in self.places) and not any(k[0] == ont for k in self.models.keys()):
            for v in VIOLATIONS:
                mp = MODELS_DIR / f"model_{vslug(v)}.joblib"
                mt = MODELS_DIR / f"meta_{vslug(v)}.json"
                if mp.exists():
                    try: self.models[(ont, v)] = joblib.load(mp)
                    except Exception: pass
                if mt.exists():
                    try:
                        with open(mt) as f: self.meta[(ont, v)] = json.load(f)
                    except Exception: pass

    def _load_backtests_from_disk(self):
        bt_path = MODELS_DIR / "backtests.json"
        if bt_path.exists():
            try:
                with open(bt_path) as f:
                    self.backtests = json.load(f)
            except Exception:
                self.backtests = {}
        else:
            self.backtests = {}

    # ---------- startup fallback (fit once) ----------
    def _ensure_models_and_backtests(self):
        for place in self.places:
            for v in VIOLATIONS:
                if (place, v) not in self.models:
                    mdl = self._fit_startup_model(place, v)
                    if mdl is not None:
                        self.models[(place, v)] = mdl
                        self.meta[(place, v)] = {
                            "violation": v,
                            "place": place,
                            "auto_model": "Ridge(startup)",
                            "train_upto_year": self._last_obs_year(place, v),
                            "last_observed_year": self._last_obs_year(place, v),
                        }
        for place in self.places:
            for v in VIOLATIONS:
                for yr in (2021, 2022, 2023):
                    if str(yr) in self.backtests.get(place, {}).get(v, {}): 
                        continue
                    rec = self._compute_backtest(place, v, yr)
                    if rec is None: 
                        continue
                    self.backtests.setdefault(place, {}).setdefault(v, {})[str(yr)] = rec

    def _last_obs_year(self, place: str, v: str):
        sub = self.df_all[(self.df_all["GEO"] == place) & (self.df_all["Violations"] == v)]
        if sub.empty: return None
        return int(sub["REF_DATE"].max())

    def _fit_startup_model(self, place: str, violation: str):
        sub = self.df_all[(self.df_all["GEO"] == place) & (self.df_all["Violations"] == violation)].copy()
        sub = sub[["REF_DATE","Actual_incidents"]].dropna().sort_values("REF_DATE")
        if len(sub) < 3: return None
        df = sub.copy()
        df["lag1"] = df["Actual_incidents"].shift(1)
        df["lag2"] = df["Actual_incidents"].shift(2)
        df = df.dropna()
        if len(df) < 5: return None
        X = df[["lag1","lag2"]].values
        y = df["Actual_incidents"].values
        mdl = Ridge(alpha=1.0)
        mdl.fit(X, y)
        return mdl

    def _compute_backtest(self, place: str, violation: str, year: int):
        sub = self.df_all[(self.df_all["GEO"] == place) & (self.df_all["Violations"] == violation)].copy()
        sub = sub[["REF_DATE","Actual_incidents"]].dropna().sort_values("REF_DATE")
        if sub.empty: return None
        s = sub.set_index("REF_DATE")["Actual_incidents"]
        if not (year in s.index and (year-1) in s.index and (year-2) in s.index): return None
        df = sub.copy()
        df["lag1"] = df["Actual_incidents"].shift(1)
        df["lag2"] = df["Actual_incidents"].shift(2)
        df = df.dropna()
        train = df[df["REF_DATE"] <= (year - 1)]
        if train.empty: return None
        X = train[["lag1","lag2"]].values
        y = train["Actual_incidents"].values
        mdl = Ridge(alpha=1.0)
        mdl.fit(X, y)
        x = np.array([[float(s[year-1]), float(s[year-2])]])
        yhat = float(mdl.predict(x)[0])
        return {
            "year": int(year),
            "yhat": float(max(0.0, yhat)),
            "actual": float(s[year]),
            "train_upto_year": int(train["REF_DATE"].max()),
        }

    # ---------- helpers for aggregation ----------
    def _historical_series_single(self, place: str, violation: str):
        sub = self.df_all[(self.df_all["GEO"] == place) & (self.df_all["Violations"] == violation)].copy()
        sub = sub[["REF_DATE", "Actual_incidents"]].dropna().sort_values("REF_DATE")
        years = sub["REF_DATE"].tolist()
        actual = sub["Actual_incidents"].tolist()
        return years, actual

    def _historical_series_agg(self, places: list[str], violation: str):
        sub = self.df_all[(self.df_all["GEO"].isin(places)) & (self.df_all["Violations"] == violation)].copy()
        if sub.empty:
            return [], [], None
        gp = sub.groupby("REF_DATE", as_index=True)["Actual_incidents"].sum().sort_index()
        years = gp.index.to_list()
        actual = gp.values.tolist()
        last_obs = max(years) if years else None
        return years, actual, last_obs

    # ---------- public APIs ----------
    def list_places(self):
        return self.places

    def list_violations(self):
        return VIOLATIONS

    def historical_series(self, place: str, violation: str):
        years, actual = self._historical_series_single(place, violation)
        return {
            "years": years,
            "actual": actual,
            "last_observed_year": max(years) if years else None,
        }

    def historical_series_multi(self, places: list[str], violation: str):
        years, actual, last_obs = self._historical_series_agg(places, violation)
        return {
            "years": years,
            "actual": actual,
            "last_observed_year": last_obs,
        }

    def forecast_to_year(self, place: str, violation: str, to_year: int):
        key = (place, violation, int(to_year))
        if key in self._forecast_cache:
            return self._forecast_cache[key]

        sub = self.df_all[(self.df_all["GEO"] == place) & (self.df_all["Violations"] == violation)].copy()
        sub = sub[["REF_DATE","Actual_incidents"]].dropna().sort_values("REF_DATE")
        if sub.empty:
            res = {"forecast": [], "from_year": None, "to_year": None}
            self._forecast_cache[key] = res
            return res

        model = self.models.get((place, violation))
        years = sub["REF_DATE"].tolist()
        values = sub["Actual_incidents"].astype(float).tolist()
        if not years or model is None:
            res = {"forecast": [], "from_year": None, "to_year": None}
            self._forecast_cache[key] = res
            return res

        last_year = years[-1]
        if to_year <= last_year:
            res = {"forecast": [], "from_year": last_year + 1, "to_year": to_year}
            self._forecast_cache[key] = res
            return res

        y = values.copy()
        out = []
        for yr in range(last_year + 1, to_year + 1):
            if len(y) < 2: break
            x = np.array([[y[-1], y[-2]]])
            pred = float(model.predict(x)[0])
            pred = max(0.0, pred)
            y.append(pred)
            out.append({"year": yr, "yhat": pred})

        res = {"forecast": out, "from_year": last_year + 1, "to_year": to_year}
        self._forecast_cache[key] = res
        return res

    def forecast_to_year_multi(self, places: list[str], violation: str, to_year: int):
        # Sum per-year forecasts across places
        sums: dict[int, float] = {}
        from_years = []
        for p in places:
            fc = self.forecast_to_year(p, violation, to_year)
            if fc["from_year"] is not None:
                from_years.append(fc["from_year"])
            for item in fc["forecast"]:
                sums[item["year"]] = sums.get(item["year"], 0.0) + float(item["yhat"])
        # Build compact list sorted by year
        years_sorted = sorted(sums.keys())
        out = [{"year": y, "yhat": sums[y]} for y in years_sorted]
        from_year = min(from_years) if from_years else None
        return {"forecast": out, "from_year": from_year, "to_year": to_year}

    def predict_specific_year(self, place: str, violation: str, year: int):
        rec = self.backtests.get(place, {}).get(violation, {}).get(str(int(year)))
        if rec:
            return {
                "year": int(rec["year"]),
                "yhat": float(rec["yhat"]),
                "actual": float(rec["actual"]),
                "train_upto_year": int(rec["train_upto_year"]),
            }
        # fallback: return actual if exists
        sub = self.df_all[(self.df_all["GEO"] == place) & (self.df_all["Violations"] == violation)]
        s = sub.set_index("REF_DATE")["Actual_incidents"] if not sub.empty else None
        actual = float(s.get(year)) if s is not None and year in s.index else None
        return {"year": int(year), "yhat": None, "actual": actual, "train_upto_year": None}

    def predict_specific_year_multi(self, places: list[str], violation: str, year: int):
        # Sum backtests across places (2021–2023); include summed actual
        total_yhat = 0.0
        have_pred = False
        total_actual = 0.0
        for p in places:
            rec = self.backtests.get(p, {}).get(violation, {}).get(str(int(year)))
            if rec:
                total_yhat += float(rec["yhat"])
                total_actual += float(rec["actual"])
                have_pred = True
            else:
                # fallback to actual only
                sub = self.df_all[(self.df_all["GEO"] == p) & (self.df_all["Violations"] == violation)]
                if not sub.empty:
                    s = sub.set_index("REF_DATE")["Actual_incidents"]
                    if year in s.index:
                        total_actual += float(s[year])
        return {
            "year": int(year),
            "yhat": float(total_yhat) if have_pred else None,
            "actual": float(total_actual) if total_actual else None,
            "train_upto_year": None,
        }

store = ModelStore()
