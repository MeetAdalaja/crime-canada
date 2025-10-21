# # api/app.py
# from fastapi import FastAPI, Query, HTTPException
# from fastapi.middleware.cors import CORSMiddleware
# from pydantic import BaseModel
# from typing import List
# from pipeline import store, VIOLATIONS

# app = FastAPI(title="Ontario Crime Forecast API", version="1.1.0")

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],  # tighten later if you want
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# class HistoricalResponse(BaseModel):
#     violation: str
#     years: List[int]
#     actual: List[float]
#     last_observed_year: int

# class ForecastItem(BaseModel):
#     year: int
#     yhat: float

# class ForecastResponse(BaseModel):
#     violation: str
#     from_year: int
#     to_year: int
#     forecast: List[ForecastItem]

# class PredictYearResponse(BaseModel):
#     violation: str
#     year: int
#     yhat: float | None
#     actual: float | None
#     train_upto_year: int | None

# @app.get("/api/v1/violations")
# def list_violations():
#     return {"place": "Ontario [35]", "violations": store.list_violations()}

# @app.get("/api/v1/historical", response_model=HistoricalResponse)
# def historical(violation: str = Query(...)):
#     if violation not in VIOLATIONS:
#         raise HTTPException(400, "Unknown violation")
#     hs = store.historical_series(violation)
#     return {"violation": violation, **hs}

# @app.get("/api/v1/forecast", response_model=ForecastResponse)
# def forecast(violation: str = Query(...), horizon: int = Query(2030, ge=2021, le=2035)):
#     if violation not in VIOLATIONS:
#         raise HTTPException(400, "Unknown violation")
#     fc = store.forecast_to_year(violation, to_year=horizon)
#     return {"violation": violation, **fc}

# @app.get("/api/v1/predict_year", response_model=PredictYearResponse)
# def predict_year(violation: str = Query(...), year: int = Query(..., ge=2021, le=2030)):
#     if violation not in VIOLATIONS:
#         raise HTTPException(400, "Unknown violation")
#     res = store.predict_specific_year(violation, year)
#     return {"violation": violation, **res}



# api/app.py
from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from pipeline import store, VIOLATIONS

app = FastAPI(title="Ontario Crime Forecast API", version="1.2.0")

# CORS: keep permissive for now, tighten later if you want
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # or ["http://localhost:5173","https://<your-vercel>"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------- Pydantic models (single) ----------
class HistoricalResponse(BaseModel):
    violation: str
    years: List[int]
    actual: List[float]
    last_observed_year: int

class ForecastItem(BaseModel):
    year: int
    yhat: float

class ForecastResponse(BaseModel):
    violation: str
    from_year: Optional[int]
    to_year: Optional[int]
    forecast: List[ForecastItem]

class PredictYearResponse(BaseModel):
    violation: str
    year: int
    yhat: Optional[float]
    actual: Optional[float]
    train_upto_year: Optional[int]

# ---------- Pydantic models (multi) ----------
class HistoricalItem(HistoricalResponse):
    pass

class HistoricalMultiResponse(BaseModel):
    place: str
    items: List[HistoricalItem]

class ForecastItemMulti(BaseModel):
    violation: str
    from_year: Optional[int]
    to_year: Optional[int]
    forecast: List[ForecastItem]

class ForecastMultiResponse(BaseModel):
    place: str
    horizon: int
    items: List[ForecastItemMulti]

class PredictYearItemMulti(PredictYearResponse):
    pass

class PredictYearMultiResponse(BaseModel):
    place: str
    year: int
    items: List[PredictYearItemMulti]

# ---------- Helpers ----------
def _norm_violations(qv: Optional[List[str]]) -> List[str]:
    if not qv or len(qv) == 0:
        return VIOLATIONS
    # Allow "ALL" / "all"
    lower = [v.lower() for v in qv]
    if "all" in lower:
        return VIOLATIONS
    bad = [v for v in qv if v not in VIOLATIONS]
    if bad:
        raise HTTPException(400, f"Unknown violations: {bad}")
    return qv

# ---------- Existing single endpoints ----------
@app.get("/api/v1/violations")
def list_violations():
    return {"place": "Ontario [35]", "violations": store.list_violations()}

@app.get("/api/v1/historical", response_model=HistoricalResponse)
def historical(violation: str = Query(...)):
    if violation not in VIOLATIONS:
        raise HTTPException(400, "Unknown violation")
    hs = store.historical_series(violation)
    return {"violation": violation, **hs}

@app.get("/api/v1/forecast", response_model=ForecastResponse)
def forecast(violation: str = Query(...), horizon: int = Query(2030, ge=2021, le=2035)):
    if violation not in VIOLATIONS:
        raise HTTPException(400, "Unknown violation")
    fc = store.forecast_to_year(violation, to_year=horizon)
    return {"violation": violation, **fc}

@app.get("/api/v1/predict_year", response_model=PredictYearResponse)
def predict_year(violation: str = Query(...), year: int = Query(..., ge=2021, le=2030)):
    if violation not in VIOLATIONS:
        raise HTTPException(400, "Unknown violation")
    res = store.predict_specific_year(violation, year)
    return {"violation": violation, **res}

# ---------- New multi endpoints ----------
@app.get("/api/v1/historical_multi", response_model=HistoricalMultiResponse)
def historical_multi(violations: Optional[List[str]] = Query(None)):
    vs = _norm_violations(violations)
    items: List[Dict[str, Any]] = []
    for v in vs:
        hs = store.historical_series(v)
        items.append({"violation": v, **hs})
    return {"place": "Ontario [35]", "items": items}

@app.get("/api/v1/forecast_multi", response_model=ForecastMultiResponse)
def forecast_multi(
    violations: Optional[List[str]] = Query(None),
    horizon: int = Query(2030, ge=2021, le=2035)
):
    vs = _norm_violations(violations)
    items: List[Dict[str, Any]] = []
    for v in vs:
        fc = store.forecast_to_year(v, to_year=horizon)
        items.append({"violation": v, **fc})
    return {"place": "Ontario [35]", "horizon": horizon, "items": items}

@app.get("/api/v1/predict_year_multi", response_model=PredictYearMultiResponse)
def predict_year_multi(
    violations: Optional[List[str]] = Query(None),
    year: int = Query(..., ge=2021, le=2030)
):
    vs = _norm_violations(violations)
    items: List[Dict[str, Any]] = []
    for v in vs:
        res = store.predict_specific_year(v, year)
        items.append({"violation": v, **res})
    return {"place": "Ontario [35]", "year": year, "items": items}
