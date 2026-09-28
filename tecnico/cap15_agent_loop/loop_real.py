import json
import os
from openai import OpenAI

client = OpenAI()
MODEL = os.getenv("OPENAI_MODEL", "gpt-6-astra")
MAX_TURNS = 6

def inspect_service() -> dict:
    return {"http_status": 503, "error": "database authentication failed"}

def check_database() -> dict:
    return {"reachable": True, "authentication": "failed",
            "hint": "application password may be outdated"}

FUNCTIONS = {"inspect_service": inspect_service, "check_database": check_database}
EMPTY_SCHEMA = {"type": "object", "properties": {}, "additionalProperties": False}
TOOLS = [
    {"type": "function", "name": "inspect_service",
     "description": "Inspect the web service health and latest error.",
     "parameters": EMPTY_SCHEMA, "strict": True},
    {"type": "function", "name": "check_database",
     "description": "Check database reachability and authentication.",
     "parameters": EMPTY_SCHEMA, "strict": True},
]

history = [{"role": "user", "content": "Diagnose why the web service is unavailable."}]

for _ in range(MAX_TURNS):
    response = client.responses.create(
        model=MODEL, input=history, tools=TOOLS, reasoning={"effort": "medium"}
    )
    history.extend(response.output)
    calls = [item for item in response.output if item.type == "function_call"]

    if not calls:
        print(response.output_text)
        break

    for call in calls:
        try:
            args = json.loads(call.arguments or "{}")
            result = FUNCTIONS[call.name](**args)
        except Exception as exc:
            result = {"ok": False, "error": str(exc)}

        history.append({
            "type": "function_call_output",
            "call_id": call.call_id,
            "output": json.dumps(result),
        })
else:
    raise RuntimeError("Agent reached MAX_TURNS without a final answer.")
