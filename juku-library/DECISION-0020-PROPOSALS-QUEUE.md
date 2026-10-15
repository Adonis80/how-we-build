# Decision 0020: one proposals queue — every idea battle-tested before it is built

**Agreed by the CTO (Claude, Opus 5.5 high) and the consultant (Astra, GPT-6.1 Sol high), 13 October 2026, two rounds, AGREED; the decision record is [issue #199](https://github.com/Adonis80/how-we-build/issues/199).** Asked by the Chairman, 13 October 2026: every improvement idea goes into one queue, contributed by every product, battle-tested by Claude and GPT before anything is built, so products don't diverge and each contributes to the whole system. It stands under CHARTER 13 as his explicit ruling about how he wants the system to work. [Decision 0011](DECISION-0011-IDEAS-FOR-LATER.md) and [decision 0012](DECISION-0012-SHARED-IDEAS.md) are not edited; this record supersedes them in one place, the route of a rulebook or shared idea, which was a pull request and is now a `proposal` issue. Every other sentence of theirs stands. It holds no product text: the rulebook is public.

## What was agreed

Issue #199's seven points, verbatim.

1. **One view, two owners.** The build board shows one ranked list of every idea. Ownership stays where it lands: a product-only idea is a `proposed` item on that product's roadmap under [decision 0011](https://github.com/Adonis80/how-we-build/issues/142)'s joint review; a rulebook or shared idea ([decision 0012](https://github.com/Adonis80/how-we-build/issues/145)'s test) is a rulebook issue labelled `proposal`, written generally (the repository is public).
2. **Nothing is built before its review agrees**, except a proven defect's repair. Chairman-reserved decisions and the independent PR review stay as they are.
3. **Agreement grants eligibility, not a pull request.** The PR opens when work starts. The issue records the decision, next action and implementation link. Agreed ideas never outrank authorised revenue work.
4. **Ranking:** recorded priority with its reason, then dependencies, then oldest.
5. **When debated:** batch intake when 3 proposals await debate or one is 7 days old (trial thresholds), counted at an active session's opening, never on a timer; each proposal settled and recorded separately; early debate when the current slice needs it. No consultant: pending, other work goes on.
6. **Contribution:** each product session's closing handover asks "Any material system improvement found?" "None" is valid; no invented ideas. Search open and closed proposals and PRs first; new evidence goes to the existing owner.
7. **Pages to reconcile in one rulebook PR:** `library/ideas-for-later.md` (a lift is a proposal issue, not a PR), README, `library/changing-the-rulebook.md`, the session/efficiency guidance, and the board (open proposals in its ideas card, refreshed when issues change). Existing issues are linked, not duplicated; active PRs and old decision records are untouched.

## What changed whose mind

Astra moved the CTO on: agreement not auto-opening a PR; real ranking; trial thresholds checked at session opening, not timers; "none" as a valid answer instead of a daily idea; reconciling every page that describes the route. The CTO moved Astra on scope: one view, two owners, so product ideas aren't debated twice.

## The strongest objection left

Astra's: review effort may still exceed the savings and delay revenue delivery; the keep-or-revert test must count that cost even when every proposal was handled correctly. `library/ideas-for-later.md` carries it into its month test.

## Where it is written

The pull request that adds this record: `library/ideas-for-later.md` owns the route; `README.md`, `library/changing-the-rulebook.md`, `library/carries-sessions.md`, `library/session-changeover.md` and `library/build-board.md` point at it.

**Not yet built: the board's half of point 1 and point 7.** The board's reads are made by its workflow, whose token reads pull requests and checks but not issues, and wakes on pull requests and verdicts but not issues; that scope is held by the review gate. Listing open proposals on its ideas card needs a change to the workflow and the gate, which this words change does not make. Until then the queue is read from this repository's open issues labelled `proposal`, and the board's ideas card shows product ideas only.

**First proposals:** the reviewer-wait investigation ([#200](https://github.com/Adonis80/how-we-build/issues/200)), and [#197](https://github.com/Adonis80/how-we-build/issues/197) (modular architecture, agreed), linked, not duplicated.
