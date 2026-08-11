"""API de producción. Vercel detecta `app` acá y la despliega como función
serverless (ver /docs/functions/runtimes/python) — no hay adaptador ASGI que
escribir a mano, ni servidor que levantar en el código.

El modelo se carga una sola vez a nivel de módulo: en cold start paga el costo
de leer `models/model.joblib`, y las invocaciones sobre una instancia ya
caliente (Fluid Compute) lo reusan sin volver a leerlo del disco.
"""

import sys
from pathlib import Path

import pandas as pd
from fastapi import FastAPI

from lima_rent._native import preload_libgomp

# Tiene que correr ANTES que cualquier import (directo o indirecto, vía
# joblib.load del modelo) de `lightgbm` — ver src/lima_rent/_native.py.
preload_libgomp()

# Vercel puede cargar este archivo como script suelto (no como el submódulo
# `api.main`), donde `from api.schemas import ...` fallaría. Agregamos esta
# carpeta al path e importamos `schemas` a secas: funciona igual corriendo
# local vía `uvicorn api.main:app` que desplegado en Vercel.
sys.path.insert(0, str(Path(__file__).resolve().parent))

from schemas import (  # noqa: E402
    BaselinePredictResponse,
    DistrictInfo,
    HealthResponse,
    ListingFeatures,
    PredictResponse,
    TopFactor,
)

from lima_rent.explain import predict_contributions, top_factors  # noqa: E402
from lima_rent.features import FEATURE_COLUMNS, build_features  # noqa: E402
from lima_rent.models.baseline import GLOBAL_FALLBACK_KEY, predict_baseline  # noqa: E402
from lima_rent.models.registry import ModelArtifact, load_artifact  # noqa: E402

app = FastAPI(
    title="lima-rent-ml API",
    description="Predicción de precio de alquiler en Lima Metropolitana.",
    version="0.1.0",
)

_artifact: ModelArtifact = load_artifact()


def _listing_to_dataframe(listing: ListingFeatures) -> pd.DataFrame:
    row = {
        "district": listing.district.value,
        "area_m2": listing.area_m2,
        "bedrooms": listing.bedrooms,
        "bathrooms": listing.bathrooms,
        "floor": listing.floor,
        "has_parking": listing.has_parking,
        "has_elevator": listing.has_elevator,
        "is_furnished": listing.is_furnished,
        "building_age_years": listing.building_age_years,
        "dist_to_station_km": listing.dist_to_station_km,
    }
    return pd.DataFrame([row], columns=FEATURE_COLUMNS)


@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(status="ok", model_version=_artifact.model_version)


@app.post("/predict", response_model=PredictResponse)
def predict(listing: ListingFeatures) -> PredictResponse:
    x = build_features(_listing_to_dataframe(listing))
    # `.booster_.predict()` (no `.predict()` del wrapper sklearn): el wrapper
    # necesita scikit-learn instalado para `get_params()` internamente, y no
    # está en las dependencias de producción a propósito (ver pyproject.toml).
    predicted_price = float(_artifact.model.booster_.predict(x)[0])

    contributions = predict_contributions(_artifact.model, x)
    factors = [TopFactor(**f) for f in top_factors(contributions, top_n=3)]

    mae = _artifact.metrics["lgbm_mae_pen"]
    confidence_interval = [round(predicted_price - mae, 1), round(predicted_price + mae, 1)]

    return PredictResponse(
        predicted_price_pen=round(predicted_price, 1),
        model_version=_artifact.model_version,
        confidence_interval=confidence_interval,
        top_factors=factors,
    )


@app.post("/predict/baseline", response_model=BaselinePredictResponse)
def predict_baseline_endpoint(listing: ListingFeatures) -> BaselinePredictResponse:
    df = _listing_to_dataframe(listing)
    predicted_price = float(predict_baseline(df, _artifact.district_medians).iloc[0])
    return BaselinePredictResponse(predicted_price_pen=round(predicted_price, 1))


@app.get("/districts", response_model=list[DistrictInfo])
def districts() -> list[DistrictInfo]:
    medians = _artifact.district_medians.drop(GLOBAL_FALLBACK_KEY)
    return [
        DistrictInfo(district=district, median_price_per_m2_pen=round(float(value), 1))
        for district, value in medians.sort_values(ascending=False).items()
    ]


@app.get("/", include_in_schema=False)
def root() -> dict[str, str]:
    return {"docs": "/docs", "health": "/health"}
