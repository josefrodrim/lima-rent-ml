.PHONY: install data train serve app test lint demo clean

install:  ## Instala el paquete Python (todos los extras) y las deps de Next.js
	pip install -e ".[all]"
	npm install

data:  ## Genera y limpia el dataset sintético (data/raw + data/processed)
	python -m lima_rent.data.generate
	python -m lima_rent.data.clean

train:  ## Entrena baseline + LightGBM y guarda artefactos en models/
	python -m lima_rent.models.train

serve:  ## Levanta la API FastAPI en http://localhost:8000
	uvicorn api.main:app --reload --port 8000

app:  ## Levanta el frontend Next.js en http://localhost:3000 (necesita `make serve` corriendo aparte)
	npm run dev

test:  ## Corre la suite de pytest
	pytest -v

lint:  ## Corre ruff sobre src/, api/ y tests/
	ruff check src api tests

demo:  ## Levanta API (Docker) + frontend Next.js juntos, con un solo comando
	docker compose up -d --build; trap 'docker compose down' EXIT; npm run dev

clean:  ## Borra artefactos generados (datos, modelos, caches)
	rm -rf data/raw/*.csv data/processed/*.csv models/*.joblib models/*.json
	rm -rf .pytest_cache .ruff_cache **/__pycache__
