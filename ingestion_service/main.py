from fastapi import FastAPI
import logging
from prometheus_client import start_http_server

# OpenTelemetry
from opentelemetry import trace
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor

from config.config import get_settings, init_kafka_producer
from contextlib import asynccontextmanager
from routes import events_router, metrics_router
from services import kafka_service

settings = get_settings()

@asynccontextmanager
async def lifespan(app):
    try:
        resource = Resource.create({"service.name": settings.SERVICE_NAME})
        provider = TracerProvider(resource=resource)
        otlp_exporter = OTLPSpanExporter(endpoint=settings.OTEL_EXPORTER_OTLP_ENDPOINT)
        provider.add_span_processor(BatchSpanProcessor(otlp_exporter))
        trace.set_tracer_provider(provider)
        FastAPIInstrumentor.instrument_app(app)
    except Exception as e:
        print(f"Failed to setup OTEL: {e}")

    producer = None
    try:
        producer = await init_kafka_producer(settings, kafka_service)
    except Exception as e:
        print(f"Failed to initialize Kafka producer: {e}")
    
    yield
    if producer:
        await producer.stop()

app = FastAPI(title="ingestion-service", lifespan=lifespan)

# Include routers
app.include_router(events_router)
app.include_router(metrics_router)
