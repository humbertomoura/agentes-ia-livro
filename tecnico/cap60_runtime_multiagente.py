"""Código do Capítulo 60 — Implementando um runtime multiagente sem framework.

Extraído da versão técnica v26 do livro "Agentes de Inteligência Artificial".
Mantenha este arquivo idêntico à listagem publicada no manuscrito.
"""
from __future__ import annotations

 
import hashlib
import uuid
from dataclasses import dataclass, field
from typing import Callable, FrozenSet
 
 
@dataclass(frozen=True)
class TaskPacket:
    task_id: str
    objective: str
    context: dict
    parent_task_id: str | None = None


@dataclass(frozen=True)
class AgentResult:
    status: str
    summary: str
    artifacts: tuple[str, ...] = ()


@dataclass(frozen=True)
class Artifact:
    artifact_id: str
    run_id: str
    created_by: str
    kind: str
    content: str


class ArtifactStore:
    def __init__(self):
        self._items: dict[str, Artifact] = {}

    def put(self, run_id: str, created_by: str, kind: str, content: str) -> str:
        digest = hashlib.sha256(
            f"{run_id}|{created_by}|{kind}|{content}".encode()
        ).hexdigest()[:12]
        artifact_id = f"art-{digest}"
        self._items[artifact_id] = Artifact(
            artifact_id, run_id, created_by, kind, content
        )
        return artifact_id

    def get(self, artifact_id: str) -> Artifact:
        return self._items[artifact_id]


@dataclass(frozen=True)
class AgentContext:
    run_id: str
    agent_name: str
    scopes: FrozenSet[str]
    artifacts: ArtifactStore


AgentHandler = Callable[[TaskPacket, AgentContext], AgentResult]


@dataclass(frozen=True)
class AgentSpec:
    name: str
    handler: AgentHandler
    delegates_to: FrozenSet[str] = frozenset()
    context_keys: FrozenSet[str] = frozenset()
    scopes: FrozenSet[str] = frozenset()


@dataclass
class RunState:
    run_id: str
    owner: str
    principal_scopes: FrozenSet[str]
    max_hops: int = 8
    hops: int = 0
    trace: list[dict] = field(default_factory=list)
 
 
class MultiAgentRuntime:
    def __init__(self, specs: list[AgentSpec]):
        self.registry = {spec.name: spec for spec in specs}
        if len(self.registry) != len(specs):
            raise ValueError("duplicate agent name")
        self.artifacts = ArtifactStore()
 
    def start(self, owner: str, principal_scopes: set[str],
              max_hops: int = 8) -> RunState:
        if owner not in self.registry:
            raise KeyError(f"unknown agent: {owner}")
        return RunState(
            run_id=f"run-{uuid.uuid4().hex[:8]}",
            owner=owner,
            principal_scopes=frozenset(principal_scopes),
            max_hops=max_hops,
        )
 
    def _authorize_edge(self, caller: str, target: str) -> None:
        if caller not in self.registry or target not in self.registry:
            raise KeyError(f"unknown agent: {caller} or {target}")
        if target not in self.registry[caller].delegates_to:
            raise PermissionError(f"{caller} cannot delegate to {target}")
 
    def _consume_hop(self, state: RunState) -> None:
        if state.hops >= state.max_hops:
            raise RuntimeError("hop limit reached")
        state.hops += 1
 


    def _invoke(self, state: RunState, agent_name: str, packet: TaskPacket, mode: str):
        spec = self.registry[agent_name]
        effective_scopes = state.principal_scopes & spec.scopes
        filtered = {
            key: value for key, value in packet.context.items()
            if key in spec.context_keys
        }
        local_packet = TaskPacket(
            task_id=packet.task_id,
            objective=packet.objective,
            context=filtered,
            parent_task_id=packet.parent_task_id,
        )
        ctx = AgentContext(
            run_id=state.run_id,
            agent_name=agent_name,
            scopes=effective_scopes,
            artifacts=self.artifacts,
        )
        result = spec.handler(local_packet, ctx)
        state.trace.append({
            "mode": mode,
            "agent": agent_name,
            "task_id": packet.task_id,
            "context_keys": sorted(filtered),
            "scopes": sorted(effective_scopes),
            "status": result.status,
        })
        return result

    def call_as_tool(
        self,
        state: RunState,
        caller: str,
        target: str,
        objective: str,
        context: dict,
    ) -> AgentResult:
        self._authorize_edge(caller, target)
        self._consume_hop(state)
        packet = TaskPacket(
            task_id=str(uuid.uuid4()),
            objective=objective,
            context=context,
        )
        return self._invoke(state, target, packet, mode="agent_as_tool")

    def handoff(
        self,
        state: RunState,
        caller: str,
        target: str,
        objective: str,
        context: dict,
    ) -> AgentResult:
        if state.owner != caller:
            return AgentResult("BLOCKED", "caller does not own the run")
        try:
            self._authorize_edge(caller, target)
            self._consume_hop(state)
        except (PermissionError, RuntimeError, KeyError) as exc:
            return AgentResult("BLOCKED", str(exc))
        state.owner = target
        packet = TaskPacket(
            task_id=str(uuid.uuid4()),
            objective=objective,
            context=context,
        )
        return self._invoke(state, target, packet, mode="handoff")


def manager_handler(packet: TaskPacket, ctx: AgentContext) -> AgentResult:
    return AgentResult("SUCCESS", "manager ready")


