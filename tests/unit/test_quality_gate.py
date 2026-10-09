from testops.domain.models import QualityPolicy, TestResult as Result, TestStatus as Status
from testops.domain.services import QualityGate


def result(test_id: str, status: Status, duration: int = 100) -> Result:
    return Result(test_id, status, duration)


def test_gate_passes_when_policy_is_satisfied() -> None:
    decision = QualityGate().evaluate([result("a", Status.PASSED)], [], QualityPolicy())
    assert decision.passed
    assert decision.violations == ()


def test_gate_rejects_failure_rate_above_policy() -> None:
    decision = QualityGate().evaluate(
        [result("a", Status.PASSED), result("b", Status.FAILED)],
        [],
        QualityPolicy(max_failure_rate=0.10),
    )
    assert not decision.passed
    assert decision.violations[0].rule == "failure_rate"


def test_gate_detects_flaky_test_across_runs() -> None:
    decision = QualityGate().evaluate(
        [result("checkout", Status.PASSED)],
        [result("checkout", Status.FAILED)],
        QualityPolicy(max_flaky_tests=0),
    )
    assert decision.metrics.flaky_tests == ("checkout",)
    assert not decision.passed


def test_gate_enforces_p95_duration_budget() -> None:
    decision = QualityGate().evaluate(
        [result("fast", Status.PASSED, 100), result("slow", Status.PASSED, 1500)],
        [],
        QualityPolicy(max_p95_duration_ms=1000),
    )
    assert not decision.passed
    assert decision.violations[0].rule == "p95_duration_ms"
