"""Schemas Pydantic v2 de la API. Los ejemplos de `json_schema_extra` son los
que se ven en `/docs` — se proyectan en pantalla durante el taller, tienen que
verse bien.
"""

import re
from enum import Enum

from pydantic import BaseModel, Field

from lima_rent.data.districts import DISTRICT_NAMES


def _slug(name: str) -> str:
    return re.sub(r"\W+", "_", name).strip("_").upper()


District = Enum("District", {_slug(name): name for name in DISTRICT_NAMES})


class ListingFeatures(BaseModel):
    district: District
    area_m2: float = Field(ge=20, le=400, description="Área techada en m²")
    bedrooms: int = Field(ge=1, le=5, description="Número de dormitorios")
    bathrooms: int = Field(ge=1, le=4, description="Número de baños")
    floor: int = Field(ge=1, le=20, description="Piso del departamento")
    has_parking: bool = Field(description="¿Tiene cochera?")
    has_elevator: bool = Field(description="¿El edificio tiene ascensor?")
    is_furnished: bool = Field(description="¿Está amoblado?")
    building_age_years: int = Field(ge=0, le=60, description="Antigüedad del edificio, en años")
    # Lat/lon (no distancia directa): el frontend manda la posición del pin en
    # el mapa, la API calcula dist_to_station_km server-side con la misma
    # haversine_km que usa el generador de datos y el notebook — un solo
    # lugar con esa lógica, no una copia en TypeScript.
    latitude: float = Field(ge=-12.35, le=-11.80, description="Latitud del pin en el mapa")
    longitude: float = Field(ge=-77.25, le=-76.85, description="Longitud del pin en el mapa")

    model_config = {
        "json_schema_extra": {
            "example": {
                "district": "Miraflores",
                "area_m2": 65,
                "bedrooms": 2,
                "bathrooms": 1,
                "floor": 8,
                "has_parking": True,
                "has_elevator": True,
                "is_furnished": False,
                "building_age_years": 10,
                "latitude": -12.1211,
                "longitude": -77.0294,
            }
        }
    }


class Factor(BaseModel):
    feature: str
    label: str
    contribution_pen: float


class PredictResponse(BaseModel):
    predicted_price_pen: float
    model_version: str
    confidence_interval: list[float] = Field(
        description="[precio - MAE, precio + MAE] del modelo en el set de prueba"
    )
    base_value_pen: float = Field(description="Predicción base antes de aplicar los factores")
    dist_to_station_km: float = Field(description="Distancia calculada a la estación más cercana")
    top_factors: list[Factor] = Field(description="Los 3 factores de mayor impacto absoluto")
    all_factors: list[Factor] = Field(description="Los 10 factores, para el waterfall completo")


class BaselinePredictResponse(BaseModel):
    predicted_price_pen: float
    model_version: str = "baseline-median-per-district"


class DistrictInfo(BaseModel):
    district: str
    median_price_per_m2_pen: float


class HealthResponse(BaseModel):
    status: str
    model_version: str
