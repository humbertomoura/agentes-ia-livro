"""Testes do Cap. 24 (versão técnica), extraídos do livro."""
from tecnico.cap24_tool_runtime.runtime import *  # noqa: F401,F403
def test_approval_and_idempotency():
    INCIDENTS.clear(); DEDUP.clear()
    approvals = ApprovalStore()
    args = {"service": "payments", "severity": "high", "summary": "High error rate"}
    run_id, now = "run-test", 1_800_000_000.0

    blocked = execute_tool("create_incident", args, run_id=run_id, call_id="c2",
                           approvals=approvals, now=now)
    assert blocked["result"]["error"]["code"] == "APPROVAL_REQUIRED"

    approvals.approve(run_id, "c2")
    first = execute_tool("create_incident", args, run_id=run_id, call_id="c2",
                         approvals=approvals, now=now)
    approvals.approve(run_id, "c3")
    second = execute_tool("create_incident", args, run_id=run_id, call_id="c3",
                          approvals=approvals, now=now)

    assert first["result"]["value"]["deduplicated"] is False
    assert second["result"]["value"]["deduplicated"] is True
    assert first["result"]["value"]["incident_id"] == second["result"]["value"]["incident_id"]
