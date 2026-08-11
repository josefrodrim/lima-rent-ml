"""Configuración central del proyecto: semilla, rutas y paleta visual.

Todo lo que deba ser idéntico entre el generador de datos, el entrenamiento,
la API y la app vive acá. Ningún otro módulo debe hardcodear estos valores.
"""

from pathlib import Path

# La reproducibilidad del taller depende de esta única constante: dos corridas
# de `make train` deben dar el mismo MAE hasta el segundo decimal.
SEED = 42

# Rutas relativas a la raíz del repo, para que el proyecto corra igual
# en Colab, en Docker o en la laptop del instructor.
ROOT_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT_DIR / "data"
RAW_DATA_PATH = DATA_DIR / "raw" / "listings_raw.csv"
CLEAN_DATA_PATH = DATA_DIR / "processed" / "listings_clean.csv"
MODELS_DIR = ROOT_DIR / "models"
MODEL_PATH = MODELS_DIR / "model.joblib"
MODEL_METADATA_PATH = MODELS_DIR / "metadata.json"

N_ROWS = 8000

# Paleta única usada en todos los gráficos (notebooks, viz.py) y en la app,
# para que el taller se vea como un solo producto y no como un collage.
COLOR_NAVY = "#0A2559"
COLOR_BLUE = "#1A56E8"
COLOR_MAGENTA = "#E6115E"
PALETTE = [COLOR_NAVY, COLOR_BLUE, COLOR_MAGENTA]

# Criterios de aceptación del modelo (Fase C del prompt del taller).
# Si el generador de datos cambia, estos rangos son el chequeo de cordura.
BASELINE_MAE_MIN_PEN = 450.0
LGBM_MAE_MIN_PEN = 150.0
LGBM_MAE_MAX_PEN = 220.0
MAX_TRAIN_SECONDS = 10.0
