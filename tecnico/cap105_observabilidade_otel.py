"""Código do Capítulo 105 — Implementando observabilidade com OpenTelemetry sem framework agêntico.

Extraído da versão técnica v26 do livro "Agentes de Inteligência Artificial".
Mantenha este arquivo idêntico à listagem publicada no manuscrito.
"""
from __future__ import annotations

# BEGIN FILE agent_observability_part12.py

from contextlib import contextmanager
from dataclasses import dataclass
from hashlib import sha256
import json
from time import perf_counter
from typing import Any, Callable, Iterator
from uuid import uuid4

from opentelemetry.context import attach, detach
from opentelemetry.propagate import extract, inject
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import InMemoryMetricReader
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter
from opentelemetry.trace import Status, StatusCode


@dataclass(frozen=True)
class ObservabilityConfig:
    service_name: str = "book-agent"
    capture_content: bool = False


def subject_hash(subject_id: str) -> str:
    return sha256(subject_id.encode("utf-8")).hexdigest()[:16]


class AgentTelemetry:
    """Minimal agent observability layer using OpenTelemetry directly."""

    def __init__(self, config: ObservabilityConfig = ObservabilityConfig()):
        self.config = config
        resource = Resource.create({"service.name": config.service_name})

        self.span_exporter = InMemorySpanExporter()
        self.tracer_provider = TracerProvider(resource=resource)
        self.tracer_provider.add_span_processor(
            SimpleSpanProcessor(self.span_exporter)
        )
        self.tracer = self.tracer_provider.get_tracer("book.agent")

        self.metric_reader = InMemoryMetricReader()
        self.meter_provider = MeterProvider(
            resource=resource,
            metric_readers=[self.metric_reader],
        )
        self.meter = self.meter_provider.get_meter("book.agent")

        self.run_count = self.meter.create_counter(
            "agent.run.count", unit="{run}"
        )
        self.model_duration = self.meter.create_histogram(
            "gen_ai.client.operation.duration", unit="s"
        )
        self.token_usage = self.meter.create_histogram(
            "gen_ai.client.token.usage", unit="{token}"
        )
        self.tool_duration = self.meter.create_histogram(
            "agent.tool.duration", unit="s"
        )

    @contextmanager
    def agent_run(
        self,
        agent_name: str,
        run_id: str,
        subject_id: str | None = None,
    ) -> Iterator[None]:
        attributes: dict[str, Any] = {
            "gen_ai.operation.name": "invoke_agent",
            "gen_ai.agent.name": agent_name,
            "app.run.id": run_id,
        }
        if subject_id:
            attributes["app.subject.hash"] = subject_hash(subject_id)

        with self.tracer.start_as_current_span(
            f"invoke_agent {agent_name}", attributes=attributes
        ) as span:
            self.run_count.add(1, {"gen_ai.agent.name": agent_name})
            try:
                yield
            except Exception as exc:
                self._record_error(span, exc)
                raise

    def model_call(
        self,
        *,
        provider: str,
        model: str,
        prompt: str,
        fn: Callable[[str], dict[str, Any]],
    ) -> dict[str, Any]:
        attributes = {
            "gen_ai.operation.name": "chat",
            "gen_ai.provider.name": provider,
            "gen_ai.request.model": model,
        }
        started = perf_counter()
        input_tokens: int | None = None
        output_tokens: int | None = None

        with self.tracer.start_as_current_span(
            f"chat {model}", attributes=attributes
        ) as span:
            if self.config.capture_content:
                span.set_attribute(
                    "gen_ai.input.messages",
                    json.dumps([{"role": "user", "content": prompt}]),
                )
            try:
                result = fn(prompt)
                input_tokens = int(result.get("input_tokens", 0))
                output_tokens = int(result.get("output_tokens", 0))
                span.set_attribute("gen_ai.usage.input_tokens", input_tokens)
                span.set_attribute("gen_ai.usage.output_tokens", output_tokens)
                span.set_attribute(
                    "gen_ai.response.finish_reasons",
                    [str(result.get("finish_reason", "stop"))],
                )
                if self.config.capture_content:
                    span.set_attribute(
                        "gen_ai.output.messages",
                        json.dumps(
                            [
                                {
                                    "role": "assistant",
                                    "content": str(result.get("text", "")),
                                }
                            ]
                        ),
                    )
                return result
            except Exception as exc:
                self._record_error(span, exc)
                raise
            finally:
                metric_attributes = {
                    "gen_ai.operation.name": "chat",
                    "gen_ai.provider.name": provider,
                    "gen_ai.request.model": model,
                }
                self.model_duration.record(
                    perf_counter() - started, metric_attributes
                )
                if input_tokens is not None:
                    self.token_usage.record(
                        input_tokens,
                        {**metric_attributes, "gen_ai.token.type": "input"},
                    )
                    self.token_usage.record(
                        output_tokens or 0,
                        {**metric_attributes, "gen_ai.token.type": "output"},
                    )

    def tool_call(
        self,
        *,
        tool_name: str,
        arguments: dict[str, Any],
        fn: Callable[..., Any],
    ) -> Any:
        call_id = f"call_{uuid4().hex[:12]}"
        attributes = {
            "gen_ai.operation.name": "execute_tool",
            "gen_ai.tool.name": tool_name,
            "gen_ai.tool.type": "function",
            "gen_ai.tool.call.id": call_id,
        }
        started = perf_counter()

        with self.tracer.start_as_current_span(
            f"execute_tool {tool_name}", attributes=attributes
        ) as span:
            if self.config.capture_content:
                span.set_attribute(
                    "gen_ai.tool.call.arguments",
                    json.dumps(arguments, sort_keys=True, default=str),
                )
            try:
                result = fn(**arguments)
                if self.config.capture_content:
                    span.set_attribute(
                        "gen_ai.tool.call.result",
                        json.dumps(result, sort_keys=True, default=str),
                    )
                return result
            except Exception as exc:
                self._record_error(span, exc)
                raise
            finally:
                self.tool_duration.record(
                    perf_counter() - started,
                    {"gen_ai.tool.name": tool_name},
                )

    def inject_context(self, carrier: dict[str, str]) -> dict[str, str]:
        inject(carrier)
        return carrier

    @contextmanager
    def extracted_context(
        self, carrier: dict[str, str]
    ) -> Iterator[None]:
        token = attach(extract(carrier))
        try:
            yield
        finally:
            detach(token)

    def finished_spans(self):
        return self.span_exporter.get_finished_spans()

    def metric_points(self, metric_name: str):
        data = self.metric_reader.get_metrics_data()
        points = []
        for resource_metrics in data.resource_metrics:
            for scope_metrics in resource_metrics.scope_metrics:
                for metric in scope_metrics.metrics:
                    if metric.name == metric_name:
                        points.extend(metric.data.data_points)
        return points

    @staticmethod
    def _record_error(span, exc: Exception) -> None:
        span.set_attribute("error.type", type(exc).__name__)
        span.record_exception(exc)
        span.set_status(Status(StatusCode.ERROR))


