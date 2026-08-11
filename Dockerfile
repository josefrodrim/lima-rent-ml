# Imagen de conveniencia para correr la API localmente sin depender de un
# venv (`make demo` / `docker compose up`). El despliegue real es Vercel (ver
# vercel.json) — esta imagen NO es lo que corre en producción.
FROM python:3.11-slim

WORKDIR /app

COPY pyproject.toml .
COPY src ./src
COPY api ./api
COPY models ./models

RUN pip install --no-cache-dir -e ".[serve-local]"

EXPOSE 8000

CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
