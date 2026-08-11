import pandas as pd
import pytest

from lima_rent.models.baseline import GLOBAL_FALLBACK_KEY, fit_district_medians, predict_baseline


@pytest.fixture
def train_df() -> pd.DataFrame:
    # Miraflores: price/m2 = 100, 100, 200 -> mediana 100. Comas: 20, 40 -> mediana 30.
    return pd.DataFrame(
        {
            "district": ["Miraflores", "Miraflores", "Miraflores", "Comas", "Comas"],
            "area_m2": [50.0, 60.0, 40.0, 50.0, 50.0],
            "price_pen": [5000.0, 6000.0, 8000.0, 1000.0, 2000.0],
        }
    )


def test_fit_district_medians_computes_per_district_median(train_df):
    medians = fit_district_medians(train_df)
    assert medians["Miraflores"] == pytest.approx(100.0)
    assert medians["Comas"] == pytest.approx(30.0)


def test_fit_district_medians_includes_global_fallback(train_df):
    medians = fit_district_medians(train_df)
    assert GLOBAL_FALLBACK_KEY in medians.index


def test_predict_baseline_multiplies_median_by_area(train_df):
    medians = fit_district_medians(train_df)
    test_df = pd.DataFrame({"district": ["Miraflores"], "area_m2": [70.0]})

    pred = predict_baseline(test_df, medians)

    assert pred.iloc[0] == pytest.approx(100.0 * 70.0)


def test_predict_baseline_falls_back_for_unseen_district(train_df):
    medians = fit_district_medians(train_df)
    test_df = pd.DataFrame({"district": ["Ate"], "area_m2": [50.0]})

    pred = predict_baseline(test_df, medians)

    assert pred.iloc[0] == pytest.approx(medians[GLOBAL_FALLBACK_KEY] * 50.0)


def test_predict_baseline_handles_multiple_districts_at_once(train_df):
    medians = fit_district_medians(train_df)
    test_df = pd.DataFrame(
        {"district": ["Miraflores", "Comas"], "area_m2": [10.0, 10.0]}
    )

    pred = predict_baseline(test_df, medians)

    assert pred.tolist() == pytest.approx([1000.0, 300.0])
