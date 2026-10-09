import json
from pathlib import Path

from testops.application.use_cases import EvaluateQuality
from testops.domain.models import QualityPolicy
from testops.domain.services import QualityGate
from testops.infrastructure.json_adapters import (
    JsonHistoryRepository,
    JsonResultReader,
)


class RecordingPublisher:
    def __init__(self) -> None:
        self.published = False

    def publish(self, decision: object) -> None:
        self.published = True


def test_json_pipeline_persists_history(tmp_path: Path) -> None:
    results = tmp_path / "results.json"
    history = tmp_path / "history.json"

    results.write_text(
        json.dumps(
            [
                {
                    "test_id": "api::health",
                    "status": "passed",
                    "duration_ms": 42,
                }
            ]
        )
    )

    publisher = RecordingPublisher()

    use_case = EvaluateQuality(
        JsonResultReader(results),
        JsonHistoryRepository(history),
        publisher,
        QualityGate(),
    )

    decision = use_case.execute(QualityPolicy())

    assert decision.passed
    assert publisher.published
    assert len(json.loads(history.read_text())) == 1
