"""Código do Capítulo 78 — Implementando um runtime durável sem framework.

Extraído da versão técnica v26 do livro "Agentes de Inteligência Artificial".
Mantenha este arquivo idêntico à listagem publicada no manuscrito.
"""
from __future__ import annotations

from dataclasses import dataclass
import json
import sqlite3
import uuid

RUNNABLE = {"READY", "RUNNING"}
TERMINAL = {"SUCCESS", "FAILURE", "LIMIT_REACHED", "CANCELLED"}


class ManualClock:
    def __init__(self, now: float = 1000.0):
        self.now = now

    def time(self) -> float:
        return self.now

    def advance(self, seconds: float) -> None:
        self.now += seconds


class EffectStore:
    """Models an external service that supports idempotency keys."""
    def __init__(self):
        self.results: dict[str, dict] = {}
        self.physical_calls = 0

    def publish_once(self, key: str, report_id: str) -> dict:
        if key in self.results:
            return {**self.results[key], "deduplicated": True}
        self.physical_calls += 1
        result = {"publication_id": f"PUB-{self.physical_calls:04d}",
                  "report_id": report_id}
        self.results[key] = result
        return {**result, "deduplicated": False}

class SQLiteRuntimeStore:
    def __init__(self, path: str = ":memory:"):
        self.db = sqlite3.connect(path)
        self.db.row_factory = sqlite3.Row
        self.db.execute("PRAGMA foreign_keys = ON")
        self.db.executescript(
            """
            CREATE TABLE IF NOT EXISTS runs (
                run_id TEXT PRIMARY KEY,
                tenant_id TEXT NOT NULL,
                status TEXT NOT NULL,
                state_json TEXT NOT NULL,
                max_steps INTEGER NOT NULL,
                cancel_requested INTEGER NOT NULL DEFAULT 0,
                updated_at REAL NOT NULL
            );
            CREATE TABLE IF NOT EXISTS jobs (
                job_id TEXT PRIMARY KEY,
                run_id TEXT NOT NULL,
                tenant_id TEXT NOT NULL,
                kind TEXT NOT NULL,
                state TEXT NOT NULL,
                available_at REAL NOT NULL,
                leased_by TEXT,
                lease_until REAL,
                attempts INTEGER NOT NULL DEFAULT 0,
                dedupe_key TEXT NOT NULL UNIQUE,
                FOREIGN KEY(run_id) REFERENCES runs(run_id)
            );
            CREATE TABLE IF NOT EXISTS events (
                seq INTEGER PRIMARY KEY AUTOINCREMENT,
                run_id TEXT NOT NULL,
                event_type TEXT NOT NULL,
                payload_json TEXT NOT NULL,
                created_at REAL NOT NULL
            );
            """
        )
        self.db.commit()

    def create_run(self, run_id: str, tenant_id: str, state: dict,
                   max_steps: int, now: float) -> None:
        self.db.execute(
            "INSERT INTO runs VALUES (?, ?, 'READY', ?, ?, 0, ?)",
            (run_id, tenant_id, json.dumps(state), max_steps, now),
        )
        self.db.commit()

    def load_run(self, run_id: str) -> dict:
        row = self.db.execute(
            "SELECT * FROM runs WHERE run_id=?", (run_id,)
        ).fetchone()
        if row is None:
            raise KeyError(run_id)
        return {**dict(row), "state": json.loads(row["state_json"])}

    def save_run(self, run_id: str, status: str, state: dict, now: float) -> None:
        self.db.execute(
            "UPDATE runs SET status=?, state_json=?, updated_at=? WHERE run_id=?",
            (status, json.dumps(state), now, run_id),
        )
        self.db.commit()

    def request_cancel(self, run_id: str, now: float) -> None:
        self.db.execute(
            "UPDATE runs SET cancel_requested=1, updated_at=? WHERE run_id=?",
            (now, run_id),
        )
        self.db.commit()

    def enqueue(self, run_id: str, tenant_id: str, kind: str,
                dedupe_key: str, now: float, delay: float = 0) -> None:
        self.db.execute(
            """INSERT OR IGNORE INTO jobs
               (job_id, run_id, tenant_id, kind, state, available_at,
                leased_by, lease_until, attempts, dedupe_key)
               VALUES (?, ?, ?, ?, 'AVAILABLE', ?, NULL, NULL, 0, ?)""",
            (str(uuid.uuid4()), run_id, tenant_id, kind, now + delay, dedupe_key),
        )
        self.db.commit()

    def claim(self, worker_id: str, tenant_id: str, now: float,
              lease_seconds: float = 30) -> dict | None:
        self.db.execute("BEGIN IMMEDIATE")
        row = self.db.execute(
            """SELECT j.* FROM jobs j
               JOIN runs r ON r.run_id=j.run_id
               WHERE j.tenant_id=? AND j.state='AVAILABLE'
                 AND j.available_at<=?
                 AND r.status IN ('READY','RUNNING')
                 AND r.cancel_requested=0
               ORDER BY j.available_at, j.rowid LIMIT 1""",
            (tenant_id, now),
        ).fetchone()
        if row is None:
            self.db.commit()
            return None
        self.db.execute(
            """UPDATE jobs SET state='LEASED', leased_by=?, lease_until=?,
               attempts=attempts+1 WHERE job_id=?""",
            (worker_id, now + lease_seconds, row["job_id"]),
        )
        self.db.commit()
        return dict(self.db.execute(
            "SELECT * FROM jobs WHERE job_id=?", (row["job_id"],)
        ).fetchone())

    def complete_job(self, job_id: str, worker_id: str) -> None:
        cur = self.db.execute(
            """UPDATE jobs SET state='DONE', leased_by=NULL, lease_until=NULL
               WHERE job_id=? AND state='LEASED' AND leased_by=?""",
            (job_id, worker_id),
        )
        if cur.rowcount != 1:
            raise RuntimeError("worker does not own this lease")
        self.db.commit()

    def reap_expired(self, now: float) -> int:
        cur = self.db.execute(
            """UPDATE jobs SET state='AVAILABLE', leased_by=NULL, lease_until=NULL
               WHERE state='LEASED' AND lease_until<?""",
            (now,),
        )
        self.db.commit()
        return cur.rowcount

    def event(self, run_id: str, event_type: str, payload: dict, now: float) -> None:
        self.db.execute(
            "INSERT INTO events(run_id,event_type,payload_json,created_at) VALUES (?,?,?,?)",
            (run_id, event_type, json.dumps(payload), now),
        )
        self.db.commit()

    def events(self, run_id: str) -> list[dict]:
        rows = self.db.execute(
            "SELECT * FROM events WHERE run_id=? ORDER BY seq", (run_id,)
        ).fetchall()
        return [{**dict(r), "payload": json.loads(r["payload_json"])} for r in rows]

