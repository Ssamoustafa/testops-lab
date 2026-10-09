# Architecture

TestOps Lab uses a lightweight **hexagonal / clean architecture**. Dependencies point inward.

```text
GitHub Actions / CLI
        |
        v
   Interfaces
        |
        v
  Application use cases ---- Ports
        |                     ^
        v                     |
      Domain            Infrastructure adapters
  models + policies      JSON today; JUnit/DB later
```

## Boundaries

- **Domain** owns quality vocabulary and policy evaluation. It imports no CI, persistence, or presentation technology.
- **Application** coordinates a use case through ports.
- **Infrastructure** translates external formats into domain objects.
- **Interfaces** are delivery mechanisms such as the CLI.

This keeps vendor-specific integrations replaceable and the decision logic fast to unit test.

## Senior engineering choices

The project intentionally avoids a universal `utils.py`, mutable global state, framework inheritance hierarchies, and vendor objects leaking into the domain. Composition is preferred over inheritance; ports exist at actual volatility boundaries rather than around every class.
