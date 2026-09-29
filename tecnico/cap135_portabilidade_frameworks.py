"""Código do Capítulo 135 — Implementando uma camada de portabilidade entre frameworks.

Extraído da versão técnica v26 do livro "Agentes de Inteligência Artificial".
Mantenha este arquivo idêntico à listagem publicada no manuscrito.
"""
from __future__ import annotations

# BEGIN FRAMEWORK_PORTABILITY_EXAMPLE

from dataclasses import dataclass, field
from enum import Enum
from typing import Callable, Protocol
import uuid


class Capability(str, Enum):
    TOOLS = "tools"
    STRUCTURED_OUTPUT = "structured_output"
    HANDOFF = "handoff"
    CHECKPOINT = "checkpoint"
    HITL = "human_in_the_loop"
    TRACING = "tracing"


class UnsupportedCapability(RuntimeError):
    pass


class ToolNotAuthorized(PermissionError):
    pass


class AdapterFailure(RuntimeError):
    pass


@dataclass(frozen=True)
class ToolSpec:
    name: str
    description: str


@dataclass(frozen=True)
class PortableAgentSpec:
    name: str
    instructions: str
    tools: tuple[ToolSpec, ...] = ()
    required_capabilities: frozenset[Capability] = frozenset()


@dataclass(frozen=True)
class RunRequest:
    tenant_id: str
    user_input: str
    correlation_id: str = field(default_factory=lambda: uuid.uuid4().hex)


@dataclass(frozen=True)
class RunEvent:
    kind: str
    correlation_id: str
    attributes: dict[str, object] = field(default_factory=dict)
    extensions: dict[str, object] = field(default_factory=dict)


@dataclass(frozen=True)
class RunResult:
    output: str
    adapter: str
    correlation_id: str
    events: tuple[RunEvent, ...]


@dataclass(frozen=True)
class FrameworkManifest:
    name: str
    capabilities: frozenset[Capability]


class FrameworkAdapter(Protocol):
    @property
    def manifest(self) -> FrameworkManifest:
        ...

    def run(
        self,
        spec: PortableAgentSpec,
        request: RunRequest,
        invoke_tool: Callable[[str, str], str],
    ) -> RunResult:
        ...


ToolExecutor = Callable[[str], str]
ToolAuthorizer = Callable[[str], bool]


@dataclass
class RegisteredTool:
    spec: ToolSpec
    execute: ToolExecutor
    authorize: ToolAuthorizer


class ToolRegistry:
    def __init__(self) -> None:
        self._tools: dict[str, RegisteredTool] = {}

    def register(
        self,
        spec: ToolSpec,
        execute: ToolExecutor,
        authorize: ToolAuthorizer,
    ) -> None:
        if spec.name in self._tools:
            raise ValueError(f"duplicate tool: {spec.name}")
        self._tools[spec.name] = RegisteredTool(spec, execute, authorize)

    def invoke(self, tenant_id: str, tool_name: str, argument: str) -> str:
        tool = self._tools[tool_name]
        if not tool.authorize(tenant_id):
            raise ToolNotAuthorized(f"{tenant_id} cannot call {tool_name}")
        return tool.execute(argument)


class ApplicationKernel:
    def __init__(self, adapter: FrameworkAdapter, tools: ToolRegistry) -> None:
        self.adapter = adapter
        self.tools = tools

    def run(self, spec: PortableAgentSpec, request: RunRequest) -> RunResult:
        missing = spec.required_capabilities - self.adapter.manifest.capabilities
        if missing:
            names = ", ".join(sorted(x.value for x in missing))
            raise UnsupportedCapability(
                f"adapter {self.adapter.manifest.name} lacks: {names}"
            )

        declared = {tool.name for tool in spec.tools}

        def invoke_tool(name: str, argument: str) -> str:
            if name not in declared:
                raise KeyError(f"agent did not declare tool: {name}")
            return self.tools.invoke(request.tenant_id, name, argument)

        try:
            result = self.adapter.run(spec, request, invoke_tool)
        except (ToolNotAuthorized, KeyError):
            raise
        except Exception as exc:
            raise AdapterFailure(str(exc)) from exc

        if result.correlation_id != request.correlation_id:
            raise AdapterFailure("adapter changed correlation_id")
        return result


