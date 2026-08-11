# Sobre los datos

**Los datos de este repositorio son 100% sintéticos.** No provienen de ningún portal de avisos ni de ningún scraper. Se generan con `src/lima_rent/data/generate.py`, un script determinista (`SEED = 42`) que produce siempre el mismo `data/raw/listings_raw.csv`.

## Por qué sintéticos y no reales

- **Reproducibilidad del taller.** Un taller en vivo de 120 minutos no puede depender de que un scraper siga funcionando el día del evento, ni de la disponibilidad de un servicio externo.
- **Licencias.** Scrapear un portal inmobiliario para redistribuir el dataset en un repo público abierto tiene una licencia ambigua en el mejor de los casos. Los datos sintéticos evitan el problema por completo.
- **Control pedagógico.** Al generarlos nosotros, podemos garantizar que el efecto de `dist_to_station_km` sobre el precio exista y sea claro — es justo lo que el TODO 2 y el SHAP del taller necesitan mostrar.

Los valores base (`price_per_m2_base` por distrito, en `src/lima_rent/data/districts.py`) están **calibrados a rangos públicos de referencia** de precio por m² en Lima Metropolitana, no son datos reales de avisos individuales.

## Cómo sustituirlos por datos reales

Si en algún momento quieres correr este pipeline sobre datos reales:

1. Reemplaza `data/raw/listings_raw.csv` por tu propio CSV, respetando las mismas columnas (ver la tabla en `generate.py`).
2. Ajusta o reescribe `src/lima_rent/data/clean.py` según la suciedad real de tu fuente (los pasos de limpieza acá son específicos a la suciedad que nosotros mismos inyectamos).
3. Vuelve a correr `make train`: `features.py` y `train.py` no asumen nada sobre el origen de los datos, solo sobre el schema de columnas.

## Archivos

- `raw/listings_raw.csv` — salida directa del generador, con ~4% de suciedad intencional (outliers, NaNs, inconsistencias de formato, duplicados).
- `processed/listings_clean.csv` — salida de `clean.py`, es la que consume el modelo.
