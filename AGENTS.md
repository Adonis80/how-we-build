Rulebook: this repository. A session reads `HOW-WE-BUILD.md`; this file exists for the reviewer of changes to the rulebook itself, because a reviewing tool loads only `AGENTS.md`. It is the brief for the reviewer — the badge, asked with `/claude review` — and `.github/workflows/review.yml` reads it from protected `main`, never from the head under review, so a pull request cannot write its own reviewer's instructions.

# AGENTS.md — how-we-build

What is particular here: this repository is the rulebook, not a product. It changes only by pull request against protected `main`. Adding a rule, step, file, check or agent needs the charter's gate (§13) or the Chairman's own ruling; removing one, or correcting wording, needs neither. The proposer does not clear its own addition; the cold review does (§13). So the CTO may merge an addition of its own only on a commit a reviewer has read and left no blocking finding on, never on one where it answered a blocking finding. Disagreeing with a blocking finding is not clearance: the disagreement goes to the Chairman, who settles it.

`check.sh` holds that rule, not a hand: green only on a commit a reviewer has read and left nothing blocking on, red while the head carries a blocking finding. The answer to one is a push, whose commit the reviewer reads afresh. An advisory finding opens the gate and stays standing on the pull request, the CTO's to take or leave; which a finding is, the reviewer says, never the proposer (R-2026-09-24a). The Chairman's hand is not the control: he approves by looking (R-2026-09-14a). `check.sh` is the only check; `.github/workflows/review.yml` is a reviewer it waits for, not a second check. There is no `roadmap.json`: the queue here is the open pull requests (`library/changing-the-rulebook.md`).

