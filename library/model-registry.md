# The model registry

Scope: every repository under this rulebook, in either stack. Open when: asking which model holds a role, or switching the model behind a role.

**One file names models: `model-registry/registry.json`.** Everything else asks for a role: `reviewer-main`, `reviewer-risky`, `reviewer-frontend`, `coder-fast`, `coder-max`, `frontend-fast`, `frontend-max`, `agent-fast`, `max-subagent`, and the debate's seats (`lead`, `consultant`, `lead-step-up`, `consultant-step-up`, `breaker`), conversation roles no machine calls (`library/consultant.md`). `check.sh` refuses a model id anywhere else here, and each fact in the registry carries the date it was checked and its source.

**Asking for a role.** `python3 model-registry/resolve.py model-registry/registry.json <role>` prints the model, provider, calling interface, credential, effort and fallback; add a field's name for that field alone. A role that cannot resolve cleanly is an error, never a default. Calls go through `model-registry/ask.py`, the OpenAI-compatible interface, so a new provider is a registry entry and an Actions secret, never code.

**Who reads what.** `reviewer-main` reads ordinary changes: open-weight, never the lead's own model, at max. `reviewer-risky` reads the six risky classes (`library/reviewer.md`) on the Claude plan, so it spends no review cash; *rare* means the risky list holds those classes and nothing else. Nothing stands behind either: a role that gives no verdict leaves the commit unread and the gate red, and `review.yml` tells him on one issue. The reviewers read the registry from `main`, so a pull request never picks its own reviewer. A product's code goes to the registry's provider, and `ask.py` sends nothing to a provider that does not promise not to store or train on it.

**Switching.** Change the role's `model`, `effort` or `fallback` in `registry.json`, with the new model's entry, its `checked` date and `source`; `resolve.py --check` and `check.sh` must pass. It is a risky change. If the pinned Claude Code does not know the model, the pin moves in both reviewers and `review-gate.py`, proved first on a full-size read. Rolling back is reverting it.

**Not built yet**: re-reading only what changed since the last read; a weekly model check proposing a registry pull request; the main coder on an open-weight model.
