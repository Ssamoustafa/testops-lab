from __future__ import annotations

from collections.abc import Sequence
from typing import Protocol

from testops.domain.models import GateDecision, TestResult


class ResultReader(Protocol):
    def read(self) -> Sequence[TestResult]: ...


class HistoryRepository(Protocol):
    def load(self) -> Sequence[TestResult]: ...
    def append(self, results: Sequence[TestResult]) -> None: ...


class DecisionPublisher(Protocol):
    def publish(self, decision: GateDecision) -> None: ...
