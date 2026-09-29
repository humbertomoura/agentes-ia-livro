"""Código do Capítulo 136 — Projeto 1 — Construindo um agent loop mínimo.

Extraído da versão técnica v26 do livro "Agentes de Inteligência Artificial".
Mantenha este arquivo idêntico à listagem publicada no manuscrito.
"""

# BEGIN PROJECT136_MINIMAL_AGENT
from dataclasses import dataclass
from typing import Callable, Iterable

@dataclass(frozen=True)
class Action:
    kind: str
    name: str = ""
    argument: str = ""
    output: str = ""

@dataclass(frozen=True)
class RunResult:
    output: str
    steps: int

class ScriptedModel:
    def __init__(self, actions: Iterable[Action]):
        self._actions = iter(actions)

    def decide(self, goal: str, observation: str | None) -> Action:
        return next(self._actions)

class ToolRegistry:
    def __init__(self):
        self._tools: dict[str, Callable[[str], str]] = {}

    def register(self, name: str, fn: Callable[[str], str]) -> None:
        if name in self._tools:
            raise ValueError(f"duplicate tool: {name}")
        self._tools[name] = fn

    def invoke(self, name: str, argument: str) -> str:
        if name not in self._tools:
            raise KeyError(f"unknown tool: {name}")
        return self._tools[name](argument)

def run_agent(goal: str, model: ScriptedModel, tools: ToolRegistry, max_steps: int = 6) -> RunResult:
    observation: str | None = None
    for step in range(1, max_steps + 1):
        action = model.decide(goal, observation)
        if action.kind == "final":
            return RunResult(action.output, step)
        if action.kind != "tool":
            raise ValueError(f"invalid action kind: {action.kind}")
        observation = tools.invoke(action.name, action.argument)
    raise RuntimeError("step limit reached")

def build_tools() -> ToolRegistry:
    catalog = {"alpha": "42", "beta": "agentic"}
    registry = ToolRegistry()
    registry.register("lookup", lambda key: catalog.get(key, "NOT_FOUND"))
    return registry

def test_tool_then_final() -> None:
    model = ScriptedModel([
        Action("tool", name="lookup", argument="alpha"),
        Action("final", output="alpha=42"),
    ])
    result = run_agent("read alpha", model, build_tools())
    assert result == RunResult("alpha=42", 2)

def test_unknown_tool_fails_closed() -> None:
    model = ScriptedModel([Action("tool", name="delete_all", argument="x")])
    try:
        run_agent("danger", model, build_tools())
        raise AssertionError("unknown tool should fail")
    except KeyError:
        pass

def test_invalid_action_is_rejected() -> None:
    model = ScriptedModel([Action("thought")])
    try:
        run_agent("x", model, build_tools())
        raise AssertionError("invalid action should fail")
    except ValueError:
        pass

def test_step_limit_stops_runaway_loop() -> None:
    model = ScriptedModel([Action("tool", name="lookup", argument="alpha")] * 3)
    try:
        run_agent("loop", model, build_tools(), max_steps=2)
        raise AssertionError("step limit should stop the run")
    except RuntimeError as exc:
        assert "step limit" in str(exc)

def run_tests() -> None:
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_") and callable(v)]
    for test in tests:
        test()
        print("PASS", test.__name__)
    print(f"{len(tests)} tests passed")

if __name__ == "__main__":
    run_tests()
# END PROJECT136_MINIMAL_AGENT
