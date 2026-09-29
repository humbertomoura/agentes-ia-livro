"""Código do Capítulo 87 — Implementando um portfólio de agentes especializados sem framework.

Extraído da versão técnica v26 do livro "Agentes de Inteligência Artificial".
Mantenha este arquivo idêntico à listagem publicada no manuscrito.
"""

from dataclasses import dataclass, field
from typing import Callable


class PolicyDenied(Exception):
    pass


class ApprovalRequired(Exception):
    pass


@dataclass(frozen=True)
class Task:
    task_id: str
    kind: str
    request: str
    tenant_id: str
    principal_scopes: frozenset[str]
    inputs: dict = field(default_factory=dict)
    approvals: frozenset[str] = frozenset()


@dataclass(frozen=True)
class Artifact:
    artifact_id: str
    kind: str
    created_by: str
    task_id: str
    content: str
    sources: tuple[str, ...] = ()


@dataclass(frozen=True)
class ToolSpec:
    name: str
    required_scopes: frozenset[str]
    handler: Callable
    approval: str | None = None


@dataclass(frozen=True)
class SpecialistSpec:
    name: str
    kinds: frozenset[str]
    max_scopes: frozenset[str]
    allowed_tools: frozenset[str]
    input_keys: frozenset[str]
    handler: Callable



class ArtifactStore:
    def __init__(self):
        self.items = []

    def add(self, kind, created_by, task_id, content, sources=()):
        artifact = Artifact(
            artifact_id=f"A{len(self.items) + 1}",
            kind=kind,
            created_by=created_by,
            task_id=task_id,
            content=content,
            sources=tuple(sources),
        )
        self.items.append(artifact)
        return artifact


class SpecialistContext:
    def __init__(self, spec, task, tools, artifacts):
        self.spec = spec
        self.task = task
        self.tools = tools
        self.artifacts = artifacts
        self.effective_scopes = task.principal_scopes & spec.max_scopes
        self.inputs = {k: v for k, v in task.inputs.items() if k in spec.input_keys}

    def call_tool(self, name, **kwargs):
        if name not in self.spec.allowed_tools:
            raise PolicyDenied(f"TOOL_NOT_ALLOWED:{name}")
        tool = self.tools[name]
        if not tool.required_scopes <= self.effective_scopes:
            raise PolicyDenied(f"MISSING_SCOPE:{name}")
        if tool.approval and tool.approval not in self.task.approvals:
            raise ApprovalRequired(tool.approval)
        return tool.handler(self.task.tenant_id, **kwargs)

    def artifact(self, kind, content, sources=()):
        return self.artifacts.add(
            kind=kind,
            created_by=self.spec.name,
            task_id=self.task.task_id,
            content=content,
            sources=sources,
        )



class SpecialistHub:
    def __init__(self, tools, specialists):
        self.tools = {tool.name: tool for tool in tools}
        self.specialists = {kind: spec for spec in specialists for kind in spec.kinds}
        self.artifacts = ArtifactStore()

    def dispatch(self, task):
        spec = self.specialists.get(task.kind)
        if spec is None:
            return {"status": "NO_SPECIALIST", "kind": task.kind}
        ctx = SpecialistContext(spec, task, self.tools, self.artifacts)
        try:
            artifact = spec.handler(task, ctx)
            return {"status": "SUCCESS", "specialist": spec.name, "artifact": artifact}
        except ApprovalRequired as exc:
            return {"status": "APPROVAL_REQUIRED", "approval": str(exc), "specialist": spec.name}
        except PolicyDenied as exc:
            return {"status": "DENIED", "reason": str(exc), "specialist": spec.name}



