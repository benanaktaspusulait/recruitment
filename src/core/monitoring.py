from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
from azure.monitor.opentelemetry.exporter import AzureMonitorTraceExporter
from fastapi import FastAPI
from sqlalchemy.engine import Engine
from src.core.config import get_settings

settings = get_settings()

def setup_azure_monitoring(app: FastAPI, engine: Engine) -> None:
    """Setup Azure Application Insights monitoring"""
    if not settings.ENVIRONMENT == "production" or not settings.AZURE_INSIGHTS_CONNECTION_STRING:
        return

    # Set up the tracer
    tracer_provider = TracerProvider()
    azure_exporter = AzureMonitorTraceExporter.from_connection_string(
        settings.AZURE_INSIGHTS_CONNECTION_STRING
    )
    span_processor = BatchSpanProcessor(azure_exporter)
    tracer_provider.add_span_processor(span_processor)
    trace.set_tracer_provider(tracer_provider)

    # Instrument FastAPI
    FastAPIInstrumentor.instrument_app(app)

    # Instrument SQLAlchemy
    SQLAlchemyInstrumentor().instrument(
        engine=engine,
        service="recruitment-db",
    ) 