"""Analytics service main application."""

from contextlib import asynccontextmanager
from fastapi import FastAPI

# OpenTelemetry
from opentelemetry import trace
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from prometheus_client import start_http_server

from config.config import get_settings
from config.database import init_pool, close_pool
from routes import analytics_router, metrics_router
from services import init_redis, close_redis

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan using async context manager.

    Performs startup actions (metrics, OpenTelemetry, Redis init) before the
    `yield`, and shutdown actions (Redis close) after.
    """
    # Startup actions
    # Start metrics server
    start_http_server(settings.METRICS_PORT)

    # Setup OpenTelemetry
    resource = Resource.create({"service.name": settings.SERVICE_NAME})
    provider = TracerProvider(resource=resource)
    otlp_exporter = OTLPSpanExporter(endpoint=settings.OTEL_EXPORTER_OTLP_ENDPOINT)
    provider.add_span_processor(BatchSpanProcessor(otlp_exporter))
    trace.set_tracer_provider(provider)
    FastAPIInstrumentor.instrument_app(app)

    # Init DB pool
    init_pool()

    # Initialize Redis connection
    await init_redis(settings.REDIS_URL)

    try:
        yield
    finally:
        # Shutdown actions
        await close_redis()
        # Close DB pool
        close_pool()


app = FastAPI(title=settings.SERVICE_NAME, lifespan=lifespan)


# Include routers
app.include_router(analytics_router, prefix="/analytics")
app.include_router(metrics_router)
