"""Código do Capítulo 114 — Implementando uma camada de segurança sem framework.

Extraído da versão técnica v26 do livro "Agentes de Inteligência Artificial".
Mantenha este arquivo idêntico à listagem publicada no manuscrito.
"""
from __future__ import annotations

 
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from enum import Enum
from hashlib import sha256
from typing import Any, Callable
import json
 
 
class Trust(str, Enum):
    TRUSTED = "trusted"
    UNTRUSTED = "untrusted"
    SECRET = "secret"
 
 
class DecisionKind(str, Enum):
    ALLOW = "allow"
    DENY = "deny"
    APPROVAL_REQUIRED = "approval_required"
 
 
@dataclass(frozen=True)
class LabeledValue:
    value: Any
    trust: Trust = Trust.TRUSTED
    source: str = "application"
 
 
@dataclass(frozen=True)
class Principal:
    subject_id: str
    tenant_id: str
    scopes: frozenset[str]
 
 
@dataclass(frozen=True)
class Delegation:
    delegated_scopes: frozenset[str]
    expires_at: datetime
 
    def active(self, now: datetime) -> bool:
        return now < self.expires_at
 
 
@dataclass(frozen=True)
class ToolSpec:
    name: str
    required_scopes: frozenset[str]
    read_only: bool
    high_impact: bool = False
    external_egress: bool = False
    allow_untrusted_arguments: bool = False
    tenant_bound: bool = True
 
 
@dataclass(frozen=True)
class ActionRequest:
    tool_name: str
    arguments: dict[str, LabeledValue]
    target_tenant: str
    task_id: str
    remote_component: str | None = None
 
 
@dataclass(frozen=True)
class SecurityDecision:
    kind: DecisionKind
    reason: str
    effective_scopes: frozenset[str] = frozenset()
    action_digest: str | None = None
 
 
@dataclass(frozen=True)
class Approval:
    action_digest: str
    approved_by: str
    expires_at: datetime
 
    def valid_for(self, digest: str, now: datetime) -> bool:
        return self.action_digest == digest and now < self.expires_at
 
 
@dataclass(frozen=True)
class AuditEvent:
    event_type: str
    task_id: str
    subject_id: str
    tenant_id: str
    tool_name: str
    decision: str
    reason: str
 
 
@dataclass
class SecurityPolicy:
    allowed_tools: frozenset[str]
    trusted_remote_components: frozenset[str] = frozenset()
    require_approval_for_high_impact: bool = True
    deny_secret_egress: bool = True
    deny_untrusted_high_impact_arguments: bool = True
 
 
class AuditLog:
    def __init__(self) -> None:
        self._events: list[AuditEvent] = []
 
    def append(self, event: AuditEvent) -> None:
        self._events.append(event)
 
    def events_for_tenant(self, tenant_id: str) -> list[AuditEvent]:
        return [event for event in self._events if event.tenant_id == tenant_id]
 
    def all_events(self) -> tuple[AuditEvent, ...]:
        return tuple(self._events)
 
 
def canonical_action(request: ActionRequest) -> str:
    serializable = {
        "tool_name": request.tool_name,
        "target_tenant": request.target_tenant,
        "task_id": request.task_id,
        "remote_component": request.remote_component,
        "arguments": {
            key: {
                "value": value.value,
                "trust": value.trust.value,
                "source": value.source,
            }
            for key, value in sorted(request.arguments.items())
        },
    }
    return json.dumps(serializable, sort_keys=True, separators=(",", ":"), default=str)
 
 
def action_digest(request: ActionRequest) -> str:
    return sha256(canonical_action(request).encode("utf-8")).hexdigest()
 
 
