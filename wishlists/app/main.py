from fastapi import FastAPI
from app.endpoints.wishlist_router import wishlist_router
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from prometheus_fastapi_instrumentator import Instrumentator

app = FastAPI(title="Wishlists Service")

app.include_router(wishlist_router, prefix="/api")

# Настройка ресурса
resource = Resource(attributes={
    "service.name": "wishlists-service"
})

# Настройка OTLP-экспортера для отправки трассировок в Jaeger
otlp_exporter = OTLPSpanExporter(
    endpoint="http://jaeger:4317",
    insecure=True,  # Отключение проверки сертификатов
)

provider = TracerProvider(resource=resource)
processor = BatchSpanProcessor(otlp_exporter)
provider.add_span_processor(processor)
trace.set_tracer_provider(provider)

# Инструментирование FastAPI для OpenTelemetry
FastAPIInstrumentor.instrument_app(app)

# Инструментирование FastAPI для Prometheus
Instrumentator().instrument(app).expose(app)
