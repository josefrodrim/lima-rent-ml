"""Genera `notebooks/clase_magistral.ipynb`: recorrido narrado del ciclo de
vida completo del proyecto — datos, baseline, LightGBM, explicabilidad, la
API, y el despliegue real en Vercel (con la historia real de los bugs que
aparecieron). Pensado para que un instructor lo narre celda por celda frente
a una audiencia no técnica; no tiene TODOs, todo corre solo.

Uso: `python scripts/build_masterclass.py` desde la raíz del repo.
"""

from pathlib import Path

import nbformat as nbf

REPO_URL = "https://github.com/josefrodrim/lima-rent-ml"
LIVE_URL = "https://lima-rent-ml.vercel.app"
NOTEBOOKS_DIR = Path(__file__).resolve().parents[1] / "notebooks"


def md(source: str) -> nbf.NotebookNode:
    return nbf.v4.new_markdown_cell(source.strip() + "\n")


def code(source: str) -> nbf.NotebookNode:
    return nbf.v4.new_code_cell(source.strip() + "\n")


def colab_badge(notebook_name: str) -> str:
    url = f"https://colab.research.google.com/github/josefrodrim/lima-rent-ml/blob/main/notebooks/{notebook_name}"
    return f"[![Abrir en Colab](https://colab.research.google.com/assets/colab-badge.svg)]({url})"


