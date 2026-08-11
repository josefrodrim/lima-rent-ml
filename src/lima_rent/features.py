"""Funciones de features compartidas entre el generador de datos, el notebook y el modelo.

`haversine_km` vive acá (y no en `data/generate.py`) porque el alumno la vuelve
a usar en el TODO 2 del notebook: es la misma función, provista, no algo que
tenga que reimplementar.
"""

import numpy as np


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
