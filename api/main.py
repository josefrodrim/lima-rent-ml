"""API de producción. Vercel detecta `app` acá y la despliega como función
serverless (ver /docs/functions/runtimes/python) — no hay adaptador ASGI que
escribir a mano, ni servidor que levantar en el código.

El modelo se carga una sola vez a nivel de módulo: en cold start paga el costo
de leer `models/model.joblib`, y las invocaciones sobre una instancia ya
caliente (Fluid Compute) lo reusan sin volver a leerlo del disco.
"""

import sys
from pathlib import Path

import numpy as np
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
    Factor,
    HealthResponse,
    ListingFeatures,
    PredictResponse,
)

from lima_rent.data.districts import DISTRICTS  # noqa: E402
from lima_rent.data.stations import TRANSIT_STATIONS  # noqa: E402
from lima_rent.explain import predict_contributions, top_factors  # noqa: E402
from lima_rent.features import FEATURE_COLUMNS, build_features, haversine_km  # noqa: E402
from lima_rent.models.baseline import GLOBAL_FALLBACK_KEY, predict_baseline  # noqa: E402
from lima_rent.models.registry import ModelArtifact, load_artifact  # noqa: E402

_STATION_LATS = np.array([lat for _, lat, _ in TRANSIT_STATIONS])
_STATION_LONS = np.array([lon for _, _, lon in TRANSIT_STATIONS])

app = FastAPI(
    title="lima-rent-ml API",
    description="Predicción de precio de alquiler en Lima Metropolitana.",
    version="0.1.0",
)

_artifact: ModelArtifact = load_artifact()


def _nearest_station_km(latitude: float, longitude: float) -> float:
    distances = haversine_km(latitude, longitude, _STATION_LATS, _STATION_LONS)
    return float(min(distances))


def _listing_to_dataframe(listing: ListingFeatures) -> tuple[pd.DataFrame, float]:
    dist_to_station_km = _nearest_station_km(listing.latitude, listing.longitude)
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
        "dist_to_station_km": dist_to_station_km,
    }
    return pd.DataFrame([row], columns=FEATURE_COLUMNS), dist_to_station_km


@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(status="ok", model_version=_artifact.model_version)


@app.post("/predict", response_model=PredictResponse)
def predict(listing: ListingFeatures) -> PredictResponse:
    df, dist_to_station_km = _listing_to_dataframe(listing)
    x = build_features(df)
    # `.booster_.predict()` (no `.predict()` del wrapper sklearn): el wrapper
    # necesita scikit-learn instalado para `get_params()` internamente, y no
    # está en las dependencias de producción a propósito (ver pyproject.toml).
    predicted_price = float(_artifact.model.booster_.predict(x)[0])

    contributions = predict_contributions(_artifact.model, x)
    top_3 = [Factor(**f) for f in top_factors(contributions, top_n=3)]
    all_9 = [Factor(**f) for f in top_factors(contributions, top_n=len(FEATURE_COLUMNS))]

    mae = _artifact.metrics["lgbm_mae_pen"]
    confidence_interval = [round(predicted_price - mae, 1), round(predicted_price + mae, 1)]

    return PredictResponse(
        predicted_price_pen=round(predicted_price, 1),
        model_version=_artifact.model_version,
        confidence_interval=confidence_interval,
        base_value_pen=round(contributions["base_value"], 1),
        dist_to_station_km=round(dist_to_station_km, 3),
        top_factors=top_3,
        all_factors=all_9,
        mae_pen=round(mae, 1),
    )


@app.post("/predict/baseline", response_model=BaselinePredictResponse)
def predict_baseline_endpoint(listing: ListingFeatures) -> BaselinePredictResponse:
    df, _ = _listing_to_dataframe(listing)
    predicted_price = float(predict_baseline(df, _artifact.district_medians).iloc[0])
    return BaselinePredictResponse(
        predicted_price_pen=round(predicted_price, 1),
        mae_pen=_artifact.metrics["baseline_mae_pen"],
    )


@app.get("/districts", response_model=list[DistrictInfo])
def districts() -> list[DistrictInfo]:
    medians = _artifact.district_medians.drop(GLOBAL_FALLBACK_KEY)
    return [
        DistrictInfo(
            district=district,
            median_price_per_m2_pen=round(float(value), 1),
            centroid_lat=DISTRICTS[district]["centroid_lat"],
            centroid_lon=DISTRICTS[district]["centroid_lon"],
        )
        for district, value in medians.sort_values(ascending=False).items()
    ]


# Sin handler en "/": esa ruta la sirve el frontend Next.js. Compartir dominio
# con la API (confirmado con un spike real: Vercel no recorta el prefijo,
# expone las rutas de la función tal cual las define FastAPI) significa que
# "/" tiene que quedar libre para la home de Next.js.
