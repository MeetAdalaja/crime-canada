# # api/train_and_export.py
# import json, os, re, joblib
# import numpy as np
# import pandas as pd
# from pathlib import Path
# from sklearn.linear_model import Ridge
# from sklearn.ensemble import ExtraTreesRegressor
# from xgboost import XGBRegressor

# ROOT = Path(__file__).parent
# DATA_PATH = ROOT / "data" / "Merged_Unemployment_Data.csv"
# MODELS_DIR = ROOT / "models"
# MODELS_DIR.mkdir(parents=True, exist_ok=True)

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

# AUTO_MODEL = {
#     "Total robbery [160]": ExtraTreesRegressor(n_estimators=600, random_state=42),
#     "Total property crime violations [200]": XGBRegressor(
#         n_estimators=800, max_depth=5, learning_rate=0.05, subsample=0.9, colsample_bytree=0.9, random_state=42
#     ),
#     "Total theft under $5,000 (non-motor vehicle) [240]": XGBRegressor(
#         n_estimators=800, max_depth=5, learning_rate=0.05, subsample=0.9, colsample_bytree=0.9, random_state=42
#     ),
#     "Total theft of motor vehicle [220]": ExtraTreesRegressor(n_estimators=700, random_state=42),
#     "Total mischief [250]": ExtraTreesRegressor(n_estimators=700, random_state=42),
#     "Total drug violations [401]": XGBRegressor(
#         n_estimators=600, max_depth=4, learning_rate=0.05, subsample=0.9, colsample_bytree=0.9, random_state=42
#     ),
#     "Sexual assault, level 3, aggravated [1310]": Ridge(alpha=1.0),
#     "Abduction under age 14, by parent or guardian [1560]": Ridge(alpha=1.0),
#     "Criminal harassment [1625]": Ridge(alpha=1.0),
# }

# def is_province_geo(name: str) -> bool:
#     m = re.search(r"\[(\d+)\]", str(name))
#     return bool(m and len(m.group(1)) == 2)  # provinces/territories use 2-digit codes

# def place_slug(place: str) -> str:
#     # "Ontario [35]" -> "Ontario_35"
#     name = re.sub(r"\s*\[(\d+)\]\s*$", r"_\1", place.strip())
#     name = re.sub(r"[^\w\-]+", "_", name)
#     return name

# def build_lag_frame(df_violation, target_col="Actual_incidents", lags=(1, 2)):
#     df = df_violation[["REF_DATE", target_col]].dropna().sort_values("REF_DATE").copy()
#     for L in lags:
#         df[f"{target_col}_lag{L}"] = df[target_col].shift(L)
#     df = df.dropna().reset_index(drop=True)
#     return df

# def train_and_save_for_place(df_place: pd.DataFrame, place: str, backtests_accum: dict):
#     pslug = place_slug(place)
#     out_dir = MODELS_DIR / pslug
#     out_dir.mkdir(parents=True, exist_ok=True)

#     meta_summary = {}
#     for v in VIOLATIONS:
#         sub = df_place[df_place["Violations"] == v].copy()
#         sub = sub[["REF_DATE", "Actual_incidents"]].dropna().sort_values("REF_DATE")
#         if sub.empty:
#             print(f"[WARN] {place}: no rows for {v}")
#             continue

#         lagdf = build_lag_frame(sub, "Actual_incidents", (1, 2))
#         if lagdf.empty:
#             print(f"[WARN] {place}: not enough lag rows for {v}")
#             continue

#         last_obs = int(lagdf["REF_DATE"].max())
#         X = lagdf[["Actual_incidents_lag1", "Actual_incidents_lag2"]].values
#         y = lagdf["Actual_incidents"].values

#         model = AUTO_MODEL[v]
#         model.fit(X, y)

#         vslug = re.sub(r"[^\w\-]+", "_", v)
#         joblib.dump(model, out_dir / f"model_{vslug}.joblib")

#         meta = {
#             "violation": v, "place": place,
#             "train_upto_year": last_obs,
#             "auto_model": type(model).__name__,
#             "last_observed_year": last_obs,
#         }
#         with open(out_dir / f"meta_{vslug}.json", "w") as f:
#             json.dump(meta, f, indent=2)
#         meta_summary[v] = meta
#         print(f"[OK] {place}: trained {v} → {meta['auto_model']} (≤{last_obs})")

