"""Genera `notebooks/taller_solucion.ipynb` y deriva `notebooks/taller_alumno.ipynb`.

Los dos notebooks se generan desde ESTE único archivo para que nunca se
desincronicen: las celdas de los 4 TODOs se escriben una sola vez, con su
versión resuelta y su versión vacía (stub) juntas. `taller_alumno.ipynb` se
arma copiando la solución y reemplazando cada celda marcada `todo_id` por su
stub — nunca a mano.

Uso: `python scripts/build_notebooks.py` desde la raíz del repo.
"""

from pathlib import Path

import nbformat as nbf

REPO_URL = "https://github.com/josefrodrim/lima-rent-ml"
NOTEBOOKS_DIR = Path(__file__).resolve().parents[1] / "notebooks"


def md(source: str) -> nbf.NotebookNode:
    return nbf.v4.new_markdown_cell(source.strip() + "\n")


def code(source: str, todo_id: int | None = None) -> nbf.NotebookNode:
    cell = nbf.v4.new_code_cell(source.strip() + "\n")
    if todo_id is not None:
        cell.metadata["todo_id"] = todo_id
    return cell


def colab_badge(notebook_name: str) -> str:
    url = f"https://colab.research.google.com/github/josefrodrim/lima-rent-ml/blob/main/notebooks/{notebook_name}"
    return f"[![Abrir en Colab](https://colab.research.google.com/assets/colab-badge.svg)]({url})"


# --- Stubs de los 4 TODOs (van al notebook del alumno) ----------------------

TODO_STUBS = {
    1: '''
# TODO 1: crea la columna `price_per_m2`.
# Es price_pen dividido entre area_m2. Nada más.

df["price_per_m2"] = ...  # tu código acá

assert "price_per_m2" in df.columns, "Falta crear la columna price_per_m2"
assert abs(df["price_per_m2"].iloc[0] - df["price_pen"].iloc[0] / df["area_m2"].iloc[0]) < 1e-6, (
    "price_per_m2 debe ser exactamente price_pen / area_m2"
)
print("TODO 1 resuelto correctamente.")
''',
    2: '''
# TODO 2: para cada aviso, calcula la distancia (km) a la estación de
# transporte más cercana. Tienes `haversine_km(lat1, lon1, lat2, lon2)` ya
# importada y la lista `TRANSIT_STATIONS` (nombre, lat, lon).
# Pista: una comprensión de lista sobre TRANSIT_STATIONS + min() te alcanza.

def dist_to_nearest_station(lat: float, lon: float) -> float:
    ...  # tu código acá

df["dist_to_station_km_calc"] = df.apply(
    lambda row: dist_to_nearest_station(row["latitude"], row["longitude"]), axis=1
)

assert np.allclose(df["dist_to_station_km_calc"], df["dist_to_station_km"], atol=0.01), (
    "Tu distancia calculada no coincide con la real. "
    "Revisa que estés tomando el mínimo sobre TODAS las estaciones."
)
print("TODO 2 resuelto correctamente.")
''',
    3: '''
# TODO 3: implementa el modelo tonto. `predict_baseline(df)` debe predecir
# cada aviso con la MEDIANA de price_per_m2 de SU distrito, multiplicada por
# su area_m2. Usamos toda la tabla (no hay train/test acá, es solo para que
# veas el número con el que competimos).

def predict_baseline(df: pd.DataFrame) -> pd.Series:
    ...  # tu código acá

baseline_pred = predict_baseline(df)
baseline_mae = (df["price_pen"] - baseline_pred).abs().mean()

assert 300 < baseline_mae < 750, (
    f"MAE del baseline = S/ {baseline_mae:,.0f}, fuera de lo esperado. "
    "Revisa que agrupes por distrito y uses la mediana, no el promedio."
)
print(f"MAE del modelo tonto: S/ {baseline_mae:,.0f}")
''',
}


