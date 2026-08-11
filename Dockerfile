# Imagen de conveniencia para correr la API localmente sin depender de un
# venv (`make demo` / `docker compose up`). El despliegue real es Vercel (ver
# vercel.json) — esta imagen NO es lo que corre en producción.
FROM python:3.11-slim

# LightGBM carga una librería nativa que depende de OpenMP; la imagen slim no
# la trae y falla en el import con "libgomp.so.1: cannot open shared object".
RUN apt-get update && apt-get install -y --no-install-recommends libgomp1 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY pyproject.toml .
COPY src ./src
COPY api ./api
COPY models ./models

RUN pip install --no-cache-dir -e ".[serve-local]"

EXPOSE 8000

CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
