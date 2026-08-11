import numpy as np
import pandas as pd
import pytest

from lima_rent.features import FEATURE_COLUMNS, build_features, haversine_km


def test_haversine_km_same_point_is_zero():
    assert haversine_km(-12.05, -77.03, -12.05, -77.03) == pytest.approx(0.0, abs=1e-9)


def test_haversine_km_known_distance():
    # San Isidro (centro) -> Miraflores (centro): ~3-4 km en línea recta.
    dist = haversine_km(-12.0972, -77.0367, -12.1211, -77.0294)
    assert 2.5 < dist < 4.5


def test_haversine_km_symmetric():
    a = haversine_km(-12.09, -77.03, -12.15, -77.02)
    b = haversine_km(-12.15, -77.02, -12.09, -77.03)
    assert a == pytest.approx(b)


def test_haversine_km_vectorized_matches_scalar():
    lats1 = np.array([-12.09, -12.10])
    lons1 = np.array([-77.03, -77.02])
    lat2, lon2 = -12.15, -77.02

    vectorized = haversine_km(lats1, lons1, lat2, lon2)
    scalar = [haversine_km(lats1[i], lons1[i], lat2, lon2) for i in range(2)]

    assert vectorized == pytest.approx(scalar)


def test_haversine_km_matches_known_earth_geometry():
    # Un grado de latitud son ~111.2 km en cualquier punto de la Tierra.
    dist = haversine_km(0.0, 0.0, 1.0, 0.0)
    assert dist == pytest.approx(111.2, abs=0.5)


@pytest.fixture
def sample_df() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "district": ["Miraflores", "Comas"],
            "area_m2": [60.0, 80.0],
            "bedrooms": [2, 3],
            "bathrooms": [1, 2],
            "floor": [5, 2],
            "has_parking": [True, False],
            "has_elevator": [True, False],
            "is_furnished": [False, False],
            "building_age_years": [10, 20],
            "dist_to_station_km": [0.5, 3.0],
            "price_pen": [3000.0, 1200.0],
        }
    )


def test_build_features_selects_expected_columns(sample_df):
    x = build_features(sample_df)
    assert list(x.columns) == FEATURE_COLUMNS


def test_build_features_district_is_category_dtype(sample_df):
    x = build_features(sample_df)
    assert isinstance(x["district"].dtype, pd.CategoricalDtype)


def test_build_features_casts_booleans_to_int(sample_df):
    x = build_features(sample_df)
    for col in ["has_parking", "has_elevator", "is_furnished"]:
        assert x[col].dtype.kind in "iu"
