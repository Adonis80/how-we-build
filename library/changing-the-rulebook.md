# Changing the rulebook

Scope: this repository. Open when: proposing or reviewing a change here, or starting *build* with this repository chosen.

**By pull request only**, against protected `main`. `check.sh` runs in CI and refuses: the operating page over 600 words; the README, a library page or the boot over its size; a file not on the lists; anything that looks like a secret; and, in a pull request, a commit the reviewer has not read clean.

**What needs the gate.** Adding a rule, step, file, check or agent needs the charter's gate (§13) or the Chairman's own ruling. Removing one, or correcting wording, needs neither. The CTO settles and merges changes here without him (his ruling); he is asked only for money, a permission, a product outcome or a picture. The reviewer still reads every change cold.

**A ruling of his about how we build is not on the record until it is in this repository**, just as a product decision is not until it is in that product's. Each rule lives in one place, current truth only. Why it is so lives in the pull request that made it and in the `decision` issues.

**Caps are paid for in wording, never in requirements.** Compress phrasing first. A change that cannot fit without removing something the page requires says so in its pull request, and the cap is argued about there. The operating page's 600 words is the ceiling: a rule in means a rule out.

**"Build" here** takes the open pull request that is ready: highest priority first, oldest within a priority (his priority model, decision 0001). This repository has no `roadmap.json`; its queue is its open pull requests. Each carries a `Priority:` line, set by test rather than by feel:

- **P1**, stop the line: a reproducible failure that blocks a required build, check, review or deploy; lets through what should be refused; loses, duplicates, corrupts or deletes work or data; or crosses a trust boundary wrongly. It names the failing case.
- **P2**, repair: a reproducible wrong result short of that.
- **P3**, build: approved new capability with no failing case.
- **P4**, observe: removing it would leave what runs unchanged.

His asking makes a thing authorised, not P1: priority is the state of the system, not who asked. Ready comes first, so priority cannot bulldoze a dependency or a decision that is his. A pull request waiting on his answer is not ready. One with no `Priority:` line gets one from the first session to read it, written into its body.

A session on *build* here reads the queue in that order and moves pull requests on: answers findings, pushes the round's fixes as one push, asks once. It closes one that is stale. With none ready, it says so and stops.

**Every product picks a change up at its next session**, because every session reads this repository live; there is no copy to refresh. A running session keeps the page it read when it began: a rule landed at noon binds the next session, not the one in front of you.
