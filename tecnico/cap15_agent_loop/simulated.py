"""Seção 15.4: decisor simulado (roda sem chave de API)."""
import json
import os

MAX_TURNS = 6

def inspect_service() -> dict:
    return {"http_status": 503, "error": "database authentication failed"}

def check_database() -> dict:
    return {"reachable": True, "authentication": "failed",
            "hint": "application password may be outdated"}

FUNCTIONS = {"inspect_service": inspect_service, "check_database": check_database}


def simulated_model(tool_results: dict) -> tuple[list[dict], str | None]:
    if "inspect_service" not in tool_results:
        return [{"name": "inspect_service", "arguments": {}}], None

    if "check_database" not in tool_results:
        return [{"name": "check_database", "arguments": {}}], None

    return [], (
        "The service is unavailable because database authentication failed; "
        "the application password is likely outdated."
    )


def run_simulated() -> str:
    tool_results = {}
    for _ in range(6):
        calls, final = simulated_model(tool_results)
        if not calls:
            return final
        for call in calls:
            tool_results[call["name"]] = FUNCTIONS[call["name"]](**call["arguments"])
    raise RuntimeError("Simulated agent reached the turn limit.")


if __name__ == "__main__":
    print(run_simulated())
