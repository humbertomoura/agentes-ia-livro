"""Código do Capítulo 144 — Projeto final — Um serviço agêntico production-grade.

Extraído da versão técnica v26 do livro "Agentes de Inteligência Artificial".
Mantenha este arquivo idêntico à listagem publicada no manuscrito.
"""
from __future__ import annotations

# BEGIN PROJECT144_PRODUCTION_CORE
from dataclasses import dataclass, field
from enum import Enum
from typing import Callable
import uuid

class RunStatus(str, Enum):
    RUNNING = "RUNNING"
    PAUSED = "PAUSED"
    SUCCESS = "SUCCESS"
    FAILURE = "FAILURE"
    LIMIT_REACHED = "LIMIT_REACHED"

class AuthorizationError(RuntimeError): pass
class TransientError(RuntimeError): pass
class InvalidTransition(RuntimeError): pass

@dataclass(frozen=True)
class Document:
    doc_id: str
    tenant_id: str
    allowed_principals: frozenset[str]
    text: str

@dataclass(frozen=True)
class Action:
    kind: str
    name: str = ""
    argument: str = ""
    output: str = ""

@dataclass
class Run:
    run_id: str
    tenant_id: str
    principal_id: str
    goal: str
    correlation_id: str
    status: RunStatus = RunStatus.RUNNING
    step: int = 0
    observation: str | None = None
    output: str | None = None
    approved: bool = False
    attempts: dict[str, int] = field(default_factory=dict)
    provenance: list[str] = field(default_factory=list)

@dataclass(frozen=True)
class Event:
    run_id: str
    correlation_id: str
    kind: str
    detail: str

class Telemetry:
    def __init__(self) -> None:
        self.events: list[Event] = []

    def emit(self, run: Run, kind: str, detail: str = "") -> None:
        self.events.append(Event(run.run_id, run.correlation_id, kind, detail))

class RunStore:
    def __init__(self) -> None:
        self.runs: dict[str, Run] = {}

    def create(self, tenant_id: str, principal_id: str, goal: str, correlation_id: str | None = None) -> Run:
        run = Run(
            run_id=str(uuid.uuid4()),
            tenant_id=tenant_id,
            principal_id=principal_id,
            goal=goal,
            correlation_id=correlation_id or str(uuid.uuid4()),
        )
        self.runs[run.run_id] = run
        return run

    def get(self, run_id: str) -> Run:
        return self.runs[run_id]

class KnowledgeBase:
    def __init__(self, documents: list[Document]) -> None:
        self.documents = documents

    def search(self, tenant_id: str, principal_id: str, query: str) -> list[Document]:
        q = query.lower()
        return [
            d for d in self.documents
            if d.tenant_id == tenant_id
            and principal_id in d.allowed_principals
            and q in d.text.lower()
        ]

@dataclass(frozen=True)
class Tool:
    name: str
    authorize: Callable[[str, str], bool]
    execute: Callable[[str], str]
    effectful: bool = False

class IdempotencyStore:
    def __init__(self) -> None:
        self.results: dict[str, str] = {}

    def run_once(self, key: str, fn: Callable[[], str]) -> str:
        if key not in self.results:
            self.results[key] = fn()
        return self.results[key]

class ToolRegistry:
    def __init__(self, idem: IdempotencyStore) -> None:
        self.tools: dict[str, Tool] = {}
        self.idem = idem

    def register(self, tool: Tool) -> None:
        if tool.name in self.tools:
            raise ValueError(f"duplicate tool: {tool.name}")
        self.tools[tool.name] = tool

    def invoke(self, run: Run, name: str, argument: str, operation_key: str) -> str:
        tool = self.tools.get(name)
        if tool is None:
            raise KeyError(f"unknown tool: {name}")
        if not tool.authorize(run.tenant_id, run.principal_id):
            raise AuthorizationError(f"not authorized for tool: {name}")
        if tool.effectful:
            return self.idem.run_once(operation_key, lambda: tool.execute(argument))
        return tool.execute(argument)

class DeterministicPlanner:
    def plan(self, run: Run) -> Action:
        goal = run.goal
        if goal.startswith("lookup:"):
            if run.observation is None:
                return Action("retrieve", argument=goal.split(":", 1)[1].strip())
            return Action("final", output=run.observation)
        if goal.startswith("echo:"):
            if run.observation is None:
                return Action("tool", name="echo", argument=goal.split(":", 1)[1].strip())
            return Action("final", output=run.observation)
        if goal.startswith("publish:"):
            payload = goal.split(":", 1)[1].strip()
            if not run.approved:
                return Action("approval", name="publish", argument=payload)
            if run.observation is None:
                return Action("tool", name="publish", argument=payload)
            return Action("final", output=run.observation)
        if goal.startswith("flaky:"):
            if run.observation is None:
                return Action("tool", name="flaky", argument=goal.split(":", 1)[1].strip())
            return Action("final", output=run.observation)
        if goal.startswith("unknown-tool:"):
            return Action("tool", name="missing", argument="x")
        if goal == "runaway":
            return Action("tool", name="echo", argument="again")
        return Action("final", output="NO_ACTION")

