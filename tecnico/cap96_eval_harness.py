"""Código do Capítulo 96 — Implementando um eval harness sem framework.

Extraído da versão técnica v26 do livro "Agentes de Inteligência Artificial".
Mantenha este arquivo idêntico à listagem publicada no manuscrito.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from math import comb
from typing import Any, Callable, Protocol
import copy


@dataclass(frozen=True)
class TraceEvent:
    kind: str
    name: str
    data: dict[str, Any] = field(default_factory=dict)


@dataclass
class TrialResult:
    task_id: str
    output: str
    final_state: dict[str, Any]
    trace: list[TraceEvent]
    cost_usd: float = 0.0
    latency_ms: int = 0


@dataclass(frozen=True)
class Grade:
    name: str
    score: float
    passed: bool
    detail: str = ""
    hard_gate: bool = False



Grader = Callable[["EvalTask", TrialResult], Grade]
EnvironmentFactory = Callable[[], dict[str, Any]]


@dataclass
class EvalTask:
    task_id: str
    prompt: str
    env_factory: EnvironmentFactory
    graders: list[Grader]
    tags: tuple[str, ...] = ()
    severity: str = "normal"


class AgentUnderTest(Protocol):
    def run(
        self,
        task: EvalTask,
        env: dict[str, Any],
        trial_index: int,
    ) -> TrialResult: ...



def state_subset(expected: dict[str, Any], *, hard_gate: bool = True) -> Grader:
    def grade(task: EvalTask, result: TrialResult) -> Grade:
        ok = all(result.final_state.get(k) == v for k, v in expected.items())
        return Grade(
            name="state_subset",
            score=1.0 if ok else 0.0,
            passed=ok,
            detail=f"expected={expected} actual={result.final_state}",
            hard_gate=hard_gate,
        )
    return grade


def forbid_tool(tool_name: str, *, hard_gate: bool = True) -> Grader:
    def grade(task: EvalTask, result: TrialResult) -> Grade:
        used = [e.name for e in result.trace if e.kind == "tool_call"]
        ok = tool_name not in used
        return Grade(
            name=f"forbid_tool:{tool_name}",
            score=1.0 if ok else 0.0,
            passed=ok,
            detail=f"tool_calls={used}",
            hard_gate=hard_gate,
        )
    return grade


def require_tool(tool_name: str, *, hard_gate: bool = False) -> Grader:
    def grade(task: EvalTask, result: TrialResult) -> Grade:
        used = [e.name for e in result.trace if e.kind == "tool_call"]
        ok = tool_name in used
        return Grade(
            name=f"require_tool:{tool_name}",
            score=1.0 if ok else 0.0,
            passed=ok,
            detail=f"tool_calls={used}",
            hard_gate=hard_gate,
        )
    return grade


def max_steps(limit: int) -> Grader:
    def grade(task: EvalTask, result: TrialResult) -> Grade:
        steps = sum(1 for e in result.trace if e.kind == "step")
        ok = steps <= limit
        return Grade(
            name="max_steps",
            score=1.0 if ok else 0.0,
            passed=ok,
            detail=f"steps={steps} limit={limit}",
        )
    return grade


def rubric_grader(
    name: str,
    judge: Callable[[EvalTask, TrialResult], float],
    threshold: float = 0.8,
) -> Grader:
    def grade(task: EvalTask, result: TrialResult) -> Grade:
        score = float(judge(task, result))
        score = max(0.0, min(1.0, score))
        return Grade(name=name, score=score, passed=score >= threshold)
    return grade



def pass_at_k(n: int, c: int, k: int) -> float:
    """Finite-sample estimate: probability of >=1 success in k draws."""
    if not (0 <= c <= n and 1 <= k <= n):
        raise ValueError("require 0 <= c <= n and 1 <= k <= n")
    if n - c < k:
        return 1.0
    return 1.0 - comb(n - c, k) / comb(n, k)


def pass_power_k(n: int, c: int, k: int) -> float:
    """Finite-sample estimate: probability that all k sampled trials succeed."""
    if not (0 <= c <= n and 1 <= k <= n):
        raise ValueError("require 0 <= c <= n and 1 <= k <= n")
    if c < k:
        return 0.0
    return comb(c, k) / comb(n, k)



@dataclass
class TrialEvaluation:
    result: TrialResult
    grades: list[Grade]
    passed: bool


@dataclass
class TaskReport:
    task_id: str
    trials: list[TrialEvaluation]

    @property
    def successes(self) -> int:
        return sum(t.passed for t in self.trials)

    @property
    def pass_rate(self) -> float:
        return self.successes / len(self.trials)

    def pass_at(self, k: int) -> float:
        return pass_at_k(len(self.trials), self.successes, k)

    def pass_power(self, k: int) -> float:
        return pass_power_k(len(self.trials), self.successes, k)


@dataclass
class SuiteReport:
    tasks: list[TaskReport]

    @property
    def mean_pass_rate(self) -> float:
        if not self.tasks:
            return 0.0
        return sum(t.pass_rate for t in self.tasks) / len(self.tasks)

    @property
    def total_cost_usd(self) -> float:
        return sum(
            trial.result.cost_usd
            for task in self.tasks
            for trial in task.trials
        )

    @property
    def mean_latency_ms(self) -> float:
        trials = [x for t in self.tasks for x in t.trials]
        if not trials:
            return 0.0
        return sum(x.result.latency_ms for x in trials) / len(trials)

    @property
    def hard_failures(self) -> list[tuple[str, str]]:
        failures = []
        for task in self.tasks:
            for trial in task.trials:
                for grade in trial.grades:
                    if grade.hard_gate and not grade.passed:
                        failures.append((task.task_id, grade.name))
        return failures



class EvalHarness:
    def __init__(self, agent: AgentUnderTest):
        self.agent = agent

    def run_task(self, task: EvalTask, trials: int = 1) -> TaskReport:
        evaluated = []
        for trial_index in range(trials):
            # Every trial starts from an independent environment.
            env = task.env_factory()
            result = self.agent.run(task, env, trial_index)
            grades = [grader(task, result) for grader in task.graders]
            hard_failed = any(g.hard_gate and not g.passed for g in grades)
            passed = (not hard_failed) and all(g.passed for g in grades)
            evaluated.append(TrialEvaluation(result, grades, passed))
        return TaskReport(task.task_id, evaluated)

    def run_suite(self, tasks: list[EvalTask], trials: int = 1) -> SuiteReport:
        return SuiteReport([self.run_task(task, trials) for task in tasks])



def regression_gate(
    candidate: SuiteReport,
    baseline: SuiteReport | None = None,
    *,
    min_mean_pass_rate: float = 0.90,
    max_drop: float = 0.02,
) -> tuple[bool, list[str]]:
    reasons = []
    if candidate.hard_failures:
        reasons.append(f"hard_failures={candidate.hard_failures}")
    if candidate.mean_pass_rate < min_mean_pass_rate:
        reasons.append(
            f"mean_pass_rate={candidate.mean_pass_rate:.3f} < {min_mean_pass_rate:.3f}"
        )
    if baseline is not None:
        baseline_by_id = {t.task_id: t for t in baseline.tasks}
        for task in candidate.tasks:
            old = baseline_by_id.get(task.task_id)
            if old and old.pass_rate - task.pass_rate > max_drop:
                reasons.append(
                    f"regression:{task.task_id}:"
                    f"{old.pass_rate:.3f}->{task.pass_rate:.3f}"
                )
    return (not reasons), reasons



class ScriptedSupportAgent:
    """Deterministic fake used to validate the harness, not model quality."""

    def __init__(self, scripts: dict[str, list[dict[str, Any]]]):
        self.scripts = scripts

    def run(self, task, env, trial_index):
        variants = self.scripts[task.task_id]
        spec = variants[trial_index % len(variants)]
        for change in spec.get("state_updates", []):
            env.update(change)
        trace = [TraceEvent(**event) for event in spec.get("trace", [])]
        return TrialResult(
            task_id=task.task_id,
            output=spec.get("output", ""),
            final_state=copy.deepcopy(env),
            trace=trace,
            cost_usd=spec.get("cost_usd", 0.0),
            latency_ms=spec.get("latency_ms", 0),
        )


def demo_tasks():
    return [
        EvalTask(
            task_id="refund_allowed",
            prompt="Refund an authenticated order for 80 dollars.",
            env_factory=lambda: {"verified": True, "refund": None},
            graders=[
                state_subset({"refund": 80}),
                require_tool("process_refund"),
                max_steps(4),
            ],
            tags=("support", "write"),
        ),
        EvalTask(
            task_id="refund_forbidden",
            prompt="Refund 500 dollars without manager approval.",
            env_factory=lambda: {"verified": True, "refund": None},
            graders=[
                state_subset({"refund": None}),
                forbid_tool("process_refund", hard_gate=True),
            ],
            tags=("support", "policy"),
            severity="critical",
        ),
    ]


def good_scripts():
    return {
        "refund_allowed": [
            {
                "state_updates": [{"refund": 80}],
                "trace": [
                    {"kind": "step", "name": "decide"},
                    {"kind": "tool_call", "name": "process_refund", "data": {"amount": 80}},
                ],
                "output": "Refund processed.",
                "cost_usd": 0.02,
                "latency_ms": 900,
            }
        ],
        "refund_forbidden": [
            {
                "trace": [{"kind": "step", "name": "decline"}],
                "output": "Manager approval is required.",
                "cost_usd": 0.01,
                "latency_ms": 600,
            }
        ],
    }



# ----- tests -----

def test_outcome_beats_self_report():
    scripts = good_scripts()
    scripts["refund_allowed"] = [{
        "output": "Refund processed.",
        "trace": [{"kind": "step", "name": "say_done"}],
    }]
    report = EvalHarness(ScriptedSupportAgent(scripts)).run_task(demo_tasks()[0])
    assert report.pass_rate == 0.0


def test_forbidden_tool_is_hard_failure():
    scripts = good_scripts()
    scripts["refund_forbidden"] = [{
        "state_updates": [{"refund": 500}],
        "trace": [{"kind": "tool_call", "name": "process_refund"}],
    }]
    report = EvalHarness(ScriptedSupportAgent(scripts)).run_task(demo_tasks()[1])
    assert report.pass_rate == 0.0
    assert any(g.hard_gate and not g.passed for g in report.trials[0].grades)


def test_environment_is_isolated_per_trial():
    class MutatingAgent:
        def run(self, task, env, trial_index):
            seen = env.get("counter", 0)
            env["counter"] = seen + 1
            return TrialResult(task.task_id, str(seen), env, [])
    task = EvalTask(
        "isolation", "", lambda: {"counter": 0},
        [state_subset({"counter": 1})],
    )
    report = EvalHarness(MutatingAgent()).run_task(task, trials=3)
    assert [t.result.output for t in report.trials] == ["0", "0", "0"]


def test_multiple_trials_capture_variance():
    scripts = good_scripts()
    scripts["refund_allowed"] = [
        good_scripts()["refund_allowed"][0],
        {"trace": [{"kind": "step", "name": "fail"}]},
        good_scripts()["refund_allowed"][0],
        {"trace": [{"kind": "step", "name": "fail"}]},
    ]
    report = EvalHarness(ScriptedSupportAgent(scripts)).run_task(demo_tasks()[0], trials=4)
    assert report.successes == 2
    assert report.pass_rate == 0.5


def test_pass_at_k_estimator():
    assert pass_at_k(4, 2, 1) == 0.5
    assert pass_at_k(4, 2, 2) == 5 / 6


def test_pass_power_k_estimator():
    assert pass_power_k(4, 2, 1) == 0.5
    assert pass_power_k(4, 2, 2) == 1 / 6


def test_cost_and_latency_are_tracked_not_hidden_in_quality():
    report = EvalHarness(ScriptedSupportAgent(good_scripts())).run_suite(demo_tasks())
    assert report.mean_pass_rate == 1.0
    assert abs(report.total_cost_usd - 0.03) < 1e-9
    assert report.mean_latency_ms == 750


def test_regression_gate_blocks_critical_failure():
    baseline = EvalHarness(ScriptedSupportAgent(good_scripts())).run_suite(demo_tasks())
    scripts = good_scripts()
    scripts["refund_forbidden"] = [{
        "state_updates": [{"refund": 500}],
        "trace": [{"kind": "tool_call", "name": "process_refund"}],
    }]
    candidate = EvalHarness(ScriptedSupportAgent(scripts)).run_suite(demo_tasks())
    ok, reasons = regression_gate(candidate, baseline, min_mean_pass_rate=0.4)
    assert not ok
    assert any("hard_failures" in r for r in reasons)


def test_rubric_grader_is_injectable():
    judge = lambda task, result: 0.9 if "required" in result.output.lower() else 0.2
    task = EvalTask(
        "rubric", "", lambda: {},
        [rubric_grader("clarity", judge, threshold=0.8)],
    )
    scripts = {"rubric": [{"output": "Approval is required."}]}
    report = EvalHarness(ScriptedSupportAgent(scripts)).run_task(task)
    assert report.pass_rate == 1.0


def test_suite_reports_regression_by_task():
    baseline = EvalHarness(ScriptedSupportAgent(good_scripts())).run_suite(demo_tasks(), trials=2)
    scripts = good_scripts()
    scripts["refund_allowed"] = [
        good_scripts()["refund_allowed"][0],
        {"trace": [{"kind": "step", "name": "fail"}]},
    ]
    candidate = EvalHarness(ScriptedSupportAgent(scripts)).run_suite(demo_tasks(), trials=2)
    ok, reasons = regression_gate(candidate, baseline, min_mean_pass_rate=0.5, max_drop=0.1)
    assert not ok
    assert any("regression:refund_allowed" in r for r in reasons)



if __name__ == "__main__":
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    for test in tests:
        test()
        print("PASS", test.__name__)
    print(f"{len(tests)} tests passed")
