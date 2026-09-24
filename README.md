# how-we-build

The rulebook for every product Dhayan's AI studio builds. This repository says **how** we work. Each product's own repository says **what** we build.

**Three files matter.**

- `HOW-WE-BUILD.md` — the operating page, short and machine-checked; the cap lives in `check.sh`. The first thing a working session loads, with *What every product carries* below.
- `CHARTER.md` — the Systems Blueprint, the reasoning behind the page. Read once, never loaded into a working session.
- `RICH-DATA.md` — the method for what a product learns from and how we know its AI got smarter. Read on the trigger in *What every product carries*, and not otherwise.

A fourth, `AGENTS.md`, is not for sessions at all: it carries the reviewer's brief for changes to this repository, because the reviewing tool loads only a file of that name.

**And the `decision` issues in this repository: why a rule is what it is, rather than the obvious alternative.** They hold the one thing he has ruled worth keeping from a conversation (his ruling, 22 September 2026, [decision 0003](https://github.com/Adonis80/how-we-build/issues/59): *"The only thing that we should be storing that is valuable is the architecture consensus that we reach with two intelligent AI models"*) — a consensus two capable models reached after genuinely disagreeing, each carrying the question, what was rejected, who was overruled on what evidence, and what is still unproved. **Read like `CHARTER.md`, not like the operating page:** when a rule is about to change or its reason is in question, and never loaded into a working session. Nothing executable depends on them — delete them all and the system behaves identically, and only the reasoning is lost. A record is never edited to stay current; a later one supersedes it and the earlier stands as history.

**Why it is public.** It holds no secrets, prices or customer data — only the way we work — and a public repository is the one thing every session, in either stack, can read directly, with no extra setup. Product repositories stay private.

## Where each topic lives

One page per topic, current truth only, each opened when its trigger fires. Why a rule is what it is lives in the pull request that made it and in the `decision` issues, never loaded at boot.

| Page | Open when |
|---|---|
| `library/reviewer.md`: *The independent reviewer* | asking for a read, answering one, or a slice cannot get one |
| `library/review-machinery.md` | changing `check.sh`, `review-gate.py` or a workflow; porting the badge; installing the App |
| `library/consultant.md`, `library/consultant-instructions.md` | asking the consultant, answering it, it cannot be reached, or setting its instructions |
| `library/session-changeover.md`: *Session changeover* | deciding to stay or start fresh, and before leaving |
| `library/two-stacks.md`: *The two stacks* | choosing the lead or its effort, handing work between stacks, a job that needs hands, code versus words |
| `library/screen-design.md`: *How a screen gets designed* | a new or reworked screen |
| `library/changing-the-rulebook.md`: *Changing the rulebook* | changing this repository, or *build* with it chosen |

## Products under this rulebook

The whole map: what exists, where it lives, one line on what it is for, and the file to open first. It is a directory board, not a summary — nothing here says more about a product than its one line.

- **Myst** — `https://github.com/Adonis80/myst` (private; Juku Perfume, `juku-perfume`, until 16 September 2026). The App for Perfume Collectors, a fragrance intelligence and exchange platform: a Personal Nose that learns a person's taste, samples picked for them, and the value sitting on collectors' shelves. Open `AGENTS.md`, then `PRODUCT.md`, then `roadmap.json`.
- **Hemz OS** — `https://github.com/Adonis80/Hemz-OS` (private). The operating system for an alterations business, grown out of Alma's Alterations in Brighton. Open `AGENTS.md`, then `PRODUCT.md`, then `roadmap.json`.

A repository not listed here is not under this rulebook.

**Which repository a chat Project reads (the Chairman's ruling, 11 September 2026).** The Juku OS Project — the chat Project named for this system — reads this repository and uses the map above as the whole register of what exists, opening a product repository only when it needs live detail; its instructions are the second template below. The Hemz OS Project reads `Adonis80/Hemz-OS` plus the global rules here; the Myst Project reads `Adonis80/myst` plus the same. This is where to read, not permission to read: each Project's own GitHub connection is proved by fetching live commits and open pull requests from inside that Project, because a successful read somewhere else proves nothing for it. Reuse this register; never start a second map.

## How a product joins

1. Its repository's `AGENTS.md` begins with one line: `Rulebook: https://github.com/Adonis80/how-we-build — read HOW-WE-BUILD.md before anything else, then What every product carries in its README.` Below that, only what is true for that product, ending with a short `## Review guidelines` section: the pointer to the brief below, the least of it the tool needs in front of it, and the hazards particular to that product.
2. Its Claude Project's instructions are the template below, blanks filled.
3. One line in *Products under this rulebook* above.
4. The `juku-reviewer` App installed on the repository — a session's own hands, by API, never his tap. The route that reviews a product's pull requests from here reads only the products on its own list (*What every product carries*); until a product that joins is on it, it has no read its gate can count, so its slices park at step 5.

**Nothing is copied into a Claude Project's knowledge or context — not the rulebook, not a product's files.** A Project's GitHub option copies file contents in; it cannot write back, and the copy is stale the moment anyone pushes. Two copies of one truth is the failure this whole structure exists to end. A session reads the rulebook live (it is public) and the product repo live (through whatever route its README names). A Project holds its instructions text and nothing else — no files, ever (the Chairman's ruling, 6 September 2026). That instructions text is therefore the only place a session can be told how to reach a private repo, and it has no version history: if it is ever lost or wrong, re-paste it from the template below.

### Project instructions template

```
# <Product> — how this project works

Rulebook: https://github.com/Adonis80/how-we-build. At the start of every working
session, read HOW-WE-BUILD.md from it (clone the repo, or fetch the raw file) — it says
who decides, the loop, and when a slice is done — then its README's section "What every
product carries": if this repo or this Project lacks anything on that list, make it
current first. Nothing below overrides the rulebook.

This project builds <Product>. Its repo is https://github.com/Adonis80/<repo> (private).
The repo's AGENTS.md holds the rules true only for this product; PRODUCT.md is what we
are building; roadmap.json is what comes next.

Read both live, every session; never from a copy kept in this Project. Words — rules,
roadmap, product pages — may change from here through the Mac, by pull request; anything
that runs is built in a code session started attached to the repo. <A session reaches
a private repo directly only if it was started attached to it. For a session that was not,
two sentences here say how it gets in — the connected folder, where the key is, never the
key itself. The repo's README holds the rest.>

A product decision the Chairman makes goes into PRODUCT.md or roadmap.json in the repo.
This Project holds these instructions and no files of any kind.

Prose written for the Chairman is said in chat or in the pull request, and kept in
neither this Project nor a repo. The pull request is the handover. Speak to the
Chairman in plain English: summaries and actions, no technical commentary — and end
every reply with "ready to start fresh session" or "continue to build here". "Continue
to build here" means this session carries on. "Ready to start fresh session" is never
left bare: it carries everything `HOW-WE-BUILD.md` requires of it, and here *where*
means Cowork, or code mode at https://claude.ai/code with this repository chosen.
```

### The Juku OS Project's instructions

The chat Project named for this system is not a product. It builds nothing, it reads this repository, and it is where the system's own words change. Its instructions are the text below, whole — the same rule as a product's: nothing is copied in, and it holds no files.

```
# Juku OS — how this project works

Juku OS is the name for the way we build, not a product. Nothing is built here. Its
repo is the public rulebook: https://github.com/Adonis80/how-we-build.

At the start of every session, read HOW-WE-BUILD.md from it (clone the repo, or fetch
the raw file) — it says who decides, the loop, and when a slice is done — then its
README whole: the map of products, the reviewer, the consultant, the two stacks, and
"What every product carries". Read it live, every session, never from a copy kept in
this Project.

The map in that README is the whole register of what exists. Open a product's repo
only when this session needs live detail from it; never start a second map. A change
to one product's own rules belongs in that product's Project, not this one.

This is where the system's own words change — the rulebook, the charter, the screen
law, the templates, a Project's instructions text — by pull request through the Mac:
the connected folder ~/Documents/Claude/Projects, where the key is the file
.alma-secrets/github-token; read it into a shell variable, never print it. Anything
that runs — check.sh, review-gate.py, the workflow — is built in a code session
started attached to this repo, not from here.

Before proposing a change to the rulebook, read its AGENTS.md, its CHARTER.md §13 and
its README's "Changing the rulebook": between them they hold the gate, who clears a
change, and what the pull request must carry.

This Project holds these instructions and no files of any kind.

Prose written for the Chairman is said in chat or in the pull request, and kept in
neither this Project nor a repo. The pull request is the handover. Speak to the
Chairman in plain English: summaries and actions, no technical commentary — and end
every reply with "ready to start fresh session" or "continue to build here".
"Continue to build here" means this session carries on. "Ready to start fresh
session" is never left bare: it carries everything `HOW-WE-BUILD.md` requires of it,
and here *where* means Cowork, or code mode at https://claude.ai/code with this
repository chosen.
```

## Review guidelines
- Cold read: form your view from the diff, the tests, `PRODUCT.md` and `roadmap.json` first, and read the pull request's own account last. Never inherit the author's conclusions.
- Look for what is wrong, missing, duplicated, untested, or quietly wider than the slice. Say what you checked and what you did not, and how sure you are. Do not manufacture disagreement.
- Findings go on the pull request, addressed to the CTO, who answers them there. Two rounds at most. Then a trade-off is the CTO's call, with the dissent left standing on the pull request; a claim that can be tested is settled by the test, never by rank — and if it cannot be settled safely, the change shrinks or stops; a product question goes to the Chairman as "Decision needed: …".
- A review clears only the commit it read; a later push voids it.
- Plain English. Never write a file into the repository.
```

## What every product carries

How a change reaches every product: it is made here once and then lands everywhere — a change to how we build not by anyone remembering, but because every session is sent to this list at its start (by the first line of its `AGENTS.md`, and by its Project's instructions) and a repo that lacks something on it makes itself current in its next pull request. One line each, as of 17 September 2026; the why of each lives in the pull request that added it.

- `AGENTS.md` ending with `## Review guidelines`: the pointer to the brief (`library/reviewer.md`), the least of it the tool needs in front of it, and the product's own hazards — under 500 words, machine-checked.
- A check that goes green only when the reviewer has read the current commit: where the badge counts, its check run on that commit; where a gate still counts Codex, a submitted review or a plain comment naming the commit (`library/reviewer.md`).
- The badge ported to its gate, and then Codex retired there: done in Hemz OS, Myst next (`library/reviewer.md`; how, `library/review-machinery.md`).
- Open pull requests read before starting: a slice parked only for review, or waiting under **Hands needed:**, is moved on rather than rebuilt or restarted — its findings answered, its fixes pushed, its ask made, its hands asked for, and that is the session's work — while a stale or abandoned one is closed or taken over, and anything else is left alone and the next roadmap item taken. An open pull request defers a slice; it never blocks every slice.
- A session that cannot move says so once on the pull request and stops hard (his ruling, 10 September 2026). No clock wakes it — no check-in, timer, loop, scheduled task or background watch, and no shell left waiting past the work in hand, which still allows the waits a slice needs, such as the deploy's couple of minutes. Something happening may wake it: a review landing, a check failing, the Chairman writing. `.claude/settings.json` denies the clock tools — `ScheduleWakeup`, `CronCreate`, `RemoteTrigger`, `mcp__*__send_later`, `mcp__*__create_trigger`, `mcp__*__update_trigger`, `mcp__*__fire_trigger` — and the check fails if one goes missing; a shell left sleeping is forbidden by the rule, which no file can catch. On the OpenAI side the same rule forbids Codex automations, schedules and polling in the build loop.
- The lead's default effort, medium, as `effortLevel` in `.claude/settings.json`: [decision 0005](https://github.com/Adonis80/how-we-build/issues/75) rules on effort by name (`library/two-stacks.md`).
- A consultant that cannot be reached never holds up a slice (`library/consultant.md`).
- A `roadmap.json` left fit for a one-word start (his ruling, 9 September 2026: *make sure the session has all the context it needs so all I have to do is say "build"*): every `next` line current, self-sufficient, and in the order the work will be taken up — ready first (no item it depends on and no decision of his still open), then priority, then oldest, each item naming its level: his priority model ([decision 0001](https://github.com/Adonis80/how-we-build/issues/57), 22 September 2026, which keeps an item's level beside it in the roadmap), whose four levels and their tests are written once, in *Changing the rulebook* — so that *build* alone is enough and he is never handed a paragraph to paste. Words still waiting in an unmerged pull request are the one exception, and the session that opened them says so and carries the difference meanwhile.
- Money milestones in `roadmap.json` (his ruling, 17 September 2026): each revenue figure he gives, and what he is reminded of when it is reached — at least *revenue passes £1,000 a month: a real business, so move the host to its paid plan*. Never build work. The slice that first counts a product's revenue shows it where he can see it and checks the milestones every time it counts, so a reminder fires on its own.
- Evidence recorded with its origin (his ruling, 17 September 2026): for anything the product learns from, whether it is a person's statement, a recorded observation or a derived result, along with where it came from, who recorded it and when, and under which notice. Kept only for a permitted purpose and period, with personal records and anything identifiable derived from them provably deletable, and any justified exception written down. The proof is the product's own test in the slice that changes the behaviour; a line in this list is not a machine gate.
- The handover's `evidence` field, which `HOW-WE-BUILD.md` names with the rest: what evidence this slice captures, or deliberately does not capture; which decision it can improve; and what cost or retention obligation it adds. "None, because ..." is a valid answer, which is what stops it becoming a box everyone ticks.
- `PRODUCT.md` and `NAMES.md`: what the product is, and the words it uses for its own things.
- `RICH-DATA.md` read whole by any slice that changes what the product learns from, shows about a person, or claims about its own accuracy — and not otherwise. `PRODUCT.md` carries the five-heading section that page's §10 names and says how to fill; the headings are written there, once. "Unknown" and "deliberately not captured" are valid answers.
- A `README.md` route section saying that a session attached to the repo at its start works in it directly, a session started without it goes through the Mac, and the ten-second test tells which.
- A Project whose instructions are the template above, whole, and nothing else.
- For a product with a user interface, a `design/` folder (`library/screen-design.md`). It holds its own constitution on one capped, machine-checked page, with only what is true there, and one spec per designed screen. Its check holds the shape: one constitution page, one brief at a time, one spec per screen, no two specs sharing an id.

**GitHub's build minutes are finite and shared too (learned 23 September 2026).** On the free plan every private repository under this account draws on one pool of 2,000 Actions minutes a month; a public repository — this rulebook — draws nothing. Hemz OS spent about 1,720 of them by the 23rd, the pool ran dry, and #67's deploy and every product's checks stopped: a job that is refused a machine fails in seconds with no step run, which reads like a broken workflow and is not. What made it a wall rather than a bill was an Actions budget of $0 with stop-at-limit on, and no card. The Chairman's ruling that day: a card on file and that same Actions budget raised to **$5 a month, stop-at-limit kept on** — no subscription, no plan — with the other $0 budgets left as they are. The ceiling is not the answer; spending less is. **A product's checks do each piece of work once**: one full run per commit, not one for the push and another for the pull request; a posted review re-checks the review, not the suite; a newer push cancels the older run on a branch, never on `main`; a words-only change runs the word checks, not browsers and a deploy it cannot affect; and a browser's setup is cached, not reinstalled. Every test that runs today still runs on every commit that can reach `main` — quality is the constraint, minutes the thing trimmed. Hemz OS carries this as A15; every product ports it.

**The deploy, in shape.** Deploys run from CI with the deploy key held as a repository secret, so no session of any kind ever holds it — and this says what is built, because no product can read another product's repository to find out. CI builds the app, deploys it as a preview and smoke-tests that exact deployment; a merge to `main` promotes the same deployment — never a rebuild, never "whatever is newest" — then smokes the live addresses and, if they are red, promotes the previous production deployment straight back and fails loudly. The previous deployment is recorded before anything moves. The host's own Git integration stays off on purpose: it would put every push into production untested. Four things cost Hemz OS real runs and need cost the next product none: the deploy tool reads GitHub-flavoured environment variables and a `github.com` remote as an integration deploy, which a private repo on the free plan refuses outright with no visible error, so both are put out of its sight for the deploy call; a team-scoped key works where a project-scoped one authenticates and then dies with a misleading missing-project message; promoting a preview-built deployment mints a production copy rather than repointing production, so the check passes on the smoked id **or** on a deployment whose original is the smoked id; and the edge serves the new build a little after the control plane calls it live, so ask again for a couple of minutes before calling it red.
**Money out waits for money in (his ruling, 21 September 2026).** *"We should not be sending money until we are generating revenue."* It is not only the host's plan: **no session proposes a paid plan, a paid tool or a paid service while a product earns nothing**, and a feature that needs one is built on the free route or parked with the cost named. Where a paid lock would have enforced a rule, the rule still stands and is enforced by the checks and the review, which is the trade he is making knowingly. He had already answered this once, on 5 September, in Hemz OS's own Backstage: asked whether to pay to stop untested work reaching the live site, he answered *"later"* — *"I want to see the software working and being used by staff before committing more money."* A session asked him again on 21 September because the roadmap said the question had never been put to him, and the answer was sitting in the product all along. **So: before putting a cost to him, read what he has already decided**, in the place this rulebook already names: *a product decision the Chairman makes goes into `PRODUCT.md` or `roadmap.json` in the repo* — the Project template, unchanged. A session reads those two and nothing else; where the roadmap's gate line disagrees with `PRODUCT.md`, the gate line is the copy, `PRODUCT.md` wins, and the copy is corrected in the same pull request. The 5 September answer was in neither file, which is why a session could read the roadmap honestly and still put the question a second time; an answer he gives inside a product is not on the record until it reaches the repository, and Hemz OS's line is corrected in [Adonis80/Hemz-OS#68](https://github.com/Adonis80/Hemz-OS/pull/68).

**The host's plan (his ruling, 17 September 2026).** No product is a real business until its revenue passes £1,000 a month. Until then it stays on the host's free plan and deploys there as normal: production is promoted, never held back waiting for a paid plan. The free plan's terms reserve it for non-commercial use; he was told, and the call is his. The paid plan is his to buy when a product's milestone fires, and no session buys it.
**A Project's instructions write themselves from here.** Nobody carries text between products. At the start of a session, if the Project's instructions differ from the template above filled in for this product, the session sets them to it — before anything else, once — and anything product-specific it finds in the old text goes into the product's `AGENTS.md` by pull request, since the Project holds the template and nothing else. When either template changes, every next session does the same, the Juku OS Project against its own.

**The session sets them; the Chairman is handed no paste (his ruling, 14 September 2026).** It works in the Claude app's built-in browser (`library/two-stacks.md`), signed in to `claude.ai` by him: `claude.ai/projects` → *New project* → the name and one line saying what it is → *Create project* → *Instructions* → *Edit instructions* → the template, whole → *Save instructions*. An existing Project is the same route from its own page. Nothing is ever added to a Project's *Context*: it holds instructions and no files. The session then reloads the page, reopens the instructions, reads them back and says what it set — a Project is not reported as done on the strength of having typed into it. If that browser is not signed in, he is handed that one tap and nothing else. The text whole is for a session with no Mac connected, and that is the exception, not the route.

**Text for the Chairman is handed over whole.** When the template above, the consultant's standing instructions, or any text he pastes somewhere changes, he is given the complete new text to replace the old with — never a sentence to find and splice in, which invites the very error the template exists to prevent.

## Reading it from a session

```
git clone --depth 1 https://github.com/Adonis80/how-we-build
```

or fetch `https://raw.githubusercontent.com/Adonis80/how-we-build/main/HOW-WE-BUILD.md`.
