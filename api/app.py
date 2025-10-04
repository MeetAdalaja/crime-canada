# api/app.py
from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from pipeline import store, VIOLATIONS


app = FastAPI(title="Ontario Crime Forecast API", version="1.0.0")

# CORS — update origins when frontend domain is known
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
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

@app.get("/api/v1/violations")
def list_violations():
    return {
        "place": "Ontario [35]",
        "violations": store.list_violations()
    }

@app.get("/api/v1/historical", response_model=HistoricalResponse)
def historical(violation: str = Query(..., description="Exact violation name")):
    if violation not in VIOLATIONS:
        raise HTTPException(400, "Unknown violation")
    hs = store.historical_series(violation)
    return {
        "violation": violation,
        **hs
    }

@app.get("/api/v1/forecast", response_model=ForecastResponse)
def forecast(
    violation: str = Query(...),
    horizon: int = Query(2030, ge=2024, le=2035)  # default to 2030, cap for safety
):
    if violation not in VIOLATIONS:
        raise HTTPException(400, "Unknown violation")
    fc = store.forecast_to_year(violation, to_year=horizon)
    if not fc["forecast"]:
        # still respond with structure
        return {
            "violation": violation,
            "from_year": fc.get("from_year") or 0,
            "to_year": fc.get("to_year") or horizon,
            "forecast": []
        }
    return {
        "violation": violation,
        **fc
    }