class LoopStyleAdapter:
    """Deterministic stand-in for a code-first agent-loop SDK."""

    manifest = FrameworkManifest(
        name="loop-style",
        capabilities=frozenset(
            {
                Capability.TOOLS,
                Capability.STRUCTURED_OUTPUT,
                Capability.HANDOFF,
                Capability.TRACING,
            }
        ),
    )

    def run(
        self,
        spec: PortableAgentSpec,
        request: RunRequest,
        invoke_tool: Callable[[str, str], str],
    ) -> RunResult:
        events = [
            RunEvent(
                "model_call",
                request.correlation_id,
                {"agent": spec.name},
                {"loop.trace_id": "trace-loop-1"},
            )
        ]
        if spec.tools:
            tool = spec.tools[0]
            events.append(
                RunEvent(
                    "tool_call",
                    request.correlation_id,
                    {"tool": tool.name},
                )
            )
            value = invoke_tool(tool.name, request.user_input)
            output = f"{spec.name}: {value}"
        else:
            output = f"{spec.name}: {request.user_input}"
        events.append(RunEvent("completed", request.correlation_id))
        return RunResult(
            output=output,
            adapter=self.manifest.name,
            correlation_id=request.correlation_id,
            events=tuple(events),
        )


class GraphStyleAdapter:
    """Deterministic stand-in for a graph/stateful framework."""

    manifest = FrameworkManifest(
        name="graph-style",
        capabilities=frozenset(
            {
                Capability.TOOLS,
                Capability.CHECKPOINT,
                Capability.HITL,
                Capability.TRACING,
            }
        ),
    )

    def run(
        self,
        spec: PortableAgentSpec,
        request: RunRequest,
        invoke_tool: Callable[[str, str], str],
    ) -> RunResult:
        events = [
            RunEvent(
                "checkpoint",
                request.correlation_id,
                {"node": "start"},
                {"graph.checkpoint": "cp-1"},
            )
        ]
        if spec.tools:
            tool = spec.tools[0]
            value = invoke_tool(tool.name, request.user_input)
            events.append(
                RunEvent(
                    "tool_call",
                    request.correlation_id,
                    {"tool": tool.name, "node": "tool"},
                )
            )
            output = f"{spec.name}: {value}"
        else:
            output = f"{spec.name}: {request.user_input}"
        events.append(RunEvent("completed", request.correlation_id))
        return RunResult(
            output=output,
            adapter=self.manifest.name,
            correlation_id=request.correlation_id,
            events=tuple(events),
        )


class BrokenCorrelationAdapter(LoopStyleAdapter):
    def run(self, spec, request, invoke_tool):
        result = super().run(spec, request, invoke_tool)
        return RunResult(
            result.output,
            result.adapter,
            "wrong-correlation",
            result.events,
        )


class ExplodingAdapter(LoopStyleAdapter):
    def run(self, spec, request, invoke_tool):
        raise RuntimeError("provider unavailable")


def build_registry() -> ToolRegistry:
    registry = ToolRegistry()
    registry.register(
        ToolSpec("echo", "Return a normalized value."),
        execute=lambda value: value.strip().upper(),
        authorize=lambda tenant: tenant != "blocked",
    )
    return registry


def portable_spec(*required: Capability) -> PortableAgentSpec:
    return PortableAgentSpec(
        name="portable-agent",
        instructions="Use the declared tool and return its result.",
        tools=(ToolSpec("echo", "Return a normalized value."),),
        required_capabilities=frozenset({Capability.TOOLS, *required}),
    )


def test_loop_adapter_executes_declared_tool() -> None:
    kernel = ApplicationKernel(LoopStyleAdapter(), build_registry())
    result = kernel.run(portable_spec(), RunRequest("tenant-a", "  hello "))
    assert result.output == "portable-agent: HELLO"
    assert [e.kind for e in result.events] == ["model_call", "tool_call", "completed"]


