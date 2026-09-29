"""Código do Capítulo 69 — Implementando adaptadores de protocolo sem framework.

Extraído da versão técnica v26 do livro "Agentes de Inteligência Artificial".
Mantenha este arquivo idêntico à listagem publicada no manuscrito.
"""

from dataclasses import dataclass, field
from hashlib import sha256
from typing import Any, Callable
import json
import uuid

MCP_VERSION = "2026-07-28"


@dataclass(frozen=True)
class Principal:
    subject: str
    scopes: frozenset[str]


@dataclass(frozen=True)
class ToolSpec:
    name: str
    description: str
    required_scopes: frozenset[str]
    input_schema: dict
    output_schema: dict
    handler: Callable[[dict], Any]


@dataclass(frozen=True)
class AgentSkill:
    skill_id: str
    name: str
    description: str
    required_scopes: frozenset[str]


@dataclass
class Task:
    task_id: str
    context_id: str
    state: str
    message: str | None = None
    artifacts: list[dict] = field(default_factory=list)


class DomainService:
    """Protocol-neutral application core."""

    def __init__(self):
        self._published = {}

    def search_policy(self, args: dict) -> dict:
        topic = args["topic"].lower()
        if "deploy" in topic:
            return {"policy_id": "POL-17", "text": "Production deploys require approval."}
        return {"policy_id": None, "text": "No matching policy."}

    def publish_report(self, args: dict) -> dict:
        report_id = args["report_id"]
        body = args["body"]
        key = sha256(f"{report_id}|{body}".encode()).hexdigest()
        if key in self._published:
            return {"report_id": report_id, "published": True, "deduplicated": True}
        self._published[key] = body
        return {"report_id": report_id, "published": True, "deduplicated": False}


class Registry:
    def __init__(self, service: DomainService):
        self.tools = {
            "search_policy": ToolSpec(
                name="search_policy",
                description="Search an internal policy by topic.",
                required_scopes=frozenset({"policy:read"}),
                input_schema={"type": "object", "required": ["topic"]},
                output_schema={"type": "object"},
                handler=service.search_policy,
            ),
            "publish_report": ToolSpec(
                name="publish_report",
                description="Publish an approved report.",
                required_scopes=frozenset({"report:publish"}),
                input_schema={"type": "object", "required": ["report_id", "body"]},
                output_schema={"type": "object"},
                handler=service.publish_report,
            ),
        }
        self.skills = {
            "policy_research": AgentSkill(
                "policy_research",
                "Policy research",
                "Research an internal policy and return an artifact.",
                frozenset({"policy:read"}),
            ),
            "report_publication": AgentSkill(
                "report_publication",
                "Report publication",
                "Publish a report after authorization and approval.",
                frozenset({"report:publish"}),
            ),
        }

class MCPAdapter:
    """Didactic adapter inspired by MCP 2026-07-28.

    It demonstrates version pinning, explicit capabilities, authorization,
    stateless calls, and a multi-round-trip approval. It is not a replacement
    for an official MCP SDK or conformance implementation.
    """

    def __init__(self, registry: Registry):
        self.registry = registry

    def discover(self, principal: Principal) -> dict:
        visible = [
            self._public_tool(spec)
            for spec in self.registry.tools.values()
            if spec.required_scopes <= principal.scopes
        ]
        visible.sort(key=lambda x: x["name"])
        return {
            "protocolVersion": MCP_VERSION,
            "tools": visible,
            "extensions": ["io.modelcontextprotocol/tasks"],
        }

    def call_tool(
        self,
        principal: Principal,
        name: str,
        arguments: dict,
        *,
        protocol_version: str = MCP_VERSION,
        input_responses: dict | None = None,
        request_state: str | None = None,
    ) -> dict:
        if protocol_version != MCP_VERSION:
            return {"error": "UNSUPPORTED_PROTOCOL_VERSION"}
        spec = self.registry.tools.get(name)
        if spec is None:
            return {"error": "UNKNOWN_TOOL"}
        if not spec.required_scopes <= principal.scopes:
            return {"error": "FORBIDDEN"}
        missing = [key for key in spec.input_schema.get("required", []) if key not in arguments]
        if missing:
            return {"error": "INVALID_ARGUMENTS", "missing": missing}

        if name == "publish_report":
            expected_state = self._request_state(name, arguments, principal.subject)
            if request_state is not None and request_state != expected_state:
                return {"error": "INVALID_REQUEST_STATE"}
            approved = bool((input_responses or {}).get("approval"))
            if not approved:
                return {
                    "resultType": "input_required",
                    "requestState": expected_state,
                    "inputRequests": {
                        "approval": {
                            "kind": "elicitation",
                            "prompt": "Approve publication of this report?",
                        }
                    },
                }

        result = spec.handler(arguments)
        return {"resultType": "complete", "structuredContent": result}

    @staticmethod
    def _request_state(name: str, arguments: dict, subject: str) -> str:
        raw = json.dumps([subject, name, arguments], sort_keys=True)
        return sha256(raw.encode()).hexdigest()

    @staticmethod
    def _public_tool(spec: ToolSpec) -> dict:
        return {
            "name": spec.name,
            "description": spec.description,
            "inputSchema": spec.input_schema,
            "outputSchema": spec.output_schema,
        }

