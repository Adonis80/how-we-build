# Changing the rulebook: size and reconciliation

Scope: this repository. Open when: changing a rule, or a page reads over its size target.

**A repair or an upgrade is never refused for length alone, and the dead text leaves in the same change** (his ruling, 8 October 2026, [decision 0017](../juku-library/DECISION-0017-SIZE-SIGNALS-AND-RECONCILIATION.md)). `check.sh` prints sizes against targets: the operating page 600 words, the screen law 450, a library page 4,000 bytes (`library/hypersolid.md` 6,500). A reading over target is a signal, never a failure, and never a cleanup debt on an unrelated change.

**What a rule change owes instead.** For each rule it changes: find the current owner and the consumers it affects, by focused search, not by reading everything; make them agree; delete what the change supersedes; keep every live requirement. Shorter must never mean weaker: a trim that drops a requirement is a loss, not a saving. The cold review holds this (`AGENTS.md`); `check.sh` does not.

**Batches.** Word changes go in several small pull requests, each one dependency-coherent and asked once per round (his brief, 9 October 2026: *"A review of a small words change now costs a few cents, so several small batches are cheaper than one big one."*). It, decision 0016 (H: *"Stale wording is removed in dependency-coherent batches, every operative condition kept whole at its triggered owner, each conflict listed in its pull request"*) and decision 0017 replace both rules of the 25 September tidying freeze: pages are moved, merged and reworded whenever that removes stale or duplicated text, and one session's word changes no longer go in one pull request, read once. The spend guard that stays is one ask per round, its fixes in one push (`library/reviewer-asking.md`).

**What it does not promise.** A stale line nobody connects to a change can survive until cleanup or a failure finds it.
