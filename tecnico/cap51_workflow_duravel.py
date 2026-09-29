"""Código do Capítulo 51 — Implementando um workflow durável sem framework.

Extraído da versão técnica v26 do livro "Agentes de Inteligência Artificial".
Mantenha este arquivo idêntico à listagem publicada no manuscrito.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Callable, Any
import json, sqlite3, time, uuid
 
END = "__END__"
 
class RunStatus(str, Enum):
    READY = "READY"
    RUNNING = "RUNNING"
    PAUSED = "PAUSED"
    BLOCKED = "BLOCKED"
    SUCCESS = "SUCCESS"
    FAILURE = "FAILURE"
    LIMIT_REACHED = "LIMIT_REACHED"
    CANCELLED = "CANCELLED"
 
class TransientError(RuntimeError):
    pass
 
@dataclass
class NodeResult:
    update: dict = field(default_factory=dict)
    route: str = "next"
    pause: dict | None = None
    terminal_status: RunStatus | None = None
 
@dataclass
class NodeSpec:
    name: str
    handler: Callable[[dict, "ExecutionContext"], NodeResult]
    max_attempts: int = 1
 
class WorkflowDefinition:
    def __init__(self, name, version, start):
        self.name, self.version, self.start = name, version, start
        self.nodes: dict[str, NodeSpec] = {}
        self.edges: dict[tuple[str, str], str] = {}
 
    def add_node(self, spec):
        if spec.name in self.nodes:
            raise ValueError(f"duplicate node: {spec.name}")
        self.nodes[spec.name] = spec
        return self
 
    def add_edge(self, source, target, route="next"):
        self.edges[(source, route)] = target
        return self
 
    def resolve(self, source, route):
        key = (source, route)
        if key not in self.edges:
            raise ValueError(f"missing edge for {source!r}/{route!r}")
        return self.edges[key]
 
    def validate(self):
        if self.start not in self.nodes:
            raise ValueError("start node does not exist")
        for (src, _), dst in self.edges.items():
            if src not in self.nodes:
                raise ValueError(f"unknown source node: {src}")
            if dst != END and dst not in self.nodes:
                raise ValueError(f"unknown target node: {dst}")

class SQLiteStore:
    def __init__(self, path=":memory:"):
        self.db = sqlite3.connect(path)
        self.db.row_factory = sqlite3.Row
        self.db.executescript("""
        CREATE TABLE IF NOT EXISTS runs(
          run_id TEXT PRIMARY KEY, workflow TEXT, workflow_version TEXT,
          status TEXT, current_node TEXT, state_json TEXT,
          steps INTEGER, updated_at REAL);
        CREATE TABLE IF NOT EXISTS events(
          seq INTEGER PRIMARY KEY AUTOINCREMENT, run_id TEXT,
          event_type TEXT, node TEXT, payload_json TEXT, created_at REAL);
        """)
 
    def create(self, run_id, wf, state):
        self.db.execute(
            "INSERT INTO runs VALUES(?,?,?,?,?,?,?,?)",
            (run_id, wf.name, wf.version, RunStatus.READY.value,
             wf.start, json.dumps(state), 0, time.time()))
        self.db.commit()
 
    def load(self, run_id):
        row = self.db.execute(
            "SELECT * FROM runs WHERE run_id=?", (run_id,)).fetchone()
        if row is None:
            raise KeyError(run_id)
        return dict(row)
 
    def checkpoint(self, run_id, status, node, state, steps):
        self.db.execute(
            "UPDATE runs SET status=?, current_node=?, state_json=?, "
            "steps=?, updated_at=? WHERE run_id=?",
            (status.value, node, json.dumps(state), steps, time.time(), run_id))
        self.db.commit()
 
    def event(self, run_id, kind, node, payload=None):
        self.db.execute(
            "INSERT INTO events(run_id,event_type,node,payload_json,created_at) "
            "VALUES(?,?,?,?,?)",
            (run_id, kind, node, json.dumps(payload or {}), time.time()))
        self.db.commit()
 
    def events(self, run_id):
        return [dict(r) for r in self.db.execute(
            "SELECT * FROM events WHERE run_id=? ORDER BY seq", (run_id,))]

class ExecutionContext:
    def __init__(self, run_id, store, services):
        self.run_id, self.store, self.services = run_id, store, services
 
class FakePublisher:
    def __init__(self):
        self.responses = {}
        self.physical_calls = 0
 
    def publish(self, report_id, idempotency_key):
        if idempotency_key in self.responses:
            return {**self.responses[idempotency_key], "deduplicated": True}
        self.physical_calls += 1
        result = {"publication_id": f"PUB-{self.physical_calls:04d}",
                  "report_id": report_id, "deduplicated": False}
        self.responses[idempotency_key] = result
        return result

class WorkflowEngine:
    TERMINAL = {RunStatus.SUCCESS.value, RunStatus.FAILURE.value,
                RunStatus.LIMIT_REACHED.value, RunStatus.CANCELLED.value}
 
    def __init__(self, wf, store, services=None):
        wf.validate()
        self.wf, self.store = wf, store
        self.services = services or {}
 
    def start(self, state, run_id=None):
        run_id = run_id or f"run_{uuid.uuid4().hex[:10]}"
        self.store.create(run_id, self.wf, state)
        self.store.event(run_id, "run_started", self.wf.start)
        return run_id
 
    def resume(self, run_id, human_input, max_steps=50):
        row = self.store.load(run_id)
        if row["status"] != RunStatus.PAUSED.value:
            raise ValueError("run is not paused")
        state = json.loads(row["state_json"])
        state.pop("pause_request", None)
        state["human_input"] = human_input
        self.store.checkpoint(run_id, RunStatus.READY,
                              row["current_node"], state, row["steps"])
        self.store.event(run_id, "resumed", row["current_node"])
        return self.run(run_id, max_steps=max_steps)
 
    def run(self, run_id, max_steps=50):
        row = self.store.load(run_id)
        if row["status"] in self.TERMINAL:
            return self.result(run_id)
 
        state = json.loads(row["state_json"])
        node = row["current_node"]
        steps = row["steps"]
        ctx = ExecutionContext(run_id, self.store, self.services)
        self.store.checkpoint(run_id, RunStatus.RUNNING, node, state, steps)
 
        while node != END:
            if steps >= max_steps:
                self.store.checkpoint(run_id, RunStatus.LIMIT_REACHED,
                                      node, state, steps)
                self.store.event(run_id, "limit_reached", node)
                return self.result(run_id)
 
            spec = self.wf.nodes[node]
            self.store.event(run_id, "node_started", node,
                             {"step": steps + 1})
            last_error = None
            result = None
            for attempt in range(1, spec.max_attempts + 1):
                try:
                    result = spec.handler(dict(state), ctx)
                    break
                except TransientError as exc:
                    last_error = str(exc)
                    self.store.event(run_id, "node_retry", node,
                                     {"attempt": attempt, "error": last_error})
                except Exception as exc:
                    state["error"] = {"type": type(exc).__name__, "message": str(exc)}
                    self.store.checkpoint(run_id, RunStatus.FAILURE, node, state, steps)
                    self.store.event(run_id, "node_failed", node, state["error"])
                    return self.result(run_id)
            if result is None:
                state["error"] = {"type": "TransientError",
                                  "message": last_error}
                self.store.checkpoint(run_id, RunStatus.FAILURE,
                                      node, state, steps)
                self.store.event(run_id, "node_failed", node,
                                 {"error": last_error})
                return self.result(run_id)
 
            state.pop("human_input", None)  # single use: consumed by this node
            state.update(result.update)
            steps += 1
            if result.terminal_status is not None:
                self.store.checkpoint(run_id, result.terminal_status, END, state, steps)
                self.store.event(run_id, "run_finished", node,
                                 {"status": result.terminal_status.value})
                return self.result(run_id)
            if result.pause is not None:
                state["pause_request"] = result.pause
                self.store.checkpoint(run_id, RunStatus.PAUSED,
                                      node, state, steps)
                self.store.event(run_id, "pause_requested", node, result.pause)
                return self.result(run_id)
 
            next_node = self.wf.resolve(node, result.route)
            self.store.event(run_id, "transition_taken", node,
                             {"route": result.route, "target": next_node})
            self.store.event(run_id, "node_completed", node)
            node = next_node
            status = RunStatus.SUCCESS if node == END else RunStatus.RUNNING
            self.store.checkpoint(run_id, status, node, state, steps)
 
        return self.result(run_id)
 
    def result(self, run_id):
        row = self.store.load(run_id)
        return {"run_id": run_id, "status": row["status"],
                "current_node": row["current_node"],
                "steps": row["steps"], "state": json.loads(row["state_json"])}

def validate_report(state, ctx):
    if not state.get("report_id"):
        raise ValueError("report_id is required")
    return NodeResult()
 
def classify_risk(state, ctx):
    route = "high" if state.get("risk") == "high" else "low"
    return NodeResult(route=route)
 
def approval(state, ctx):
    decision = state.get("human_input")
    if decision is None:
        return NodeResult(pause={"action": "publish_report",
                                 "report_id": state["report_id"]})
    return NodeResult(update={"approved": bool(decision.get("approved"))},
                      route="approved" if decision.get("approved") else "rejected")
 
def prepare(state, ctx):
    return NodeResult(update={"prepared": True})
 
def publish(state, ctx):
    publisher = ctx.services["publisher"]
    key = f"publish:{state['report_id']}"
    result = publisher.publish(state["report_id"], idempotency_key=key)
    return NodeResult(update={"publication": result})
 
def cancelled(state, ctx):
    return NodeResult(update={"cancel_reason": "approval rejected"},
                      terminal_status=RunStatus.CANCELLED)
 
wf = WorkflowDefinition("report_publication", "1.0", start="validate")
for spec in [
    NodeSpec("validate", validate_report),
    NodeSpec("classify", classify_risk),
    NodeSpec("approval", approval),
    NodeSpec("prepare", prepare),
    NodeSpec("publish", publish),
    NodeSpec("cancelled", cancelled),
]:
    wf.add_node(spec)
 
wf.add_edge("validate", "classify")
wf.add_edge("classify", "prepare", "low")
wf.add_edge("classify", "approval", "high")
wf.add_edge("approval", "prepare", "approved")
wf.add_edge("approval", "cancelled", "rejected")
wf.add_edge("prepare", "publish")
wf.add_edge("publish", END)

def flaky_enrichment_factory():
    calls = {"n": 0}
    def handler(state, ctx):
        calls["n"] += 1
        if calls["n"] == 1:
            raise TransientError("temporary dependency failure")
        return NodeResult(update={"enriched": True})
    return handler, calls

def build_engine():
    store = SQLiteStore()
    publisher = FakePublisher()
    return WorkflowEngine(wf, store, {"publisher": publisher}), publisher
 
def test_low_risk_happy_path():
    engine, publisher = build_engine()
    run_id = engine.start({"report_id": "R-1", "risk": "low"})
    result = engine.run(run_id)
    assert result["status"] == "SUCCESS"
    assert result["state"]["publication"]["publication_id"] == "PUB-0001"
    assert publisher.physical_calls == 1
 
def test_high_risk_pauses_and_resumes():
    engine, _ = build_engine()
    run_id = engine.start({"report_id": "R-2", "risk": "high"})
    paused = engine.run(run_id)
    assert paused["status"] == "PAUSED"
    assert paused["current_node"] == "approval"
    done = engine.resume(run_id, {"approved": True})
    assert done["status"] == "SUCCESS"
    assert done["state"]["approved"] is True
 
def test_rejection_takes_cancel_branch():
    engine, _ = build_engine()
    run_id = engine.start({"report_id": "R-3", "risk": "high"})
    engine.run(run_id)
    done = engine.resume(run_id, {"approved": False})
    assert done["status"] == "CANCELLED"
    assert done["state"]["cancel_reason"] == "approval rejected"
    assert "publication" not in done["state"]
 
def test_completed_nodes_are_not_reexecuted_after_resume():
    engine, _ = build_engine()
    run_id = engine.start({"report_id": "R-4", "risk": "high"})
    engine.run(run_id)
    before = [e["event_type"] for e in engine.store.events(run_id)]
    assert before.count("node_completed") == 2  # validate + classify
    engine.resume(run_id, {"approved": True})
    after = [e["event_type"] for e in engine.store.events(run_id)]
    assert after.count("node_completed") == 5  # + approval + prepare + publish
 
def test_idempotent_publish_survives_duplicate_call():
    publisher = FakePublisher()
    first = publisher.publish("R-5", "publish:R-5")
    second = publisher.publish("R-5", "publish:R-5")
    assert first["publication_id"] == second["publication_id"]
    assert second["deduplicated"] is True
    assert publisher.physical_calls == 1
 
def test_retry_policy():
    handler, calls = flaky_enrichment_factory()
    local = WorkflowDefinition("retry_demo", "1.0", "enrich")
    local.add_node(NodeSpec("enrich", handler, max_attempts=2))
    local.add_edge("enrich", END)
    engine = WorkflowEngine(local, SQLiteStore())
    run_id = engine.start({})
    result = engine.run(run_id)
    assert result["status"] == "SUCCESS"
    assert calls["n"] == 2
 
def test_permanent_error_becomes_failure():
    engine, _ = build_engine()
    run_id = engine.start({"risk": "low"})
    result = engine.run(run_id)
    assert result["status"] == "FAILURE"
    assert result["state"]["error"]["type"] == "ValueError"
 
def test_step_limit_terminates_loop():
    def again(state, ctx):
        return NodeResult(route="again")
    local = WorkflowDefinition("loop_demo", "1.0", "loop")
    local.add_node(NodeSpec("loop", again))
    local.add_edge("loop", "loop", "again")
    engine = WorkflowEngine(local, SQLiteStore())
    run_id = engine.start({})
    result = engine.run(run_id, max_steps=3)
    assert result["status"] == "LIMIT_REACHED"
    assert result["steps"] == 3
 
def test_human_input_is_single_use():
    local = WorkflowDefinition("two_approvals", "1.0", "a1")
    local.add_node(NodeSpec("a1", approval))
    local.add_node(NodeSpec("a2", approval))
    local.add_node(NodeSpec("stop", cancelled))
    local.add_edge("a1", "a2", "approved")
    local.add_edge("a2", END, "approved")
    local.add_edge("a1", "stop", "rejected")
    local.add_edge("a2", "stop", "rejected")
    engine = WorkflowEngine(local, SQLiteStore())
    run_id = engine.start({"report_id": "R-9"})
    assert engine.run(run_id)["current_node"] == "a1"
    second = engine.resume(run_id, {"approved": True})
    # a decisão sobre a1 não pode aprovar a2
    assert second["status"] == "PAUSED"
    assert second["current_node"] == "a2"

def classify_risk_with_model(state, ctx):
    label = ctx.services["risk_classifier"].classify(state["report_text"])
    if label not in {"low", "high"}:
        return NodeResult(route="high")  # fail closed
    return NodeResult(route=label)
