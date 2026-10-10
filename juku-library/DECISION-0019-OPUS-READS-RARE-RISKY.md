**Decision 0019 — Opus 5.5 at high reads the rare risky changes (9 October 2026)**

Parties: the Chairman's ruling, and the CTO (Claude) who built it. **Live** once the pull request that adds this record merges. It is a ruling carried out, not a debate.

**His ruling, 9 October 2026, whole:** *"opus 5.5 at hight effort only for rare risky cases"*. Recorded on [#103](https://github.com/Adonis80/how-we-build/issues/103). Asked after the bake-off of [#179](https://github.com/Adonis80/how-we-build/pull/179): on four known-bad and four clean historical changes, Opus 5.5 caught 2 of 4 defects and wrongly blocked 2 of 4 clean changes; GLM 5.3 Flash caught 1 and blocked none wrongly.

**What it amends, for `reviewer-risky` alone.** His rulings of 5 and 6 October 2026, that only open-weight models review; of 28 September 2026, *"every read at max"*; and of 29 September 2026, that no reviewer role holds the lead's own model. `reviewer-main` keeps all three: GLM 5.3 Flash at max for every ordinary change.

**What is built.**

1. **The switch is one edit.** `model-registry/registry.json`: `reviewer-risky` is `claude-opus-5-5` at `high`. No model is named anywhere else. `review-gate.py` holds each reviewer role at its own effort, max and high, and both reviewers refuse any other.
2. **The route costs no review cash.** Opus reads through the `claude-code` interface: the Claude Code tool pinned at 2.1.285 in both reviewers, on `CLAUDE_CODE_OAUTH_TOKEN` in the `reviewer` environment, which is the Claude plan allowance. The credential was still there on 9 October 2026: review run 38003891281 shows it set (masked). Opus last read on that route on 26 September 2026 ([#110](https://github.com/Adonis80/how-we-build/pull/110), cited on #103).
3. **The canary reads both roles.** It used to ask through OpenRouter alone and fail on any other interface. It now installs the same pinned tool, in a step with no secret, and reads a `claude-code` role the way `review.yml` does, every tool off. `review-gate.py` holds the pin, the step and the flags.
4. **Rare.** The risky list holds the six classes, and decision 0008's two prerequisites (personal data; secrets and credentials), and nothing else: pricing; live data or schema; sign-in and permissions; public trust boundaries; deploy and release; and the review gate itself. Two names came off. **`AGENTS.md`**, the brief, is the reviewer's words, read from `main` whatever a head says, so it is not the gate. **Every dot-directory except three**: `.github` (CI, its scripts and its owners), `.claude/settings*` (an agent's permissions and hooks) and `.vercel/` (the host's project link). A brief, a skill or an agent's instructions are still read as code, by `reviewer-main`.
5. **Two rounds at most** still holds. A blocking finding the CTO disputes goes to the Chairman to settle, as `AGENTS.md` says. It never goes into a third round.

**Pages checked for the rules it amends.** Beyond the pages this change edits, `library/reviewer-verdict.md` and `library/money.md` were read for *every read at max* and *only open-weight models review*: neither states either. `money.md`'s cash check already records plan allowance beside cash, never in it, which is how an Opus read is counted.

**What the list costs, measured.** Of this repository's last 20 merged pull requests (#140 to #180), 18 would have gone to Opus under the new list, the same 18 as before. Each one touched the gate: `review-gate.py`, `check.sh`, a workflow, the registry or `product-reads/`. The two that would not are #171 and #152, which were pages only. Here, nearly all work is gate work, so here risky is not rare. In a product, where the gate is not the work, it is.

**Strongest objection left.** Opus wrongly blocked half the clean changes in the bake-off. Two rounds and the Chairman's settlement bound the cost of a false blocker. They do not remove it.