@dataclass
class AgentRuntime:
    store: SQLiteRuntimeStore
    effects: EffectStore
    clock: ManualClock

    def start(self, tenant_id: str, report_id: str, risk: str,
              max_steps: int = 6, loop: bool = False) -> str:
        run_id = str(uuid.uuid4())
        state = {"report_id": report_id, "risk": risk, "phase": "inspect",
                 "steps": 0, "approval": None, "loop": loop}
        now = self.clock.time()
        self.store.create_run(run_id, tenant_id, state, max_steps, now)
        self.store.enqueue(run_id, tenant_id, "agent_step",
                           f"{run_id}:step:0", now)
        self.store.event(run_id, "run_created", {"tenant_id": tenant_id}, now)
        return run_id

    def cancel(self, run_id: str) -> None:
        now = self.clock.time()
        self.store.request_cancel(run_id, now)
        run = self.store.load_run(run_id)
        self.store.save_run(run_id, "CANCELLED", run["state"], now)
        self.store.event(run_id, "run_cancelled", {}, now)

    def resume(self, run_id: str, approved: bool) -> dict:
        run = self.store.load_run(run_id)
        if run["status"] != "PAUSED":
            raise RuntimeError("run is not paused")
        state = run["state"]
        state["approval"] = bool(approved)
        now = self.clock.time()
        if not approved:
            self.store.save_run(run_id, "CANCELLED", state, now)
            self.store.event(run_id, "approval_rejected", {}, now)
            return self.store.load_run(run_id)
        self.store.save_run(run_id, "RUNNING", state, now)
        self.store.enqueue(run_id, run["tenant_id"], "agent_step",
                           f"{run_id}:resume:{state['steps']}", now)
        self.store.event(run_id, "run_resumed", {"approved": True}, now)
        return self.store.load_run(run_id)

    def run_one(self, worker_id: str, tenant_id: str,
                lease_seconds: float = 30,
                crash_after_effect: bool = False) -> dict | None:
        now = self.clock.time()
        job = self.store.claim(worker_id, tenant_id, now, lease_seconds)
        if job is None:
            return None
        run = self.store.load_run(job["run_id"])
        state = run["state"]

        if run["cancel_requested"]:
            self.store.save_run(run["run_id"], "CANCELLED", state, now)
            self.store.complete_job(job["job_id"], worker_id)
            return self.store.load_run(run["run_id"])

        if state["steps"] >= run["max_steps"]:
            self.store.save_run(run["run_id"], "LIMIT_REACHED", state, now)
            self.store.complete_job(job["job_id"], worker_id)
            self.store.event(run["run_id"], "step_limit", {}, now)
            return self.store.load_run(run["run_id"])

        self.store.save_run(run["run_id"], "RUNNING", state, now)
        phase = state["phase"]
        self.store.event(run["run_id"], "step_started", {"phase": phase}, now)

        if state["loop"]:
            state["steps"] += 1
            state["phase"] = "inspect"
            self.store.save_run(run["run_id"], "RUNNING", state, now)
            self.store.complete_job(job["job_id"], worker_id)
            self.store.enqueue(run["run_id"], tenant_id, "agent_step",
                               f"{run['run_id']}:loop:{state['steps']}", now)
            return self.store.load_run(run["run_id"])

        if phase == "inspect":
            state["inspection"] = "ready"
            state["phase"] = "decide"
        elif phase == "decide":
            if state["risk"] == "high" and state["approval"] is None:
                state["steps"] += 1
                self.store.save_run(run["run_id"], "PAUSED", state, now)
                self.store.complete_job(job["job_id"], worker_id)
                self.store.event(run["run_id"], "approval_required", {}, now)
                return self.store.load_run(run["run_id"])
            state["phase"] = "publish"
        elif phase == "publish":
            result = self.effects.publish_once(
                f"publish:{run['run_id']}", state["report_id"]
            )
            if crash_after_effect:
                raise RuntimeError("simulated worker crash after external effect")
            state["publication"] = result
            state["phase"] = "done"
        else:
            self.store.save_run(run["run_id"], "FAILURE", state, now)
            self.store.complete_job(job["job_id"], worker_id)
            return self.store.load_run(run["run_id"])

        state["steps"] += 1
        terminal = state["phase"] == "done"
        self.store.save_run(run["run_id"], "SUCCESS" if terminal else "RUNNING", state, now)
        self.store.complete_job(job["job_id"], worker_id)
        self.store.event(run["run_id"], "step_completed", {"phase": phase}, now)
        if not terminal:
            self.store.enqueue(run["run_id"], tenant_id, "agent_step",
                               f"{run['run_id']}:step:{state['steps']}", now)
        return self.store.load_run(run["run_id"])

