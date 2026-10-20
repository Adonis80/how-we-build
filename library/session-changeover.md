# Session changeover

Scope: every session, in either stack. Open when: deciding whether to stay in a session or start a fresh one, and before leaving one.

**One brief per session**: one bounded deliverable and a stop condition. Hand over when it is met or blocked, at about 400,000 tokens of context whatever the progress, and before ending a turn on a wait of an hour or more (on him, a review, a check it cannot watch) once past about 150,000 tokens, since resuming a large session reloads it all. No repeated investigation without new evidence. A fresh session rebuilds its picture from the repository and issues, never the old chat.

**The cost.** The boot already paid is sunk; compare the remaining work, verification and likely rework of continuing against a fresh start. No other clock, cache or idle threshold decides it. Boots that routinely dominate product slices mean wrong slicing: fix it where `next` lines are written.

**A product code session** starts with both repositories attached, the product's and `Adonis80/how-we-build`. From the rulebook it may dispatch only the asker (`ask-product-reads.yml`) and the recovery route (`review-product.yml`); rulebook words change only from an advisory session, by pull request.

**Readiness before any deep read.** From the item's live body, find the outcome and the next action this session can take, checking only the blockers that decide it: a secret, hands, his decision, an unmerged dependency. A blocked item is parked with its unblock condition and the next is assessed.

**At a boundary** (slice merged, parked with its blocker, or advisory question settled) continue to the next item in the same repository and stack only when all hold: it is within the brief and short of the limits above; its next action is ready; retained understanding demonstrably helps (the session can state the item's outcome, what it reuses and what it still must read); and no degradation is present. Before acting, verify the target's head, diff, checks, reviews and dependencies and a clean working tree, and record `Continued: <from> → <to> — main <sha> — reuse <what>; next <outcome>`. Otherwise checkpoint and leave.

**Rules that land meanwhile** bind at the next boundary, never mid-slice: fix the rulebook revision at boot and at each boundary; at a boundary compare `main` with it and read what changed. A change to `HOW-WE-BUILD.md` ends the session.

**Stop on degradation**: the repository disproves something the session asserted; the repeated-failure signs in `HOW-WE-BUILD.md`; it cannot state the slice, next action and open findings without reconstructing them; or the surface reports the history compacted. Finish the operation in hand, write and verify the handover, leave.

**Leaving.** Every durable fact goes into GitHub. The checkpoint comment names its cause, `Checkpoint: boundary — slice complete | parked: <blocker> | advisory settled` or `Checkpoint: degradation — <sign>`; the next session's first comment is `Resumed: clean` or `Resumed: corrected — <fact>`. "Ready to start fresh session" is said only once the repository carries what the next session needs; for a product code session it names both repositories. Codex applies the same test across slices within a task.