#         # rolling-origin backtests for 2021–2023
#         s = sub.set_index("REF_DATE")["Actual_incidents"]
#         for yr in (2021, 2022, 2023):
#             if yr in s.index and (yr-1) in s.index and (yr-2) in s.index:
#                 lagdf_bt = build_lag_frame(sub, "Actual_incidents", (1, 2))
#                 tr = lagdf_bt[lagdf_bt["REF_DATE"] <= (yr-1)]
#                 if tr.empty: 
#                     continue
#                 Xtr = tr[["Actual_incidents_lag1", "Actual_incidents_lag2"]].values
#                 ytr = tr["Actual_incidents"].values
#                 mdl_bt = AUTO_MODEL[v]
#                 mdl_bt.fit(Xtr, ytr)
#                 pred = float(mdl_bt.predict(np.array([[float(s[yr-1]), float(s[yr-2])]]) )[0])
#                 pred = max(0.0, pred)
#                 backtests_accum.setdefault(place, {}).setdefault(v, {})[str(yr)] = {
#                     "year": yr,
#                     "yhat": pred,
#                     "actual": float(s[yr]),
#                     "train_upto_year": int(tr["REF_DATE"].max()),
#                 }
#                 print(f"[BT] {place} · {v} · {yr}: {pred:.1f} (act {float(s[yr]):.1f})")

#     with open(out_dir / "summary.json", "w") as f:
#         json.dump(meta_summary, f, indent=2)

# def main():
#     df = pd.read_csv(DATA_PATH)
#     need = {"REF_DATE","GEO","Violations","Actual_incidents"}
#     missing = need - set(df.columns)
#     if missing:
#         raise ValueError(f"Missing columns: {missing}")

#     df["REF_DATE"] = pd.to_numeric(df["REF_DATE"], errors="coerce").astype("Int64")
#     df = df.dropna(subset=["REF_DATE","Actual_incidents","GEO","Violations"])
#     df["REF_DATE"] = df["REF_DATE"].astype(int)

#     places = sorted({g for g in df["GEO"].unique() if is_province_geo(g)})
#     print(f"[INFO] Provinces/territories detected ({len(places)}): {places}")

#     backtests_all = {}
#     for place in places:
#         df_place = df[(df["GEO"] == place) & (df["Violations"].isin(VIOLATIONS))].copy()
#         if df_place.empty:
#             print(f"[WARN] no data for {place}, skipping.")
#             continue
#         train_and_save_for_place(df_place, place, backtests_all)

#     with open(MODELS_DIR / "backtests.json", "w") as f:
#         json.dump(backtests_all, f, indent=2)
#     print(f"[OK] wrote backtests for all places → {MODELS_DIR/'backtests.json'}")

# if __name__ == "__main__":
#     main()


# api/train_and_export.py
import json, re, joblib
import numpy as np
import pandas as pd
from pathlib import Path
from sklearn.linear_model import Ridge
from sklearn.ensemble import ExtraTreesRegressor
from xgboost import XGBRegressor

ROOT = Path(__file__).parent
DATA_PATH = ROOT / "data" / "Merged_Unemployment_Data.csv"
MODELS_DIR = ROOT / "models"
MODELS_DIR.mkdir(parents=True, exist_ok=True)

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
        n_estimators=800, max_depth=5, learning_rate=0.05, subsample=0.9, colsample_bytree=0.9, random_state=42
    ),
    "Total theft under $5,000 (non-motor vehicle) [240]": XGBRegressor(
        n_estimators=800, max_depth=5, learning_rate=0.05, subsample=0.9, colsample_bytree=0.9, random_state=42
    ),
    "Total theft of motor vehicle [220]": ExtraTreesRegressor(n_estimators=700, random_state=42),
    "Total mischief [250]": ExtraTreesRegressor(n_estimators=700, random_state=42),
    "Total drug violations [401]": XGBRegressor(
        n_estimators=600, max_depth=4, learning_rate=0.05, subsample=0.9, colsample_bytree=0.9, random_state=42
    ),
    "Sexual assault, level 3, aggravated [1310]": Ridge(alpha=1.0),
    "Abduction under age 14, by parent or guardian [1560]": Ridge(alpha=1.0),
    "Criminal harassment [1625]": Ridge(alpha=1.0),
}

def is_province_geo(name: str) -> bool:
    m = re.search(r"\[(\d+)\]", str(name))
    return bool(m and len(m.group(1)) == 2)  # provinces/territories = 2-digit GEO code

def place_slug(place: str) -> str:
    # "Ontario [35]" -> "Ontario_35"
    name = re.sub(r"\s*\[(\d+)\]\s*$", r"_\1", place.strip())
    name = re.sub(r"[^\w\-]+", "_", name)
    return name

