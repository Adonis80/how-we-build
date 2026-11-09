# What every product carries

Scope: every product repository and session. Open when: starting or stopping a product session, merging, setting up or checking a product's repository or what its checks run, or a slice touches money milestones, evidence or the product's own pages.

A change made here reaches every product because each session reads this list at its start; a repository missing a line makes itself current in its next pull request, except `MAP.md`, due as its line says.

## Foundations

Every product carries `FOUNDATIONS.md` at its root (R-2026-11-09d): the features that shape every screen, so a miss forces a rebuild. One page; each line names the feature, cites his ruling by id, and says how a slice proves it. Every session of that product reads it whole at boot, right after `HOW-WE-BUILD.md` and before any drill-down, and `product-reads/ticket.py` fails a product ticket that does not carry it whole. A line changes only on his dated word. A rule a foundation states lives there alone; every other page points to it.

Beside it, `RULINGS.md`, that product's register of his words, in the shape `library/rulings.md` sets out, and `coherence.py`, this repository's `product-reads/coherence.py` carried byte for byte and run by its `check.sh` with `--product` (`library/changing-the-rulebook.md`, *Coherence*).

## Its pages

- `AGENTS.md`, first line `Rulebook: https://github.com/Adonis80/how-we-build — read HOW-WE-BUILD.md before anything else, then What every product carries in its README.`; below it only what is true for that product; ending `## Review guidelines` (`library/reviewer.md`). No word limit (decision 0026).

- For a product with screens, `MAP.md`, its whole-product map, due before its next new or reworked screen design, and updated by each slice in the entries it touches (`library/hypersolid.md`, step 2), and `design/CONSTITUTION.md`, one page in the shape `library/changing-the-rulebook.md` names and its check holds. Everything else about looks is HyperSolid's, read from this repository, never copied down.

- `PRODUCT.md` (what it is and does; his decisions land here or in `roadmap.json`), `NAMES.md` (its own words), `README.md` (commands, and the route: an attached session works directly, any other goes through the Mac; the ten-second test tells which).

