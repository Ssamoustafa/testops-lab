import json
import sys
from pathlib import Path

from testops.interfaces.cli import main


def test_cli_runs_gate_and_persists_history(
    tmp_path: Path, monkeypatch, capsys
) -> None:
    results = tmp_path / "results.json"
    history = tmp_path / "history.json"
    results.write_text(
        json.dumps([{"test_id": "api::health", "status": "passed", "duration_ms": 42}]),
        encoding="utf-8",
    )
    monkeypatch.setattr(
        sys,
        "argv",
        ["testops", str(results), "--history", str(history), "--max-p95-ms", "100"],
    )

    assert main() == 0
    assert "QUALITY GATE: PASSED" in capsys.readouterr().out

    assert main() == 0
    assert len(json.loads(history.read_text(encoding="utf-8"))) == 2


def test_cli_returns_failure_when_quality_gate_rejects_results(
    tmp_path: Path, monkeypatch, capsys
) -> None:
    results = tmp_path / "results.json"
    history = tmp_path / "history.json"
    results.write_text(
        json.dumps([{"test_id": "api::health", "status": "failed", "duration_ms": 42}]),
        encoding="utf-8",
    )
    monkeypatch.setattr(
        sys,
        "argv",
        ["testops", str(results), "--history", str(history), "--max-failure-rate", "0"],
    )

    assert main() == 1
    assert "QUALITY GATE: FAILED" in capsys.readouterr().out
