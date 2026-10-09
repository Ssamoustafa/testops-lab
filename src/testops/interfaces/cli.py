from __future__ import annotations

import argparse
from pathlib import Path

from testops.application.use_cases import EvaluateQuality
from testops.domain.models import QualityPolicy
from testops.domain.services import QualityGate
from testops.infrastructure.json_adapters import ConsolePublisher, JsonHistoryRepository, JsonResultReader


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Evaluate CI test results against a quality policy.")
    parser.add_argument("results", type=Path)
    parser.add_argument("--history", type=Path, default=Path("artifacts/history.json"))
    parser.add_argument("--max-failure-rate", type=float, default=0.0)
    parser.add_argument("--max-flaky-tests", type=int, default=0)
    parser.add_argument("--max-p95-ms", type=int)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    use_case = EvaluateQuality(
        reader=JsonResultReader(args.results),
        history=JsonHistoryRepository(args.history),
        publisher=ConsolePublisher(),
        gate=QualityGate(),
    )
    decision = use_case.execute(QualityPolicy(args.max_failure_rate, args.max_flaky_tests, args.max_p95_ms))
    return 0 if decision.passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