# ----- deterministic demo environment -----
REPOS = {
    "acme": {
        "app.py": "def total(xs):\n    return sum(xs) + 1\n",
        "tests": "test_total expects total([1, 2]) == 3",
    }
}
SOURCES = {
    "acme": [
        ("S1", "Deployment policy", "Production deploys require human approval."),
        ("S2", "Runbook", "Rollback is allowed after a failed health check."),
    ]
}
DATASETS = {
    "acme": {"revenue": [120, 80, 100]}
}
TICKETS = {
    "acme": {"INC-7": {"status": "open", "summary": "payment latency"}}
}


def read_repo_file(tenant_id, path):
    return REPOS[tenant_id][path]


def run_tests(tenant_id):
    code = REPOS[tenant_id]["app.py"]
    return {"passed": "+ 1" not in code, "summary": REPOS[tenant_id]["tests"]}


def search_sources(tenant_id, query):
    terms = set(query.lower().split())
    rows = []
    for source_id, title, text in SOURCES[tenant_id]:
        if terms & set(text.lower().replace(".", "").split()):
            rows.append({"source_id": source_id, "title": title, "text": text})
    return rows


def query_dataset(tenant_id, metric):
    values = DATASETS[tenant_id][metric]
    return {"metric": metric, "count": len(values), "sum": sum(values)}


def read_ticket(tenant_id, ticket_id):
    return dict(TICKETS[tenant_id][ticket_id])


def update_ticket(tenant_id, ticket_id, status):
    TICKETS[tenant_id][ticket_id]["status"] = status
    return dict(TICKETS[tenant_id][ticket_id])


TOOLS = [
    ToolSpec("read_repo_file", frozenset({"repo:read"}), read_repo_file),
    ToolSpec("run_tests", frozenset({"repo:execute"}), run_tests),
    ToolSpec("search_sources", frozenset({"research:read"}), search_sources),
    ToolSpec("query_dataset", frozenset({"data:read"}), query_dataset),
    ToolSpec("read_ticket", frozenset({"ops:read"}), read_ticket),
    ToolSpec("update_ticket", frozenset({"ops:write"}), update_ticket, approval="ticket_write"),
]



def coding_handler(task, ctx):
    code = ctx.call_tool("read_repo_file", path="app.py")
    tests = ctx.call_tool("run_tests")
    patch = "Remove the extra '+ 1' from total()." if not tests["passed"] else "No patch required."
    # The specialist sees only keys declared by its contract.
    visible = sorted(ctx.inputs)
    return ctx.artifact("patch_plan", f"{patch}\nvisible_inputs={visible}\ncode={code.strip()}")


def research_handler(task, ctx):
    rows = ctx.call_tool("search_sources", query=task.request)
    citations = [row["source_id"] for row in rows]
    lines = [f"[{row['source_id']}] {row['text']}" for row in rows]
    return ctx.artifact("evidence_report", "\n".join(lines), sources=citations)


def data_handler(task, ctx):
    result = ctx.call_tool("query_dataset", metric="revenue")
    return ctx.artifact("analysis", f"revenue_sum={result['sum']}; rows={result['count']}")


def ops_handler(task, ctx):
    ticket_id = ctx.inputs.get("ticket_id", "INC-7")
    ticket = ctx.call_tool("read_ticket", ticket_id=ticket_id)
    if "close" in task.request.lower():
        ticket = ctx.call_tool("update_ticket", ticket_id=ticket_id, status="closed")
    return ctx.artifact("ticket_result", f"{ticket_id}:{ticket['status']}")


SPECIALISTS = [
    SpecialistSpec(
        "coding", frozenset({"coding"}),
        frozenset({"repo:read", "repo:execute"}),
        frozenset({"read_repo_file", "run_tests"}),
        frozenset({"repo"}), coding_handler,
    ),
    SpecialistSpec(
        "research", frozenset({"research"}),
        frozenset({"research:read"}),
        frozenset({"search_sources"}),
        frozenset({"research_scope"}), research_handler,
    ),
    SpecialistSpec(
        "data", frozenset({"data"}),
        frozenset({"data:read"}),
        frozenset({"query_dataset"}),
        frozenset({"dataset"}), data_handler,
    ),
    SpecialistSpec(
        "operations", frozenset({"ops"}),
        frozenset({"ops:read", "ops:write"}),
        frozenset({"read_ticket", "update_ticket"}),
        frozenset({"ticket_id"}), ops_handler,
    ),
]



