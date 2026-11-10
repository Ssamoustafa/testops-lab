# TestOps Lab

> A quality engineering control plane demonstrating how a senior SDET can turn raw test executions into explicit, reviewable CI quality decisions.

[![CI](https://github.com/Ssamoustafa/testops-lab/actions/workflows/ci.yml/badge.svg)](https://github.com/Ssamoustafa/testops-lab/actions/workflows/ci.yml)

## Why this exists

Most automation repositories answer **"can I execute tests?"** TestOps Lab answers the more senior question: **"how should an engineering organization make reliable release decisions from test evidence?"**

The first vertical slice ingests test results, combines them with execution history, detects flaky behavior, computes failure and latency signals, evaluates policy, publishes a decision, and persists history for the next run.

```text
Test executors
     |
     v
Result adapters ---> Quality use case ---> Policy engine
                          |                    |
                          v                    v
                    History port        Gate decision
                          |                    |
                          v                    v
                    JSON / future DB     CI exit code/report
```

## What it demonstrates

- Clean / hexagonal architecture with dependency inversion at real integration boundaries
- Immutable typed domain models and explicit invariants
- Policy-as-code rather than opaque pipeline shell logic
- Flaky-test detection from historical outcomes instead of hiding failures with retries
- Performance budgets through p95 test duration
- CLI designed for local reproduction and CI use
- Replaceable adapters for result formats, persistence, and publishing
- Strict static analysis and a 90% CI coverage gate
- Architecture Decision Records documenting trade-offs

## Quick start

Requires Python 3.12+.

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
pytest
testops examples/results.json --max-failure-rate 0 --max-flaky-tests 0 --max-p95-ms 2000
```

Expected decision:

```text
QUALITY GATE: PASSED
Tests: 3 | Failures: 0
Failure rate: 0.00%
Flaky tests: 0
p95 duration: 820 ms
```

A failed policy returns a non-zero process exit code, allowing the same domain decision to block a pull request or deployment.

## Clean-code rules used here

**Single responsibility:** parsing, orchestration, policy evaluation, persistence, and presentation are separate concerns.

**Dependency inversion:** the application depends on `ResultReader`, `HistoryRepository`, and `DecisionPublisher` protocols. JSON is an adapter, not an architectural dependency.

**Composition over inheritance:** the use case receives collaborators explicitly. There is no base-class framework that consumers must inherit from.

**Domain language over generic helpers:** concepts are named `QualityPolicy`, `GateDecision`, and `TestResult`; there is deliberately no dumping-ground `utils.py`.

**Fail explicitly:** invalid domain values raise errors and a failed quality gate returns exit code `1`.

## Roadmap

The repository is intentionally evolvable. Strong next increments are JUnit/Allure ingestion, PostgreSQL history, changed-test selection, quarantine workflow with expiry/ownership, trend reporting, OpenTelemetry, and a small API/dashboard. Each should arrive behind an existing or deliberately introduced port rather than contaminating the domain.

## Architecture

See [`docs/architecture.md`](docs/architecture.md) and the ADRs under [`docs/adr`](docs/adr).