def drive(runtime: AgentRuntime, run_id: str, worker: str, tenant: str) -> dict:
    while True:
        run = runtime.store.load_run(run_id)
        if run["status"] in TERMINAL or run["status"] == "PAUSED":
            return run
        if runtime.run_one(worker, tenant) is None:
            return runtime.store.load_run(run_id)


def build_runtime(path=":memory:"):
    return AgentRuntime(SQLiteRuntimeStore(path), EffectStore(), ManualClock())

def test_claim_is_exclusive():
    rt = build_runtime()
    run_id = rt.start("acme", "R-1", "low")
    first = rt.store.claim("w1", "acme", rt.clock.time(), 30)
    second = rt.store.claim("w2", "acme", rt.clock.time(), 30)
    assert first is not None and first["run_id"] == run_id
    assert second is None


def test_tenant_isolation():
    rt = build_runtime()
    rt.start("other", "R-X", "low")
    assert rt.store.claim("w1", "acme", rt.clock.time(), 30) is None


def test_pause_and_resume():
    rt = build_runtime()
    run_id = rt.start("acme", "R-2", "high")
    paused = drive(rt, run_id, "w1", "acme")
    assert paused["status"] == "PAUSED"
    rt.resume(run_id, True)
    done = drive(rt, run_id, "w2", "acme")
    assert done["status"] == "SUCCESS"
    assert done["state"]["publication"]["publication_id"] == "PUB-0001"


