# api/app.py
from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
from pipeline import store, VIOLATIONS

app = FastAPI(title="Ontario Crime Forecast API", version="1.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten later if you want
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
    from_year: int
    to_year: int
    forecast: List[ForecastItem]

class PredictYearResponse(BaseModel):
    violation: str
    year: int
    yhat: float | None
    actual: float | None
    train_upto_year: int | None

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
