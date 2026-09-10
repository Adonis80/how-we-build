Rulebook: this repository. A working session reads `HOW-WE-BUILD.md`; this file exists for the reviewer of changes to the rulebook itself.

# AGENTS.md — how-we-build

This repository is the development system, not a product. Changes land only by pull request against protected `main`. Adding global machinery must be justified by the Charter or Dhayan's explicit ruling; deletion, consolidation and wording corrections need no separate architecture layer. `check.sh` is the deterministic guard.

## Review guidelines
Cold-read the changed global files and current architecture before the pull request's own account. Look especially for: two owners of one truth; provider-specific detail leaking into global rules; old rules left beside replacements; new machinery where deletion would work; recurring token/context cost; a setup that still requires Dhayan to relay technical state; and any claim that `build` is self-sufficient when a fresh provider session could not actually recover the work. Say what you checked, what you did not, and how sure you are. Prefer simplification over another exception. Do not manufacture disagreement.