def build_solution_notebook() -> nbf.NotebookNode:
    nb = nbf.v4.new_notebook()
    cells = []

    cells.append(
        md(f"""
# De cero a producción en 2 horas: cuánto vale realmente tu alquiler

{colab_badge("taller_solucion.ipynb")}

**Este es el notebook de SOLUCIÓN** — todo resuelto, con comentarios extra.
Si te atoraste en el notebook del alumno, seguí desde acá sin perder el hilo.

Vamos a predecir el precio de alquiler (S/) de un departamento en Lima
Metropolitana. Corre las celdas en orden, de arriba hacia abajo.
""")
    )

    cells.append(
        code(f"""
!git clone -q {REPO_URL}.git
%cd lima-rent-ml
!pip install -q -e ".[notebook]"
""")
    )

    cells.append(
        code("""
import numpy as np
import pandas as pd
from IPython.display import HTML, display

from lima_rent.config import CLEAN_DATA_PATH, COLOR_MAGENTA, SEED
from lima_rent.data.stations import TRANSIT_STATIONS
from lima_rent.explain import shap_explainer
from lima_rent.features import build_features, haversine_km
from lima_rent.models.train import train as run_training
from lima_rent.viz import build_price_heatmap, plot_distance_vs_price, plot_price_per_m2_by_district

pd.set_option("display.max_columns", 20)
""")
    )

    cells.append(md("## 1. Los datos\n\nYa vienen generados y limpios en el repo (`data/processed/listings_clean.csv`), listos para modelar."))
    cells.append(
        code("""
df = pd.read_csv(CLEAN_DATA_PATH)
print(f"{len(df):,} avisos, {df['district'].nunique()} distritos")
df.head()
""")
    )
    cells.append(code("df.describe()"))

    cells.append(md(
        "## 2. EDA geoespacial\n\n"
        "El mapa de calor es el primer visual que vende la idea: la ubicación importa, "
        "y se nota a simple vista. Los puntos magenta son las estaciones de transporte."
    ))
    cells.append(code('build_price_heatmap(df, value_col="price_pen")'))

    cells.append(md(
        "## 3. TODO 1 — `price_per_m2`\n\n"
        "La victoria fácil: crea la columna dividiendo `price_pen` entre `area_m2`."
    ))
    cells.append(code('df["price_per_m2"] = df["price_pen"] / df["area_m2"]\n\nassert "price_per_m2" in df.columns\nprint("TODO 1 resuelto correctamente.")', todo_id=1))
    cells.append(code("plot_price_per_m2_by_district(df)"))

    cells.append(md(
        "## 4. TODO 2 — `dist_to_station_km`\n\n"
        "La variable que más peso tiene en el precio, y la que tú mismo vas a construir."
    ))
    cells.append(
        code(
            """
def dist_to_nearest_station(lat: float, lon: float) -> float:
    return min(haversine_km(lat, lon, s_lat, s_lon) for _, s_lat, s_lon in TRANSIT_STATIONS)


df["dist_to_station_km_calc"] = df.apply(
    lambda row: dist_to_nearest_station(row["latitude"], row["longitude"]), axis=1
)

assert np.allclose(df["dist_to_station_km_calc"], df["dist_to_station_km"], atol=0.01)
print("TODO 2 resuelto correctamente.")
""",
            todo_id=2,
        )
    )
    cells.append(code("plot_distance_vs_price(df)"))

    cells.append(md(
        "## 5. TODO 3 — el modelo tonto (baseline)\n\n"
        "El rival que tiene que perder. Sin este número, un MAE de S/ 180 no significa nada."
    ))
    cells.append(
        code(
            """
def predict_baseline(df: pd.DataFrame) -> pd.Series:
    district_median = df.groupby("district")["price_per_m2"].transform("median")
    return district_median * df["area_m2"]


baseline_pred = predict_baseline(df)
baseline_mae = (df["price_pen"] - baseline_pred).abs().mean()

assert 300 < baseline_mae < 750
print(f"MAE del modelo tonto: S/ {baseline_mae:,.0f}")
""",
            todo_id=3,
        )
    )
    cells.append(code('display(HTML(f"<h1 style=\'color:{COLOR_MAGENTA}\'>S/ {baseline_mae:,.0f}</h1>"))'))

    cells.append(md(
        "## 6. El modelo de verdad: LightGBM\n\n"
        "Ya está resuelto — corre las celdas. Usa exactamente el mismo pipeline que entrena "
        "el modelo que sirve la API en producción (`lima_rent.models.train`), así que el número "
        "que ves acá es el mismo que ves en producción.\n\n"
        "**Para jugar con un hiperparámetro:** antes de correr la celda, probá por ejemplo "
        "`import lima_rent.models.train as train_mod; train_mod.LGBM_PARAMS[\"num_leaves\"] = 63` "
        "y volvé a entrenar. Mirá cómo se mueve el MAE."
    ))
    cells.append(
        code(
            """
artifact = run_training()

print()
print(f"Modelo tonto (baseline):  S/ {artifact.metrics['baseline_mae_pen']:,.0f}")
print(f"LightGBM:                 S/ {artifact.metrics['lgbm_mae_pen']:,.0f}")
print(f"Tiempo de entrenamiento:  {artifact.metrics['train_seconds']:.2f}s")
"""
        )
    )

    cells.append(md(
        "## 7. TODO 4 — leé el SHAP\n\n"
        "Elegimos un aviso cualquiera del dataset. El *waterfall* muestra cómo cada "
        "característica empuja el precio arriba o abajo desde el valor base "
        "(el promedio de todos los avisos)."
    ))
    cells.append(
        code(
            """
listing_idx = 0
listing_row = build_features(df.iloc[[listing_idx]])
predicted_price = artifact.model.predict(listing_row)[0]

print(f"Aviso: {df.iloc[listing_idx]['district']}, {df.iloc[listing_idx]['area_m2']} m²")
print(f"Precio real:    S/ {df.iloc[listing_idx]['price_pen']:,.0f}")
print(f"Precio predicho: S/ {predicted_price:,.0f}")

explainer = shap_explainer(artifact.model)
shap_values = explainer(listing_row)
shap_values.base_values = np.asarray(shap_values.base_values).reshape(-1)

import shap
shap.plots.waterfall(shap_values[0])
"""
        )
    )
    cells.append(md(
        """
### TODO 4 — tu turno (no hay una respuesta única)

Mirando el waterfall de arriba, respondé en 2-3 líneas cada una:

1. **¿Qué empuja el precio hacia arriba?**

   _(tu respuesta acá)_

2. **¿Qué lo empuja hacia abajo?**

   _(tu respuesta acá)_

3. **¿Coincide con tu intuición como limeño/a?** ¿Hay algo que el modelo "cree" que a ti te sorprende?

   _(tu respuesta acá)_
"""
    ))

    cells.append(md(
        f"""
---

## Y ahora ¿qué?

Esto fue una probadita. Quedó afuera a propósito: validación espacial, monitoreo de
drift, tuning de hiperparámetros en serio, tests exhaustivos, feature store — ver
`docs/guion_taller.md` para el porqué de cada uno.

Repo completo, con la API y el frontend en producción: [{REPO_URL}]({REPO_URL})
"""
    ))

    nb["cells"] = cells
    nb.metadata["kernelspec"] = {"name": "python3", "display_name": "Python 3", "language": "python"}
    return nb


