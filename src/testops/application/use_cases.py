from __future__ import annotations

from dataclasses import dataclass

from testops.application.ports import DecisionPublisher, HistoryRepository, ResultReader
from testops.domain.models import GateDecision, QualityPolicy
from testops.domain.services import QualityGate


@dataclass(slots=True)
class EvaluateQuality:
    reader: ResultReader
    history: HistoryRepository
    publisher: DecisionPublisher
    gate: QualityGate

    def execute(self, policy: QualityPolicy) -> GateDecision:
        current = self.reader.read()
        previous = self.history.load()
        decision = self.gate.evaluate(current, previous, policy)
        self.publisher.publish(decision)
        self.history.append(current)
        return decision