def build_hub():
    return SpecialistHub(TOOLS, SPECIALISTS)



# ----- tests -----
def test_routes_by_contract():
    hub = build_hub()
    task = Task("T1", "coding", "fix total", "acme", frozenset({"repo:read", "repo:execute"}))
    result = hub.dispatch(task)
    assert result["status"] == "SUCCESS"
    assert result["specialist"] == "coding"


def test_unknown_kind_fails_closed():
    hub = build_hub()
    task = Task("T2", "legal", "review", "acme", frozenset())
    assert hub.dispatch(task)["status"] == "NO_SPECIALIST"


def test_scope_cannot_be_elevated_by_specialist():
    hub = build_hub()
    task = Task("T3", "ops", "close ticket", "acme", frozenset({"ops:read"}),
                inputs={"ticket_id": "INC-7"}, approvals=frozenset({"ticket_write"}))
    result = hub.dispatch(task)
    assert result["status"] == "DENIED"
    assert "MISSING_SCOPE" in result["reason"]


def test_approval_gate_for_write():
    TICKETS["acme"]["INC-7"]["status"] = "open"
    hub = build_hub()
    task = Task("T4", "ops", "close ticket", "acme",
                frozenset({"ops:read", "ops:write"}), inputs={"ticket_id": "INC-7"})
    result = hub.dispatch(task)
    assert result["status"] == "APPROVAL_REQUIRED"
    assert TICKETS["acme"]["INC-7"]["status"] == "open"


def test_approved_write_changes_state():
    TICKETS["acme"]["INC-7"]["status"] = "open"
    hub = build_hub()
    task = Task("T5", "ops", "close ticket", "acme",
                frozenset({"ops:read", "ops:write"}), inputs={"ticket_id": "INC-7"},
                approvals=frozenset({"ticket_write"}))
    result = hub.dispatch(task)
    assert result["status"] == "SUCCESS"
    assert TICKETS["acme"]["INC-7"]["status"] == "closed"


def test_context_is_filtered():
    hub = build_hub()
    task = Task("T6", "coding", "fix total", "acme",
                frozenset({"repo:read", "repo:execute"}),
                inputs={"repo": "demo", "secret": "do-not-leak"})
    artifact = hub.dispatch(task)["artifact"]
    assert "secret" not in artifact.content
    assert "do-not-leak" not in artifact.content


def test_research_preserves_source_ids():
    hub = build_hub()
    task = Task("T7", "research", "production approval", "acme",
                frozenset({"research:read"}))
    artifact = hub.dispatch(task)["artifact"]
    assert artifact.sources == ("S1",)
    assert "[S1]" in artifact.content


def test_data_specialist_is_read_only():
    hub = build_hub()
    spec = hub.specialists["data"]
    assert "update_ticket" not in spec.allowed_tools
    task = Task("T8", "data", "sum revenue", "acme", frozenset({"data:read", "ops:write"}))
    result = hub.dispatch(task)
    assert result["status"] == "SUCCESS"
    assert result["artifact"].content == "revenue_sum=300; rows=3"


def test_artifact_provenance():
    hub = build_hub()
    task = Task("T9", "research", "rollback failed health", "acme",
                frozenset({"research:read"}))
    artifact = hub.dispatch(task)["artifact"]
    assert artifact.created_by == "research"
    assert artifact.task_id == "T9"
    assert artifact.artifact_id == "A1"



if __name__ == "__main__":
    tests = [v for k, v in globals().items() if k.startswith("test_") and callable(v)]
    for test in sorted(tests, key=lambda f: f.__name__):
        test()
        print("PASS", test.__name__)
    print(f"{len(tests)} tests passed")
