# --- 24.3 Domínio e ToolSpec ---
from __future__ import annotations
from concurrent.futures import ThreadPoolExecutor, TimeoutError
from dataclasses import dataclass, field
from hashlib import sha256
from typing import Any, Callable
import json, os, time, uuid

SERVICES = {"payments": "degraded", "catalog": "healthy", "identity": "healthy"}
INCIDENTS: dict[str, dict[str, Any]] = {}
DEDUP: dict[str, dict[str, Any]] = {}

@dataclass(frozen=True)
class ToolSpec:
    name: str
    description: str
    schema: dict[str, Any]
    handler: Callable[..., dict[str, Any]]
    validator: Callable[[dict[str, Any]], str | None]
    read_only: bool
    requires_approval: bool = False
    timeout_seconds: float = 5.0
    idempotency_key: Callable[[dict[str, Any], float], str] | None = None


def get_service_health(*, service: str) -> dict[str, Any]:
    return {"service": service, "status": SERVICES[service]}


def create_incident(*, service: str, severity: str, summary: str) -> dict[str, Any]:
    incident_id = f"INC-{len(INCIDENTS) + 1:04d}"
    item = {"incident_id": incident_id, "service": service,
            "severity": severity, "summary": summary, "deduplicated": False}
    INCIDENTS[incident_id] = item
    return item

# --- 24.4 Validação e idempotência pertencem ao spec ---
def validate_health(args: dict[str, Any]) -> str | None:
    return None if args.get("service") in SERVICES else "INVALID_SERVICE"


def validate_incident(args: dict[str, Any]) -> str | None:
    if args.get("service") not in SERVICES:
        return "INVALID_SERVICE"
    if args.get("severity") not in {"low", "high"}:
        return "INVALID_SEVERITY"
    if not str(args.get("summary", "")).strip():
        return "SUMMARY_REQUIRED"
    return None


