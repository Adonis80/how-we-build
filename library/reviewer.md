# The independent reviewer

Scope: every product and this repository. Open when: asking for a read, answering one, or a slice cannot get one.

**Who.** One reviewer: the model and effort named in this repository's `review-gate.py`, today Claude Sonnet 5 at max effort (his ruling). Codex is retired as a reviewer (his ruling) in every repository whose gate counts the badge: this one and Hemz OS. Myst's gate still counts only the Codex bot until the pull request that ports the badge lands there, and that port is the next work. Until then its pull requests ask `@codex review`, and an OpenAI-led slice there does not start in the six classes (pricing, live database changes or schema, authentication and authorisation, public trust boundaries, deploy and release machinery, the gate itself): Claude leads it, and unsure means crossed. Where the badge counts, there is no second read on any class (his ruling), and nothing covers the reviewer's absence.

**What it reads.** Cold, in its own run: the diff against `main`'s tip, never the pull request's base, and the pages as the change leaves them. Its brief is the repository's `AGENTS.md`, taken from protected `main`, never from the head. It is never shown the pull request's body or thread, so an answer that lives only in a comment never reaches it. It reviews the change (the diff, the tests, what regressed, whether its claims match its code) and does not challenge a design. Every pull request carries `Lead stack:` and `Reviewed by:`.

**Asking.** Here: a comment that opens with `/claude review`; a comment quoting it spends nothing. For a product: a writer dispatches `review-product.yml` on `main` (`review-machinery.md`). Nothing is pasted between models or passes through the Chairman.

**One ask per round.** The allowance is one pool for every repository, and an ask per small push empties it for all. So a round's fixes land as one push, then one ask, then stop. The check turns green by itself when the verdict lands, so nothing is gained by watching. Two rounds bind the CTO too: answer what the first two raise, then land with any dissent left standing on the pull request. A third round means the slice is too big: shrink it and ship what is proved.

**A read clears only the commit it read.** A later push voids it. The verdict is a check run on that commit, and the check reads it by itself, with no hand re-run. Here the proposer may not clear its own addition: findings keep the head red until the push that answers them is read clean. A report to the Chairman names the commit reviewed.

**Parking.** A slice parks only on a refusal it was given itself, on that pull request, in that hour. Never park on a note, a roadmap line or another session's report that the reviewer is out: ask, then park on the answer. When the gate can count no read (the reviewer unreachable, its allowance spent, the service down), the gate neither opens nor is waived. The slice parks with one comment naming the blocker, then no pushes and no asks.

Nothing watches for the reviewer's return. The next session to start asks on the first parked pull request, in the repository's own order, and the rest follow one ask each. Meanwhile the next slice starts from `main` in its own session. None of this reaches the Chairman unless it moves something he was promised.