def test_graph_adapter_preserves_application_contract() -> None:
    kernel = ApplicationKernel(GraphStyleAdapter(), build_registry())
    result = kernel.run(portable_spec(), RunRequest("tenant-a", "hello"))
    assert result.output == "portable-agent: HELLO"
    assert result.adapter == "graph-style"


def test_missing_capability_fails_closed() -> None:
    kernel = ApplicationKernel(LoopStyleAdapter(), build_registry())
    try:
        kernel.run(portable_spec(Capability.CHECKPOINT), RunRequest("tenant-a", "x"))
        raise AssertionError("unsupported capability should fail")
    except UnsupportedCapability:
        pass


def test_human_in_loop_requirement_selects_semantics_not_name() -> None:
    graph = ApplicationKernel(GraphStyleAdapter(), build_registry())
    result = graph.run(portable_spec(Capability.HITL), RunRequest("tenant-a", "x"))
    assert result.events[0].kind == "checkpoint"


def test_tool_authorization_is_owned_by_application() -> None:
    kernel = ApplicationKernel(LoopStyleAdapter(), build_registry())
    try:
        kernel.run(portable_spec(), RunRequest("blocked", "secret"))
        raise AssertionError("blocked tenant should not execute tool")
    except ToolNotAuthorized:
        pass


def test_adapter_cannot_call_undeclared_tool() -> None:
    class RogueAdapter(LoopStyleAdapter):
        def run(self, spec, request, invoke_tool):
            invoke_tool("admin_delete", "all")
            raise AssertionError("unreachable")

    kernel = ApplicationKernel(RogueAdapter(), build_registry())
    try:
        kernel.run(portable_spec(), RunRequest("tenant-a", "x"))
        raise AssertionError("undeclared tool should fail")
    except KeyError:
        pass


def test_correlation_id_is_preserved() -> None:
    request = RunRequest("tenant-a", "hello", correlation_id="corr-123")
    kernel = ApplicationKernel(LoopStyleAdapter(), build_registry())
    result = kernel.run(portable_spec(), request)
    assert result.correlation_id == "corr-123"
    assert all(e.correlation_id == "corr-123" for e in result.events)


def test_broken_correlation_is_rejected() -> None:
    kernel = ApplicationKernel(BrokenCorrelationAdapter(), build_registry())
    try:
        kernel.run(portable_spec(), RunRequest("tenant-a", "x"))
        raise AssertionError("correlation mutation should fail")
    except AdapterFailure as exc:
        assert "correlation_id" in str(exc)


def test_vendor_extensions_remain_namespaced() -> None:
    loop = ApplicationKernel(LoopStyleAdapter(), build_registry())
    graph = ApplicationKernel(GraphStyleAdapter(), build_registry())
    loop_result = loop.run(portable_spec(), RunRequest("tenant-a", "x"))
    graph_result = graph.run(portable_spec(), RunRequest("tenant-a", "x"))
    assert "loop.trace_id" in loop_result.events[0].extensions
    assert "graph.checkpoint" in graph_result.events[0].extensions


def test_provider_failure_is_normalized() -> None:
    kernel = ApplicationKernel(ExplodingAdapter(), build_registry())
    try:
        kernel.run(portable_spec(), RunRequest("tenant-a", "x"))
        raise AssertionError("adapter failure should be normalized")
    except AdapterFailure as exc:
        assert "provider unavailable" in str(exc)


def test_duplicate_tool_registration_is_rejected() -> None:
    registry = build_registry()
    try:
        registry.register(
            ToolSpec("echo", "duplicate"),
            execute=lambda value: value,
            authorize=lambda tenant: True,
        )
        raise AssertionError("duplicate tool should fail")
    except ValueError as exc:
        assert "duplicate tool" in str(exc)


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
# END FRAMEWORK_PORTABILITY_EXAMPLE
