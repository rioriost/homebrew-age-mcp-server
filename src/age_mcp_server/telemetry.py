import logging
from collections.abc import Iterator
from contextlib import contextmanager
from time import monotonic
from typing import Any

from opentelemetry import metrics, trace
from opentelemetry.trace import Status, StatusCode

log = logging.getLogger(__name__)


class Telemetry:
    """Privacy-preserving traces and metrics for tools and database operations."""

    def __init__(self, instrumentation_name: str = "age_mcp_server"):
        self.tracer = trace.get_tracer(instrumentation_name)
        meter = metrics.get_meter(instrumentation_name)
        self.duration = meter.create_histogram(
            "age_mcp_server.operation.duration",
            unit="s",
            description="Duration of MCP and database operations",
        )
        self.operations = meter.create_counter(
            "age_mcp_server.operation.count",
            description="Count of MCP and database operations",
        )
        self.failures = meter.create_counter(
            "age_mcp_server.operation.failures",
            description="Count of failed MCP and database operations",
        )

    @contextmanager
    def observe(self, span_name: str, attributes: dict[str, Any]) -> Iterator[None]:
        safe_attributes = {
            key: value
            for key, value in attributes.items()
            if isinstance(value, (bool, int, float, str))
        }
        started = monotonic()
        with self.tracer.start_as_current_span(span_name, attributes=safe_attributes) as span:
            try:
                yield
            except Exception as exc:
                error_attributes = {**safe_attributes, "error.type": type(exc).__name__}
                self.failures.add(1, error_attributes)
                span.set_attribute("error.type", type(exc).__name__)
                span.set_status(Status(StatusCode.ERROR, type(exc).__name__))
                raise
            finally:
                self.operations.add(1, safe_attributes)
                self.duration.record(monotonic() - started, safe_attributes)


def configure_otel_exporters(
    service_name: str = "age-mcp-server",
) -> None:
    """Configure OTLP tracing and metrics using standard OTEL environment variables."""
    try:
        from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import (
            OTLPMetricExporter,
        )
        from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import (
            OTLPSpanExporter,
        )
        from opentelemetry.sdk.metrics import MeterProvider
        from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
        from opentelemetry.sdk.resources import Resource
        from opentelemetry.sdk.trace import TracerProvider
        from opentelemetry.sdk.trace.export import BatchSpanProcessor
    except ImportError as exc:
        raise RuntimeError("Telemetry exporters require 'age_mcp_server[telemetry]'") from exc

    resource = Resource.create({"service.name": service_name})
    tracer_provider = TracerProvider(resource=resource)
    tracer_provider.add_span_processor(BatchSpanProcessor(OTLPSpanExporter()))
    trace.set_tracer_provider(tracer_provider)

    metric_reader = PeriodicExportingMetricReader(OTLPMetricExporter())
    metrics.set_meter_provider(MeterProvider(resource=resource, metric_readers=[metric_reader]))
    log.info("OpenTelemetry OTLP exporters enabled")
