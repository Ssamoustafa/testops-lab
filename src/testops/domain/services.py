from __future__ import annotations

import math
from collections import defaultdict
from collections.abc import Iterable

from testops.domain.models import (
    GateDecision,
    GateViolation,
    QualityMetrics,
    QualityPolicy,
    TestResult,
    TestStatus,
)


def _percentile_95(values: list[int]) -> int:
    if not values:
        return 0
    ordered = sorted(values)
    index = max(0, math.ceil(0.95 * len(ordered)) - 1)
    return ordered[index]


class QualityGate:
    """Pure domain service: policy evaluation without CI, files, or vendor dependencies."""

    def evaluate(
        self,
        current: Iterable[TestResult],
        history: Iterable[TestResult],
        policy: QualityPolicy,
    ) -> GateDecision:
        current_results = tuple(current)
        historical_results = tuple(history)
        failed = sum(result.status is TestStatus.FAILED for result in current_results)
        total = len(current_results)
        failure_rate = failed / total if total else 0.0
        flaky = self._find_flaky_tests((*historical_results, *current_results))
        metrics = QualityMetrics(
            total=total,
            failed=failed,
            failure_rate=failure_rate,
            p95_duration_ms=_percentile_95([r.duration_ms for r in current_results]),
            flaky_tests=flaky,
        )
        violations = self._violations(metrics, policy)
        return GateDecision(not violations, metrics, violations)

    @staticmethod
    def _find_flaky_tests(results: Iterable[TestResult]) -> tuple[str, ...]:
        statuses: dict[str, set[TestStatus]] = defaultdict(set)
        for result in results:
            if result.status is not TestStatus.SKIPPED:
                statuses[result.test_id].add(result.status)
        return tuple(sorted(test_id for test_id, seen in statuses.items() if len(seen) > 1))

    @staticmethod
    def _violations(metrics: QualityMetrics, policy: QualityPolicy) -> tuple[GateViolation, ...]:
        violations: list[GateViolation] = []
        if metrics.failure_rate > policy.max_failure_rate:
            violations.append(GateViolation("failure_rate", f"{metrics.failure_rate:.2%}", f"<= {policy.max_failure_rate:.2%}"))
        if len(metrics.flaky_tests) > policy.max_flaky_tests:
            violations.append(GateViolation("flaky_tests", str(len(metrics.flaky_tests)), f"<= {policy.max_flaky_tests}"))
        if policy.max_p95_duration_ms is not None and metrics.p95_duration_ms > policy.max_p95_duration_ms:
            violations.append(GateViolation("p95_duration_ms", str(metrics.p95_duration_ms), f"<= {policy.max_p95_duration_ms}"))
        return tuple(violations)