def test_rejection_cancels():
    rt = build_runtime()
    run_id = rt.start("acme", "R-3", "high")
    drive(rt, run_id, "w1", "acme")
    rejected = rt.resume(run_id, False)
    assert rejected["status"] == "CANCELLED"


def test_expired_lease_is_requeued():
    rt = build_runtime()
    run_id = rt.start("acme", "R-4", "low")
    job = rt.store.claim("dead-worker", "acme", rt.clock.time(), 5)
    assert job and job["run_id"] == run_id
    rt.clock.advance(6)
    assert rt.store.reap_expired(rt.clock.time()) == 1
    reclaimed = rt.store.claim("w2", "acme", rt.clock.time(), 5)
    assert reclaimed and reclaimed["job_id"] == job["job_id"]


def test_effect_is_idempotent_across_worker_crash():
    rt = build_runtime()
    run_id = rt.start("acme", "R-5", "low")
    rt.run_one("w1", "acme")  # inspect
    rt.run_one("w1", "acme")  # decide
    try:
        rt.run_one("w1", "acme", lease_seconds=5, crash_after_effect=True)
    except RuntimeError:
        pass
    assert rt.effects.physical_calls == 1
    rt.clock.advance(6)
    rt.store.reap_expired(rt.clock.time())
    done = rt.run_one("w2", "acme")
    assert done["status"] == "SUCCESS"
    assert rt.effects.physical_calls == 1
    assert done["state"]["publication"]["deduplicated"] is True


def test_cancelled_run_is_not_dispatched():
    rt = build_runtime()
    run_id = rt.start("acme", "R-6", "low")
    rt.cancel(run_id)
    assert rt.store.claim("w1", "acme", rt.clock.time(), 30) is None
    assert rt.store.load_run(run_id)["status"] == "CANCELLED"


def test_step_limit_terminates_loop():
    rt = build_runtime()
    run_id = rt.start("acme", "R-7", "low", max_steps=3, loop=True)
    result = drive(rt, run_id, "w1", "acme")
    assert result["status"] == "LIMIT_REACHED"
    assert result["state"]["steps"] == 3


def test_checkpoint_survives_process_reopen(tmp_path=None):
    import pathlib, tempfile
    base = pathlib.Path(tmp_path or tempfile.mkdtemp())
    db_path = str(base / "runtime_test.sqlite")
    rt1 = build_runtime(db_path)
    run_id = rt1.start("acme", "R-8", "low")
    rt1.run_one("w1", "acme")
    assert rt1.store.load_run(run_id)["state"]["phase"] == "decide"
    rt1.store.db.close()
    rt2 = AgentRuntime(SQLiteRuntimeStore(db_path), rt1.effects, rt1.clock)
    done = drive(rt2, run_id, "w2", "acme")
    assert done["status"] == "SUCCESS"


if __name__ == "__main__":
    tests = [
        test_claim_is_exclusive,
        test_tenant_isolation,
        test_pause_and_resume,
        test_rejection_cancels,
        test_expired_lease_is_requeued,
        test_effect_is_idempotent_across_worker_crash,
        test_cancelled_run_is_not_dispatched,
        test_step_limit_terminates_loop,
        test_checkpoint_survives_process_reopen,
    ]
    for test in tests:
        test()
        print(f"PASS {test.__name__}")
