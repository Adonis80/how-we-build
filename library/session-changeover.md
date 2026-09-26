# Session changeover

Scope: every session, in either stack. Open when: deciding whether to stay in a session or start a fresh one, and before leaving one.

His rulings: 10 September 2026, at every turn weigh whether staying or starting fresh is cheaper; 25 September, the session decides that itself; 26 September, a boundary never forces a fresh session after barely any work. Settled with the consultant as decision 0006, revised as [decision 0009](https://github.com/Adonis80/how-we-build/issues/114).

**The shape of the cost.** The boot paid is sunk. Compare the remaining work, verification and likely rework under continuation and a fresh start. No global cache-age, idle, token, clock or load threshold decides it.

**Readiness before any deep read.** The first act on a queue item is to find, from its live body, the outcome asked and the next action this session can perform, verifying only the blockers deciding it: a secret, hands, a decision of his, an unmerged dependency. A `Ready:` line is where to look, never an authority. A blocked action is parked with its unblock condition and the next eligible item assessed. Missing information is unconfirmed readiness: settle it with a focused check; an investigation is its own bounded action.

**At a boundary** (slice merged, parked with its blocker written, or advisory question settled) the session decides; never leaving by reflex. It continues onto the next eligible item, same repository and stack, only when all hold: continuing is preferable to starting fresh; that item's next action is ready; retained understanding demonstrably helps, meaning the session can state the item's bounded outcome, the evidence it will reuse and the reading still needed without reconstructing its grasp of the last item; the rulebook permits it (below); no degradation or hard-stop condition is present. Before acting it verifies the target's head and diff, its checks, reviews and dependencies, and that the working tree carries nothing from the item left, then records on the item taken `Continued: <from> → <to> — main <sha> — reuse <what>; next <outcome>`. Otherwise it checkpoints and leaves.

**Rules that land meanwhile.** Fix the governing revision at boot and each accepted boundary transition; take on no later rules mid-slice. At a boundary compare rulebook `main` with that revision. Reassess required pages and read those added or changed before adopting the verified revision. A change to `HOW-WE-BUILD.md`, a required rebootstrap or inability to apply the changed rules ends the session.

**Stop on degradation** inside any item, on any one of: the repository disproves a material state the session just asserted; the repeated-failure signs `HOW-WE-BUILD.md` owns under *When something goes wrong*; the session cannot state the slice, next action and open findings without reconstructing them; the surface reports the history compacted. Then no new substantive work: finish the operation in hand, write and verify the handover, leave. A routine check failing, or an expected change to repository state, is neither a boundary nor degradation: diagnose it inside the item.

**Leaving.** Every durable fact goes into GitHub; the pull request and roadmap handover stand alone. The checkpoint comment names its cause: `Checkpoint: boundary — slice complete | parked: <blocker> | advisory settled`, or `Checkpoint: degradation — <sign>`; the next session's first comment says `Resumed: clean`, or `Resumed: corrected — <fact>, wrong at handover | changed since`. A fact wrong at handover counts against continuing only with evidence linking it to carried assumptions. These lines are evidence for revising this page, not a controlled measure.

**"Ready to start fresh session" is said only once the session has decided it must end**, as a claim checked first: the repository carries what the next session needs, nothing pasted.

For Codex, the same continuation test applies across slices within a cloud task or thread.
