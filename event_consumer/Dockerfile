FROM python:3.11-slim
WORKDIR /app
COPY event_consumer/pyproject.toml ./pyproject.toml
RUN pip install --no-cache-dir -e .
COPY event_consumer ./event_consumer
WORKDIR /app/event_consumer
CMD ["python", "main.py"]