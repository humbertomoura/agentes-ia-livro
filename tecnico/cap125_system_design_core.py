"""Código do Capítulo 125 — Implementando um núcleo de System Design sem framework agêntico.

Extraído da versão técnica v26 do livro "Agentes de Inteligência Artificial".
Mantenha este arquivo idêntico à listagem publicada no manuscrito.
"""
from __future__ import annotations

 
from dataclasses import dataclass, field
from enum import Enum
import heapq
import itertools
import uuid
 
 
class WorkloadClass(str, Enum):
    INTERACTIVE = "interactive"
    BACKGROUND = "background"
 
 
class RunStatus(str, Enum):
    QUEUED = "queued"
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    REJECTED = "rejected"
 
 
@dataclass(frozen=True)
class ModelProfile:
    name: str
    max_complexity: int
    cost_per_step: float
 
 
@dataclass(frozen=True)
class RunRequest:
    tenant_id: str
    idempotency_key: str
    capability: str
    workload: WorkloadClass
    complexity: int
    estimated_steps: int
    max_cost_usd: float
    preferred_region: str
    resumable: bool = True
    replicated_state: bool = True
 
 
@dataclass
class RunRecord:
    run_id: str
    tenant_id: str
    request: RunRequest
    status: RunStatus
    model: str | None = None
    region: str | None = None
    estimated_cost_usd: float = 0.0
    actual_cost_usd: float = 0.0
    rejection_reason: str | None = None
 
 
@dataclass(frozen=True)
class PlatformPolicy:
    allowed_capabilities: frozenset[str]
    max_queue_depth: int = 100
    max_running_per_tenant: int = 2
 
 
class ModelRouter:
    def __init__(self, profiles: list[ModelProfile]):
        self._profiles = sorted(profiles, key=lambda p: p.cost_per_step)
 
    def choose(self, request: RunRequest) -> tuple[ModelProfile, float] | None:
        for profile in self._profiles:
            if request.complexity <= profile.max_complexity:
                estimated = profile.cost_per_step * request.estimated_steps
                if estimated <= request.max_cost_usd:
                    return profile, estimated
        return None
 
 
class RegionRouter:
    def __init__(self, regions: list[str]):
        self._regions = tuple(regions)
        self._healthy = {region: True for region in regions}
 
    def set_health(self, region: str, healthy: bool) -> None:
        self._healthy[region] = healthy
 
    def choose(self, request: RunRequest) -> str | None:
        if self._healthy.get(request.preferred_region, False):
            return request.preferred_region
        if not (request.resumable and request.replicated_state):
            return None
        return next((r for r in self._regions if self._healthy.get(r, False)), None)
 
 
