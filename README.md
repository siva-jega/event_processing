# Event Processing Platform

This repository contains a small event processing platform composed of three main services and supporting infrastructure:

1. Ingestion Service — accepts incoming HTTP event requests from clients and publishes them to Kafka.
2. Event Consumer — consumes events from Kafka and persists them into Postgres.
3. Analytics Service — reads events from Postgres and exposes analytics APIs (and the data that Superset dashboards use).

This top-level README explains how the services are connected, how to run the full stack with Docker Compose, how to run components locally, and useful operational tasks (load testing, backing up and deleting test rows, observability and troubleshooting).

## Architecture (high level)

```mermaid
flowchart LR
Client["Clients"]
Ingest["Ingestion Service"]
Prom["Prometheus / OTEL"]
Kafka["Kafka topic: events"]
Consumer["Event Consumer"]
Postgres["Postgres (public.events)"]
Analytics["Analytics Service"]

Client --> Ingest
Ingest -- publishes to --> Kafka
Ingest <--> Prom
Kafka --> Consumer
Consumer -->|writes| Postgres
Analytics -->|reads| Postgres
Analytics <--> Prom
```

## Dashboard snapshot

Below is a sample Superset dashboard screenshot showing event volumes and top event types.

![Event processing dashboard](docs/charts.jpeg)


### Notes

All three services expose health/metrics endpoints where applicable. Check each service README for details and ports.
The platform is designed to run together in the provided Docker Compose setup for local development.

## Key concepts and responsibilities

⁠Ingestion Service
  - Exposes a POST endpoint to accept event payloads from clients.
  - Performs minimal validation/enrichment and publishes messages to Kafka.
  - Exports request and producer metrics, and (optionally) traces via OTEL.

Event Consumer
  - Consumes from the configured Kafka topic and writes normalized rows into Postgres.
  - Handles batching, retrying and writing to a dead-letter queue (if configured) on persistent errors.

Analytics Service
  - Reads persisted events in Postgres, provides aggregate endpoints, and is the recommended backend for dashboards.

This will build the services and start the platform. Watch the logs to ensure dependent services (Postgres, Kafka) are healthy before the services start.

## Quickstart — simple steps

If you just want to bring the stack up and verify dashboards quickly, follow these minimal steps:

1. Start the platform with Docker Compose

```bash
cd docker
docker compose up --build
```

2. Create the analytics database 

```bash
# inside repo root
docker exec -it postgres psql -U postgres -c "CREATE DATABASE events_db;"
```

3. Run Superset migrations and initialization:

```bash
docker exec -it superset superset db upgrade
docker exec -it superset superset fab create-admin \
  --username admin --firstname Superset --lastname Admin \
  --email admin@superset.com --password admin123
docker exec -it superset superset init
```

4. In the Superset UI (http://localhost:8088) add a new database connection pointing at Postgres and the `events_db` database. Example SQLAlchemy URI (replace user/password if different):

```
postgresql://postgres:postgres@postgres:5432/events_db
```

5. Import the Postman collection to exercise the APIs (Postman -> Import -> choose file):

```
postman/Event_Processing_Platform.postman_collection.json
```

6. Send bulk test events using the helper script

```bash
python tools/send_events.py
```

That’s it — after these steps you can create charts in Superset using the connected Postgres datasource and verify the pipeline end-to-end.

### Notes
⁠If you need to rebuild after code changes: ⁠ docker compose up --build --force-recreate <service> ⁠
The Compose file in ⁠ docker/docker-compose.yml ⁠ defines the service names and environment variables. Use those names when connecting services from inside Docker (for example, ⁠ postgres ⁠ is usually the Postgres host inside the Compose network).

## Load testing and sending test events

⁠There is a load test script ⁠ load_test.py ⁠ in the repo root. It can generate a configurable RPS for a duration against the ingestion endpoint.
⁠A helper script ⁠ tools/send_events.py ⁠ was added to send batches of synthetic events (e.g., 300 events across 30 users). Use these scripts from the host while the Docker stack is running.

Example (PowerShell) to send 300 events (the helper script uses ⁠ http://localhost:8004/events ⁠ by default):

⁠ powershell
python .\tools\send_events.py
 ⁠

If you use the load test, start conservatively and increase RPS after verifying the pipeline can handle it.

## Observability

⁠Metrics: Each service exposes ⁠ /metrics ⁠ (Prometheus ⁠ prometheus_client ⁠) where configured. Use the Prometheus job/target to scrape these.
Tracing: The stack can be configured to export traces to an OTEL collector (check ⁠ OTEL_EXPORTER_OTLP_ENDPOINT ⁠ in service configs).
Superset: Superset runs in Docker (if enabled) and can connect to the analytics DB for dashboards; when configuring Superset inside Docker, use the internal ⁠ postgres ⁠ hostname.

## Links to service READMEs

1. ![Ingestion service README](ingestion_service/README.md) ⁠ — details for the ingestion service (run, config, observability).
2. ![Event Consumer README](event_consumer/README.md) ⁠ — details for the consumer (batching, database write patterns, DLQ behavior).
3. ![Analytics Service README](analytics_service/README.md) ⁠ — reference for analytics endpoints and dashboard wiring.

## API endpoints:

1. Ingestion: POST http://localhost:8001/events
2. Analytics: GET http://localhost:8002/analytics/events/count?from_ts=...&to_ts=...

## Schema:
events table: event_id (PK), user_id, event_name, metadata (jsonb), timestamp, processed_at

## Observability and tracing

1. ⁠An OpenTelemetry Collector is included in ⁠ docker/docker-compose.yml ⁠ (service ⁠ otel-collector ⁠).
2. Services send traces to the collector using OTLP (HTTP endpoint at ⁠ http://otel-collector:4318 ⁠).