class A2AAdapter:
    """Didactic adapter that models A2A Agent Cards and task lifecycle."""

    def __init__(self, registry: Registry):
        self.registry = registry
        self.tasks: dict[str, Task] = {}

    def agent_card(self, principal: Principal) -> dict:
        skills = [
            {
                "id": spec.skill_id,
                "name": spec.name,
                "description": spec.description,
            }
            for spec in self.registry.skills.values()
            if spec.required_scopes <= principal.scopes
        ]
        skills.sort(key=lambda x: x["id"])
        return {
            "name": "Institutional Operations Agent",
            "version": "1.0.0",
            "capabilities": {"streaming": True, "pushNotifications": False},
            "defaultInputModes": ["text"],
            "defaultOutputModes": ["text", "application/json"],
            "skills": skills,
        }

    def send_task(
        self,
        principal: Principal,
        skill_id: str,
        payload: dict,
        *,
        context_id: str | None = None,
    ) -> Task:
        skill = self.registry.skills.get(skill_id)
        if skill is None:
            return self._new_task(context_id, "rejected", "Unknown skill.")
        if not skill.required_scopes <= principal.scopes:
            return self._new_task(context_id, "auth-required", "Additional authorization required.")

        task = self._new_task(context_id, "working", "Task accepted.")
        if skill_id == "policy_research":
            topic = payload.get("topic")
            if not topic:
                task.state = "input-required"
                task.message = "A topic is required."
                return task
            result = self.registry.tools["search_policy"].handler({"topic": topic})
            task.artifacts.append({
                "artifactId": f"artifact-{task.task_id}",
                "name": "policy-result",
                "parts": [{"kind": "data", "data": result}],
            })
            task.state = "completed"
            task.message = "Policy research completed."
            return task

        if skill_id == "report_publication":
            if not payload.get("approved"):
                task.state = "input-required"
                task.message = "Human approval is required before publication."
                return task
            result = self.registry.tools["publish_report"].handler(payload)
            task.artifacts.append({
                "artifactId": f"artifact-{task.task_id}",
                "name": "publication-result",
                "parts": [{"kind": "data", "data": result}],
            })
            task.state = "completed"
            task.message = "Report published."
            return task

        task.state = "failed"
        task.message = "No handler for skill."
        return task

    def _new_task(self, context_id: str | None, state: str, message: str) -> Task:
        task = Task(
            task_id=str(uuid.uuid4()),
            context_id=context_id or str(uuid.uuid4()),
            state=state,
            message=message,
        )
        self.tasks[task.task_id] = task
        return task

class AGUIAdapter:
    """Small event adapter for a user-facing frontend.

    The event names follow AG-UI concepts, but this example only illustrates
    lifecycle and state filtering; it is not a complete AG-UI implementation.
    """

    def stream_policy_run(self, thread_id: str, topic: str, result: dict):
        run_id = str(uuid.uuid4())
        yield {"type": "RUN_STARTED", "threadId": thread_id, "runId": run_id}
        yield {
            "type": "STATE_SNAPSHOT",
            "snapshot": {"topic": topic, "status": "searching"},
        }
        yield {
            "type": "TOOL_CALL_START",
            "toolCallId": "tc-1",
            "toolCallName": "search_policy",
        }
        yield {
            "type": "TOOL_CALL_RESULT",
            "messageId": "m-1",
            "toolCallId": "tc-1",
            "content": json.dumps(result),
        }
        yield {
            "type": "STATE_DELTA",
            "delta": [{"op": "replace", "path": "/status", "value": "done"}],
        }
        yield {"type": "RUN_FINISHED", "threadId": thread_id, "runId": run_id}