class AgentPlatform:
    """Small control-plane core for illustrating system-design invariants."""
 
    def __init__(
        self,
        *,
        policy: PlatformPolicy,
        model_router: ModelRouter,
        region_router: RegionRouter,
    ) -> None:
        self.policy = policy
        self.model_router = model_router
        self.region_router = region_router
        self._records: dict[str, RunRecord] = {}
        self._idempotency: dict[tuple[str, str], str] = {}
        self._queue: list[tuple[int, int, str]] = []
        self._seq = itertools.count()
        self._running_by_tenant: dict[str, int] = {}
        self.events: list[dict[str, object]] = []
 
    def submit(self, request: RunRequest) -> RunRecord:
        idem = (request.tenant_id, request.idempotency_key)
        if idem in self._idempotency:
            return self._records[self._idempotency[idem]]
 
        if request.capability not in self.policy.allowed_capabilities:
            return self._reject(request, "capability_not_allowed")
        if len(self._queue) >= self.policy.max_queue_depth:
            return self._reject(request, "queue_overloaded")
 
        routed = self.model_router.choose(request)
        if routed is None:
            return self._reject(request, "budget_or_complexity_unsatisfied")
        model, estimated_cost = routed
 
        region = self.region_router.choose(request)
        if region is None:
            return self._reject(request, "region_unavailable_without_safe_failover")
 
        run_id = f"run_{uuid.uuid4().hex[:12]}"
        record = RunRecord(
            run_id=run_id,
            tenant_id=request.tenant_id,
            request=request,
            status=RunStatus.QUEUED,
            model=model.name,
            region=region,
            estimated_cost_usd=estimated_cost,
        )
        self._records[run_id] = record
        self._idempotency[idem] = run_id
        priority = 0 if request.workload is WorkloadClass.INTERACTIVE else 10
        heapq.heappush(self._queue, (priority, next(self._seq), run_id))
        self._event("run_accepted", record)
        return record
 
    def claim_next(self) -> RunRecord | None:
        deferred: list[tuple[int, int, str]] = []
        claimed: RunRecord | None = None
        while self._queue:
            item = heapq.heappop(self._queue)
            record = self._records[item[2]]
            running = self._running_by_tenant.get(record.tenant_id, 0)
            if running >= self.policy.max_running_per_tenant:
                deferred.append(item)
                continue
            record.status = RunStatus.RUNNING
            self._running_by_tenant[record.tenant_id] = running + 1
            self._event("run_started", record)
            claimed = record
            break
        for item in deferred:
            heapq.heappush(self._queue, item)
        return claimed
 
    def complete(self, run_id: str, *, actual_cost_usd: float) -> RunRecord:
        record = self._records[run_id]
        if record.status is not RunStatus.RUNNING:
            raise ValueError("run must be RUNNING")
        record.status = RunStatus.SUCCEEDED
        record.actual_cost_usd = actual_cost_usd
        self._running_by_tenant[record.tenant_id] -= 1
        self._event("run_succeeded", record, actual_cost_usd=actual_cost_usd)
        return record
 
    def get(self, tenant_id: str, run_id: str) -> RunRecord:
        record = self._records[run_id]
        if record.tenant_id != tenant_id:
            raise PermissionError("tenant boundary violation")
        return record
 
    def queue_depth(self) -> int:
        return len(self._queue)
 
    def _reject(self, request: RunRequest, reason: str) -> RunRecord:
        run_id = f"rejected_{uuid.uuid4().hex[:12]}"
        record = RunRecord(
            run_id=run_id,
            tenant_id=request.tenant_id,
            request=request,
            status=RunStatus.REJECTED,
            rejection_reason=reason,
        )
        self._records[run_id] = record
        self._event("run_rejected", record, reason=reason)
        return record
 
    def _event(self, event_type: str, record: RunRecord, **extra: object) -> None:
        self.events.append(
            {
                "event_type": event_type,
                "run_id": record.run_id,
                "tenant_id": record.tenant_id,
                "status": record.status.value,
                **extra,
            }
        )
 
 
def build_platform(*, queue_depth: int = 100, per_tenant: int = 2) -> AgentPlatform:
    models = [
        ModelProfile("economy", max_complexity=2, cost_per_step=0.01),
        ModelProfile("standard", max_complexity=5, cost_per_step=0.03),
        ModelProfile("reasoning", max_complexity=10, cost_per_step=0.08),
    ]
    return AgentPlatform(
        policy=PlatformPolicy(
            allowed_capabilities=frozenset({"research", "code_review", "data_analysis"}),
            max_queue_depth=queue_depth,
            max_running_per_tenant=per_tenant,
        ),
        model_router=ModelRouter(models),
        region_router=RegionRouter(["sa-east", "us-east"]),
    )
 
 
def req(
    key: str,
    *,
    tenant: str = "tenant-a",
    capability: str = "research",
    workload: WorkloadClass = WorkloadClass.BACKGROUND,
    complexity: int = 2,
    steps: int = 3,
    budget: float = 1.0,
    region: str = "sa-east",
    resumable: bool = True,
    replicated_state: bool = True,
) -> RunRequest:
    return RunRequest(
        tenant_id=tenant,
        idempotency_key=key,
        capability=capability,
        workload=workload,
        complexity=complexity,
        estimated_steps=steps,
        max_cost_usd=budget,
        preferred_region=region,
        resumable=resumable,
        replicated_state=replicated_state,
    )
 
 