def incident_key(args: dict[str, Any], now: float) -> str:
    bucket = int(now // (15 * 60))
    raw = f"{args['service']}|{args['severity']}|{bucket}"
    return sha256(raw.encode()).hexdigest()[:20]


def spec_to_tool(spec: ToolSpec) -> dict[str, Any]:
    return {"type": "function", "name": spec.name,
            "description": spec.description,
            "parameters": spec.schema, "strict": True}


REGISTRY = {
    "get_service_health": ToolSpec(
        name="get_service_health",
        description="Read the current health of one service.",
        schema={"type": "object", "properties": {"service": {
            "type": "string", "enum": list(SERVICES)}},
            "required": ["service"], "additionalProperties": False},
        handler=get_service_health, validator=validate_health, read_only=True,
    ),
    "create_incident": ToolSpec(
        name="create_incident",
        description="Create an operations incident after health has been checked.",
        schema={"type": "object", "properties": {
            "service": {"type": "string", "enum": list(SERVICES)},
            "severity": {"type": "string", "enum": ["low", "high"]},
            "summary": {"type": "string"}},
            "required": ["service", "severity", "summary"],
            "additionalProperties": False},
        handler=create_incident, validator=validate_incident, read_only=False,
        requires_approval=True, timeout_seconds=5.0, idempotency_key=incident_key,
    ),
}
TOOLS = [spec_to_tool(spec) for spec in REGISTRY.values()]

# --- 24.5 Aprovação por chamada, BLOCKED e retomada ---
class ApprovalStore:
    def __init__(self) -> None:
        self._approved: set[tuple[str, str]] = set()

    def approve(self, run_id: str, call_id: str) -> None:
        self._approved.add((run_id, call_id))

    def valid(self, run_id: str, call_id: str) -> bool:
        return (run_id, call_id) in self._approved


@dataclass
class RunState:
    run_id: str
    history: list[Any]
    step: int = 0
    status: str = "READY"
    pending_calls: list[dict[str, str]] = field(default_factory=list)
    trace: list[dict[str, Any]] = field(default_factory=list)

# --- 24.6 Executor genérico com timeout, retry de leitura e trace ---
def tool_error(code: str, detail: str) -> dict[str, Any]:
    return {"ok": False, "error": {"code": code, "detail": detail}}


def call_with_timeout(spec: ToolSpec, args: dict[str, Any]) -> dict[str, Any]:
    attempts = 2 if spec.read_only else 1
    last_error = "UNKNOWN"
    for _ in range(attempts):
        pool = ThreadPoolExecutor(max_workers=1)
        future = pool.submit(spec.handler, **args)
        try:
            value = future.result(timeout=spec.timeout_seconds)
            pool.shutdown(wait=False, cancel_futures=True)
            return {"ok": True, "value": value}
        except TimeoutError:
            last_error = "TIMEOUT"
        except Exception as exc:
            last_error = type(exc).__name__
        finally:
            pool.shutdown(wait=False, cancel_futures=True)
    return tool_error(last_error, spec.name)


def execute_tool(name: str, args: dict[str, Any], *, run_id: str, call_id: str,
                 approvals: ApprovalStore, now: float | None = None) -> dict[str, Any]:
    started = time.perf_counter()
    spec = REGISTRY.get(name)
    authorization = "not_required"
    if spec is None:
        result = tool_error("UNKNOWN_TOOL", name)
    else:
        problem = spec.validator(args)
        if problem:
            result = tool_error("VALIDATION_ERROR", problem)
        elif spec.requires_approval and not approvals.valid(run_id, call_id):
            authorization = "blocked"
            result = tool_error("APPROVAL_REQUIRED", call_id)
        else:
            if spec.requires_approval:
                authorization = "approved"
            key = spec.idempotency_key(args, now or time.time()) if spec.idempotency_key else None
            if key and key in DEDUP:
                value = dict(DEDUP[key]); value["deduplicated"] = True
                result = {"ok": True, "value": value}
            else:
                result = call_with_timeout(spec, args)
                if key and result.get("ok"):
                    DEDUP[key] = dict(result["value"])

    return {"result": result, "authorization": authorization,
            "duration_ms": round((time.perf_counter() - started) * 1000, 2)}

# --- 24.7 Loop real com GPT-6 Astra ---
def parse_args(raw: str) -> tuple[dict[str, Any] | None, dict[str, Any] | None]:
    try:
        value = json.loads(raw)
        if not isinstance(value, dict):
            raise ValueError("arguments must be an object")
        return value, None
    except Exception as exc:
        return None, tool_error("INVALID_ARGUMENTS", type(exc).__name__)


def continue_run(run: RunState, approvals: ApprovalStore, client: OpenAI,
                 model: str, max_steps: int = 8) -> RunState:
    run.status = "RUNNING"
    while run.step < max_steps:
        response = client.responses.create(model=model, input=run.history, tools=TOOLS)
        run.history += response.output
        calls = [x for x in response.output if x.type == "function_call"]
        if not calls:
            run.status = "SUCCESS"
            run.history.append({"type": "final_text", "text": response.output_text})
            return run

        for index, call in enumerate(calls):
            args, parse_error = parse_args(call.arguments)
            if parse_error:
                envelope = {"result": parse_error, "authorization": "not_evaluated",
                            "duration_ms": 0.0}
            else:
                envelope = execute_tool(call.name, args, run_id=run.run_id,
                                        call_id=call.call_id, approvals=approvals)

            run.trace.append({"step": run.step + 1, "call_id": call.call_id,
                              "tool": call.name, "args": args,
                              **envelope})
            error = envelope["result"].get("error", {})
            if error.get("code") == "APPROVAL_REQUIRED":
                run.pending_calls = [{"name": c.name, "call_id": c.call_id,
                                      "arguments": c.arguments} for c in calls[index:]]
                run.status = "BLOCKED"
                return run

            run.history.append({"type": "function_call_output",
                                "call_id": call.call_id,
                                "output": json.dumps(envelope["result"])})
        run.step += 1

    run.status = "LIMIT_REACHED"
    return run
def resume_run(run: RunState, approvals: ApprovalStore, client: OpenAI,
               model: str) -> RunState:
    if run.status != "BLOCKED" or not run.pending_calls:
        return run
    run.status = "RUNNING"
    while run.pending_calls:
        call = run.pending_calls[0]
        args, parse_error = parse_args(call["arguments"])
        envelope = ({"result": parse_error, "authorization": "not_evaluated",
                     "duration_ms": 0.0} if parse_error else
                    execute_tool(call["name"], args, run_id=run.run_id,
                                 call_id=call["call_id"], approvals=approvals))
        if envelope["result"].get("error", {}).get("code") == "APPROVAL_REQUIRED":
            run.status = "BLOCKED"
            return run
        run.history.append({"type": "function_call_output", "call_id": call["call_id"],
                            "output": json.dumps(envelope["result"])})
        run.trace.append({"step": run.step + 1, "call_id": call["call_id"],
                          "tool": call["name"], "args": args, **envelope})
        run.pending_calls.pop(0)
    run.step += 1
    return continue_run(run, approvals, client, model)
def start_agent(user_request: str) -> tuple[RunState, ApprovalStore]:
    from openai import OpenAI
    run = RunState(run_id=str(uuid.uuid4()),
                   history=[{"role": "user", "content": user_request}])
    return run, ApprovalStore()


if __name__ == "__main__":
    client = OpenAI()
    model = os.getenv("OPENAI_MODEL", "gpt-6-astra")
    run, approvals = start_agent(
        "Check payments. If degraded, request a high severity incident."
    )
    run = continue_run(run, approvals, client, model)
    if run.status == "BLOCKED":
        approvals.approve(run.run_id, run.pending_calls[0]["call_id"])
        run = resume_run(run, approvals, client, model)
    print(run.status)
    print(run.trace)