def vslug(v: str) -> str:
    return re.sub(r"[^\w\-]+", "_", v)

def build_lag_frame(df_violation, target_col="Actual_incidents", lags=(1, 2)):
    df = df_violation[["REF_DATE", target_col]].dropna().sort_values("REF_DATE").copy()
    for L in lags:
        df[f"{target_col}_lag{L}"] = df[target_col].shift(L)
    df = df.dropna().reset_index(drop=True)
    return df

def train_and_save_for_place(df_place: pd.DataFrame, place: str, backtests_accum: dict):
    pslug = place_slug(place)
    out_dir = MODELS_DIR / pslug
    out_dir.mkdir(parents=True, exist_ok=True)

    meta_summary = {}
    for v in VIOLATIONS:
        sub = df_place[df_place["Violations"] == v].copy()
        sub = sub[["REF_DATE", "Actual_incidents"]].dropna().sort_values("REF_DATE")
        if sub.empty:
            print(f"[WARN] {place}: no rows for {v}")
            continue

        lagdf = build_lag_frame(sub, "Actual_incidents", (1, 2))
        if lagdf.empty:
            print(f"[WARN] {place}: not enough lag rows for {v}")
            continue

        last_obs = int(lagdf["REF_DATE"].max())
        X = lagdf[["Actual_incidents_lag1", "Actual_incidents_lag2"]].values
        y = lagdf["Actual_incidents"].values

        model = AUTO_MODEL[v]
        model.fit(X, y)

        joblib.dump(model, out_dir / f"model_{vslug(v)}.joblib")
        meta = {
            "violation": v, "place": place,
            "train_upto_year": last_obs,
            "auto_model": type(model).__name__,
            "last_observed_year": last_obs,
        }
        with open(out_dir / f"meta_{vslug(v)}.json", "w") as f:
            json.dump(meta, f, indent=2)
        meta_summary[v] = meta
        print(f"[OK] {place}: trained {v} → {meta['auto_model']} (≤{last_obs})")

        # rolling-origin backtests for 2021–2023
        s = sub.set_index("REF_DATE")["Actual_incidents"]
        for yr in (2021, 2022, 2023):
            if yr in s.index and (yr-1) in s.index and (yr-2) in s.index:
                lagdf_bt = build_lag_frame(sub, "Actual_incidents", (1, 2))
                tr = lagdf_bt[lagdf_bt["REF_DATE"] <= (yr-1)]
                if tr.empty:
                    continue
                Xtr = tr[["Actual_incidents_lag1", "Actual_incidents_lag2"]].values
                ytr = tr["Actual_incidents"].values
                mdl_bt = AUTO_MODEL[v]
                mdl_bt.fit(Xtr, ytr)
                pred = float(mdl_bt.predict(np.array([[float(s[yr-1]), float(s[yr-2])]]) )[0])
                pred = max(0.0, pred)
                backtests_accum.setdefault(place, {}).setdefault(v, {})[str(yr)] = {
                    "year": yr,
                    "yhat": pred,
                    "actual": float(s[yr]),
                    "train_upto_year": int(tr["REF_DATE"].max()),
                }
                print(f"[BT] {place} · {v} · {yr}: {pred:.1f} (act {float(s[yr]):.1f})")

    with open(out_dir / "summary.json", "w") as f:
        json.dump(meta_summary, f, indent=2)

def main():
    df = pd.read_csv(DATA_PATH)
    need = {"REF_DATE","GEO","Violations","Actual_incidents"}
    missing = need - set(df.columns)
    if missing:
        raise ValueError(f"Missing columns: {missing}")

    df["REF_DATE"] = pd.to_numeric(df["REF_DATE"], errors="coerce").astype("Int64")
    df = df.dropna(subset=["REF_DATE","Actual_incidents","GEO","Violations"])
    df["REF_DATE"] = df["REF_DATE"].astype(int)

    places = sorted({g for g in df["GEO"].unique() if is_province_geo(g)})
    print(f"[INFO] Provinces/territories detected ({len(places)}): {places}")

    backtests_all = {}
    for place in places:
        df_place = df[(df["GEO"] == place) & (df["Violations"].isin(VIOLATIONS))].copy()
        if df_place.empty:
            print(f"[WARN] no data for {place}, skipping.")
            continue
        train_and_save_for_place(df_place, place, backtests_all)

    with open(MODELS_DIR / "backtests.json", "w") as f:
        json.dump(backtests_all, f, indent=2)
    print(f"[OK] wrote backtests for all places → {MODELS_DIR/'backtests.json'}")

if __name__ == "__main__":
    main()