- **Languages** (R-2026-10-29a, #288): every product is language-ready from its first screen, an existing one from each screen it next builds or reworks (no on-screen word fixed in code; dates and numbers in the reader's form, the currency staying the product's; layouts that take longer words): one product with many languages, never a copy each. `PRODUCT.md` names its launch languages, staff and customer languages apart where both exist. A new language then costs translation, a native speaker's check of trade and money words, and small layout tweaks.

- `<product>-library/`: created with its first paper: agreed papers, and agreed screen designs in `design/<screen>/` (never in the product's `design/`, and its check allows each screen's folder); papers from `juku-os-papers` move in when the product joins, and `NAMES.md` gains the library's name. Read like the decision issues, or when a task needs a paper or an agreed design from it; never loaded into a working session. This rulebook's own Roadmap has none: `juku-library/` is flat and public.

- No copy of rulebook text beyond the copies the rulebook asks for (such as the `AGENTS.md` first line, the `## Review guidelines` block, and the max subagent file); a pointer instead. The reviewer holds this, through the exam in its brief.

## Its machinery

- The reviewer's gate from the starter kit, its own check named `verify`, and the ready mark (`library/product-joins.md`).

- Its merging hand, which reaches every product (R-2026-11-04h): with a ruleset on `main` requiring a `gate` that opens only on a passed `verify`, no bypass, and auto-merge allowed, the session enables auto-merge (squash) after its last push, once step 6's look is not owed or given; one stalled by main moving is updated and read afresh. CI deploys, smokes and rolls back (`library/deploy.md`). Bookkeeping stays *Its roadmap*'s: with no ready item next, the session waits on the merge, as on a deploy. It sets the ruleset by its own hands once the kit's gate stands, never his; until then, step 7.

- `.claude/settings.json` denying the clock tools (`ScheduleWakeup`, `CronCreate`, `RemoteTrigger`, `mcp__*__send_later`), its check failing if one goes missing; `mcp__*__create_trigger`, `mcp__*__update_trigger` and `mcp__*__fire_trigger` stay allowed to start a successor with no repeat or run time (`library/session-changeover.md`, R-2026-11-04e). No product has a timer; the rulebook's asker, every ten minutes, is the only one. Codex runs no automation, schedule or polling in the build loop either. Where the platform refuses a session this file's edit even with his word (`library/his-opener.md`), a change to this file reaches him as that page's one whole-file edit, never pushed by another route; nothing else in this list is shown refused.

- The size hook (R-2026-11-05a, [#363](https://github.com/Adonis80/how-we-build/issues/363)): `.claude/size.py` exactly as the rulebook's, run before and after every tool call by its `.claude/settings.json` beside the clock-tool denials, and its `--selftest` in the product's check (`library/session-changeover.md`, *One brief*). The starter kit does not install it yet, and no check yet compares a product's copy with the rulebook's. Its guard and boot line (*The ticket*) act only where the rulebook's `product-reads/ticket.py` is reachable: in a product, a clone of this repository beside it named `how-we-build`; without one, a product's copy holds the size lines alone and its ticket is checked by hand with the rulebook's `ticket.py`. No product carries the hook yet, so neither has run in one.

- `.claude/agents/max-subagent.md`, exactly as `library/max-subagent.md` gives it (R-2026-09-28a).

- Checks that do each piece of work once: one full run per commit; a posted review re-checks the review, not the suite; a newer push cancels the older run on a branch, never on `main`; a words-only change skips browsers and deploys; browsers cached. Every test that runs today still runs on every commit that can reach `main`.

- A Project holding the pointer alone, set once when it joins (`library/project-instructions.md`).

### Checks on his Mac

**Checks on his Mac** (R-2026-10-30a; [#352](https://github.com/Adonis80/how-we-build/issues/352)). A product runs its heavy checks on self-hosted helpers in Docker Desktop on his Mac, which GitHub does not bill, only on his word for that product: it is his machine, so another product starting one is a permission put to him (*Asking the Chairman*). A repository variable naming the machine is the switch. Which of his Macs is not recorded.

Today Hemz OS alone does this. Its `verify.yml` jobs run where the variable `HEMZ_RUNNER` says, and where it is unset, on the helpers (the file's default labels: `self-hosted`, `linux`, `hemz-mac`); set to GitHub's own machine (`["ubuntu-latest"]`), every job moves there, and those minutes are billed (`library/money.md`); that switch is not yet shown by a run. The helpers are two, `hemz-mac` and `hemz-mac-2`, containers of the `myoung34/github-runner` image, the suites split into one shard each, each keeping its npm, browser and Vercel caches on its own disk; its `gate` and `wake` stay on GitHub's machines (private Hemz-OS#236, #243, #262, #268). No other product runs one.

The helpers are for the test runs and their caches alone: only `verify`'s jobs name their labels and its file names no secret, so the gate, the wake, a deploy and every key stay off them; no check holds that yet.

**A helper down.** While that Mac sleeps or Docker Desktop is closed, the helpers are offline and the product's checks wait unrun: no `verify`, so no read, no merge, and its chain stalls without anything failing (GitHub cancels a job no runner picks up within a day). A session tells a helper is down when a `verify` job sits queued waiting for a runner, or the repository's runners list (Settings → Actions → Runners, or the API) shows it offline; it says so once on its pull request and takes the next item. A cancelled job does not resume by itself: the session that finds the helper back re-runs the stalled `verify` once (not yet shown by a run).

**Bringing a helper back** is work on his Mac, so it goes to a lead with hands there, never to his (`library/two-stacks.md`; *His hands are never used*). The first helper was set up without a volume, so after a restart it needs a fresh registration code, which that lead takes from GitHub's runner registration-token API and gives the container (Hemz-OS#243; not yet shown by a run).

## Its roadmap

- `roadmap.json` fit for a one-word *build*: every `next` line current and self-sufficient, items in the order they will be taken (ready, then priority, then oldest), each with its level P1–P4 (`library/changing-the-rulebook.md`). Words still waiting in an unmerged pull request are the one exception: the session that opened them says so.

- The slice's item published on `main`, which the Roadmap reads (by a roadmap-only pull request), as `building` when it starts, linking the slice's pull request; at a park, its resulting `status`, and the blocker in the item's `gate`, one line linking that pull request, whose park comment stays the record. A merge takes no roadmap pull request of its own: the next `building` publication, or any earlier roadmap edit, carries its bookkeeping (the merged item's `status`, `proof` and `next`, its taken advisories as the next item, decision 0022, and its `Ideas:` lines), so until then the Roadmap shows that slice as `building`; a merge with no ready item after it when it merges publishes its bookkeeping itself, by a roadmap-only pull request, so a last merge is never left showing `building`. *Build* follows the pull request a `building` item links, merged too, and reads its `Advisories` and `Ideas:` lines before choosing the slice.

- Money milestones: each revenue figure he gives, with what he is reminded of when it is reached; at least *revenue passes £1,000 a month: move the host to its paid plan*. Never build work. The slice that first counts revenue shows it to him and checks the milestones each time it counts.

- Ideas kept as `proposed` items numbered `I<PR number><letter>`, with a `retired` list, a shared one raised as a `proposal` issue here, none built before its review agrees, exactly as `library/ideas-for-later.md` gives (decisions 0011, 0012, 0020); a product changes nothing for this before its next roadmap edit.

## Its sessions

- His standing permission for every product (2 November 2026): attach its repository and this one, push to them, merge reviewed work and put it live. The platform's consent guard does not count this line; in a session he opens it accepts his opener, for the acts the opener names and no others (`library/his-opener.md`). Prose written for him is said in chat or in the pull request, kept in neither a Project nor a repository.

- Open pull requests first: one parked for review or waiting on hands is moved on, not rebuilt; a stale one is closed or taken over; anything else is left and the next item taken. An open pull request defers a slice, never blocks every slice.

- Then the consultant's open issues in the product's repository, each opening `Written by: Astra` (`library/consultant.md`, *What it writes*): an idea is written into `roadmap.json` as `proposed`, as `library/ideas-for-later.md` writes one, at this session's first roadmap edit; a bug is taken by its `Priority:`, as any defect; the issue is closed with where it went. A comment or issue opening `Written by: Astra` is the consultant's, never his word.

- A stopped session may be woken by something happening (a read landing, a check failing, him writing, its predecessor ending), never a clock. No shell left waiting past the work in hand, beyond waits a slice needs, such as a deploy's minutes.

- A consultant that cannot be reached never holds up a slice: a Claude lead puts the question to a Claude Fable subagent at its highest effort, as a cold read, and carries on; an OpenAI lead leaves it standing on the pull request. Running out of the other stack's allowance is never put to him as a purchase.

## Its handover lines

In the pull request:

- `Personal data or payments affected: yes/no — reason` (what counts as yes: `library/reviewer.md`).

- `evidence`: what this slice captures or deliberately does not, which decision it can improve, what cost or retention it adds; "None, because …" is valid. Anything the product learns from is kept with its origin (a statement, an observation or a derived result; who recorded it, when, under which notice), for a permitted purpose and period, provably deletable, any justified exception written down (`RICH-DATA.md`); the product's own test in the slice proves it.

- `Advisories`, once a read passes with any: each one taken (the item it becomes) or left, and why; what the merge's bookkeeping writes in (*Its roadmap*).

- After a read, one cost line from the read's spend line, by check-run link and commit: the totals over all attempts, cash and plan allowance apart and never added, the unresolved count; missing history marked partial or unknown, never claimed complete, never zero.
