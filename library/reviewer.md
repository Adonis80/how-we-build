# The independent reviewer

Scope: every repository under this rulebook, in either stack. Open when: working out who reviews a change, what it is shown, or what a risky class of change is owed.

**Who.** Step 5 of `HOW-WE-BUILD.md`: one reviewer reads every pull request cold, in every repository under this rulebook. It answers only as the `juku-reviewer` App's check run (`library/reviewer-verdict.md`); the model behind it is the registry's to name, by role (`library/model-registry.md`), and only open-weight models review, except the rare risky change, which Opus 5.5 reads at high (decision 0019). Codex does not review anywhere (his ruling, 22 September 2026). A product never changes who reviews, or what a class is owed, on its own: that changes here, in step 5.

**What it reads.** The *change*: the diff, the tests, what regressed, and whether the change's own claims match its code. Independent means a session of its own, forming its view from the diff and the tests before the pull request's own account; it does not challenge a design. It is shown the diff against `main`'s tip, not the pull request's base, and the pages as the change leaves them, never the pull request's body or thread, so an answer to a finding that lives only in a comment never reaches it. Nothing is pasted between models and nothing passes through the Chairman. Its brief is the repository's own `AGENTS.md`, which is why this repository, though not a product, carries one.

**What a read is shown is a selection, risky or not** (his ruling, 9 October 2026, [decision 0018](../juku-library/DECISION-0018-READ-NARROWING-ON.md)): the touched files, past 40 KB as their touched sections, their partners both ways, the pages naming them and the registry; every other file is named and sized. A reader needing more asks for a file or one unit of one, and gets each whole or the read stays incomplete.

**The ask.** A comment on the pull request that opens with `/claude review`; only one that opens with it, so a comment quoting it spends nothing. The reviewer reads the current commit and signs a verdict on it.

**The six risky classes**: pricing logic; live database mutation or schema; authentication and authorisation; public trust-boundary changes; deploy and release machinery; and the review gate itself. They go to `reviewer-risky` (`library/carries-reviewer.md`) and get one cold read, like everything else. A change to the gate is judged by the gate it proposes, since `check.yml` runs the head's own `check.sh`: this repository's check prints a `note:` line on any such pull request, green or red, so a reader weighs the diff rather than the green.

Every pull request carries `Lead stack:` and `Reviewed by:`.