**One reviewer.** It answers one way only: as a check run created by the `juku-reviewer` GitHub App, a login no branch can wear, a signal no writer can edit or erase. Its private key sits in the `reviewer` environment, which admits `main` alone, and `.github/workflows/door.yml` is the standing proof of that. Nothing is read out of prose: the gate counts no comment and no submitted review, which `_check_routes` enforces by refusing a register entry that carries a login at all. The model behind that identity is routed by risk from `model-registry/registry.json`, the only file that names one ([decision 0008](https://github.com/Adonis80/how-we-build/issues/103)): ordinary changes to `reviewer-main`, open-weight and at max, with nothing behind either (R-2026-10-05a); when the role does not read, the commit stays unread and he is told on an issue. Risky ones go to `reviewer-risky` (R-2026-10-09c); on a gate change, that is the lead's own model reading the gate. Who holds each role, at what effort, is the registry's to say, and only the registry's.

**A gate change is judged by the gate it proposes.** A change to `check.sh`, `review-gate.py` or anything under `.github/workflows/` clears on the same single read as anything else (R-2026-09-22c), and `check.yml` checks the head out and runs that tree's `check.sh`. The check prints a `note:` line saying so on any such pull request, green or red; it shuts nothing. On a gate change, read the diff rather than the green, and treat that class as the one where a finding is worth more than a clean pass.

## Review guidelines
The brief is *The independent reviewer*: `library/reviewer.md` and the pages the README's index names beside it; these lines repeat the least of it the tool needs in front of it. Address the CTO. Form your view from the diff and the existing pages before the pull request's own account. With each finding say what you checked, what you did not, and how sure you are. Mark each finding blocking or advisory, or needs-context naming the files the read lacked, which is read once more with them; give every finding in one read. Two rounds at most, then as the brief says. Prefer a deletion to another exception, and do not manufacture disagreement. Never write a file into this repository.

For each rule a change touches, its current owner and the consumers it affects stay consistent: block a demonstrated contradiction, a replaced instruction left standing, or a deletion or relocation that loses an operative requirement; a specific missing dependency is needs-context; extra length alone is never blocking; each blocker names its concrete counterexample.

**Hazards particular here.**
- An addition to how we build without the gate or the Chairman's ruling; a file not on the list; provider-specific detail leaking into a global rule; a rule kept in prose that `check.sh` could hold.
- Any claim that *build* is self-sufficient when a fresh session in either stack could not actually recover the work.
- **A gate change, which is one read of the gate by the gate it proposes**: weigh it on the diff, and treat a clean pass on it as the weakest evidence here, not the strongest. A gate change whose `note:` line is missing, or waved through on a green the change itself produced.
- The gate's register of reviewers and the wake job's condition drifting apart, so a read lands that nothing re-runs the check for.
- The reviewer workflow gaining any trigger beyond `issue_comment`, or losing its `environment: reviewer` line: either lets a branch run a reviewer of its own writing or reach the key it signs with. Its ask reachable by somebody who cannot already write here, this repository being public and its reviewer spending a shared allowance.

- The Roadmap's build, `build-board.yml`: printing anything a product holds, or a key, into this repository's public logs; gaining a trigger, a wider token, an App key or a read; checking out anything of a pull request; uploading an artifact; able to leave a deploy live that no smoke has passed.
- The Roadmap's function, `board/build.py`: reading with more than a GET, from a host beyond GitHub and OpenRouter's daily activity; following a redirect; sending one key to the other's host; reading a product off the map.
- The product reviewer, `review-product.yml`: printing anything a product holds into this repository's public logs; signing a commit it was not given; reading a product the README's map does not list; holding a token that reaches past the one product.
- The asker, `ask-product-reads.yml`: gaining any trigger beyond `workflow_dispatch` and its one ten-minute `schedule`, the only timer under this rulebook, which no product gets (R-2026-10-04a); asking twice about a commit; retrying a read that failed; reading a GitHub error as "nothing ready"; holding a token past read on one product; asking for a read `review-product.yml` would refuse.
- `product-reads/` changed without its selftests, or the starter kit's gate or wake drifting from the rulebook's own.
- Machinery described on a page before a run has shown it working.

**The exam** (R-2026-10-20c; placed in this brief, read from `main`, by its agreed debate). On a change to a rule page (`HOW-WE-BUILD.md`, `README.md`, `CHARTER.md`, `RICH-DATA.md`, `AGENTS.md` or a library page, as `product-reads/rules-check.py` counts them), answer each question below that the change could affect, from the pages as the change leaves them. Each answer names its owning page. A wrong owner, two pages giving different answers, or no page answering is blocking. A question is added or removed with its rule; the brief is read from `main`, so a change is judged by the questions already there.

1. On a Hemz screen, which decides the look: HyperSolid or Hemz's own pages? — HyperSolid (`HOW-WE-BUILD.md`, *Which rule wins*); Hemz supplies tokens, units, money and domain law, and dated picture approvals.

2. A product's constitution says "no spatial layer" with no dated picture approval. Does it bind? — No; void (*Which rule wins*).

3. Memory says one thing, the rulebook another. Which wins? — The rulebook; memory is never a rule (*Which rule wins*).

4. `PRODUCT.md` and `roadmap.json` disagree. Which wins? — `PRODUCT.md`; the copy is corrected (*Which rule wins*).

5. Who decides a product's prices, figures and how it looks? — The Chairman (*Who decides*).

6. Who decides a technical question, and may the session ask him? — The CTO; never ask him (*Who decides*).

7. Who merges a green pull request? — The session itself (loop step 7); here, GitHub's auto-merge, which the session enables (`library/changing-the-rulebook.md`); in a product with its ruleset, the same, once his look is not owed or given (`library/carries-sessions.md`).

8. How many review rounds, and what after them? — Two; then the CTO's call, dissent left standing; a disputed blocking finding goes to him (`library/reviewer.md`).

9. The reviewer is unreachable. What happens? — The slice parks, one comment, the next item begins (`library/reviewer-parking.md`).

10. May a session set a timer to check back later? — No (`HOW-WE-BUILD.md`, the loop).

11. Where does a new rulebook rule's text go, and what must leave? — Its one home; what it replaces, in the same pull request (`library/changing-the-rulebook.md`).

12. A change makes a page longer. Must it cut words elsewhere? — No; no page has a word limit, and a page splits only where a distinct task can then read less (`library/changing-the-rulebook.md`, R-2026-11-04c).

13. What must a product's constitution contain, and nothing else? — Tokens, Units, Money, Domain law, Approved by picture (dated, with the picture) (`library/changing-the-rulebook.md`).

14. Where are past decisions, and when are they read? — The decision issues and `juku-library/`; read only when a rule is changing or its reason is questioned, or a build needs a paper; never loaded into a working session (`library/rulebook-files.md`).

15. What reaches the Chairman, and how? — Money, a permission, product truth, a picture, a preview to tap through, or the one whole-file edit no session may make; each self-contained (*Asking the Chairman*).

16. What ends every reply to him? — "continue to build here", or the fresh-session line naming the successor started, else where and what to type; "ARCHIVE" ends a session's last (*Asking the Chairman*).

17. What does "build" mean? — Take the top ready item; never a question (`HOW-WE-BUILD.md`).

18. Where do a product's words change, and where does code? — Both in a Cowork session, by pull request; code mode only for a job Cowork cannot do (`library/two-stacks.md`).

19. Which file names a model? — `model-registry/registry.json` alone (`library/model-registry.md`).

20. A design brief or correction plans the layout, or skips `brief-check.py`. Allowed? — No; the goal, never the plan (`library/hypersolid.md`, step 3).

21. A slice merged. Who writes its roadmap bookkeeping, and when? — The next `building` publication or any earlier roadmap edit, from its `Advisories` and `Ideas:` lines; a merge with nothing ready after it, itself (`library/carries-sessions.md`).

22. A rule change alters a rule's meaning or scope. Where does it start, and what must the changed text carry? — His originals in `juku-library/` and his later rulings, each side naming the obligations before reading the other's; the text rests on the source words (his by register id), cites each source as `path#heading`, and names a dated authority beside any weakening, loss or contradiction (`library/changing-the-rulebook.md`, *What a rule change owes*).

23. May a session start a fresh session itself? — Yes: its own successor, at once, when it ends with an item ready, by firing its repository's standing task (no repeat or run time), which starts a cloud session wherever the scheduler puts it; never on a clock (`library/session-changeover.md`, *A session starts its own successor*). The Juku OS Project's session rewrites and fires the standing task when the chain has dropped and an item is ready (same page, *The Juku OS Project's session*).

24. A product with screens starts a new or reworked screen. What must exist first, and where? — One whole-product map of its current agreed scope, each live item in one canonical record, at `MAP.md`. Each slice updates the jobs it touches; while no screen changes, that is not a rework and needs no brief, design or save. A job added to a screen, moved, or given a new touch path there takes the steps; a frequent job's move is his to approve by looking: by tapping through the working preview once the product's look is agreed, else by picture (`library/hypersolid.md`, the steps' opening, step 2 and *What stays*).

25. He approved a picture or a motion rehearsal that came with a prose summary limiting something. Does the limit bind? — No; his approval covers only what was shown, and a look or motion rule changes only on his approval of what it shows (`library/hypersolid.md`, opening).

26. A reply to him offers an action the CTO may already take ("if you say go, I'll restart it"). Allowed? — No; it is done, then reported (R-2026-11-04a); owner `HOW-WE-BUILD.md`, *Who decides*.

27. He opens the Juku OS Project while the rulebook's chain is alive, or after it dropped with an item ready. What does it do? — Alive: builds and fires nothing there, and tells him in one line what is running and what landed. Dropped (a line whose session's run failed included): an act parked for his consent that his opener covers, it takes itself first; an uncovered one stays parked, put to him once, holding up nothing else (`library/his-opener.md`), and while it holds such an act open it fires nothing. Then, for other ready work, it posts `Checkpoint: released` for that line, rewrites the standing task's words for the ready work and fires it, never offering to (`library/session-changeover.md`, *The Juku OS Project's session*).

28. The platform refuses an act a session needs. What does it do, and what releases the act? — Never retries it or routes round it; records the act and its unblock condition, parks it and carries on with other ready work, else checkpoints and stops, firing no successor to retry it. His opener, sent by him in a session he opened, releases only the acts it names, and that session takes the act itself, head office included (`library/his-opener.md`).
29. Where do his words live, and what does a rule page carry instead? — Once, in `library/rulings.md` (a product's, in its `RULINGS.md`); a page states the rule and cites the id, and what a change replaces is deleted, never annotated (`library/changing-the-rulebook.md`, *Coherence*).
30. What does a product session read whole at boot, before any drill-down? — `HOW-WE-BUILD.md`, then the product's `FOUNDATIONS.md`, which every product ticket carries whole (`library/carries-sessions.md`, *Foundations*).
