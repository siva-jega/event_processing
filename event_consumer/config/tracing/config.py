from opentelemetry import trace
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter


def init_tracer(settings, service_name: str = "event-consumer"):
    """Initialize OTEL tracer provider and return a tracer instance.
    
    Args:
        settings: Settings object with OTEL_EXPORTER_OTLP_ENDPOINT
        service_name: Service name for the tracer resource
        
    Returns:
        A configured tracer instance
    """
    resource = Resource.create({"service.name": service_name})
    provider = TracerProvider(resource=resource)
    otlp_exporter = OTLPSpanExporter(endpoint=settings.OTEL_EXPORTER_OTLP_ENDPOINT)
    provider.add_span_processor(BatchSpanProcessor(otlp_exporter))
    trace.set_tracer_provider(provider)
    return trace.get_tracer(__name__)
