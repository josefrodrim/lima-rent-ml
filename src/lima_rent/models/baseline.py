"""El modelo tonto: mediana de precio/m² por distrito.

Es el rival que el alumno construye en el TODO 3 del notebook, y el mismo
código que sirve la API en `/predict/baseline`. Vive acá (no solo en el
notebook) porque el punto 7 del taller pide que sea servible en producción
desde el minuto 0.
"""

import pandas as pd

GLOBAL_FALLBACK_KEY = "__global__"


def fit_district_medians(df: pd.DataFrame) -> pd.Series:
    """Calcula la mediana de precio/m² por distrito, más un fallback global.

    Se ajusta solo sobre el set de entrenamiento, para que el MAE del baseline
    en test sea comparable al del modelo de verdad.
    """
    price_per_m2 = df["price_pen"] / df["area_m2"]
    medians = price_per_m2.groupby(df["district"]).median()
    medians[GLOBAL_FALLBACK_KEY] = price_per_m2.median()
    return medians


def predict_baseline(df: pd.DataFrame, district_medians: pd.Series) -> pd.Series:
    """Predice `price_pen` como mediana(price/m² del distrito) * area_m2.

    Si el distrito no está en `district_medians` (caso raro en producción),
    usa la mediana global en vez de fallar.
    """
    fallback = district_medians[GLOBAL_FALLBACK_KEY]
    median_per_m2 = df["district"].map(district_medians).fillna(fallback)
    return median_per_m2 * df["area_m2"]
