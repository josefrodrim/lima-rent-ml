"""Funciones de features compartidas entre el generador de datos, el notebook y el modelo.

`haversine_km` vive acá (y no en `data/generate.py`) porque el alumno la vuelve
a usar en el TODO 2 del notebook: es la misma función, provista, no algo que
tenga que reimplementar.
"""

import numpy as np
import pandas as pd

# Columnas que entran al modelo. `district` va como categórica nativa de
# LightGBM (dtype "category"); el resto son numéricas o booleanas.
CATEGORICAL_COLUMNS: list[str] = ["district"]
NUMERIC_COLUMNS: list[str] = [
    "area_m2",
    "bedrooms",
    "bathrooms",
    "floor",
    "has_parking",
    "has_elevator",
    "is_furnished",
    "building_age_years",
    "dist_to_station_km",
]
FEATURE_COLUMNS: list[str] = CATEGORICAL_COLUMNS + NUMERIC_COLUMNS
TARGET_COLUMN: str = "price_pen"


def build_features(df: pd.DataFrame) -> pd.DataFrame:
    """Selecciona y tipa las columnas de `FEATURE_COLUMNS` para entrenar o predecir.

    `district` queda como dtype "category": es lo que LightGBM necesita para
    tratarla como categórica nativa sin que nosotros hagamos one-hot encoding.
    """
    x = df[FEATURE_COLUMNS].copy()
    x["district"] = x["district"].astype("category")
    for col in ["has_parking", "has_elevator", "is_furnished"]:
        x[col] = x[col].astype(int)
    return x


def haversine_km(
    lat1: float | np.ndarray,
    lon1: float | np.ndarray,
    lat2: float | np.ndarray,
    lon2: float | np.ndarray,
) -> float | np.ndarray:
    """Distancia haversine en kilómetros entre dos puntos (lat, lon) en grados.

    Acepta escalares o arrays de numpy (broadcasting estándar), para poder
    usarse tanto en una comprensión de lista fila por fila como de forma
    vectorizada sobre una columna completa.
    """
    r_earth_km = 6371.0088
    phi1, phi2 = np.radians(lat1), np.radians(lat2)
    dphi = np.radians(lat2 - lat1)
    dlambda = np.radians(lon2 - lon1)
    a = np.sin(dphi / 2) ** 2 + np.cos(phi1) * np.cos(phi2) * np.sin(dlambda / 2) ** 2
    return 2 * r_earth_km * np.arcsin(np.sqrt(a))
