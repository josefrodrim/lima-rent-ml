.PHONY: data train serve app test lint demo clean

data:  ## Genera y limpia el dataset sintético (data/raw + data/processed)
	python -m lima_rent.data.generate
	python -m lima_rent.data.clean

train:  ## Entrena baseline + LightGBM y guarda artefactos en models/
	python -m lima_rent.models.train

serve:  ## Levanta la API FastAPI en http://localhost:8000
	uvicorn api.main:app --reload --port 8000

app:  ## Levanta la app Streamlit en http://localhost:8501
	streamlit run app/streamlit_app.py

test:  ## Corre la suite de pytest
	pytest -v

lint:  ## Corre ruff sobre src/, api/, app/ y tests/
	ruff check src api app tests

demo:  ## Levanta API + app juntas con Docker Compose (un solo comando)
	docker compose up --build

clean:  ## Borra artefactos generados (datos, modelos, caches)
	rm -rf data/raw/*.csv data/processed/*.csv models/*.joblib models/*.json
	rm -rf .pytest_cache .ruff_cache **/__pycache__