class SecurityGateway:
    def __init__(
        self,
        tools: dict[str, ToolSpec],
        handlers: dict[str, Callable[[dict[str, Any]], Any]],
        policy: SecurityPolicy,
        audit_log: AuditLog | None = None,
    ) -> None:
        self.tools = tools
        self.handlers = handlers
        self.policy = policy
        self.audit_log = audit_log or AuditLog()
 
    def _effective_scopes(
        self,
        principal: Principal,
        delegation: Delegation | None,
        now: datetime,
    ) -> frozenset[str]:
        if delegation is None:
            return principal.scopes
        if not delegation.active(now):
            return frozenset()
        return principal.scopes & delegation.delegated_scopes
 
    def authorize(
        self,
        principal: Principal,
        request: ActionRequest,
        *,
        delegation: Delegation | None = None,
        approval: Approval | None = None,
        now: datetime | None = None,
    ) -> SecurityDecision:
        now = now or datetime.now(timezone.utc)
        digest = action_digest(request)
 
        if request.tool_name not in self.policy.allowed_tools:
            return SecurityDecision(DecisionKind.DENY, "tool_not_allowlisted", action_digest=digest)
 
        spec = self.tools.get(request.tool_name)
        if spec is None or request.tool_name not in self.handlers:
            return SecurityDecision(DecisionKind.DENY, "tool_not_registered", action_digest=digest)
 
        if request.remote_component is not None and request.remote_component not in self.policy.trusted_remote_components:
            return SecurityDecision(DecisionKind.DENY, "untrusted_remote_component", action_digest=digest)
 
        if spec.tenant_bound and request.target_tenant != principal.tenant_id:
            return SecurityDecision(DecisionKind.DENY, "tenant_boundary_violation", action_digest=digest)
 
        effective_scopes = self._effective_scopes(principal, delegation, now)
        if not spec.required_scopes.issubset(effective_scopes):
            return SecurityDecision(
                DecisionKind.DENY,
                "insufficient_scope",
                effective_scopes=effective_scopes,
                action_digest=digest,
            )
 
        values = tuple(request.arguments.values())
        has_secret = any(value.trust == Trust.SECRET for value in values)
        has_untrusted = any(value.trust == Trust.UNTRUSTED for value in values)
 
        if self.policy.deny_secret_egress and spec.external_egress and has_secret:
            return SecurityDecision(
                DecisionKind.DENY,
                "secret_egress_blocked",
                effective_scopes=effective_scopes,
                action_digest=digest,
            )
 
        if (
            self.policy.deny_untrusted_high_impact_arguments
            and spec.high_impact
            and has_untrusted
            and not spec.allow_untrusted_arguments
        ):
            return SecurityDecision(
                DecisionKind.DENY,
                "untrusted_data_controls_high_impact_action",
                effective_scopes=effective_scopes,
                action_digest=digest,
            )
 
        if self.policy.require_approval_for_high_impact and spec.high_impact:
            if approval is None or not approval.valid_for(digest, now):
                return SecurityDecision(
                    DecisionKind.APPROVAL_REQUIRED,
                    "high_impact_action_requires_bound_approval",
                    effective_scopes=effective_scopes,
                    action_digest=digest,
                )
 
        return SecurityDecision(
            DecisionKind.ALLOW,
            "allowed",
            effective_scopes=effective_scopes,
            action_digest=digest,
        )
 
    def execute(
        self,
        principal: Principal,
        request: ActionRequest,
        *,
        delegation: Delegation | None = None,
        approval: Approval | None = None,
        now: datetime | None = None,
    ) -> Any:
        now = now or datetime.now(timezone.utc)
        decision = self.authorize(
            principal,
            request,
            delegation=delegation,
            approval=approval,
            now=now,
        )
        self.audit_log.append(
            AuditEvent(
                event_type="security_decision",
                task_id=request.task_id,
                subject_id=principal.subject_id,
                tenant_id=principal.tenant_id,
                tool_name=request.tool_name,
                decision=decision.kind.value,
                reason=decision.reason,
            )
        )
        if decision.kind != DecisionKind.ALLOW:
            raise PermissionError(decision.reason)
 
        args = {key: value.value for key, value in request.arguments.items()}
        result = self.handlers[request.tool_name](args)
        self.audit_log.append(
            AuditEvent(
                event_type="tool_executed",
                task_id=request.task_id,
                subject_id=principal.subject_id,
                tenant_id=principal.tenant_id,
                tool_name=request.tool_name,
                decision="executed",
                reason="policy_passed",
            )
        )
        return result
 
 
# ------------------------------ demo tools ------------------------------
 