# --- Deterministic fake dependencies used by the demo and tests ---

def fake_model(prompt: str) -> dict[str, Any]:
    return {
        "text": "Check the service status.",
        "input_tokens": len(prompt.split()) + 8,
        "output_tokens": 5,
        "finish_reason": "stop",
    }


def get_service_status(service: str) -> dict[str, str]:
    return {"service": service, "status": "ok"}


def failing_tool(service: str) -> dict[str, str]:
    raise TimeoutError(f"timeout while checking {service}")


def run_demo(telemetry: AgentTelemetry) -> dict[str, str]:
    carrier: dict[str, str] = {}
    with telemetry.agent_run(
        "ops-agent", "run-001", subject_id="user@example.com"
    ):
        telemetry.model_call(
            provider="openai",
            model="gpt-example",
            prompt="Check the API service",
            fn=fake_model,
        )
        telemetry.tool_call(
            tool_name="get_service_status",
            arguments={"service": "api"},
            fn=get_service_status,
        )
        telemetry.inject_context(carrier)
    return carrier


# --- Tests ---

def test_trace_hierarchy():
    telemetry = AgentTelemetry()
    run_demo(telemetry)
    spans = {span.name: span for span in telemetry.finished_spans()}
    root = spans["invoke_agent ops-agent"]
    model = spans["chat gpt-example"]
    tool = spans["execute_tool get_service_status"]
    assert model.parent.span_id == root.context.span_id
    assert tool.parent.span_id == root.context.span_id
    assert model.context.trace_id == root.context.trace_id == tool.context.trace_id


