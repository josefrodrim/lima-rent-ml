import pytest
from fastapi.testclient import TestClient

from api.main import app

VALID_LISTING = {
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


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


def test_health_ok(client):
    resp = client.get("/health")
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "ok"
    assert "model_version" in body


def test_districts_returns_all_18(client):
    resp = client.get("/districts")
    assert resp.status_code == 200
    body = resp.json()
    assert len(body) == 18
    assert all("district" in d and "median_price_per_m2_pen" in d for d in body)


def test_predict_returns_price_and_top_factors(client):
    resp = client.post("/predict", json=VALID_LISTING)
    assert resp.status_code == 200
    body = resp.json()
    assert body["predicted_price_pen"] > 0
    assert len(body["confidence_interval"]) == 2
    low, high = body["confidence_interval"]
    assert low < body["predicted_price_pen"] < high
    assert len(body["top_factors"]) == 3
    assert len(body["all_factors"]) == 10
    assert body["dist_to_station_km"] > 0
    # La suma de todos los factores + base_value tiene que dar la predicción.
    total = body["base_value_pen"] + sum(f["contribution_pen"] for f in body["all_factors"])
    assert total == pytest.approx(body["predicted_price_pen"], abs=0.5)


def test_predict_baseline_returns_price(client):
    resp = client.post("/predict/baseline", json=VALID_LISTING)
    assert resp.status_code == 200
    body = resp.json()
    assert body["predicted_price_pen"] > 0
    assert body["model_version"] == "baseline-median-per-district"


def test_predict_rejects_invalid_district(client):
    listing = {**VALID_LISTING, "district": "Marte"}
    resp = client.post("/predict", json=listing)
    assert resp.status_code == 422


def test_predict_rejects_area_out_of_range(client):
    listing = {**VALID_LISTING, "area_m2": 500}
    resp = client.post("/predict", json=listing)
    assert resp.status_code == 422


def test_predict_and_baseline_differ_for_a_well_connected_listing(client):
    # El baseline ignora dist_to_station_km; el modelo real sí la ve.
    predict_resp = client.post("/predict", json=VALID_LISTING).json()
    baseline_resp = client.post("/predict/baseline", json=VALID_LISTING).json()
    assert predict_resp["predicted_price_pen"] != baseline_resp["predicted_price_pen"]