def build_notebook() -> nbf.NotebookNode:
    nb = nbf.v4.new_notebook()
    cells = []

    # --- Portada ---------------------------------------------------------
    cells.append(
        md(f"""
# De cero a producción: el ciclo de vida completo de lima-rent-ml

{colab_badge("clase_magistral.ipynb")}

Este notebook es distinto al del taller: acá no hay `# TODO` que resolver,
todo corre solo. La idea es que lo vayas ejecutando celda por celda mientras
alguien narra qué se hizo en cada paso y por qué — de una idea ("¿cuánto vale
mi alquiler?") a una aplicación real, viva en internet, ahora mismo, en
[{LIVE_URL}]({LIVE_URL}).

Recorremos 5 partes:

1. **Los datos** — de la nada a un dataset limpio.
2. **El modelo tonto** — el rival que hay que vencer.
3. **El modelo de verdad** — LightGBM.
4. **Entender al modelo** — por qué predice lo que predice.
5. **A producción** — servirlo por una API y desplegarlo de verdad, con los
   problemas reales que aparecieron en el camino (y no aparecen en ningún
   tutorial de 10 minutos).
""")
    )

    cells.append(
        code(f"""
!git clone -q {REPO_URL}.git
%cd lima-rent-ml
%pip install -q -e ".[notebook]"

# Un kernel ya corriendo no recoge un editable install nuevo sin reiniciar
# (Python solo procesa los .pth de pip en el arranque del intérprete), así
# que agregamos src/ al path a mano en vez de reiniciar el runtime.
import sys

sys.path.insert(0, "src")
""")
    )

    cells.append(
        code("""
import numpy as np
import pandas as pd
import requests
from IPython.display import HTML, display

from lima_rent.config import CLEAN_DATA_PATH, COLOR_MAGENTA, SEED
from lima_rent.explain import predict_contributions, shap_explainer, top_factors
from lima_rent.features import build_features
from lima_rent.models.baseline import fit_district_medians, predict_baseline
from lima_rent.models.train import train as run_training
from lima_rent.viz import build_price_heatmap, plot_distance_vs_price, plot_price_per_m2_by_district

pd.set_option("display.max_columns", 20)
""")
    )

    # --- Parte 1: el problema ---------------------------------------------
    cells.append(
        md("""
## Parte 0 — El problema, en una frase

Queremos predecir el precio de alquiler (S/) de un departamento en Lima
Metropolitana a partir de sus características (distrito, área, dormitorios,
etc.) y su ubicación exacta. Es un problema de **regresión**: la respuesta es
un número, no una categoría.

Por qué este caso funciona para explicar Machine Learning:
- Se entiende en 10 segundos, sin conocer nada de ciencia de datos.
- El error se dice en soles ("el modelo se equivoca en promedio S/ 180"), no
  hay que explicar ninguna métrica rara.
- Es geoespacial — un mapa de calor vende la idea solo, sin necesitar texto.
""")
    )

    # --- Parte 1: los datos ---------------------------------------------
    cells.append(
        md("""
## Parte 1 — Los datos: de la nada a un dataset

**No usamos datos reales de ningún portal.** Los generamos nosotros con un
script (`generate.py`), de forma determinista — dos personas que lo corran
el mismo día obtienen exactamente el mismo dataset. Esto evita depender de
scrapers que se pueden caer justo el día del taller, y evita problemas de
licencia de datos que no son nuestros.

Eso sí: la ecuación que genera los precios está diseñada para que las
relaciones que le vamos a pedir al modelo que aprenda — más cerca del
transporte público es más caro, más área es más caro, etc. — existan de
verdad en los datos, con ruido realista encima.
""")
    )
    cells.append(
        code("""
!python -m lima_rent.data.generate
!python -m lima_rent.data.clean

df = pd.read_csv(CLEAN_DATA_PATH)
df["price_per_m2"] = df["price_pen"] / df["area_m2"]
print(f"{len(df):,} avisos limpios, {df['district'].nunique()} distritos")
df.head()
""")
    )
    cells.append(code("df.describe()"))
    cells.append(
        md("**El mapa de calor**: cada punto es un aviso, coloreado por precio/m². Los puntos magenta son estaciones de transporte público.")
    )
    cells.append(code('build_price_heatmap(df, value_col="price_per_m2")'))
    cells.append(md("**Precio por m² según distrito** — la variación entre distritos es enorme, y es la primera señal que el modelo va a usar."))
    cells.append(code("plot_price_per_m2_by_district(df)"))
    cells.append(md("**Precio vs. distancia a una estación** — mientras más lejos, más barato, en promedio. Esta es la relación que más le cuesta \"ver\" al modelo tonto."))
    cells.append(code("plot_distance_vs_price(df)"))

    # --- Parte 2: baseline ---------------------------------------------
    cells.append(
        md("""
## Parte 2 — El modelo tonto (baseline)

Antes de entrenar nada "de verdad", construimos el rival más simple posible:
predecir cada aviso con la **mediana de precio/m² de su distrito**,
multiplicada por su área. Nada de dormitorios, cochera, ascensor, ni
distancia a una estación — el baseline ignora todo eso.

¿Para qué sirve un modelo tan simple? Sin él, un error de "S/ 180" no
significa nada. Con él, sabemos exactamente cuánto mejor es el modelo de
verdad — y si algún día el modelo de verdad no le gana por mucho al
baseline, es una señal de que algo anda mal.
""")
    )
    cells.append(
        code("""
medians = fit_district_medians(df)
baseline_pred = predict_baseline(df, medians)
baseline_mae = (df["price_pen"] - baseline_pred).abs().mean()

display(HTML(f"<h2 style='color:{COLOR_MAGENTA}'>MAE del modelo tonto: S/ {baseline_mae:,.0f}</h2>"))
""")
    )

    # --- Parte 3: LightGBM ---------------------------------------------
    cells.append(
        md("""
## Parte 3 — El modelo de verdad: LightGBM

LightGBM es un modelo de **gradient boosting**: entrena cientos de árboles
de decisión pequeños, uno detrás de otro, donde cada árbol nuevo se enfoca en
corregir los errores que dejaron los anteriores. Es rápido, funciona muy bien
con columnas categóricas (como "distrito") sin trucos raros, y es el
estándar de la industria para este tipo de problema tabular.

La celda de abajo entrena exactamente el mismo pipeline que usa la API en
producción (`lima_rent.models.train.train`) — el número que vas a ver acá es
el mismo que ve un usuario real de la app ahora mismo.
""")
    )
    cells.append(
        code("""
artifact = run_training()

print()
print(f"Modelo tonto (baseline):  S/ {artifact.metrics['baseline_mae_pen']:,.0f}")
print(f"LightGBM:                 S/ {artifact.metrics['lgbm_mae_pen']:,.0f}")
print(f"Tiempo de entrenamiento:  {artifact.metrics['train_seconds']:.2f}s")
""")
    )
    cells.append(
        code("""
import plotly.graph_objects as go

from lima_rent.config import COLOR_BLUE, COLOR_NAVY

fig = go.Figure(
    go.Bar(
        x=["Modelo tonto", "LightGBM"],
        y=[artifact.metrics["baseline_mae_pen"], artifact.metrics["lgbm_mae_pen"]],
        marker_color=[COLOR_NAVY, COLOR_BLUE],
        text=[f"S/ {v:,.0f}" for v in [artifact.metrics["baseline_mae_pen"], artifact.metrics["lgbm_mae_pen"]]],
        textposition="outside",
    )
)
fig.update_layout(title="Error promedio (MAE): menos es mejor", yaxis_title="S/", template="plotly_white")
fig.show()
""")
    )

    # --- Parte 4: explicabilidad ---------------------------------------------
    cells.append(
        md("""
## Parte 4 — Entender al modelo, no solo confiar en él

Un modelo que solo escupe un número no genera confianza. Necesitamos poder
decirle a alguien: "tu depa vale más por esto, y vale menos por esto otro" —
en el mismo lenguaje que usaría una persona, no en jerga de estadística.

Usamos **SHAP** (SHapley Additive exPlanations): para cada aviso, reparte el
precio predicho en la contribución exacta de cada característica, de forma
que todas las contribuciones sumadas dan exactamente la predicción. Abajo,
el *waterfall* de un aviso real del dataset.
""")
    )
    cells.append(
        code("""
listing_idx = 0
listing_row = build_features(df.iloc[[listing_idx]])
predicted_price = artifact.model.booster_.predict(listing_row)[0]

print(f"Aviso: {df.iloc[listing_idx]['district']}, {df.iloc[listing_idx]['area_m2']} m²")
print(f"Precio real:     S/ {df.iloc[listing_idx]['price_pen']:,.0f}")
print(f"Precio predicho: S/ {predicted_price:,.0f}")

explainer = shap_explainer(artifact.model)
shap_values = explainer(listing_row)
shap_values.base_values = np.asarray(shap_values.base_values).reshape(-1)

import shap

shap.plots.waterfall(shap_values[0])
""")
    )
    cells.append(
        md("Y la traducción a lenguaje humano — esto es literalmente lo que la app le muestra a un usuario real:")
    )
    cells.append(
        code("""
contributions = predict_contributions(artifact.model, listing_row)

for f in top_factors(contributions, top_n=3):
    verbo = "suma" if f["contribution_pen"] >= 0 else "resta"
    print(f"- {f['label']} {verbo} ~S/ {abs(f['contribution_pen']):.0f}")
""")
    )

    # --- Parte 5: la API ---------------------------------------------
    cells.append(
        md("""
## Parte 5 — Sirviendo el modelo: la API

Tener un modelo entrenado en un notebook no le sirve a nadie más que a
nosotros. Para que una aplicación web lo pueda usar, lo ponemos detrás de
una **API**: un mesero que recibe un pedido (las características de un
departamento, en JSON), se lo lleva a la cocina (el modelo), y trae de
vuelta la respuesta (el precio estimado).

Nuestra API (`api/main.py`, FastAPI) tiene 4 rutas:

| Ruta | Qué hace |
|---|---|
| `GET /health` | ¿Está viva la API? |
| `POST /predict` | Precio + explicación (SHAP) |
| `POST /predict/baseline` | Precio del modelo tonto |
| `GET /districts` | Mediana de precio/m² por distrito |

Abajo la probamos **sin levantar ningún servidor** — `TestClient` simula
requests HTTP directamente contra el código de la API, en el mismo proceso
del notebook.
""")
    )
    cells.append(
        code("""
from fastapi.testclient import TestClient

from api.main import app

client = TestClient(app)

response = client.post(
    "/predict",
    json={
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
    },
)
print(f"HTTP {response.status_code}")
response.json()
""")
    )

    # --- Parte 6: producción ---------------------------------------------
    cells.append(
        md(f"""
## Parte 6 — A producción de verdad

"Producción" significa una sola cosa: **cualquiera con un link puede usarlo,
no solo vos en tu laptop.** Nuestra arquitectura tiene dos piezas que
conviven en el mismo dominio, desplegadas en Vercel:

- **Next.js** — la cara bonita: el formulario, el mapa, los gráficos.
- **La función Python** (`api/main.py`) — el cerebro: cada vez que alguien
  mueve el pin en el mapa, esta función corre el modelo y devuelve un precio
  nuevo, en vivo.

### Los 4 problemas reales que aparecieron al desplegar

Ningún tutorial de 10 minutos te cuenta esto — pero es el 90% del trabajo
real de poner un modelo en producción. Los dejamos acá tal cual pasaron:

1. **Le faltaba una pieza al sistema operativo.** LightGBM necesita una
   librería del sistema (`libgomp`, para hacer cuentas en paralelo) que ni
   Docker ni el servidor de Vercel traen instalada por defecto. Solución: la
   empaquetamos nosotros mismos junto con el código y la cargamos a mano
   antes de importar el modelo.
2. **El modelo pedía una librería que decidimos no llevar a producción.**
   Para no inflar el tamaño del servidor, no instalamos scikit-learn ahí —
   pero una parte del código de LightGBM la necesitaba sin que lo
   supiéramos. Solución: usamos una función más interna del modelo que no
   depende de ella.
3. **El servidor no entendía que había DOS programas en un mismo
   proyecto** (la página web y el modelo). Al principio, construía solo uno
   y ni la página cargaba. Solución: le dijimos explícitamente qué construir
   con cada herramienta.
4. **Nuestro propio código no se encontraba a sí mismo.** Cuando la función
   se "despertaba" en el servidor, no sabía dónde buscar el resto de
   nuestros archivos. Solución: le dimos la dirección exacta.

Cada uno se encontró probando de verdad contra el servidor real — no
adivinando. Esa es, quizás, la lección más importante de esta parte: **un
modelo que funciona en tu laptop no es lo mismo que un modelo en
producción**, y la única forma de confiar en que funciona es probarlo donde
de verdad va a vivir.

### La prueba: le preguntamos a la app real, ahora mismo
""")
    )
    cells.append(
        code(f"""
resp = requests.get("{LIVE_URL}/health", timeout=10)
print(f"HTTP {{resp.status_code}}")
resp.json()
""")
    )

    # --- Cierre ---------------------------------------------
    cells.append(
        md(f"""
---

## El viaje completo, resumido

1. Generamos datos sintéticos deterministas, con relaciones realistas.
2. Construimos un modelo tonto para tener con qué comparar.
3. Entrenamos LightGBM: bajó el error de ~S/ 592 a ~S/ 188 (los números exactos de tu corrida están un poco más arriba).
4. Le pedimos al modelo que explique sus propias predicciones con SHAP.
5. Lo pusimos detrás de una API.
6. Lo desplegamos de verdad — y arreglamos los problemas reales que
   aparecieron en el camino.

**Fuera de alcance a propósito** (para explorar por tu cuenta): validación
espacial vs. aleatoria, monitoreo de drift, tuning de hiperparámetros en
serio, tests exhaustivos, feature store.

Repo completo: [{REPO_URL}]({REPO_URL}) · App en vivo: [{LIVE_URL}]({LIVE_URL})
""")
    )

    nb["cells"] = cells
    nb.metadata["kernelspec"] = {"name": "python3", "display_name": "Python 3", "language": "python"}
    return nb


def main() -> None:
    NOTEBOOKS_DIR.mkdir(parents=True, exist_ok=True)
    nb = build_notebook()
    path = NOTEBOOKS_DIR / "clase_magistral.ipynb"
    nbf.write(nb, path)
    print(f"Escrito {path}")


if __name__ == "__main__":
    main()