class AgentService:
    def __init__(self, store: RunStore, kb: KnowledgeBase, tools: ToolRegistry,
                 planner: DeterministicPlanner, telemetry: Telemetry,
                 max_steps: int = 8, retry_limit: int = 2) -> None:
        self.store = store
        self.kb = kb
        self.tools = tools
        self.planner = planner
        self.telemetry = telemetry
        self.max_steps = max_steps
        self.retry_limit = retry_limit

    def start(self, tenant_id: str, principal_id: str, goal: str,
              correlation_id: str | None = None) -> Run:
        run = self.store.create(tenant_id, principal_id, goal, correlation_id)
        self.telemetry.emit(run, "run_started", goal.split(":", 1)[0])
        return self.run_until_blocked(run.run_id)

    def approve(self, run_id: str, principal_id: str) -> Run:
        run = self.store.get(run_id)
        if run.status != RunStatus.PAUSED:
            raise InvalidTransition("run is not paused")
        if principal_id != run.principal_id:
            raise AuthorizationError("approval principal mismatch")
        run.approved = True
        run.status = RunStatus.RUNNING
        self.telemetry.emit(run, "approval_granted", principal_id)
        return self.run_until_blocked(run_id)

    def run_until_blocked(self, run_id: str) -> Run:
        run = self.store.get(run_id)
        if run.status not in {RunStatus.RUNNING}:
            return run
        while run.status == RunStatus.RUNNING:
            if run.step >= self.max_steps:
                run.status = RunStatus.LIMIT_REACHED
                self.telemetry.emit(run, "limit_reached", str(self.max_steps))
                break
            run.step += 1
            self.telemetry.emit(run, "step_started", str(run.step))
            action = self.planner.plan(run)
            try:
                self._apply(run, action)
            except TransientError as exc:
                key = action.name
                run.attempts[key] = run.attempts.get(key, 0) + 1
                self.telemetry.emit(run, "transient_error", f"{key}:{run.attempts[key]}")
                if run.attempts[key] > self.retry_limit:
                    run.status = RunStatus.FAILURE
                    run.output = str(exc)
                    self.telemetry.emit(run, "run_failed", "retry_limit")
            except (AuthorizationError, KeyError, ValueError) as exc:
                run.status = RunStatus.FAILURE
                run.output = str(exc)
                self.telemetry.emit(run, "run_failed", type(exc).__name__)
        return run

    def _apply(self, run: Run, action: Action) -> None:
        if action.kind == "final":
            run.output = action.output
            run.status = RunStatus.SUCCESS
            self.telemetry.emit(run, "run_completed", "")
            return
        if action.kind == "approval":
            run.status = RunStatus.PAUSED
            self.telemetry.emit(run, "approval_requested", action.name)
            return
        if action.kind == "retrieve":
            docs = self.kb.search(run.tenant_id, run.principal_id, action.argument)
            run.provenance = [d.doc_id for d in docs]
            run.observation = " | ".join(d.text for d in docs) if docs else "NO_EVIDENCE"
            self.telemetry.emit(run, "retrieved", ",".join(run.provenance))
            return
        if action.kind == "tool":
            op_key = f"{run.run_id}:{action.name}:logical"
            result = self.tools.invoke(run, action.name, action.argument, op_key)
            run.observation = result
            self.telemetry.emit(run, "tool_completed", action.name)
            return
        raise ValueError(f"invalid action: {action.kind}")

def build_system(max_steps: int = 8, retry_limit: int = 2):
    side_effects: list[str] = []
    flaky_attempts = {"count": 0}
    idem = IdempotencyStore()
    tools = ToolRegistry(idem)
    tools.register(Tool("echo", lambda tenant, principal: principal != "blocked",
                        lambda value: value.upper()))
    tools.register(Tool("publish", lambda tenant, principal: principal == "alice",
                        lambda value: side_effects.append(value) or f"PUBLISHED:{value}", effectful=True))
    def flaky(value: str) -> str:
        flaky_attempts["count"] += 1
        if flaky_attempts["count"] == 1:
            raise TransientError("temporary dependency failure")
        return f"RECOVERED:{value}"
    tools.register(Tool("flaky", lambda tenant, principal: True, flaky))
    kb = KnowledgeBase([
        Document("a1", "tenant-a", frozenset({"alice"}), "alpha policy is 42"),
        Document("a2", "tenant-a", frozenset({"bob"}), "alpha secret for bob"),
        Document("b1", "tenant-b", frozenset({"alice"}), "alpha from tenant b"),
    ])
    telemetry = Telemetry()
    service = AgentService(RunStore(), kb, tools, DeterministicPlanner(), telemetry,
                           max_steps=max_steps, retry_limit=retry_limit)
    return service, telemetry, side_effects, idem

