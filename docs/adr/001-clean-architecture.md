# ADR-001: Keep quality policy independent of CI vendors

**Status:** Accepted

## Context
Quality gates may run in GitHub Actions today and another orchestrator tomorrow. Coupling policy to workflow APIs makes the core hard to test and migrate.

## Decision
Keep policy evaluation in the domain and expose external dependencies through application ports.

## Consequences
The domain is deterministic and testable without I/O. Adapters add a small amount of structure but integrations can evolve independently.