def build_demo():
    service = DomainService()
    registry = Registry(service)
    return service, registry, MCPAdapter(registry), A2AAdapter(registry), AGUIAdapter()


def test_mcp_discovery_filters_authority():
    _, _, mcp, _, _ = build_demo()
    principal = Principal("alice", frozenset({"policy:read"}))
    names = [t["name"] for t in mcp.discover(principal)["tools"]]
    assert names == ["search_policy"]


def test_mcp_version_mismatch_fails_closed():
    _, _, mcp, _, _ = build_demo()
    principal = Principal("alice", frozenset({"policy:read"}))
    out = mcp.call_tool(principal, "search_policy", {"topic": "deploy"}, protocol_version="old")
    assert out["error"] == "UNSUPPORTED_PROTOCOL_VERSION"


def test_mcp_multi_round_trip_approval_and_idempotency():
    _, _, mcp, _, _ = build_demo()
    principal = Principal("publisher", frozenset({"report:publish"}))
    args = {"report_id": "R-1", "body": "Approved body"}
    first = mcp.call_tool(principal, "publish_report", args)
    assert first["resultType"] == "input_required"
    second = mcp.call_tool(
        principal,
        "publish_report",
        args,
        input_responses={"approval": True},
        request_state=first["requestState"],
    )
    third = mcp.call_tool(
        principal,
        "publish_report",
        args,
        input_responses={"approval": True},
        request_state=first["requestState"],
    )
    assert second["structuredContent"]["deduplicated"] is False
    assert third["structuredContent"]["deduplicated"] is True


def test_a2a_card_filters_skills():
    _, _, _, a2a, _ = build_demo()
    principal = Principal("alice", frozenset({"policy:read"}))
    ids = [s["id"] for s in a2a.agent_card(principal)["skills"]]
    assert ids == ["policy_research"]


def test_a2a_auth_required_is_interrupted_not_terminal_success():
    _, _, _, a2a, _ = build_demo()
    principal = Principal("alice", frozenset())
    task = a2a.send_task(principal, "report_publication", {"report_id": "R-1", "body": "x"})
    assert task.state == "auth-required"
    assert not task.artifacts


def test_a2a_completed_task_preserves_context_and_artifact():
    _, _, _, a2a, _ = build_demo()
    principal = Principal("alice", frozenset({"policy:read"}))
    task = a2a.send_task(principal, "policy_research", {"topic": "deploy"}, context_id="ctx-7")
    assert task.state == "completed"
    assert task.context_id == "ctx-7"
    assert task.artifacts[0]["parts"][0]["data"]["policy_id"] == "POL-17"


def test_a2a_input_required_for_missing_business_input():
    _, _, _, a2a, _ = build_demo()
    principal = Principal("alice", frozenset({"policy:read"}))
    task = a2a.send_task(principal, "policy_research", {})
    assert task.state == "input-required"


def test_agui_run_has_boundaries_and_no_private_state():
    service, _, _, _, agui = build_demo()
    result = service.search_policy({"topic": "deploy"})
    events = list(agui.stream_policy_run("thread-1", "deploy", result))
    assert events[0]["type"] == "RUN_STARTED"
    assert events[-1]["type"] == "RUN_FINISHED"
    serialized = json.dumps(events)
    assert "report:publish" not in serialized
    assert "policy:read" not in serialized


if __name__ == "__main__":
    tests = [
        test_mcp_discovery_filters_authority,
        test_mcp_version_mismatch_fails_closed,
        test_mcp_multi_round_trip_approval_and_idempotency,
        test_a2a_card_filters_skills,
        test_a2a_auth_required_is_interrupted_not_terminal_success,
        test_a2a_completed_task_preserves_context_and_artifact,
        test_a2a_input_required_for_missing_business_input,
        test_agui_run_has_boundaries_and_no_private_state,
    ]
    for test in tests:
        test()
        print("PASS", test.__name__)