def policy_handler(packet: TaskPacket, ctx: AgentContext) -> AgentResult:
    policy = packet.context.get("policy", "missing")
    change = packet.context.get("change", "missing")
    artifact_id = ctx.artifacts.put(
        ctx.run_id, ctx.agent_name, "policy_review",
        f"policy={policy}; change={change}",
    )
    return AgentResult("SUCCESS", "policy reviewed", (artifact_id,))


def risk_handler(packet: TaskPacket, ctx: AgentContext) -> AgentResult:
    allowed = "write:ticket" in ctx.scopes
    visible = ",".join(sorted(packet.context))
    return AgentResult(
        "SUCCESS",
        f"visible={visible}; can_write_ticket={allowed}",
    )


def support_handler(packet: TaskPacket, ctx: AgentContext) -> AgentResult:
    return AgentResult(
        "SUCCESS",
        f"support owns request: {packet.context.get('user_message', '')}",
    )


def build_runtime() -> MultiAgentRuntime:
    return MultiAgentRuntime([
        AgentSpec(
            name="manager",
            handler=manager_handler,
            delegates_to=frozenset({"policy", "risk", "support"}),
            context_keys=frozenset({"change", "policy", "telemetry", "user_message"}),
            scopes=frozenset({"read:policy", "read:telemetry", "write:ticket"}),
        ),
        AgentSpec(
            name="policy",
            handler=policy_handler,
            context_keys=frozenset({"change", "policy"}),
            scopes=frozenset({"read:policy"}),
        ),
        AgentSpec(
            name="risk",
            handler=risk_handler,
            context_keys=frozenset({"change", "telemetry"}),
            scopes=frozenset({"read:telemetry", "write:ticket"}),
        ),
        AgentSpec(
            name="support",
            handler=support_handler,
            context_keys=frozenset({"user_message"}),
            scopes=frozenset({"write:ticket"}),
        ),
    ])


def test_manager_keeps_ownership():
    rt = build_runtime()
    state = rt.start("manager", {"read:policy"})
    result = rt.call_as_tool(
        state, "manager", "policy", "review change",
        {"change": "deploy", "policy": "approval required"},
    )
    assert result.status == "SUCCESS"
    assert state.owner == "manager"


def test_handoff_transfers_ownership():
    rt = build_runtime()
    state = rt.start("manager", {"write:ticket"})
    result = rt.handoff(
        state, "manager", "support", "take over support request",
        {"user_message": "My invoice is wrong", "policy": "secret"},
    )
    assert result.status == "SUCCESS"
    assert state.owner == "support"
    assert state.trace[-1]["context_keys"] == ["user_message"]


def test_context_isolation():
    rt = build_runtime()
    state = rt.start("manager", {"read:telemetry"})
    result = rt.call_as_tool(
        state, "manager", "risk", "assess risk",
        {"change": "deploy", "telemetry": "healthy", "pii": "CPF 000"},
    )
    assert "pii" not in result.summary
    assert state.trace[-1]["context_keys"] == ["change", "telemetry"]


def test_scope_intersection_prevents_elevation():
    rt = build_runtime()
    state = rt.start("manager", {"read:telemetry"})
    result = rt.call_as_tool(
        state, "manager", "risk", "assess risk",
        {"change": "deploy", "telemetry": "healthy"},
    )
    assert "can_write_ticket=False" in result.summary
    assert state.trace[-1]["scopes"] == ["read:telemetry"]


def test_unauthorized_delegation_is_blocked():
    rt = build_runtime()
    state = rt.start("manager", {"read:policy"})
    try:
        rt.call_as_tool(state, "policy", "risk", "delegate", {})
        assert False, "expected PermissionError"
    except PermissionError:
        pass


def test_hop_limit_blocks_handoff():
    rt = build_runtime()
    state = rt.start("manager", {"write:ticket"}, max_hops=0)
    result = rt.handoff(
        state, "manager", "support", "take over",
        {"user_message": "hello"},
    )
    assert result.status == "BLOCKED"
    assert state.owner == "manager"


def test_artifact_provenance():
    rt = build_runtime()
    state = rt.start("manager", {"read:policy"})
    result = rt.call_as_tool(
        state, "manager", "policy", "review",
        {"change": "deploy", "policy": "approval required"},
    )
    artifact = rt.artifacts.get(result.artifacts[0])
    assert artifact.created_by == "policy"
    assert artifact.run_id == state.run_id


def test_specialist_results_do_not_overwrite_each_other():
    rt = build_runtime()
    state = rt.start("manager", {"read:policy", "read:telemetry"})
    policy = rt.call_as_tool(
        state, "manager", "policy", "review policy",
        {"change": "deploy", "policy": "approval required"},
    )
    risk = rt.call_as_tool(
        state, "manager", "risk", "review telemetry",
        {"change": "deploy", "telemetry": "healthy"},
    )
    assert policy.summary == "policy reviewed"
    assert "telemetry" in risk.summary
    assert state.owner == "manager"


@dataclass(frozen=True)
class CoordinationDecision:
    kind: str        # RESPOND | CALL_AGENT | HANDOFF
    target: str | None
    task: str | None

def apply_decision(runtime, state, caller, decision, context):
    if decision.kind == "CALL_AGENT":
        return runtime.call_as_tool(
            state, caller, decision.target, decision.task, context)
    if decision.kind == "HANDOFF":
        return runtime.handoff(
            state, caller, decision.target, decision.task, context)
    return AgentResult("SUCCESS", decision.task or "")