def read_ticket(args: dict[str, Any]) -> dict[str, Any]:
    return {"ticket_id": args["ticket_id"], "status": "open"}
 
 
def update_ticket(args: dict[str, Any]) -> dict[str, Any]:
    return {"ticket_id": args["ticket_id"], "status": args["status"]}
 
 
def send_webhook(args: dict[str, Any]) -> dict[str, Any]:
    return {"sent": True, "destination": args["destination"]}
 
 
def build_gateway() -> SecurityGateway:
    tools = {
        "read_ticket": ToolSpec(
            name="read_ticket",
            required_scopes=frozenset({"tickets:read"}),
            read_only=True,
        ),
        "update_ticket": ToolSpec(
            name="update_ticket",
            required_scopes=frozenset({"tickets:write"}),
            read_only=False,
            high_impact=True,
        ),
        "send_webhook": ToolSpec(
            name="send_webhook",
            required_scopes=frozenset({"webhook:send"}),
            read_only=False,
            high_impact=True,
            external_egress=True,
        ),
    }
    handlers = {
        "read_ticket": read_ticket,
        "update_ticket": update_ticket,
        "send_webhook": send_webhook,
    }
    policy = SecurityPolicy(
        allowed_tools=frozenset(tools),
        trusted_remote_components=frozenset({"mcp://helpdesk.internal", "a2a://reviewer.internal"}),
    )
    return SecurityGateway(tools, handlers, policy)
 
 
def principal_a() -> Principal:
    return Principal(
        subject_id="user-123",
        tenant_id="tenant-a",
        scopes=frozenset({"tickets:read", "tickets:write", "webhook:send"}),
    )
 
 
def approved(request: ActionRequest, now: datetime) -> Approval:
    return Approval(
        action_digest=action_digest(request),
        approved_by="reviewer-7",
        expires_at=now + timedelta(minutes=5),
    )
 
 
# -------------------------------- tests ---------------------------------
 
def test_read_is_allowed_with_minimum_scope() -> None:
    gateway = build_gateway()
    principal = Principal("reader", "tenant-a", frozenset({"tickets:read"}))
    request = ActionRequest(
        "read_ticket",
        {"ticket_id": LabeledValue("T-1")},
        "tenant-a",
        "task-1",
    )
    result = gateway.execute(principal, request)
    assert result["status"] == "open"
 
 
def test_tool_not_allowlisted_is_denied() -> None:
    gateway = build_gateway()
    gateway.policy.allowed_tools = frozenset({"read_ticket"})
    request = ActionRequest(
        "update_ticket",
        {"ticket_id": LabeledValue("T-1"), "status": LabeledValue("closed")},
        "tenant-a",
        "task-2",
    )
    decision = gateway.authorize(principal_a(), request)
    assert decision.reason == "tool_not_allowlisted"
 
 
def test_delegation_cannot_elevate_privilege() -> None:
    gateway = build_gateway()
    principal = Principal("reader", "tenant-a", frozenset({"tickets:read"}))
    now = datetime(2026, 9, 28, 12, 0, tzinfo=timezone.utc)
    delegation = Delegation(frozenset({"tickets:read", "tickets:write"}), now + timedelta(hours=1))
    request = ActionRequest(
        "update_ticket",
        {"ticket_id": LabeledValue("T-2"), "status": LabeledValue("closed")},
        "tenant-a",
        "task-3",
    )
    decision = gateway.authorize(principal, request, delegation=delegation, now=now)
    assert decision.reason == "insufficient_scope"
    assert decision.effective_scopes == frozenset({"tickets:read"})
 
 
def test_expired_delegation_fails_closed() -> None:
    gateway = build_gateway()
    now = datetime(2026, 9, 28, 12, 0, tzinfo=timezone.utc)
    delegation = Delegation(frozenset({"tickets:read"}), now - timedelta(seconds=1))
    request = ActionRequest(
        "read_ticket",
        {"ticket_id": LabeledValue("T-3")},
        "tenant-a",
        "task-4",
    )
    decision = gateway.authorize(principal_a(), request, delegation=delegation, now=now)
    assert decision.reason == "insufficient_scope"
    assert decision.effective_scopes == frozenset()
 
 
