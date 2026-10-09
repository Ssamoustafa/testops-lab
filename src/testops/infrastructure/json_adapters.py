from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path

from testops.domain.models import GateDecision, TestResult, TestStatus


class JsonResultReader:
    def __init__(self, path: Path) -> None:
        self._path = path

    def read(self) -> tuple[TestResult, ...]:
        payload = json.loads(self._path.read_text())
        return tuple(
            TestResult(
                test_id=item["test_id"],
                status=TestStatus(item["status"]),
                duration_ms=int(item["duration_ms"]),
                suite=item.get("suite", "unknown"),
            )
            for item in payload
        )


class JsonHistoryRepository:
    def __init__(self, path: Path) -> None:
        self._path = path

    def load(self) -> tuple[TestResult, ...]:
        if not self._path.exists():
            return ()
        return JsonResultReader(self._path).read()

    def append(self, results: tuple[TestResult, ...] | list[TestResult]) -> None:
        existing = list(self.load())
        combined = [*existing, *results]
        self._path.parent.mkdir(parents=True, exist_ok=True)
        self._path.write_text(json.dumps([asdict(item) for item in combined], indent=2))


class ConsolePublisher:
    def publish(self, decision: GateDecision) -> None:
        state = "PASSED" if decision.passed else "FAILED"
        print(f"QUALITY GATE: {state}")
        print(f"Tests: {decision.metrics.total} | Failures: {decision.metrics.failed}")
        print(f"Failure rate: {decision.metrics.failure_rate:.2%}")
        print(f"Flaky tests: {len(decision.metrics.flaky_tests)}")
        print(f"p95 duration: {decision.metrics.p95_duration_ms} ms")
        for violation in decision.violations:
            print(f"- {violation.rule}: {violation.actual} (expected {violation.expected})")
