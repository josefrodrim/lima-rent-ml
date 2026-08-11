"""Generador del dataset sintético de alquileres de Lima Metropolitana.

Determinista con `SEED = 42`: correrlo dos veces produce exactamente el mismo
`data/raw/listings_raw.csv`. Ver `data/README.md` para la explicación de por
qué el dataset es sintético y no scrapeado.

Uso: `python -m lima_rent.data.generate` (o `make data`, que además corre `clean.py`).
"""

import numpy as np
import pandas as pd

from lima_rent.config import N_ROWS, RAW_DATA_PATH, SEED
from lima_rent.data.districts import DISTRICT_NAMES, DISTRICTS
from lima_rent.data.stations import TRANSIT_STATIONS
from lima_rent.features import haversine_km

STATION_LATS = np.array([lat for _, lat, _ in TRANSIT_STATIONS])
STATION_LONS = np.array([lon for _, _, lon in TRANSIT_STATIONS])


def _sample_districts(rng: np.random.Generator, n: int) -> np.ndarray:
    weights = np.array([DISTRICTS[d]["weight"] for d in DISTRICT_NAMES], dtype=float)
    probs = weights / weights.sum()
    return rng.choice(DISTRICT_NAMES, size=n, p=probs)


def _sample_coordinates(rng: np.random.Generator, districts: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    sigma_deg = 0.012
    centroid_lat = np.array([DISTRICTS[d]["centroid_lat"] for d in districts])
    centroid_lon = np.array([DISTRICTS[d]["centroid_lon"] for d in districts])
    latitude = rng.normal(centroid_lat, sigma_deg)
    longitude = rng.normal(centroid_lon, sigma_deg)
    return latitude, longitude


def _sample_area_m2(rng: np.random.Generator, districts: np.ndarray) -> np.ndarray:
    area_mean = np.array([DISTRICTS[d]["area_mean_m2"] for d in districts])
    # mu se calibra para que la mediana del lognormal caiga en area_mean.
    mu = np.log(area_mean)
    sigma = 0.32
    area = rng.lognormal(mean=mu, sigma=sigma)
    area = np.clip(area, 25, 300)
    return np.round(area, 1)


def _sample_bedrooms(rng: np.random.Generator, area_m2: np.ndarray) -> np.ndarray:
    noise = rng.normal(0, 0.5, size=len(area_m2))
    bedrooms = np.round(area_m2 / 35 + noise)
    return np.clip(bedrooms, 1, 5).astype(int)


def _sample_bathrooms(rng: np.random.Generator, bedrooms: np.ndarray) -> np.ndarray:
    noise = rng.normal(0, 0.4, size=len(bedrooms))
    bathrooms = np.round(bedrooms * 0.7 + noise)
    return np.clip(bathrooms, 1, 4).astype(int)


def _district_level(districts: np.ndarray) -> np.ndarray:
    """Nivel del distrito normalizado en [0, 1] a partir de `price_per_m2_base`.

    Se reusa como proxy de "distrito más consolidado / de mayor altura" para
    sesgar piso, cochera y amoblado, en vez de inventar una escala aparte.
    """
    base = np.array([DISTRICTS[d]["price_per_m2_base"] for d in districts])
    return (base - base.min()) / (base.max() - base.min())


def _sample_floor(rng: np.random.Generator, districts: np.ndarray) -> np.ndarray:
    level = _district_level(districts)
    # Distritos periféricos (nivel bajo) sesgados a pisos bajos; distritos
    # consolidados con más edificios altos.
    shape = 1.5 + 3.0 * level
    floor = rng.gamma(shape=shape, scale=2.2, size=len(districts)) + 1
    return np.clip(np.round(floor), 1, 20).astype(int)


def _sample_amenities(
    rng: np.random.Generator, area_m2: np.ndarray, districts: np.ndarray, floor: np.ndarray
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    level = _district_level(districts)

    area_norm = np.clip((area_m2 - 25) / (300 - 25), 0, 1)
    p_parking = np.clip(0.15 + 0.55 * area_norm + 0.20 * level, 0.02, 0.97)
    has_parking = rng.random(len(area_m2)) < p_parking

    floor_norm = np.clip((floor - 1) / 19, 0, 1)
    p_elevator = np.clip(0.10 + 0.85 * floor_norm, 0.03, 0.97)
    has_elevator = rng.random(len(floor)) < p_elevator

    is_top_furnished_district = np.isin(districts, ["Miraflores", "Barranco", "San Isidro"])
    p_furnished = np.where(is_top_furnished_district, 0.40, 0.22)
    is_furnished = rng.random(len(districts)) < p_furnished

    return has_parking, has_elevator, is_furnished


def _sample_building_age(rng: np.random.Generator, n: int) -> np.ndarray:
    age = rng.gamma(shape=2.0, scale=7.0, size=n)
    return np.clip(np.round(age), 0, 45).astype(int)


def _compute_dist_to_station_km(latitude: np.ndarray, longitude: np.ndarray) -> np.ndarray:
    # Distancia vectorizada (n_avisos x n_estaciones) para no depender de un
    # loop Python; el alumno hace la versión con list comprehension en el TODO 2.
    dist_matrix = haversine_km(
        latitude[:, None], longitude[:, None], STATION_LATS[None, :], STATION_LONS[None, :]
    )
    return np.round(dist_matrix.min(axis=1), 3)


def _sample_posted_date(rng: np.random.Generator, n: int) -> np.ndarray:
    today = pd.Timestamp("2026-08-10")
    days_ago = rng.integers(0, 180, size=n)
    return (today - pd.to_timedelta(days_ago, unit="D")).values


def _compute_price_pen(
    rng: np.random.Generator,
    districts: np.ndarray,
    area_m2: np.ndarray,
    dist_to_station_km: np.ndarray,
    has_parking: np.ndarray,
    is_furnished: np.ndarray,
    has_elevator: np.ndarray,
    building_age_years: np.ndarray,
    floor: np.ndarray,
    bathrooms: np.ndarray,
) -> np.ndarray:
    price_per_m2_base = np.array([DISTRICTS[d]["price_per_m2_base"] for d in districts])

    base = price_per_m2_base * area_m2
    transit = 1 + 0.14 * np.exp(-dist_to_station_km / 0.8)
    parking = 1 + 0.09 * has_parking
    furnished = 1 + 0.13 * is_furnished
    elevator = 1 + 0.04 * has_elevator
    age = 1 - 0.006 * np.minimum(building_age_years, 30)
    floor_eff = 1 + 0.012 * floor - 0.0006 * floor**2
    bath_eff = 1 + 0.05 * (bathrooms - 1)
    noise = rng.lognormal(mean=0, sigma=0.14, size=len(districts))

    price = base * transit * parking * furnished * elevator * age * floor_eff * bath_eff * noise
    return np.round(price / 50) * 50


def _inject_dirt(df: pd.DataFrame, rng: np.random.Generator) -> pd.DataFrame:
    """Ensucia ~4% de las filas para que la limpieza del taller sea real.

    - Outliers absurdos en `area_m2` (> 800).
    - ~2% de `price_pen` como NaN.
    - Inconsistencias de formato en `district` (mayúsculas / espacios).
    - ~15 filas duplicadas exactas.
    """
    df = df.copy()
    n = len(df)

    outlier_idx = rng.choice(n, size=40, replace=False)
    df.loc[outlier_idx, "area_m2"] = rng.uniform(800, 1500, size=len(outlier_idx)).round(1)

    nan_idx = rng.choice(n, size=int(n * 0.02), replace=False)
    df.loc[nan_idx, "price_pen"] = np.nan

    dirty_format_idx = rng.choice(n, size=100, replace=False)
    format_fns = [str.lower, str.upper, lambda s: f"{s} "]
    for i in dirty_format_idx:
        fn = format_fns[rng.integers(0, len(format_fns))]
        df.loc[i, "district"] = fn(df.loc[i, "district"])

    dup_idx = rng.choice(n, size=15, replace=False)
    dup_rows = df.loc[dup_idx]
    df = pd.concat([df, dup_rows], ignore_index=True)

    return df


def generate_listings(seed: int = SEED, n_rows: int = N_ROWS) -> pd.DataFrame:
    """Genera el DataFrame sintético completo (sucio) de avisos de alquiler."""
    rng = np.random.default_rng(seed)

    districts = _sample_districts(rng, n_rows)
    latitude, longitude = _sample_coordinates(rng, districts)
    area_m2 = _sample_area_m2(rng, districts)
    bedrooms = _sample_bedrooms(rng, area_m2)
    bathrooms = _sample_bathrooms(rng, bedrooms)
    floor = _sample_floor(rng, districts)
    has_parking, has_elevator, is_furnished = _sample_amenities(rng, area_m2, districts, floor)
    building_age_years = _sample_building_age(rng, n_rows)
    dist_to_station_km = _compute_dist_to_station_km(latitude, longitude)
    posted_date = _sample_posted_date(rng, n_rows)
    price_pen = _compute_price_pen(
        rng,
        districts,
        area_m2,
        dist_to_station_km,
        has_parking,
        is_furnished,
        has_elevator,
        building_age_years,
        floor,
        bathrooms,
    )

    df = pd.DataFrame(
        {
            "listing_id": [f"LIM-{i + 1:05d}" for i in range(n_rows)],
            "district": districts,
            "latitude": latitude,
            "longitude": longitude,
            "area_m2": area_m2,
            "bedrooms": bedrooms,
            "bathrooms": bathrooms,
            "floor": floor,
            "has_parking": has_parking,
            "has_elevator": has_elevator,
            "is_furnished": is_furnished,
            "building_age_years": building_age_years,
            "dist_to_station_km": dist_to_station_km,
            "posted_date": posted_date,
            "price_pen": price_pen,
        }
    )

    return _inject_dirt(df, rng)


def main() -> None:
    df = generate_listings()
    RAW_DATA_PATH.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(RAW_DATA_PATH, index=False)
    print(f"Generadas {len(df)} filas -> {RAW_DATA_PATH}")


if __name__ == "__main__":
    main()
