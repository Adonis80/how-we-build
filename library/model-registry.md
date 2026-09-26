# The model registry

Scope: every repository under this rulebook, in either stack. Open when: asking which model holds a role, what a read resolved to, or switching the model behind a role.

**One file names models: `model-registry/registry.json`** ([decision 0008](https://github.com/Adonis80/how-we-build/issues/103), built on the 18 September consensus in `consensuses/juku-os/`). Everything else asks for a role: `reviewer-main`, `reviewer-risky`, `reviewer-fallback`, `reviewer-frontend`, `coder-fast`, `coder-max`, `frontend-fast`, `frontend-max`, `agent-fast`. `check.sh` refuses a model id anywhere else in this repository, and each fact in the registry carries the date it was checked and its source.

**Asking for a role.** `python3 model-registry/resolve.py model-registry/registry.json <role>` prints what the role resolves to: the model, its provider, the interface that calls it, the credential it needs, its effort and its fallback role. Add a field's name for that field alone. A role that cannot resolve cleanly (unknown, a blocked model, an effort the model does not take) is an error, never a default. Calls go through `model-registry/ask.py`, the OpenAI-compatible interface OpenRouter speaks today and a LiteLLM proxy or a direct provider would speak tomorrow, so a new provider is a registry entry and an Actions secret, never code.

**Who reads what.** Decision 0008 reverses his 22 September pairing, which put the open-weight model behind Sonnet as the main backup: the cheaper model now reads first. An ordinary change goes to `reviewer-main`. If it does not answer with a verdict and a review behind it, `reviewer-fallback` reads it. If neither answers, the commit stays unread and the gate stays red. A change in a risky class, or with any file whose kind the list does not know, goes to `reviewer-risky`, read whole at max, with nothing behind it. `review-gate.py` refuses a registry that sets those efforts otherwise, and runs the fallback on its own cases. The reviewers read the registry from `main`, so a pull request never picks its own reviewer. Its first live reads, each with its spend line, are cited on [#103](https://github.com/Adonis80/how-we-build/issues/103).

**Seeing what a read resolved to.** Every verdict ends with a spend line: class, role, exact model, effort, bytes and tokens in and out, the cost the provider reported, minutes, and whether the fallback read it. It is on the check run, on the comment and in the job's summary.

**Switching.** Change the role's `model` (or its `effort` or `fallback`) in `registry.json`, with the new model's entry, its `checked` date and its `source`. `resolve.py --check` and `check.sh` must pass. The change is in the gate's risky class, so `reviewer-risky` reads it, and it lands like any other pull request. Rolling back is reverting it.

**A product's code goes to Anthropic alone for now.** `review-product.yml` speaks only the claude-code interface, because no other provider has been cleared to read a product's private code, so an ordinary product read falls back to `reviewer-fallback` and says so on its spend line. This repository's own reads, which are public, go to `reviewer-main`.

**Not built yet** (decision 0008's later steps): re-reading only what changed since the last read, the weekly model check that proposes a registry pull request, and the main coder on an open-weight model.
