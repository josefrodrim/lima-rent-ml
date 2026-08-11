"""Limpieza del dataset sintético: de `listings_raw.csv` a `listings_clean.csv`.

Reproduce, en código versionado, exactamente lo que el bloque de EDA del
taller le muestra a la sala en vivo (sección 5 del guion): normalizar
`district`, botar outliers absurdos de `area_m2` y filas sin `price_pen`, y
quitar duplicados exactos.

Uso: `python -m lima_rent.data.clean` (o `make data`, que corre `generate.py` antes).
"""

import pandas as pd

from lima_rent.config import CLEAN_DATA_PATH, RAW_DATA_PATH
from lima_rent.data.districts import DISTRICT_NAMES

AREA_M2_MAX_VALID = 800

_DISTRICT_LOOKUP = {name.strip().lower(): name for name in DISTRICT_NAMES}


def _normalize_district(raw_value: str) -> str:
    key = raw_value.strip().lower()
    return _DISTRICT_LOOKUP.get(key, raw_value.strip())


def clean_listings(df_raw: pd.DataFrame) -> pd.DataFrame:
    """Aplica las reglas de limpieza y devuelve un DataFrame listo para modelar."""
    df = df_raw.copy()

    df["district"] = df["district"].apply(_normalize_district)
    df = df[df["area_m2"] <= AREA_M2_MAX_VALID]
    df = df.dropna(subset=["price_pen"])
    df = df.drop_duplicates()

    return df.reset_index(drop=True)


def main() -> None:
    df_raw = pd.read_csv(RAW_DATA_PATH)
    df_clean = clean_listings(df_raw)

    CLEAN_DATA_PATH.parent.mkdir(parents=True, exist_ok=True)
    df_clean.to_csv(CLEAN_DATA_PATH, index=False)

    print(f"Raw: {len(df_raw)} filas -> Clean: {len(df_clean)} filas -> {CLEAN_DATA_PATH}")


if __name__ == "__main__":
    main()
