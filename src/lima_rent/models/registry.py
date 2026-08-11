"""Persistencia del artefacto de modelo: `models/model.joblib` + `models/metadata.json`.

Deliberadamente simple (un archivo, no un servidor de registro) porque el
punto 5 del taller es claro: el modelo registrado se MUESTRA, no se construye
en vivo. Esto es lo mínimo que necesita la API para servir predicciones.
"""

import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

import joblib
import pandas as pd

from lima_rent.config import MODEL_METADATA_PATH, MODEL_PATH


@dataclass
class ModelArtifact:
    model: Any  # lgb.LGBMRegressor entrenado
    district_medians: pd.Series  # baseline, ver models/baseline.py
    feature_columns: list[str]
    categorical_columns: list[str]
    metrics: dict[str, float]
    model_version: str = field(default_factory=lambda: datetime.now(tz=timezone.utc).strftime("%Y%m%d-%H%M%S"))


def save_artifact(artifact: ModelArtifact) -> None:
    MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(
        {
            "model": artifact.model,
            "district_medians": artifact.district_medians,
            "feature_columns": artifact.feature_columns,
            "categorical_columns": artifact.categorical_columns,
            "model_version": artifact.model_version,
        },
        MODEL_PATH,
    )

    metadata = {
        "model_version": artifact.model_version,
        "feature_columns": artifact.feature_columns,
        "categorical_columns": artifact.categorical_columns,
        "metrics": artifact.metrics,
        "saved_at": datetime.now(tz=timezone.utc).isoformat(),
    }
    MODEL_METADATA_PATH.write_text(json.dumps(metadata, indent=2, ensure_ascii=False))


def load_artifact() -> ModelArtifact:
    payload = joblib.load(MODEL_PATH)
    metadata = json.loads(MODEL_METADATA_PATH.read_text())
    return ModelArtifact(
        model=payload["model"],
        district_medians=payload["district_medians"],
        feature_columns=payload["feature_columns"],
        categorical_columns=payload["categorical_columns"],
        metrics=metadata["metrics"],
        model_version=payload["model_version"],
    )
