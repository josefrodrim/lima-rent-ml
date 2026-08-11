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


# (nombre, centroid_lat, centroid_lon, price_per_m2_base, weight, area_mean_m2)
_DISTRICT_ROWS: list[tuple[str, float, float, float, float, float]] = [
    ("San Isidro", -12.0972, -77.0367, 75.0, 9, 85),
    ("Miraflores", -12.1211, -77.0294, 68.0, 12, 75),
    ("Barranco", -12.1494, -77.0214, 60.0, 6, 70),
    ("Surco (Santiago de Surco)", -12.1350, -76.9950, 48.0, 11, 95),
    ("La Molina", -12.0868, -76.9452, 50.0, 6, 110),
    ("Magdalena del Mar", -12.0955, -77.0757, 45.0, 6, 78),
    ("San Borja", -12.1083, -76.9986, 55.0, 7, 90),
    ("Jesús María", -12.0736, -77.0490, 44.0, 8, 80),
    ("Lince", -12.0851, -77.0333, 42.0, 5, 68),
    ("Pueblo Libre", -12.0736, -77.0631, 40.0, 5, 75),
    ("San Miguel", -12.0774, -77.0928, 38.0, 5, 78),
    ("Surquillo", -12.1147, -77.0175, 37.0, 5, 65),
    ("Chorrillos", -12.1747, -77.0181, 33.0, 4, 82),
    ("Los Olivos", -11.9689, -77.0715, 28.0, 3, 88),
    ("San Martín de Porres", -11.9989, -77.0806, 25.0, 3, 90),
    ("Callao", -12.0566, -77.1181, 26.0, 3, 85),
    ("Ate", -12.0464, -76.9160, 24.0, 2, 92),
    ("Comas", -11.9430, -77.0620, 22.0, 2, 95),
]

DISTRICTS: dict[str, DistrictSpec] = {
    name: {
        "centroid_lat": lat,
        "centroid_lon": lon,
        "price_per_m2_base": price_per_m2_base,
        "weight": weight,
        "area_mean_m2": area_mean_m2,
    }
    for name, lat, lon, price_per_m2_base, weight, area_mean_m2 in _DISTRICT_ROWS
}

DISTRICT_NAMES: list[str] = list(DISTRICTS.keys())