def build_student_notebook(solution_nb: nbf.NotebookNode) -> nbf.NotebookNode:
    nb = nbf.from_dict(solution_nb)
    for cell in nb["cells"]:
        todo_id = cell.get("metadata", {}).get("todo_id")
        if todo_id is not None:
            cell["source"] = TODO_STUBS[todo_id].strip() + "\n"
            cell["outputs"] = []
            cell["execution_count"] = None

    # Título distinto para que no se confundan los dos archivos abiertos a la vez.
    intro = nb["cells"][0]
    intro["source"] = intro["source"].replace(
        "**Este es el notebook de SOLUCIÓN** — todo resuelto, con comentarios extra.\n"
        "Si te atoraste en el notebook del alumno, seguí desde acá sin perder el hilo.",
        "Tenés 4 celdas marcadas `# TODO`. El resto ya corre solo.\n"
        "Si te atoras, el notebook de solución (`taller_solucion.ipynb`) es idéntico a este,"
        " resuelto — abrilo y seguí desde ahí sin perder el hilo del taller.",
    ).replace(
        colab_badge("taller_solucion.ipynb"), colab_badge("taller_alumno.ipynb")
    )
    return nb


def main() -> None:
    NOTEBOOKS_DIR.mkdir(parents=True, exist_ok=True)

    solution_nb = build_solution_notebook()
    solution_path = NOTEBOOKS_DIR / "taller_solucion.ipynb"
    nbf.write(solution_nb, solution_path)
    print(f"Escrito {solution_path}")

    student_nb = build_student_notebook(solution_nb)
    student_path = NOTEBOOKS_DIR / "taller_alumno.ipynb"
    nbf.write(student_nb, student_path)
    print(f"Escrito {student_path}")


if __name__ == "__main__":
    main()
