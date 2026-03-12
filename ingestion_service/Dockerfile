FROM python:3.11-slim
WORKDIR /app
# Copy pyproject.toml from repo context (build context is repo root)
COPY ingestion_service/pyproject.toml ./pyproject.toml
RUN pip install --no-cache-dir -e .
# Copy only the ingestion_service code
COPY ingestion_service ./ingestion_service
WORKDIR /app/ingestion_service
EXPOSE 8001
CMD ["sh", "-c", "python /workspace/docker/wait_for_services.py --services kafka:9092 --timeout 120 && uvicorn main:app --host 0.0.0.0 --port 8001"]
