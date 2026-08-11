"""Explicabilidad del modelo: SHAP para el notebook, contribuciones nativas para producción.

La API (y el frontend) usan `predict_contributions`, que llama a
`Booster.predict(..., pred_contrib=True)` — el TreeSHAP exacto de LightGBM,
sin la librería `shap`. Es la misma matemática que `shap.TreeExplainer` para
modelos de árboles, pero sin cargar `shap` + `numba` + `llvmlite` en una
función serverless de Vercel. El notebook sí usa `shap` (import local en
`shap_explainer`) porque en Colab el tamaño del paquete no importa y el
waterfall plot de `shap` es mejor material didáctico que uno hecho a mano.
"""

import pandas as pd

FEATURE_LABELS_ES = {
    "district": "Distrito",
    "area_m2": "Área",
    "bedrooms": "Dormitorios",
    "bathrooms": "Baños",
    "floor": "Piso",
    "has_parking": "Cochera",
    "has_elevator": "Ascensor",
    "is_furnished": "Amoblado",
    "building_age_years": "Antigüedad",
    "dist_to_station_km": "Distancia a estación",
}


def predict_contributions(model, x_row: pd.DataFrame) -> dict[str, float]:
    """Contribución en soles de cada feature a la predicción de una fila.

    `x_row` debe tener exactamente una fila y las columnas de `FEATURE_COLUMNS`.
    """
    contrib = model.booster_.predict(x_row, pred_contrib=True)[0]
    feature_names = list(x_row.columns)
    values = dict(zip(feature_names, contrib[:-1], strict=True))
    values["base_value"] = float(contrib[-1])
    return values


def top_factors(contributions: dict[str, float], top_n: int = 3) -> list[dict]:
    """Las `top_n` features de mayor impacto absoluto (en soles), listas para mostrar."""
    items = [(k, v) for k, v in contributions.items() if k != "base_value"]
    items.sort(key=lambda kv: abs(kv[1]), reverse=True)
    return [
        {"feature": k, "label": FEATURE_LABELS_ES.get(k, k), "contribution_pen": round(float(v), 1)}
        for k, v in items[:top_n]
    ]


def shap_explainer(model):
    """`shap.TreeExplainer` para uso exclusivo en el notebook — no se usa en la API."""
    import shap

    return shap.TreeExplainer(model.booster_)
