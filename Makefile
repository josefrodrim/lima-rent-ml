.PHONY: install data train serve app test lint demo clean

install:  ## Instala el paquete en modo editable con todos los extras de desarrollo
	pip install -e ".[all]"

data:  ## Genera y limpia el dataset sintético (data/raw + data/processed)
	python -m lima_rent.data.generate
	python -m lima_rent.data.clean

train:  ## Entrena baseline + LightGBM y guarda artefactos en models/
	python -m lima_rent.models.train

serve:  ## Levanta la API FastAPI en http://localhost:8000
	uvicorn api.main:app --reload --port 8000

app:  ## Levanta el frontend Next.js en http://localhost:3000 (Fase E)
	cd app && npm run dev

test:  ## Corre la suite de pytest
	pytest -v

lint:  ## Corre ruff sobre src/, api/ y tests/
	ruff check src api tests

demo:  ## Levanta la API con Docker Compose (el frontend se corre aparte con `make app`)
	docker compose up --build

clean:  ## Borra artefactos generados (datos, modelos, caches)
	rm -rf data/raw/*.csv data/processed/*.csv models/*.joblib models/*.json
	rm -rf .pytest_cache .ruff_cache **/__pycache__