def test_tenant_and_acl_isolation() -> None:
    service, _, _, _ = build_system()
    run = service.start("tenant-a", "alice", "lookup:alpha")
    assert run.status == RunStatus.SUCCESS
    assert run.output == "alpha policy is 42"
    assert run.provenance == ["a1"]

def test_blocked_principal_cannot_use_tool() -> None:
    service, _, _, _ = build_system()
    run = service.start("tenant-a", "blocked", "echo:hello")
    assert run.status == RunStatus.FAILURE
    assert "not authorized" in (run.output or "")

def test_publish_pauses_before_effect() -> None:
    service, _, effects, _ = build_system()
    run = service.start("tenant-a", "alice", "publish:release-7")
    assert run.status == RunStatus.PAUSED
    assert effects == []

def test_approval_resumes_and_commits_once() -> None:
    service, _, effects, _ = build_system()
    run = service.start("tenant-a", "alice", "publish:release-7")
    run = service.approve(run.run_id, "alice")
    assert run.status == RunStatus.SUCCESS
    assert run.output == "PUBLISHED:release-7"
    assert effects == ["release-7"]

def test_wrong_principal_cannot_approve() -> None:
    service, _, effects, _ = build_system()
    run = service.start("tenant-a", "alice", "publish:x")
    try:
        service.approve(run.run_id, "bob")
        raise AssertionError("wrong principal should not approve")
    except AuthorizationError:
        pass
    assert effects == []

def test_effect_idempotency_survives_repeat_invoke() -> None:
    service, _, effects, _ = build_system()
    run = service.start("tenant-a", "alice", "publish:x")
    run.approved = True
    run.status = RunStatus.RUNNING
    service.tools.invoke(run, "publish", "x", f"{run.run_id}:publish:logical")
    service.tools.invoke(run, "publish", "x", f"{run.run_id}:publish:logical")
    assert effects == ["x"]

def test_transient_failure_retries_then_succeeds() -> None:
    service, telemetry, _, _ = build_system(retry_limit=2)
    run = service.start("tenant-a", "alice", "flaky:job")
    assert run.status == RunStatus.SUCCESS
    assert run.output == "RECOVERED:job"
    assert any(e.kind == "transient_error" for e in telemetry.events)

def test_retry_limit_can_fail_run() -> None:
    service, _, _, _ = build_system(retry_limit=0)
    run = service.start("tenant-a", "alice", "flaky:job")
    assert run.status == RunStatus.FAILURE

def test_step_limit_stops_runaway_goal() -> None:
    service, _, _, _ = build_system(max_steps=3)
    run = service.start("tenant-a", "alice", "runaway")
    assert run.status == RunStatus.LIMIT_REACHED

def test_unknown_tool_fails_closed() -> None:
    service, _, _, _ = build_system()
    run = service.start("tenant-a", "alice", "unknown-tool:x")
    assert run.status == RunStatus.FAILURE
    assert "unknown tool" in (run.output or "")

def test_correlation_id_is_preserved() -> None:
    service, telemetry, _, _ = build_system()
    run = service.start("tenant-a", "alice", "echo:x", correlation_id="corr-9")
    events = [e for e in telemetry.events if e.run_id == run.run_id]
    assert events and all(e.correlation_id == "corr-9" for e in events)

def test_completed_run_is_terminal_for_approval() -> None:
    service, _, _, _ = build_system()
    run = service.start("tenant-a", "alice", "echo:x")
    try:
        service.approve(run.run_id, "alice")
        raise AssertionError("completed run must not accept approval")
    except InvalidTransition:
        pass

def test_no_evidence_is_explicit() -> None:
    service, _, _, _ = build_system()
    run = service.start("tenant-a", "alice", "lookup:missing")
    assert run.status == RunStatus.SUCCESS
    assert run.output == "NO_EVIDENCE"
    assert run.provenance == []

def run_tests() -> None:
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_") and callable(v)]
    for test in tests:
        test()
        print("PASS", test.__name__)
    print(f"{len(tests)} tests passed")

if __name__ == "__main__":
    run_tests()
# END PROJECT144_PRODUCTION_CORE
