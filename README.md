# how-we-build

The rulebook for every product Dhayan's AI studio builds. This repository says **how** we work; each product's own repository says **what** we build. It is public because it holds no secrets, prices or customer data, and a public repository is the one thing every session, in either stack, can read directly.

## Boot

**The boot list.** A session reads exactly this at its start, and nothing more:

1. `HOW-WE-BUILD.md`: who decides, the loop, when a slice is done.
2. This `README.md`: the map, ending with *What every product carries*.
3. In a product, its own `AGENTS.md`, the summary page of its `PRODUCT.md`, and `roadmap.json`.

Everything else is opened only when the task touches it, as the index below says. `check.sh` holds the rulebook's share of the budget: this README at most 12,000 bytes, and the two files together at most 16,000 (about 4,000 tokens). A product's share is the last line of *What every product carries*. Project instructions point here rather than listing files; the current template is dated **2026-09-23** (`library/projects.md`).

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
| `library/joining.md`: *How a product joins* | a product joins, or its review section is written or checked |
| `library/projects.md`, `library/project-template.md`, `library/juku-os-project.md` | a Project's instructions carry an older date than the one above, or a Project is set up |
| `library/ci-and-deploy.md` | a product's checks, workflows or deploy change |
| `library/money.md` | anything would cost money, or revenue is counted |
| `CHARTER.md` | a rule is about to change or its reason is in question; read once, never at boot |
| `RICH-DATA.md` | a slice changes what a product learns from, shows about a person, or claims about its own accuracy |
| `design/` | a screen is designed, drawn or reviewed |
| `AGENTS.md` | never by a working session: it is the reviewer's brief for this repository |

**The `decision` issues** hold the one thing he ruled worth keeping from a conversation: a consensus two capable models reached after genuinely disagreeing. Each carries the question, what was rejected, who was overruled on what evidence, and what is still unproved. They are read like `CHARTER.md`, and nothing executable depends on them. A record is never edited to stay current; a later one supersedes it.

Read the rulebook live: `git clone --depth 1 https://github.com/Adonis80/how-we-build`, or fetch `https://raw.githubusercontent.com/Adonis80/how-we-build/main/HOW-WE-BUILD.md`.

## Products under this rulebook

The whole register: what exists, where it lives, one line on what it is for, and the file to open first. A repository not listed here is not under this rulebook.

- **Myst**: `https://github.com/Adonis80/myst` (private). The App for Perfume Collectors, a fragrance intelligence and exchange platform: a Personal Nose that learns a person's taste, samples picked for them, and the value sitting on collectors' shelves. Open `AGENTS.md`, then `PRODUCT.md`, then `roadmap.json`.
- **Hemz OS**: `https://github.com/Adonis80/Hemz-OS` (private). The operating system for an alterations business, grown out of Alma's Alterations in Brighton. Open `AGENTS.md`, then `PRODUCT.md`, then `roadmap.json`.

**Which repository a chat Project reads** (his ruling). The Juku OS Project reads this repository, using the list above as the whole register and opening a product repository only for live detail. The Hemz OS Project reads `Adonis80/Hemz-OS`, and the Myst Project `Adonis80/myst`, each plus the global rules here. This is where to read, not permission. Each Project's GitHub connection is proved by fetching live commits and open pull requests from inside that Project. Never start a second map.

## What every product carries

Every session is sent here at its start, by the first line of its `AGENTS.md` and by its Project's instructions. A repo that lacks something on this list makes itself current in its next pull request, so a change made here once lands everywhere. One line each; the why lives in the pull request that added it.

- `AGENTS.md` ending with `## Review guidelines` (`library/joining.md`), under 500 words and machine-checked.
- A check that goes green only when the reviewer has read the current commit: where the badge counts, its check run on that commit; where a gate still counts Codex, a submitted review or a plain comment naming the commit (`library/reviewer.md`).
- The badge ported to its gate, and then Codex retired there: done in Hemz OS, Myst next (`library/review-machinery.md`).
- Open pull requests read before starting. A slice parked only for review, or waiting under **Hands needed:**, is moved on rather than rebuilt: findings answered, fixes pushed, the ask made, the hands asked for. A stale or abandoned one is closed or taken over. Anything else is left alone and the next roadmap item taken. An open pull request defers a slice; it never blocks every slice.
- The hard stop (his ruling). A session that cannot move says so once on the pull request and stops. No clock wakes it: no check-in, timer, loop, scheduled task or background watch, and no shell left waiting past the work in hand (the waits a slice needs, such as a deploy's couple of minutes, are fine). Something happening may wake it: a review landing, a check failing, the Chairman writing. `.claude/settings.json` denies `ScheduleWakeup`, `CronCreate`, `RemoteTrigger`, `mcp__*__send_later`, `mcp__*__create_trigger`, `mcp__*__update_trigger` and `mcp__*__fire_trigger`, and the check fails if one goes missing. On the OpenAI side the same rule forbids Codex automations, schedules and polling.
- The lead's default effort, medium, as `effortLevel` in `.claude/settings.json` (`library/two-stacks.md`).
- A consultant that cannot be reached never holds up a slice (`library/consultant.md`).
- A `roadmap.json` fit for a one-word start (his ruling): open items only, every `next` line current and self-sufficient. They are in the order the work is taken (ready first, then priority, then oldest), each naming its level from `library/changing-the-rulebook.md`, so *build* alone is enough. Words waiting in an unmerged pull request are the one exception, and the session that opened them says so.
- Money milestones in `roadmap.json` (`library/money.md`).
- Evidence recorded with its origin (his ruling), for anything the product learns from: a person's statement, a recorded observation or a derived result. Record where it came from, who recorded it and when, and under which notice. Keep it only for a permitted purpose and period. Personal records, and anything identifiable derived from them, are provably deletable, and any justified exception is written down. The proof is the product's own test in the slice that changes the behaviour.
- The handover's `evidence` field: what the slice captures or deliberately does not, which decision it can improve, and what cost or retention obligation it adds. "None, because …" is valid.
- `PRODUCT.md`, opening with a one-page summary with detail below, and `NAMES.md`: what the product is, and its words for its own things.
- `RICH-DATA.md` read whole by a slice that changes what the product learns from, shows about a person, or claims about its own accuracy, and not otherwise. `PRODUCT.md` carries the five-heading section its §10 names, where "unknown" and "deliberately not captured" are valid answers.
- A `README.md` route section: a session attached to the repo at its start works in it directly; one started without it goes through the Mac; the ten-second test tells which.
- A Project whose instructions are the current template, whole, and nothing else (`library/projects.md`).
- For a product with a user interface, a `design/` folder (`library/screen-design.md`). It holds its own constitution on one capped, machine-checked page, with only what is true there, and one spec per designed screen. Its check holds the shape: one constitution page, one brief at a time, one spec per screen, no two specs sharing an id.
- Checks that do each piece of work once, and the deploy in its proved shape (`library/ci-and-deploy.md`).
- **A boot budget**, held by its own check. Its `AGENTS.md`, `PRODUCT.md`'s summary page and `roadmap.json` together are at most 24,000 bytes (about 6,000 tokens), so a session boots under 10,000 tokens with the rulebook's share. One agent-instructions file, never two near-copies.