def test_genai_attributes_are_recorded():
    telemetry = AgentTelemetry()
    run_demo(telemetry)
    spans = {span.name: span for span in telemetry.finished_spans()}
    assert spans["invoke_agent ops-agent"].attributes["gen_ai.operation.name"] == "invoke_agent"
    assert spans["chat gpt-example"].attributes["gen_ai.provider.name"] == "openai"
    assert spans["execute_tool get_service_status"].attributes["gen_ai.tool.name"] == "get_service_status"


def test_content_is_not_captured_by_default():
    telemetry = AgentTelemetry()
    run_demo(telemetry)
    model = next(s for s in telemetry.finished_spans() if s.name.startswith("chat "))
    tool = next(s for s in telemetry.finished_spans() if s.name.startswith("execute_tool "))
    assert "gen_ai.input.messages" not in model.attributes
    assert "gen_ai.output.messages" not in model.attributes
    assert "gen_ai.tool.call.arguments" not in tool.attributes
    assert "gen_ai.tool.call.result" not in tool.attributes


def test_content_capture_is_explicit_opt_in():
    telemetry = AgentTelemetry(ObservabilityConfig(capture_content=True))
    run_demo(telemetry)
    model = next(s for s in telemetry.finished_spans() if s.name.startswith("chat "))
    tool = next(s for s in telemetry.finished_spans() if s.name.startswith("execute_tool "))
    assert "gen_ai.input.messages" in model.attributes
    assert "gen_ai.output.messages" in model.attributes
    assert "gen_ai.tool.call.arguments" in tool.attributes
    assert "gen_ai.tool.call.result" in tool.attributes


def test_subject_is_hashed_not_stored_raw():
    telemetry = AgentTelemetry()
    run_demo(telemetry)
    root = next(s for s in telemetry.finished_spans() if s.name.startswith("invoke_agent "))
    assert root.attributes["app.subject.hash"] == subject_hash("user@example.com")
    assert "user@example.com" not in repr(root.attributes)


def test_tool_failure_is_visible():
    telemetry = AgentTelemetry()
    try:
        with telemetry.agent_run("ops-agent", "run-err"):
            telemetry.tool_call(
                tool_name="get_service_status",
                arguments={"service": "api"},
                fn=failing_tool,
            )
    except TimeoutError:
        pass
    else:
        raise AssertionError("TimeoutError expected")

    tool = next(s for s in telemetry.finished_spans() if s.name.startswith("execute_tool "))
    assert tool.status.status_code == StatusCode.ERROR
    assert tool.attributes["error.type"] == "TimeoutError"


def test_w3c_trace_context_is_injected():
    telemetry = AgentTelemetry()
    carrier = run_demo(telemetry)
    assert "traceparent" in carrier
    assert carrier["traceparent"].startswith("00-")
    assert len(carrier["traceparent"].split("-")) == 4


def test_extracted_context_keeps_remote_trace():
    producer = AgentTelemetry()
    carrier: dict[str, str] = {}
    with producer.agent_run("producer", "run-a"):
        producer.inject_context(carrier)
    producer_root = next(
        s for s in producer.finished_spans() if s.name == "invoke_agent producer"
    )

    consumer = AgentTelemetry()
    with consumer.extracted_context(carrier):
        with consumer.agent_run("consumer", "run-b"):
            pass
    consumer_root = next(
        s for s in consumer.finished_spans() if s.name == "invoke_agent consumer"
    )
    assert consumer_root.context.trace_id == producer_root.context.trace_id
    assert consumer_root.parent.span_id == producer_root.context.span_id


def test_token_metrics_keep_input_and_output_separate():
    telemetry = AgentTelemetry()
    run_demo(telemetry)
    points = telemetry.metric_points("gen_ai.client.token.usage")
    by_type = {p.attributes["gen_ai.token.type"]: p.sum for p in points}
    assert by_type["input"] == 12
    assert by_type["output"] == 5


def test_operational_metrics_exist():
    telemetry = AgentTelemetry()
    run_demo(telemetry)
    assert len(telemetry.metric_points("agent.run.count")) == 1
    assert len(telemetry.metric_points("gen_ai.client.operation.duration")) == 1
    assert len(telemetry.metric_points("agent.tool.duration")) == 1


def run_tests() -> None:
    tests = [
        value
        for name, value in sorted(globals().items())
        if name.startswith("test_") and callable(value)
    ]
    for test in tests:
        test()
        print("PASS", test.__name__)
    print(f"{len(tests)} tests passed")


if __name__ == "__main__":
    run_tests()
# END FILE agent_observability_part12.py
