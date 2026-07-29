import pytest

from age_mcp_server.telemetry import Telemetry, configure_otel_exporters


class Recorder:
    def __init__(self):
        self.records = []

    def add(self, value, attributes):
        self.records.append((value, attributes))

    def record(self, value, attributes):
        self.records.append((value, attributes))


class Span:
    def __init__(self):
        self.attributes = {}
        self.status = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, traceback):
        return False

    def set_attribute(self, key, value):
        self.attributes[key] = value

    def set_status(self, status):
        self.status = status


class Tracer:
    def __init__(self):
        self.span = Span()
        self.start_attributes = None

    def start_as_current_span(self, _name, *, attributes):
        self.start_attributes = attributes
        return self.span


def test_observation_records_safe_attributes_success_and_failure() -> None:
    telemetry = Telemetry()
    telemetry.tracer = Tracer()
    telemetry.operations = Recorder()
    telemetry.failures = Recorder()
    telemetry.duration = Recorder()
    attributes = {"safe": "value", "number": 3, "secret": object()}

    with telemetry.observe("success", attributes):
        pass

    assert telemetry.tracer.start_attributes == {"safe": "value", "number": 3}
    assert telemetry.operations.records[0][1] == {"safe": "value", "number": 3}
    assert telemetry.duration.records[0][0] >= 0
    assert telemetry.failures.records == []

    with pytest.raises(RuntimeError, match="do not export me"):
        with telemetry.observe("failure", attributes):
            raise RuntimeError("do not export me")

    assert telemetry.failures.records[-1][1]["error.type"] == "RuntimeError"
    assert "do not export me" not in str(telemetry.failures.records)
    assert telemetry.tracer.span.attributes["error.type"] == "RuntimeError"


def test_otlp_exporter_configuration(monkeypatch) -> None:
    import opentelemetry.exporter.otlp.proto.grpc.metric_exporter as metric_exporter
    import opentelemetry.exporter.otlp.proto.grpc.trace_exporter as trace_exporter
    import opentelemetry.sdk.metrics as sdk_metrics
    import opentelemetry.sdk.metrics.export as sdk_metrics_export
    import opentelemetry.sdk.resources as sdk_resources
    import opentelemetry.sdk.trace as sdk_trace
    import opentelemetry.sdk.trace.export as sdk_trace_export

    created = {}

    class FakeResource:
        @staticmethod
        def create(attributes):
            created["resource"] = attributes
            return attributes

    class FakeTracerProvider:
        def __init__(self, *, resource):
            created["tracer_resource"] = resource

        def add_span_processor(self, processor):
            created["processor"] = processor

    monkeypatch.setattr(metric_exporter, "OTLPMetricExporter", lambda: "metric-exporter")
    monkeypatch.setattr(trace_exporter, "OTLPSpanExporter", lambda: "span-exporter")
    monkeypatch.setattr(
        sdk_metrics_export,
        "PeriodicExportingMetricReader",
        lambda exporter: ("reader", exporter),
    )
    monkeypatch.setattr(sdk_resources, "Resource", FakeResource)
    monkeypatch.setattr(sdk_trace, "TracerProvider", FakeTracerProvider)
    monkeypatch.setattr(
        sdk_trace_export,
        "BatchSpanProcessor",
        lambda exporter: ("processor", exporter),
    )
    monkeypatch.setattr(
        sdk_metrics,
        "MeterProvider",
        lambda **kwargs: ("meter-provider", kwargs),
    )
    monkeypatch.setattr(
        "age_mcp_server.telemetry.trace.set_tracer_provider",
        lambda provider: created.update(tracer_provider=provider),
    )
    monkeypatch.setattr(
        "age_mcp_server.telemetry.metrics.set_meter_provider",
        lambda provider: created.update(meter_provider=provider),
    )

    configure_otel_exporters("test-service")

    assert created["resource"] == {"service.name": "test-service"}
    assert created["processor"] == ("processor", "span-exporter")
    assert created["meter_provider"][0] == "meter-provider"
