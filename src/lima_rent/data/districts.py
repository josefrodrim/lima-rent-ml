"""Distritos de Lima Metropolitana usados en el generador de datos sintéticos.

Los valores de `price_per_m2_base`, `weight` y `area_mean_m2` están calibrados
a mano para que la distribución resultante sea *creíble* para alguien que
conoce Lima (más avisos y precios más altos en la zona top, menos avisos y
precios más bajos en la periferia), no para replicar un dataset real de
avisos. Ver `data/README.md` para la aclaración completa.
"""

from typing import TypedDict


class DistrictSpec(TypedDict):
    centroid_lat: float
    centroid_lon: float
    price_per_m2_base: float  # S/ por m², nivel base antes de ajustes por atributos
    weight: float  # peso relativo de frecuencia de avisos (no necesita sumar 1)
    area_mean_m2: float  # tamaño típico de los avisos del distrito, para el lognormal


DISTRICTS: dict[str, DistrictSpec] = {
    "San Isidro": {"centroid_lat": -12.0972, "centroid_lon": -77.0367, "price_per_m2_base": 75.0, "weight": 9, "area_mean_m2": 85},
    "Miraflores": {"centroid_lat": -12.1211, "centroid_lon": -77.0294, "price_per_m2_base": 68.0, "weight": 12, "area_mean_m2": 75},
    "Barranco": {"centroid_lat": -12.1494, "centroid_lon": -77.0214, "price_per_m2_base": 60.0, "weight": 6, "area_mean_m2": 70},
    "Surco (Santiago de Surco)": {"centroid_lat": -12.1350, "centroid_lon": -76.9950, "price_per_m2_base": 48.0, "weight": 11, "area_mean_m2": 95},
    "La Molina": {"centroid_lat": -12.0868, "centroid_lon": -76.9452, "price_per_m2_base": 50.0, "weight": 6, "area_mean_m2": 110},
    "Magdalena del Mar": {"centroid_lat": -12.0955, "centroid_lon": -77.0757, "price_per_m2_base": 45.0, "weight": 6, "area_mean_m2": 78},
    "San Borja": {"centroid_lat": -12.1083, "centroid_lon": -76.9986, "price_per_m2_base": 55.0, "weight": 7, "area_mean_m2": 90},
    "Jesús María": {"centroid_lat": -12.0736, "centroid_lon": -77.0490, "price_per_m2_base": 44.0, "weight": 8, "area_mean_m2": 80},
    "Lince": {"centroid_lat": -12.0851, "centroid_lon": -77.0333, "price_per_m2_base": 42.0, "weight": 5, "area_mean_m2": 68},
    "Pueblo Libre": {"centroid_lat": -12.0736, "centroid_lon": -77.0631, "price_per_m2_base": 40.0, "weight": 5, "area_mean_m2": 75},
    "San Miguel": {"centroid_lat": -12.0774, "centroid_lon": -77.0928, "price_per_m2_base": 38.0, "weight": 5, "area_mean_m2": 78},
    "Surquillo": {"centroid_lat": -12.1147, "centroid_lon": -77.0175, "price_per_m2_base": 37.0, "weight": 5, "area_mean_m2": 65},
    "Chorrillos": {"centroid_lat": -12.1747, "centroid_lon": -77.0181, "price_per_m2_base": 33.0, "weight": 4, "area_mean_m2": 82},
    "Los Olivos": {"centroid_lat": -11.9689, "centroid_lon": -77.0715, "price_per_m2_base": 28.0, "weight": 3, "area_mean_m2": 88},
    "San Martín de Porres": {"centroid_lat": -11.9989, "centroid_lon": -77.0806, "price_per_m2_base": 25.0, "weight": 3, "area_mean_m2": 90},
    "Callao": {"centroid_lat": -12.0566, "centroid_lon": -77.1181, "price_per_m2_base": 26.0, "weight": 3, "area_mean_m2": 85},
    "Ate": {"centroid_lat": -12.0464, "centroid_lon": -76.9160, "price_per_m2_base": 24.0, "weight": 2, "area_mean_m2": 92},
    "Comas": {"centroid_lat": -11.9430, "centroid_lon": -77.0620, "price_per_m2_base": 22.0, "weight": 2, "area_mean_m2": 95},
}

DISTRICT_NAMES: list[str] = list(DISTRICTS.keys())
