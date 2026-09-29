"""Código do Capítulo 153 — Da fronteira à produção: agenda de pesquisa e critérios de adoção.

Extraído da versão técnica v26 do livro "Agentes de Inteligência Artificial".
Mantenha este arquivo idêntico à listagem publicada no manuscrito.
"""

# BEGIN FRONTIER153_READINESS_GATE
from dataclasses import dataclass, field

@dataclass(frozen=True)
class Evidence:
    name: str
    passed: bool
    hard_gate: bool = False
    note: str = ""

@dataclass(frozen=True)
class FrontierCandidate:
    name: str
    evidence: tuple[Evidence, ...]
    rollback_tested: bool
    owner: str
    max_blast_radius: str

@dataclass(frozen=True)
class GateResult:
    promotable: bool
    failed_hard_gates: tuple[str, ...] = field(default_factory=tuple)
    warnings: tuple[str, ...] = field(default_factory=tuple)


def readiness_gate(candidate: FrontierCandidate) -> GateResult:
    if not candidate.owner.strip():
        return GateResult(False, ("missing_owner",), ())

    failed_hard = tuple(
        item.name
        for item in candidate.evidence
        if item.hard_gate and not item.passed
    )
    warnings = tuple(
        item.name
        for item in candidate.evidence
        if not item.hard_gate and not item.passed
    )

    if not candidate.rollback_tested:
        failed_hard += ("rollback_not_tested",)
    if candidate.max_blast_radius not in {"sandbox", "single_tenant", "bounded_cohort"}:
        failed_hard += ("unbounded_blast_radius",)

    return GateResult(not failed_hard, failed_hard, warnings)


def test_promotes_bounded_candidate() -> None:
    c = FrontierCandidate(
        name="dynamic-skill-pilot",
        evidence=(
            Evidence("security_review", True, hard_gate=True),
            Evidence("regression_eval", True, hard_gate=True),
            Evidence("cost_target", False),
        ),
        rollback_tested=True,
        owner="agent-platform",
        max_blast_radius="bounded_cohort",
    )
    result = readiness_gate(c)
    assert result.promotable is True
    assert result.warnings == ("cost_target",)


def test_hard_gate_blocks() -> None:
    c = FrontierCandidate(
        name="self-modifying-agent",
        evidence=(Evidence("security_review", False, hard_gate=True),),
        rollback_tested=True,
        owner="research",
        max_blast_radius="sandbox",
    )
    result = readiness_gate(c)
    assert result.promotable is False
    assert "security_review" in result.failed_hard_gates


def test_rollback_is_mandatory() -> None:
    c = FrontierCandidate(
        name="new-planner",
        evidence=(Evidence("regression_eval", True, hard_gate=True),),
        rollback_tested=False,
        owner="platform",
        max_blast_radius="single_tenant",
    )
    assert "rollback_not_tested" in readiness_gate(c).failed_hard_gates


def test_unbounded_blast_radius_blocks() -> None:
    c = FrontierCandidate(
        name="ambient-agent",
        evidence=(Evidence("security_review", True, hard_gate=True),),
        rollback_tested=True,
        owner="automation",
        max_blast_radius="all_customers",
    )
    assert readiness_gate(c).promotable is False


def test_owner_is_required() -> None:
    c = FrontierCandidate(
        name="agent-payment",
        evidence=(),
        rollback_tested=True,
        owner="",
        max_blast_radius="sandbox",
    )
    assert readiness_gate(c).failed_hard_gates == ("missing_owner",)


def run_tests() -> None:
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_") and callable(v)]
    for test in tests:
        test()
        print("PASS", test.__name__)
    print(f"{len(tests)} tests passed")


if __name__ == "__main__":
    run_tests()
# END FRONTIER153_READINESS_GATE
