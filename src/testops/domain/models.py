from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class TestStatus(StrEnum):
    PASSED = "passed"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass(frozen=True, slots=True)
class TestResult:
    test_id: str
    status: TestStatus
    duration_ms: int
    suite: str = "unknown"

    def __post_init__(self) -> None:
        if not self.test_id.strip():
            raise ValueError("test_id must not be blank")
        if self.duration_ms < 0:
            raise ValueError("duration_ms must be non-negative")


@dataclass(frozen=True, slots=True)
class QualityPolicy:
    max_failure_rate: float = 0.0
    max_flaky_tests: int = 0
    max_p95_duration_ms: int | None = None

    def __post_init__(self) -> None:
        if not 0 <= self.max_failure_rate <= 1:
            raise ValueError("max_failure_rate must be between 0 and 1")
        if self.max_flaky_tests < 0:
            raise ValueError("max_flaky_tests must be non-negative")


@dataclass(frozen=True, slots=True)
class QualityMetrics:
    total: int
    failed: int
    failure_rate: float
    p95_duration_ms: int
    flaky_tests: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class GateViolation:
    rule: str
    actual: str
    expected: str


@dataclass(frozen=True, slots=True)
class GateDecision:
    passed: bool
    metrics: QualityMetrics
    violations: tuple[GateViolation, ...]
