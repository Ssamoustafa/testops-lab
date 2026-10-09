# ADR-002: Do not use automatic retries as a quality strategy

**Status:** Accepted

Retries can be useful evidence, but silently turning a failure into a pass hides instability. TestOps Lab models pass/fail history and identifies tests that exhibit both outcomes. A future CI adapter may execute retries for diagnosis, but the quality model will preserve the original outcome and expose flakiness explicitly.
