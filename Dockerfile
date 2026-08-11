FROM python:3.11-slim

WORKDIR /app

COPY pyproject.toml .
COPY src ./src
COPY api ./api
COPY app ./app
COPY models ./models
COPY data ./data

RUN pip install --no-cache-dir -e .

EXPOSE 8000 8501

CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
