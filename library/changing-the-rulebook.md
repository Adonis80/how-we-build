# Changing the rulebook

Scope: this repository. Open when: changing a rule, proposing, prioritising or merging a change to this repository.

## The queue

**"Build" here takes the open pull request that is ready, highest priority first and oldest within a priority** (his priority model, R-2026-09-22a). This repository has no `roadmap.json`; its queue is its open pull requests, and each carries a `Priority:` line in its body, set by test rather than by feel:
- **P1**, stop the line: a reproducible failure that blocks a required build, check, review or deploy, lets through what should be refused, loses, duplicates, corrupts or deletes work or data, or crosses a trust boundary wrongly; it names the failing case.
- **P2**, repair: a reproducible wrong result short of that.
- **P3**, build: approved new capability with no failing case.
- **P4**, observe: removing it would leave what runs unchanged.

His asking for something makes it authorised, not P1: priority is the state of the system, not who asked. Ready comes first so priority cannot bulldoze a dependency or a decision that is his: a pull request waiting on his answer is not ready, and the next is taken. One with no `Priority:` line gets one from the first session to read it, written into its body so no later session derives it again.

A session started on *build* with this repository chosen reads them in that order and moves one on (answers its findings, pushes the round's fixes as one push, asks once) or closes one that is stale. A bug the consultant reported here as an issue opening `Written by: Astra` (`library/consultant.md`, *What it writes*) is read with the open pull requests and taken by its `Priority:`, its pull request closing it. With none ready, the top agreed `proposal` issue is next, its pull request opened when that work starts ([decision 0020](../juku-library/DECISION-0020-PROPOSALS-QUEUE.md); `library/ideas-for-later.md` ranks and debates them). With neither, there is nothing to build here: say so and stop. An improvement reaches a pull request only once its proposal is agreed; a proven defect's repair, and a change he rules himself, need no proposal.

**Until first revenue** unrelated audits and shared-platform construction are paused; delivery-blocking defects are still repaired; cleaning the rules is never paused (R-2026-10-20a).

## The gate and the merge

By pull request only; `main` is protected. `check.sh` runs in CI and refuses a file not on the list, anything that looks like a secret, and, in a pull request, a commit the reviewer has not read clean: unread, or read and left a blocking finding on.

**Its self-test runs in parts.** In a pull request: a fast core, and only the parts measured to read a changed file. Every part runs on a push to `main`; on a change to `check.sh`, `review-gate.py` or a workflow; on a file no part is measured to read; and while `main`'s own newest finished check is red or none has finished, since a run of parts trusts `main`'s whole run. So a red `main` is repaired by an ordinary pull request, which runs whole, and nothing holds it.

Adding a rule, step, file, check or agent needs the charter's gate (§13): the same failure twice, in two separate product tasks. Removing one, or correcting wording, needs no gate; nor does a change the Chairman rules himself.

**An agreed, reviewed change counts as his ruling.** Where he has not ruled on a change to how we build himself, it counts as his ruling once the consultant and the CTO agree it and the independent review passes it; whatever *Who decides* keeps his (money, permissions, product truth, anything irreversible, how things look) still goes to him (R-2026-11-04b). The agreement is cited, dated, in the changed text.

**The CTO settles and merges changes to this page and this repository**, without the Chairman (R-2026-09-09a). The reviewer still reads every change cold, and the gate above still applies.

**And the merge is the session's own, here and in every product: step 7 of the loop** (R-2026-09-25b). So no pull request's next action names him or another session as the hand that merges it. His look at a material user-facing change still comes first (step 6, `CHARTER.md` §12).

**Here that hand is GitHub's auto-merge** (R-2026-10-11a): after its last fix and its one ask, the session enables auto-merge (squash) on the pull request and ends its turn, waiting on nothing. Bring the branch up to date with main immediately before asking; if main moves again and prevents merging, update and obtain a fresh read. `main` requires `check`, green only on a commit the reviewer has read clean, so GitHub merges when the read lands and the wake re-runs the check, and never an unread commit. A product's own merging hand is `library/carries-sessions.md`'s (*Its machinery*).

**If a session truly cannot merge** (R-2026-09-25b): a session that can merge its own pull request does; one that has no hands hands the merge to another session, with the words to start it, and never to him; one whose size hook refuses hands over and its successor merges (`library/session-changeover.md`, *One brief*); one whose consent guard (the platform's) refuses handles it as `library/his-opener.md` alone says, and never hands the merge to him (agreed under R-2026-11-04b, 6 November 2026, how-we-build#371).

## What a change carries

**No word limits; a hierarchy of information** (R-2026-11-04c). No page has a word cap, a product's constitution and `AGENTS.md` included, and a change owes no cut for the words it adds. The guard is the shape instead, which `check.sh` holds: the front page routes, every library page is named in the README's index with when to open it, and a session loads only the pages its task's trigger names. A page splits where a distinct task can then read less, never to fit a number; one home per rule still keeps the text from repeating.

**The `Replaces:` line.** A pull request that changes a rule page carries `Replaces: <what it replaces>; products: <product pages updated, or none>`, or `Replaces: nothing — not a check because: <why>`. `product-reads/rules-check.py`, run by `check.sh`, requires the line; the reviewer never sees it, and blocks from the diff any replaced text left standing. Run by a product with `--product` over its rule pages (`AGENTS.md`, `CLAUDE.md`, `NAMES.md`, `design/`), it also holds that product's `design/CONSTITUTION.md` to the headings *Tokens*, *Units*, *Money*, *Domain law* and *Approved by picture*, each approval dated and naming its picture. A product runs it from a pinned rulebook commit once its own pull request adds the line; until then nothing checks these there by machine.

**What a rule change owes.** For each rule it changes: find the current owner and the consumers it affects, by focused search, not by reading everything; make them agree; delete what the change replaces; keep every live requirement. Shorter must never mean weaker: a trim that drops a requirement is a loss, not a saving.

**Source first** (R-2026-11-04d). A change of meaning or scope, a trim of meaning included (never spelling or a pointer), starts from his originals in `juku-library/` and his later rulings: each side names the affected obligations before reading another's interpretation, and the pull request marks each kept, weakened, lost or contradicted, with its authority. The reviewer never sees that body, so the changed text rests on the source words it relies on (his, by the register id whose entry holds them: *Coherence*), cites each source as `path#heading` (a read may ask for it), and names its dated authority beside each weakening, loss or contradiction; one without is a loss. The cold review holds this (`AGENTS.md`); `check.sh` does not.

**The exam** is the cold review's too (`AGENTS.md`, *The exam*). A product's reviewer's brief, its `## Review guidelines`, ends with short questions of its own, answered, added and removed the same way, and read from `main`.

**Batches.** Word changes go in several small pull requests, each dependency-coherent and asked once per round, since small reviews cost cents (R-2026-10-09a). A page is moved, merged or reworded whenever that removes stale, duplicated or conflicting text, every operative condition kept whole at its owner and each conflict listed in its pull request, inside a change that touches it or as cleanup of its own (R-2026-10-08a; [decision 0017](../juku-library/DECISION-0017-SIZE-SIGNALS-AND-RECONCILIATION.md); [decision 0016](../juku-library/DECISION-0016-LOCALISED-REVIEWS.md) H). Rulings made under the lifted tidying freezes stay quoted in their own pull requests and records.

## Coherence

His words live once, in `library/rulings.md` (R-2026-11-09c): one entry per ruling, with its id, its source, its one home, and his words whole. A ruling of his about how we build is not on the record until it is in this repository, exactly as a product decision is not until it is in that product's.

A rule page states each rule once, in plain lines, and cites the entry's id; it never quotes him. A rule another page owns is pointed to, never restated. What a change replaces is deleted, never annotated: git keeps history. `product-reads/coherence.py`, run by `check.sh`, holds this: every dated ruling of his on a rule page cites an id, and the id's home cites it back; no eight words of an entry stand on a rule page; no fourteen-word run appears twice across the rule pages; no line keeps the history of a replaced rule; no paragraph passes 1,600 bytes, and no section 12,000.

## The upgrade log

A pull request that changes what runs adds its one line to `library/upgrade-log.md` in the same pull request; the gate is red until the pull request changes that page, and the cold review reads that the change is its line.
