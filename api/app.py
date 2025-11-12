# # api/app.py
# from fastapi import FastAPI, Query, HTTPException
# from fastapi.middleware.cors import CORSMiddleware
# from pydantic import BaseModel
# from typing import List, Optional, Dict, Any
# from pipeline import store, VIOLATIONS

# app = FastAPI(title="Crime Forecast API (Canada provinces)", version="2.0.0")

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"],
# )

# # -------- models ----------
# class HistoricalResponse(BaseModel):
#     place: str
#     violation: str
#     years: List[int]
#     actual: List[float]
#     last_observed_year: int

# class ForecastItem(BaseModel):
#     year: int
#     yhat: float

# class ForecastResponse(BaseModel):
#     place: str
#     violation: str
#     from_year: Optional[int]
#     to_year: Optional[int]
#     forecast: List[ForecastItem]

# class PredictYearResponse(BaseModel):
#     place: str
#     violation: str
#     year: int
#     yhat: Optional[float]
#     actual: Optional[float]
#     train_upto_year: Optional[int]

# class HistoricalMultiResponse(BaseModel):
#     place: str
#     items: List[HistoricalResponse]

# class ForecastItemMulti(BaseModel):
#     place: str
#     violation: str
#     from_year: Optional[int]
#     to_year: Optional[int]
#     forecast: List[ForecastItem]

# class ForecastMultiResponse(BaseModel):
#     place: str
#     horizon: int
#     items: List[ForecastItemMulti]

# class PredictYearMultiResponse(BaseModel):
#     place: str
#     year: int
#     items: List[PredictYearResponse]

# # -------- endpoints ----------
# @app.get("/api/v1/places")
# def list_places():
#     return {"places": store.list_places()}

# @app.get("/api/v1/violations")
# def list_violations():
#     return {"violations": store.list_violations()}

# @app.get("/api/v1/historical", response_model=HistoricalResponse)
# def historical(place: str = Query("Ontario [35]"), violation: str = Query(...)):
#     if violation not in VIOLATIONS:
#         raise HTTPException(400, "Unknown violation")
#     hs = store.historical_series(place, violation)
#     return {"place": place, "violation": violation, **hs}

# @app.get("/api/v1/forecast", response_model=ForecastResponse)
# def forecast(place: str = Query("Ontario [35]"), violation: str = Query(...), horizon: int = Query(2030, ge=2021, le=2035)):
#     if violation not in VIOLATIONS:
#         raise HTTPException(400, "Unknown violation")
#     fc = store.forecast_to_year(place, violation, to_year=horizon)
#     return {"place": place, "violation": violation, **fc}

# @app.get("/api/v1/predict_year", response_model=PredictYearResponse)
# def predict_year(place: str = Query("Ontario [35]"), violation: str = Query(...), year: int = Query(..., ge=2021, le=2030)):
#     if violation not in VIOLATIONS:
#         raise HTTPException(400, "Unknown violation")
#     res = store.predict_specific_year(place, violation, year)
#     return {"place": place, "violation": violation, **res}

# @app.get("/api/v1/historical_multi", response_model=HistoricalMultiResponse)
# def historical_multi(place: str = Query("Ontario [35]"), violations: Optional[List[str]] = Query(None)):
#     vs = violations or VIOLATIONS
#     bad = [v for v in vs if v not in VIOLATIONS]
#     if bad: raise HTTPException(400, f"Unknown violations: {bad}")
#     items = []
#     for v in vs:
#         hs = store.historical_series(place, v)
#         items.append({"place": place, "violation": v, **hs})
#     return {"place": place, "items": items}

# @app.get("/api/v1/forecast_multi", response_model=ForecastMultiResponse)
# def forecast_multi(place: str = Query("Ontario [35]"), violations: Optional[List[str]] = Query(None),
#                    horizon: int = Query(2030, ge=2021, le=2035)):
#     vs = violations or VIOLATIONS
#     bad = [v for v in vs if v not in VIOLATIONS]
#     if bad: raise HTTPException(400, f"Unknown violations: {bad}")
#     items = []
#     for v in vs:
#         fc = store.forecast_to_year(place, v, to_year=horizon)
#         items.append({"place": place, "violation": v, **fc})
#     return {"place": place, "horizon": horizon, "items": items}

# @app.get("/api/v1/predict_year_multi", response_model=PredictYearMultiResponse)
# def predict_year_multi(place: str = Query("Ontario [35]"), violations: Optional[List[str]] = Query(None),
#                        year: int = Query(..., ge=2021, le=2030)):
#     vs = violations or VIOLATIONS
#     bad = [v for v in vs if v not in VIOLATIONS]
#     if bad: raise HTTPException(400, f"Unknown violations: {bad}")
#     items = []
#     for v in vs:
#         rec = store.predict_specific_year(place, v, year)
#         items.append({"place": place, "violation": v, **rec})
#     return {"place": place, "year": year, "items": items}



# api/app.py
from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from pipeline import store, VIOLATIONS

app = FastAPI(title="Crime Forecast API (Canada provinces)", version="2.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"],
)

# -------- models ----------
class HistoricalResponse(BaseModel):
    place: str
    violation: str
    years: List[int]
    actual: List[float]
    last_observed_year: int

class ForecastItem(BaseModel):
    year: int
    yhat: float

class ForecastResponse(BaseModel):
    place: str
    violation: str
    from_year: Optional[int]
    to_year: Optional[int]
    forecast: List[ForecastItem]

class PredictYearResponse(BaseModel):
    place: str
    violation: str
    year: int
    yhat: Optional[float]
    actual: Optional[float]
    train_upto_year: Optional[int]

class HistoricalMultiResponse(BaseModel):
    place: str
    items: List[HistoricalResponse]

