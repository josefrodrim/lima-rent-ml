"""Entrena el baseline y LightGBM, reporta MAE y guarda el artefacto servible.

Uso: `python -m lima_rent.models.train` (o `make train`).

El tracking de MLflow queda acá para que el código exista y sea real, pero el
taller NO levanta `mlflow ui` en vivo (punto 6 del prompt del taller): se
explica con una captura de pantalla. `mlflow.start_run()` escribe en
`./mlruns` con el backend de archivos por defecto, sin necesitar un servidor.
"""

import time

import lightgbm as lgb
import mlflow
import pandas as pd
from sklearn.metrics import mean_absolute_error
from sklearn.model_selection import train_test_split

from lima_rent.config import (
    BASELINE_MAE_MIN_PEN,
    CLEAN_DATA_PATH,
    LGBM_MAE_MAX_PEN,
    LGBM_MAE_MIN_PEN,
    MAX_TRAIN_SECONDS,
    SEED,
)
from lima_rent.features import build_features
from lima_rent.models.baseline import fit_district_medians, predict_baseline
from lima_rent.models.registry import ModelArtifact, save_artifact

LGBM_PARAMS = {
    "n_estimators": 300,
    "learning_rate": 0.05,
    "num_leaves": 31,
    "max_depth": -1,
    "min_child_samples": 20,
    "random_state": SEED,
    "verbose": -1,
}


def _check_acceptance(baseline_mae: float, lgbm_mae: float, train_seconds: float) -> list[str]:
    warnings = []
    if baseline_mae <= BASELINE_MAE_MIN_PEN:
        warnings.append(
            f"baseline_mae={baseline_mae:.1f} <= {BASELINE_MAE_MIN_PEN} (esperado por encima)"
        )
    if not (LGBM_MAE_MIN_PEN <= lgbm_mae <= LGBM_MAE_MAX_PEN):
        warnings.append(
            f"lgbm_mae={lgbm_mae:.1f} fuera de [{LGBM_MAE_MIN_PEN}, {LGBM_MAE_MAX_PEN}]"
        )
    if train_seconds >= MAX_TRAIN_SECONDS:
        warnings.append(f"train_seconds={train_seconds:.2f} >= {MAX_TRAIN_SECONDS}")
    return warnings


def train() -> ModelArtifact:
    df = pd.read_csv(CLEAN_DATA_PATH)
    df_train, df_test = train_test_split(df, test_size=0.2, random_state=SEED)

    with mlflow.start_run(run_name="lima-rent-lgbm"):
        mlflow.log_param("seed", SEED)
        mlflow.log_param("n_rows_train", len(df_train))
        mlflow.log_param("n_rows_test", len(df_test))
        mlflow.log_params(LGBM_PARAMS)

        # Baseline: mediana de precio/m² por distrito, ajustada solo en train.
        district_medians = fit_district_medians(df_train)
        baseline_pred = predict_baseline(df_test, district_medians)
        baseline_mae = mean_absolute_error(df_test["price_pen"], baseline_pred)

        # LightGBM sobre las mismas columnas que verá la API.
        x_train, y_train = build_features(df_train), df_train["price_pen"]
        x_test, y_test = build_features(df_test), df_test["price_pen"]

        start = time.perf_counter()
        model = lgb.LGBMRegressor(**LGBM_PARAMS)
        model.fit(x_train, y_train, categorical_feature=["district"])
        train_seconds = time.perf_counter() - start

        lgbm_pred = model.predict(x_test)
        lgbm_mae = mean_absolute_error(y_test, lgbm_pred)

        mlflow.log_metric("baseline_mae_pen", baseline_mae)
        mlflow.log_metric("lgbm_mae_pen", lgbm_mae)
        mlflow.log_metric("train_seconds", train_seconds)

    metrics = {
        "baseline_mae_pen": round(float(baseline_mae), 2),
        "lgbm_mae_pen": round(float(lgbm_mae), 2),
        "train_seconds": round(float(train_seconds), 3),
        "n_rows_train": len(df_train),
        "n_rows_test": len(df_test),
    }

    artifact = ModelArtifact(
        model=model,
        district_medians=district_medians,
        feature_columns=list(x_train.columns),
        categorical_columns=["district"],
        metrics=metrics,
    )
    save_artifact(artifact)

    print(f"Baseline MAE (test): S/ {baseline_mae:,.1f}")
    print(f"LightGBM MAE (test): S/ {lgbm_mae:,.1f}")
    print(f"Tiempo de entrenamiento: {train_seconds:.2f}s")

    warnings = _check_acceptance(baseline_mae, lgbm_mae, train_seconds)
    if warnings:
        print("\nADVERTENCIA — criterios de aceptación no cumplidos:")
        for w in warnings:
            print(f"  - {w}")
    else:
        print("\nCriterios de aceptación OK.")

    return artifact


if __name__ == "__main__":
    train()
