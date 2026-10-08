**Decision 0017 — size signals, not authoring caps; every rule change reconciles what it touches (8 October 2026)**

Parties: the CTO (Claude) and the consultant (Astra). **AGREED.** Built in the pull request that adds this record.

**Provenance, said plainly.** This record is the CTO's summary of the agreement, not a transcript. The debate ran in the ChatGPT chat "Lean Juku OS Review", in Astra's Juku Review project, two rounds, the consultant at high effort against the CTO's step-up seat, each model as it read itself back in that chat; neither attests the serving backend. Astra's two replies are files in that chat. The Chairman's words below are quoted whole.

**His goal, 8 October 2026, whole:** *"So just so we're clear, when I paste the prompt into the next session, is it clear that the goal is to completely remove all of the bloat and conflicting information so that the result is a super clear, easy to understand and easy to follow rule book. And for the bloat to never be allowed to happen again, there must be a mechanism to stop old stale information for uh, from being retained. This must be deleted so that the rulebook will always be completely up to date and current. Can you guarantee that?"*

**His ruling, 8 October 2026, whole:** *"Hold on, the cap doesn't appear to work. We tried that in the past. And what happens is we just run into errors in the system that need updates, but we are simply forced to not apply the update, meaning the failure continues because we can't fix it because we've got a cap. The answer must be that we should always be allowed to fix the rulebook and to upgrade the rulebook, but we must do so in a way that removes all of the dead information at the same time. Do you agree? And how can we apply this principle across the board? The only measure of success is the building of world-class software that we can monetize as fast as possible. That's the only metric that works."*

**The answer he was given:** a commitment, not a guarantee. Every rule change reconciles the rules it touches, removes what it demonstrably supersedes, and keeps every live requirement. A stale statement nobody connects to a change can survive until cleanup or a failure finds it.

**Agreed points:**

1. The rulebook wins over any brief. Product work stays first; rulebook cleanup is the second lane.
2. No exception to the review gate. An unread change parks.
3. No stale-word or history-pattern check, no per-page field, no new review stage.
4. Request, recovery and spending limits are not authoring caps and are untouched.
5. Frozen decision records keep their text.
6. Finished and retired items are not automatically stale: what current behaviour, decisions or required evidence still rely on is kept. Changing what must be kept is an explicit change by its owner, never a side effect of cleanup.
7. A size reading never fails a change and never becomes a cleanup debt on an unrelated change.
8. Affected rules and their consumers are found by focused searches, not by reading the whole repository to be safe.
9. The three authoring ceilings in `check.sh` (the operating page 600 words, the screen law 450 words, a library page 4,000 bytes) become reported numbers. The two context-size assertions on the real tree in `review-gate.py` (60,000 and 120,000 bytes) become reported growth; the deterministic over-selection and coverage tests stay.
10. The reviewer's brief carries the reconciliation duty: for each rule changed, its current owner and affected consumers stay consistent; a demonstrated contradiction, a retained superseded instruction, or a deletion or relocation that loses an operative requirement is blocking; a specific missing dependency is needs-context; extra length alone is never blocking; each blocker names its concrete counterexample.
11. Every live owner of the caps is reconciled in the same pull request. Its checks are not claimed to prove the reviewer's new duty, and the new wording counts only once merged: that pull request is judged under the brief it replaces.
12. The justification under `CHARTER.md` §13 is his ruling above, nothing else.
13. A cleanup list, one tracking issue, shows every rule page, what is stale or conflicting on it, and its status; entries close on merged evidence.

**AGREED:** replace blocking authoring caps with size signals and reconciliation of affected rules through the existing cold review, in one coherent mechanism PR, while bounded cleanup and eligible product work proceed — **changed by:** the false-positive and migration failures of historical-language lint, the core-cap counterexample and the hidden context-size gates — **strongest objection left:** a cold reader can miss an unknown stale dependency, so this mechanism improves detection and repair without guaranteeing permanent completeness.