class ForecastItemMulti(BaseModel):
    place: str
    violation: str
    from_year: Optional[int]
    to_year: Optional[int]
    forecast: List[ForecastItem]

class ForecastMultiResponse(BaseModel):
    place: str
    horizon: int
    items: List[ForecastItemMulti]

class PredictYearMultiResponse(BaseModel):
    place: str
    year: int
    items: List[PredictYearResponse]

# -------- endpoints ----------
@app.get("/api/v1/places")
def list_places():
    return {"places": store.list_places()}

@app.get("/api/v1/violations")
def list_violations():
    return {"violations": store.list_violations()}

def _label_for_places(place: Optional[str], places: Optional[List[str]]) -> str:
    if places and len(places) > 0:
        if len(places) == 1:
            return places[0]
        return " + ".join(places)
    return place or "Ontario [35]"

@app.get("/api/v1/historical", response_model=HistoricalResponse)
def historical(
    place: str = Query("Ontario [35]"),
    violation: str = Query(...),
    places: Optional[List[str]] = Query(None)
):
    if violation not in VIOLATIONS:
        raise HTTPException(400, "Unknown violation")
    label = _label_for_places(place, places)
    if places and len(places) > 1:
        hs = store.historical_series_multi(places, violation)
        return {"place": label, "violation": violation, **hs}
    # fallback to single place
    hs = store.historical_series(places[0] if places else place, violation)
    return {"place": label, "violation": violation, **hs}

@app.get("/api/v1/historical_multi", response_model=HistoricalMultiResponse)
def historical_multi(
    place: str = Query("Ontario [35]"),
    violations: Optional[List[str]] = Query(None),
    places: Optional[List[str]] = Query(None)
):
    vs = violations or VIOLATIONS
    bad = [v for v in vs if v not in VIOLATIONS]
    if bad: raise HTTPException(400, f"Unknown violations: {bad}")
    label = _label_for_places(place, places)
    items = []
    if places and len(places) > 1:
        for v in vs:
            hs = store.historical_series_multi(places, v)
            items.append({"place": label, "violation": v, **hs})
        return {"place": label, "items": items}
    # single place
    p = places[0] if places else place
    for v in vs:
        hs = store.historical_series(p, v)
        items.append({"place": label, "violation": v, **hs})
    return {"place": label, "items": items}

@app.get("/api/v1/forecast", response_model=ForecastResponse)
def forecast(
    place: str = Query("Ontario [35]"),
    violation: str = Query(...),
    horizon: int = Query(2030, ge=2021, le=2035),
    places: Optional[List[str]] = Query(None)
):
    if violation not in VIOLATIONS:
        raise HTTPException(400, "Unknown violation")
    label = _label_for_places(place, places)
    if places and len(places) > 1:
        fc = store.forecast_to_year_multi(places, violation, horizon)
        return {"place": label, "violation": violation, **fc}
    fc = store.forecast_to_year(places[0] if places else place, violation, to_year=horizon)
    return {"place": label, "violation": violation, **fc}

@app.get("/api/v1/forecast_multi", response_model=ForecastMultiResponse)
def forecast_multi(
    place: str = Query("Ontario [35]"),
    violations: Optional[List[str]] = Query(None),
    horizon: int = Query(2030, ge=2021, le=2035),
    places: Optional[List[str]] = Query(None)
):
    vs = violations or VIOLATIONS
    bad = [v for v in vs if v not in VIOLATIONS]
    if bad: raise HTTPException(400, f"Unknown violations: {bad}")
    label = _label_for_places(place, places)
    items = []
    if places and len(places) > 1:
        for v in vs:
            fc = store.forecast_to_year_multi(places, v, horizon)
            items.append({"place": label, "violation": v, **fc})
        return {"place": label, "horizon": horizon, "items": items}
    # single place
    p = places[0] if places else place
    for v in vs:
        fc = store.forecast_to_year(p, v, horizon)
        items.append({"place": label, "violation": v, **fc})
    return {"place": label, "horizon": horizon, "items": items}

@app.get("/api/v1/predict_year", response_model=PredictYearResponse)
def predict_year(
    place: str = Query("Ontario [35]"),
    violation: str = Query(...),
    year: int = Query(..., ge=2021, le=2030),
    places: Optional[List[str]] = Query(None)
):
    if violation not in VIOLATIONS:
        raise HTTPException(400, "Unknown violation")
    label = _label_for_places(place, places)
    if places and len(places) > 1:
        res = store.predict_specific_year_multi(places, violation, year)
        return {"place": label, "violation": violation, **res}
    res = store.predict_specific_year(places[0] if places else place, violation, year)
    return {"place": label, "violation": violation, **res}

@app.get("/api/v1/predict_year_multi", response_model=PredictYearMultiResponse)
def predict_year_multi(
    place: str = Query("Ontario [35]"),
    violations: Optional[List[str]] = Query(None),
    year: int = Query(..., ge=2021, le=2030),
    places: Optional[List[str]] = Query(None)
):
    vs = violations or VIOLATIONS
    bad = [v for v in vs if v not in VIOLATIONS]
    if bad: raise HTTPException(400, f"Unknown violations: {bad}")
    label = _label_for_places(place, places)
    items = []
    if places and len(places) > 1:
        for v in vs:
            rec = store.predict_specific_year_multi(places, v, year)
            items.append({"place": label, "violation": v, **rec})
        return {"place": label, "year": year, "items": items}
    # single place
    p = places[0] if places else place
    for v in vs:
        rec = store.predict_specific_year(p, v, year)
        items.append({"place": label, "violation": v, **rec})
    return {"place": label, "year": year, "items": items}