def test_tenant_boundary_is_enforced() -> None:
    gateway = build_gateway()
    request = ActionRequest(
        "read_ticket",
        {"ticket_id": LabeledValue("T-4")},
        "tenant-b",
        "task-5",
    )
    decision = gateway.authorize(principal_a(), request)
    assert decision.reason == "tenant_boundary_violation"
 
 
def test_untrusted_data_cannot_control_high_impact_action() -> None:
    gateway = build_gateway()
    request = ActionRequest(
        "update_ticket",
        {
            "ticket_id": LabeledValue("T-5"),
            "status": LabeledValue("closed", Trust.UNTRUSTED, "email-body"),
        },
        "tenant-a",
        "task-6",
    )
    decision = gateway.authorize(principal_a(), request)
    assert decision.reason == "untrusted_data_controls_high_impact_action"
 
 
def test_secret_egress_is_blocked() -> None:
    gateway = build_gateway()
    request = ActionRequest(
        "send_webhook",
        {
            "destination": LabeledValue("https://partner.example/hook"),
            "payload": LabeledValue("api-key-123", Trust.SECRET, "vault"),
        },
        "tenant-a",
        "task-7",
    )
    decision = gateway.authorize(principal_a(), request)
    assert decision.reason == "secret_egress_blocked"
 
 
def test_high_impact_action_requires_approval() -> None:
    gateway = build_gateway()
    request = ActionRequest(
        "update_ticket",
        {"ticket_id": LabeledValue("T-8"), "status": LabeledValue("closed")},
        "tenant-a",
        "task-8",
    )
    decision = gateway.authorize(principal_a(), request)
    assert decision.kind == DecisionKind.APPROVAL_REQUIRED
 
 
def test_approval_is_bound_to_exact_action() -> None:
    gateway = build_gateway()
    now = datetime(2026, 9, 28, 12, 0, tzinfo=timezone.utc)
    original = ActionRequest(
        "update_ticket",
        {"ticket_id": LabeledValue("T-9"), "status": LabeledValue("resolved")},
        "tenant-a",
        "task-9",
    )
    approval = approved(original, now)
    modified = ActionRequest(
        "update_ticket",
        {"ticket_id": LabeledValue("T-9"), "status": LabeledValue("deleted")},
        "tenant-a",
        "task-9",
    )
    decision = gateway.authorize(principal_a(), modified, approval=approval, now=now)
    assert decision.kind == DecisionKind.APPROVAL_REQUIRED
 
 
def test_expired_approval_is_rejected() -> None:
    gateway = build_gateway()
    now = datetime(2026, 9, 28, 12, 0, tzinfo=timezone.utc)
    request = ActionRequest(
        "update_ticket",
        {"ticket_id": LabeledValue("T-10"), "status": LabeledValue("resolved")},
        "tenant-a",
        "task-10",
    )
    approval = Approval(action_digest(request), "reviewer", now - timedelta(seconds=1))
    decision = gateway.authorize(principal_a(), request, approval=approval, now=now)
    assert decision.kind == DecisionKind.APPROVAL_REQUIRED
 
 
def test_untrusted_remote_component_is_denied() -> None:
    gateway = build_gateway()
    request = ActionRequest(
        "read_ticket",
        {"ticket_id": LabeledValue("T-11")},
        "tenant-a",
        "task-11",
        remote_component="mcp://unknown.example",
    )
    decision = gateway.authorize(principal_a(), request)
    assert decision.reason == "untrusted_remote_component"
 
 
def test_successful_write_is_audited_after_bound_approval() -> None:
    gateway = build_gateway()
    now = datetime(2026, 9, 28, 12, 0, tzinfo=timezone.utc)
    request = ActionRequest(
        "update_ticket",
        {"ticket_id": LabeledValue("T-12"), "status": LabeledValue("resolved")},
        "tenant-a",
        "task-12",
    )
    result = gateway.execute(principal_a(), request, approval=approved(request, now), now=now)
    assert result["status"] == "resolved"
    events = gateway.audit_log.events_for_tenant("tenant-a")
    assert [event.event_type for event in events] == ["security_decision", "tool_executed"]
    assert events[0].decision == "allow"
 
 
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
