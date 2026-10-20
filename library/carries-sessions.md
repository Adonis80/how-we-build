# What every product carries

Scope: every product repository and session. Open when: starting or stopping a product session, setting up or checking a product's repository or what its checks run, or a slice touches money milestones, evidence or the product's own pages.

A change made here reaches every product because each session reads this list at its start; a repository missing a line makes itself current in its next pull request.

**Its pages.**
- `AGENTS.md`, first line `Rulebook: https://github.com/Adonis80/how-we-build — read HOW-WE-BUILD.md before anything else, then What every product carries in its README.`; below it only what is true for that product; ending `## Review guidelines` (`library/reviewer.md`). Under 500 words.
- `design/CONSTITUTION.md`, for a product with screens, under 450 words, its headings exactly *Tokens*, *Units*, *Money*, *Domain law* and *Approved by picture* (each line dated). Everything else about looks is HyperSolid's.
- `PRODUCT.md` (what it is and does; his decisions land here or in `roadmap.json`), `NAMES.md` (its own words), `README.md` (commands, and the route: an attached session works directly, any other goes through the Mac; the ten-second test tells which).
- `<product>-library/`: agreed papers, and agreed screen designs in `design/<screen>/`; papers from `juku-os-papers` move in when the product joins, and `NAMES.md` gains the library's name. An archive: never read unless the task names it. This rulebook's own Roadmap has none: `juku-library/` is flat and public.
- No copy of rulebook text; a pointer instead. The reviewer holds this, through the exam in its brief.

**Its machinery.**
- The reviewer's gate from the starter kit, its own check named `verify`, and the ready mark (`library/product-joins.md`).
- `.claude/settings.json` denying the clock tools (`ScheduleWakeup`, `CronCreate`, `RemoteTrigger`, `mcp__*__send_later`, `mcp__*__create_trigger`, `mcp__*__update_trigger`, `mcp__*__fire_trigger`), its check failing if one goes missing. No product has a timer; the rulebook's asker, every ten minutes, is the only one. Codex runs no automation or schedule either.
- `.claude/agents/max-subagent.md` (`library/max-subagent.md`).
- Checks that do each piece of work once: one full run per commit; a posted review re-checks the review, not the suite; a newer push cancels the older run on a branch, never on `main`; a words-only change skips browsers and deploys; browsers cached. A job refused a machine fails in seconds with no step run: that is the shared minutes running out, not a broken workflow. Every test that runs today still runs on every commit that can reach `main`.
- A Project whose instructions are its template, whole (`library/project-instructions.md`).

**Its roadmap.**
- `roadmap.json` fit for a one-word *build*: every `next` line current and self-sufficient, items in the order they will be taken (ready, then priority, then oldest), each with its level P1–P4 (`library/changing-the-rulebook.md`). Words still waiting in an unmerged pull request are the one exception: the session that opened them says so.
- The slice's item published on `main` (by a roadmap-only pull request) as `building` when it starts and with its status and blocker when it parks.
- Money milestones: each revenue figure he gives, with what he is reminded of when it is reached; at least *revenue passes £1,000 a month: move the host to its paid plan*. Never build work. The slice that first counts revenue shows it to him and checks the milestones each time it counts.
- Ideas kept as `proposed` items (`library/ideas-for-later.md`).

**Its sessions.**
- Open pull requests first: one parked for review or waiting on hands is moved on, not rebuilt; a stale one is closed or taken over; anything else is left and the next item taken. An open pull request defers a slice, never blocks every slice.
- A session that cannot move says so once on the pull request and stops. No clock wakes it; something happening may (a read landing, a check failing, him writing). No shell left waiting past the work in hand, beyond waits a slice needs, such as a deploy's minutes.
- A consultant that cannot be reached never holds up a slice: a Claude lead puts the question to a Claude Fable subagent at its highest effort, as a cold read, and carries on; an OpenAI lead leaves it standing on the pull request. Running out of the other stack's allowance is never put to him as a purchase.


**Its handover lines** (in the pull request).
- `Personal data or payments affected: yes/no — reason` (hiding, capturing, logging and deleting all count as yes).
- `evidence`: what this slice captures or deliberately does not, which decision it can improve, what cost or retention it adds; "None, because …" is valid. Anything the product learns from is kept with its origin (a statement, an observation or a derived result; who recorded it, when, under which notice), for a permitted purpose and period, provably deletable, any justified exception written down (`RICH-DATA.md`); the product's own test in the slice proves it.
- After a read, one cost line from the read's spend line, by check-run link and commit: cash and plan allowance apart, unresolved counted, unknown stated as unknown, never zero.
- The pre-flight's effort (`library/reviewer.md`), unknown where not measured.
- At close or park: *Any material system improvement found?*, waste and savings included, with evidence or uncertainty and the smallest next action (decision 0014); "none" is valid. A proven waste is a defect, repaired first; an unbuilt saving is an idea titled `efficiency: …`. No quota, extra read, timer or ledger to fill the line.

**Two experiments under judgement.** This efficiency duty, and the reviewer's pre-flight, are each judged at the first ideas review on or after 2 November 2026 (`library/ideas-for-later.md`) as a keep-or-revert test (`CHARTER.md` §13): kept only if the saving actually measured (tokens, cash or delivery time, never nominal prices) exceeds what measuring, extra reads and rework cost; the pre-flight's measures are four timings per pull request (ready → asked, the read, correction, verdict → merge), the defects reads caught, and the builder's pre-flight effort, from existing check runs, commits and handovers, unknown where not available. The efficiency test also checks delivery delay and escaped defects, and the handover records the duty's own material cost; the pre-flight's covers a product's pull requests and the rulebook's alike, open and parked included, and the cost the caught defects added.
