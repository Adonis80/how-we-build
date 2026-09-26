# Decision 0009: a boundary is a decision, not an exit

**Consensus of the CTO (Claude, Juku OS Cowork session) and the consultant (Astra, GPT-6, high effort), 26 September 2026, three rounds; the decision record is [issue #114](https://github.com/Adonis80/how-we-build/issues/114).** Revises [decision 0006](https://github.com/Adonis80/how-we-build/issues/92). What lands is `library/session-changeover.md` replaced whole and one paragraph of `HOW-WE-BUILD.md`; this record is the reasoning.

## The question

The Chairman, 26 September 2026: code mode "was telling me to start a new session after barely doing any work", and asked the two of us to reach consensus on the best solution. The failing case, all on GitHub: a `how-we-build` code session booted (roughly 200K tokens of reading, most of it on Vercel) to take PR #99, whose own body said it needed a deploy key stored — a thing a code session cannot do; parked it as PR #113 with a one-line diff; then, because decision 0006 made every boundary a session end ("the next bounded work starts fresh, always"), left — while PR #111, a fix to a file it had already loaded, sat ready one item down the queue; and said "ready to start fresh session" once more on a routine check failure that changed nothing.

## What was agreed

1. **Readiness before any deep read, and it attaches to the action, not the pull request.** The first act on a queue item is to find, from its live body, the outcome asked and the next action this session can perform, verifying only the blockers that decide it: a secret, hands, a decision of his, an unmerged dependency. A `Ready:` line is where to look, never an authority; no field migration across existing pull requests. Missing information is unconfirmed readiness, settled by a focused check; an investigation is its own bounded action. A blocked action is parked with its unblock condition and the next eligible item assessed. Hands needed by one item is not a session end, and not an obligation to find something else either.
2. **A boundary is a decision, never an exit by reflex.** A session continues onto the next eligible item, same repository and stack, only after a positive assessment: continuing is preferable to starting fresh; the item's next action is ready; retained understanding demonstrably helps — the session can state the item's bounded outcome, the evidence it will reuse and the reading still needed without reconstructing its grasp of the last item; the rulebook permits it; no degradation or hard-stop condition is present. Same repository and stack is eligibility, not evidence.
3. **The boot paid is sunk.** What is compared is the remaining work, verification and likely rework under continuation against a fresh start. No global cache-age, idle, token, clock or load threshold decides it; no boundary-count cap either.
4. **Targeted verification before acting, not a second boot**: the target's head and diff, its checks, reviews and dependencies, and a working tree carrying nothing from the item left. Then `Continued: <from> → <to> — main <sha> — reuse <what>; next <outcome>` on the item taken, when continuation actually begins.
5. **Rules that land meanwhile.** The governing revision is fixed at boot and at each accepted boundary transition; no later rule is taken on mid-slice. At a boundary the session compares the rulebook's `main` with that revision, reassesses which pages it now needs, reads those added or changed, then adopts the verified revision. A change to `HOW-WE-BUILD.md`, a required rebootstrap, or inability to apply the changed rules ends the session. Never a queue worked under an old rulebook; never adoption mid-slice.
6. **Degradation stops unchanged.** A routine check failing, or an expected change to repository state, is neither a boundary nor degradation: diagnose it inside the item.
7. **Measurement narrowed.** `Checkpoint:` and `Resumed:` stay; `Resumed: corrected` now says whether the fact was wrong at handover or changed since, and a fact wrong at handover counts against continuing only with evidence linking it to carried assumptions. The lines are evidence for revising the page, not a controlled measure.
8. **"Ready to start fresh session" is said only once the session has decided it must end**, as a claim checked first.
9. **The loop paragraph** reads: one builder session at a time per repo; readiness checked before deep reading; at each boundary it weighs continuing against starting fresh — a boundary alone never ends it, degradation and hard stops do. "At a time per repo" serialises builders and is also the Chairman's 25 September ruling that two sessions never work the same repository at once; it says nothing about advisory or reviewer sessions.
10. **Codex**: the same continuation test applies across slices within a cloud task or thread. The earlier per-slice sentence would have reinstated the rule being replaced for one stack.

## Rejected and withdrawn

- CTO, withdrawn: "mostly already loaded" as a continuation condition (files having been read shows potential reuse, not usable understanding); "hands needed by one item never end the session" as an absolute; "only a fact wrong at handover counts against continuing" (timing classifies, it does not establish cause); the argument that "always fresh" fails merely by being a global rule — the ground is the Chairman's 10 September ruling to weigh at every turn, and the evidence "always" excludes, not symmetry with rejected numerical rules; and a permanent boot baseline for rule adoption, which would have contradicted itself after the first boundary.
- Consultant, withdrawn from 0006: "different slice always means fresh session". Its round-one point that resumption and boundary crossing carry the same risk was refused — a boundary introduces a new outcome and needs targeted verification plus an explicit reset of scope — and that refinement is in (4).
- 0006's escape hatch, "fix the slicing where the roadmap's `next` lines are written", does not exist for this repository: its queue is its open pull requests, many one-line word changes, under a freeze that puts one session's words in one pull request. Both sides accepted the gap.

## Settled without new wording

- The tidying freeze governs words a session **writes**, whichever pull request they land in; advancing an existing pull request without originating words is the clean case. No sentence added.
- A change to `HOW-WE-BUILD.md` is a deterministic stop; a changed library page that an item's trigger names is re-read and reassessed, and stops the session only if it requires a fresh boot or cannot be applied reliably.

## Dropped from the 0006 page, on purpose

The page is at its byte cap, so the rewrite kept every rule that still governs and cut two that did not: the temporary `START-HERE.md` for advisory work with no repository yet (GitHub is the one source of truth, his ruling of 25 September; an advisory result goes into a repository's pull request or issue, never a loose file), and the handover test "if the next session's opening words would have to carry project state, it is not finished", which "the pull request and roadmap handover stand alone" and the checked claim behind "ready to start fresh session" now carry between them. Kept, after the reviewer's read: mid-slice resumption after a gap verifies the branch, pull request and `main` facts first; and the slicing remedy for products, whose roadmap `next` lines do exist.

## Still unproved

- Whether a session judges "continuing is preferable" honestly, or the assessment becomes a reverse sign-off; the `Continued:` / `Resumed:` lines are the only check, and they miss what no one later detects.
- The consultant could not read the live repository during this exchange; its approval is of the procedure, and the diff is read cold by the reviewer as usual.
