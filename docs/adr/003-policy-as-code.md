# ADR-003: Quality gates are policy, not pipeline conditionals

**Status:** Accepted

Quality thresholds belong to a versioned policy model rather than scattered shell expressions. This enables reviewable rules, local reproduction, unit testing, and consistent behavior across CI systems.
