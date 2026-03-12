FROM python:3.11-slim
WORKDIR /app
COPY analytics_service/pyproject.toml ./pyproject.toml
RUN pip install --no-cache-dir -e .
COPY analytics_service ./analytics_service
WORKDIR /app/analytics_service
EXPOSE 8002
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8002"]