def test_idempotent_submission_returns_same_run() -> None:
    platform = build_platform()
    a = platform.submit(req("same"))
    b = platform.submit(req("same"))
    assert a.run_id == b.run_id
    assert platform.queue_depth() == 1
 
 
def test_capability_allowlist_fails_closed() -> None:
    platform = build_platform()
    result = platform.submit(req("cap", capability="delete_database"))
    assert result.status is RunStatus.REJECTED
    assert result.rejection_reason == "capability_not_allowed"
 
 
def test_model_router_selects_cheapest_sufficient_model() -> None:
    platform = build_platform()
    result = platform.submit(req("route", complexity=2, steps=4, budget=1.0))
    assert result.model == "economy"
    assert result.estimated_cost_usd == 0.04
 
 
def test_budget_can_reject_complex_workload() -> None:
    platform = build_platform()
    result = platform.submit(req("budget", complexity=9, steps=10, budget=0.50))
    assert result.status is RunStatus.REJECTED
    assert result.rejection_reason == "budget_or_complexity_unsatisfied"
 
 
def test_interactive_work_precedes_background_work() -> None:
    platform = build_platform()
    background = platform.submit(req("bg", workload=WorkloadClass.BACKGROUND))
    interactive = platform.submit(req("ui", workload=WorkloadClass.INTERACTIVE))
    claimed = platform.claim_next()
    assert claimed is not None
    assert claimed.run_id == interactive.run_id
    assert claimed.run_id != background.run_id
 
 
def test_queue_backpressure_rejects_overload() -> None:
    platform = build_platform(queue_depth=1)
    assert platform.submit(req("one")).status is RunStatus.QUEUED
    result = platform.submit(req("two"))
    assert result.status is RunStatus.REJECTED
    assert result.rejection_reason == "queue_overloaded"
 
 
def test_per_tenant_concurrency_limit_is_enforced() -> None:
    platform = build_platform(per_tenant=1)
    first = platform.submit(req("first"))
    second = platform.submit(req("second"))
    assert platform.claim_next().run_id == first.run_id
    assert platform.claim_next() is None
    platform.complete(first.run_id, actual_cost_usd=0.03)
    assert platform.claim_next().run_id == second.run_id
 
 
def test_safe_failover_requires_resumable_replicated_state() -> None:
    platform = build_platform()
    platform.region_router.set_health("sa-east", False)
    result = platform.submit(req("failover", resumable=True, replicated_state=True))
    assert result.status is RunStatus.QUEUED
    assert result.region == "us-east"
 
 
def test_nonresumable_work_fails_closed_when_home_region_is_down() -> None:
    platform = build_platform()
    platform.region_router.set_health("sa-east", False)
    result = platform.submit(req("no-failover", resumable=False, replicated_state=False))
    assert result.status is RunStatus.REJECTED
    assert result.rejection_reason == "region_unavailable_without_safe_failover"
 
 
def test_tenant_boundary_is_enforced_on_read() -> None:
    platform = build_platform()
    record = platform.submit(req("isolation", tenant="tenant-a"))
    try:
        platform.get("tenant-b", record.run_id)
        raise AssertionError("cross-tenant read should fail")
    except PermissionError:
        pass
 
 
def test_completion_records_cost_and_telemetry() -> None:
    platform = build_platform()
    record = platform.submit(req("telemetry", workload=WorkloadClass.INTERACTIVE))
    claimed = platform.claim_next()
    assert claimed is not None and claimed.run_id == record.run_id
    done = platform.complete(record.run_id, actual_cost_usd=0.07)
    assert done.status is RunStatus.SUCCEEDED
    assert done.actual_cost_usd == 0.07
    assert [e["event_type"] for e in platform.events] == [
        "run_accepted",
        "run_started",
        "run_succeeded",
    ]
 
 
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
