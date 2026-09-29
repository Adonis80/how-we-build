# how-we-build

The rulebook for every product Dhayan's AI studio builds. This repository says **how** we work; each product's repository says **what** we build. It is public: no secrets, prices or customer data, and any session in either stack reads it with no setup.

**How a session reads it (his ruling, 25 September 2026).** Load `HOW-WE-BUILD.md` whole, then this page, which is a map: the products, where each one's plan lives, what every product carries, and the library index. Open a library page only when its trigger fires, and only that page. Nothing is read whole to be safe. `CHARTER.md` is the reasoning, opened by the section a page cites; `RICH-DATA.md` is read on its trigger below; `AGENTS.md` is the reviewer's brief, opened only to change it. What each file is for is in `library/rulebook-files.md`.

## Products under this rulebook

The whole map: what exists, where it lives, one line on what it is for, and the file to open first. It is a directory board, not a summary — nothing here says more about a product than its one line.

- **Myst** — `https://github.com/Adonis80/myst` (private; Juku Perfume, `juku-perfume`, until 16 September 2026). The App for Perfume Collectors, a fragrance intelligence and exchange platform: a Personal Nose that learns a person's taste, samples picked for them, and the value sitting on collectors' shelves. Open `AGENTS.md`, then `PRODUCT.md`, then `roadmap.json`.
- **Hemz OS** — `https://github.com/Adonis80/Hemz-OS` (private). The operating system for an alterations business, grown out of Alma's Alterations in Brighton. Open `AGENTS.md`, then `PRODUCT.md`, then `roadmap.json`.
- **Phena** — `https://github.com/Adonis80/phena` (private; joined 24 September 2026). Phena App, *Documenting the Phenomena*: a living corpus of first-person extraordinary experiences, near-death experiences first, explored through the River. A Juku product at `phena.juku.pro`. Open `AGENTS.md`, then `PRODUCT.md`, then `roadmap.json`.

A repository not listed here is not under this rulebook.

## Where each product's plan lives

One line per product: where its plan is, and how it reaches the build board ([decision 0010](consensuses/juku-os/DECISION-0010-REVIEW-SPEND-AND-PLAN-MAP.md), 29 September 2026). A product with no `roadmap.json` is not a product with no plan: its plan is where this line says.

- **Juku OS** (this rulebook) — no `roadmap.json`. Its plan is its open pull requests, queued ready first, then by priority, then oldest (`library/changing-the-rulebook-merge.md`). On the board: the first row, from those pull requests, their `Priority:` and `Ready:` lines and their review check.
- **Hemz OS** — [`roadmap.json`](https://github.com/Adonis80/Hemz-OS/blob/main/roadmap.json) on `main`. On the board: its row, from that file's items and money milestones.
- **Myst** — [`roadmap.json`](https://github.com/Adonis80/myst/blob/main/roadmap.json) on `main`. On the board: its row, from that file's items.
- **Phena** — [`roadmap.json`](https://github.com/Adonis80/phena/blob/main/roadmap.json) on `main`. On the board: its row, from that file's items and money milestones.

A product joins this map in the pull request that adds it to *Products under this rulebook*. How the board is built: `library/build-board.md`.

A Project's instructions are its template, whole: `library/project-template-product.md`, or `library/project-template-juku-os.md` for the Juku OS Project.

## What every product carries

How a change reaches every product: it is made here once and then lands everywhere — a change to how we build not by anyone remembering, but because every session is sent to this list at its start (by the first line of its `AGENTS.md`, and by its Project's instructions) and a repo that lacks something on it makes itself current in its next pull request. One line each, as of 29 September 2026; the why of each lives in the pull request that added it.

- Free checks and a self-review before any paid read, and on every change the line `Personal data or payments affected: yes/no — reason` ([decision 0010](consensuses/juku-os/DECISION-0010-REVIEW-SPEND-AND-PLAN-MAP.md), 29 September 2026). Detail: `library/reviewer-asking.md`.
- `AGENTS.md` ending with `## Review guidelines`, under 500 words; a check green only when the reviewer has read the current commit; the reviewer `review-gate.py` names. Detail: `library/carries-reviewer.md`.
- Product reads asked from here through `review-product.yml`, and a model switched in one edit (met: `model-registry/`). Detail: `library/carries-review-route.md`.
- Open pull requests moved on before new work; a session that cannot move says so once and stops hard, with the clock tools denied; a consultant that cannot be reached never holds up a slice; a `roadmap.json` fit for a one-word *build*. Detail: `library/carries-sessions.md`.
- `.claude/agents/max-subagent.md`, the max subagent, exactly as its page gives it (his ruling, 28 September 2026). Detail: `library/max-subagent.md`.
- Money milestones in `roadmap.json`; evidence recorded with its origin; the handover's `evidence` field; `PRODUCT.md` and `NAMES.md`; a README route section; a Project set to its template; a `design/` folder for a product with a user interface. Detail: `library/carries-evidence.md`.
- `RICH-DATA.md` read whole by any slice that changes what the product learns from, shows about a person, or claims about its own accuracy, and not otherwise.

## Where each topic lives

One page per topic, or a named few where a topic is over the cap, opened when its trigger fires. `check.sh` holds each page's shape; what it checks is in `library/rulebook-files.md`.

| Page | Open when |
|---|---|
| `library/session-changeover.md`: *Session changeover* | deciding whether to stay in a session or start a fresh one, and before leaving one |
| `library/screen-design.md`: *How a screen gets designed* | a screen is new or reworked, before any code for it |
| `library/two-stacks.md`, `library/stack-anthropic.md`, `library/stack-openai.md`: *The two stacks* | choosing the lead or its effort, handing work between stacks, a job that needs hands |
| `library/max-subagent.md`: *The max subagent* | a lead hands its max piece on, or a product sets up or checks its max subagent file |
| `library/reviewer.md`: *The independent reviewer* | working out who reviews a change, what it is shown, or what a risky class of change is owed |
| `library/reviewer-one-vendor.md`: *The independent reviewer: one vendor, and what it costs* | weighing a same-vendor read or a gate change, or asking which repositories the badge counts in |
| `library/reviewer-verdict.md`: *The independent reviewer: what a read is* | judging whether a commit is cleared, or how a verdict is signed and why no comment counts |
| `library/reviewer-machine.md`: *The independent reviewer: the machine, and installing the App* | changing the review machinery, or putting the reviewer App on a repository |
| `library/reviewer-asking.md`: *The independent reviewer: asking, and what it spends* | asking for a read, deciding whether to ask again, or setting what a product's checks run |
| `library/reviewer-parking.md`: *The independent reviewer: parking* | about to park a slice, or the reviewer seems out |
| `library/reviewer-brief.md`: *The independent reviewer: the brief* | writing a repository's AGENTS.md or its Review guidelines, or a rule lands mid-session |
| `library/consultant.md`: *The consultant* | asking the consultant for a sweep, a bug hunt or a better procedure, or answering its findings |
| `library/consultant-instructions.md`: *The consultant: its standing instructions* | the consultant cannot be reached, or its standing instructions are set or changed |
| `library/rulebook-files.md`: *What each file here is for* | asking what a root file or a decision issue is for, or why this repository is public |
| `library/product-joins.md`: *How a product joins* | adding a product to the map, or setting up its repository |
| `library/project-template-product.md`: *Project instructions template* | setting or checking a product Project's instructions |
| `library/project-template-juku-os.md`: *The Juku OS Project's instructions* | setting or checking the Juku OS Project's instructions |
| `library/project-instructions.md`: *What a Project holds, and who sets it* | a Project's instructions differ from their template, or text for the Chairman changes |
| `library/carries-reviewer.md`: *What every product carries: the reviewer* | checking a product's gate, its reviewer or its review guidelines |
| `library/carries-review-route.md`: *What every product carries: the product read, and the model switch* | asking for a product read from here, or switching the model behind a role |
| `library/model-registry.md`: *The model registry* | asking which model holds a role, what a read resolved to, or switching the model behind a role |
| `library/carries-sessions.md`: *What every product carries: open work, stopping, the consultant, the roadmap* | starting or stopping a product session, or leaving its roadmap |
| `library/carries-evidence.md`: *What every product carries: milestones, evidence, the product's pages* | a slice touches money milestones, evidence, the product's own pages, its README route or its design folder |
| `library/build-board.md`: *The build board* | working on the build board |
| `library/deploy.md`: *The deploy, in shape* | building or changing a product's deploy |
| `library/money.md`: *Money out waits for money in* | anything would cost money, or a product's hosting plan comes up |
| `library/code-and-words.md`: *Code and words* | deciding whether a change needs a code session or can be made from Cowork |
| `library/changing-the-rulebook.md`: *Changing the rulebook: the word cap* | changing HOW-WE-BUILD.md or arguing about its word cap |
| `library/changing-the-rulebook-merge.md`: *Changing the rulebook: the queue, the gate and the merge* | proposing, prioritising or merging a change to this repository |

## How a product joins

Its steps are `library/product-joins.md`.

## Reading it from a session

```
git clone --depth 1 https://github.com/Adonis80/how-we-build
```

or fetch `https://raw.githubusercontent.com/Adonis80/how-we-build/main/HOW-WE-BUILD.md`.

## Changing the rulebook

By pull request only; `main` is protected; the CTO settles and merges without the Chairman. **Tidying is frozen (his ruling, 25 September 2026):** no page moves, splits or rewording for tidiness unless something is broken, and one session's word changes to this repository go in one pull request, read once. **The whole repository is frozen until 10 October 2026 (his ruling, 26 September, settled with the consultant that day):** no pull request here of any kind — no rule, page, check, reviewer change, decision record or consultancy — except one that names a specific product task that was attempted, the failure observed, and the smallest repair that lets that task continue; an anticipated difficulty, an advisory finding or a preference does not qualify. Open work here parks. He lifted it once, on 28 September, for every read at max ([#123](https://github.com/Adonis80/how-we-build/pull/123)) and the effort ladder ([#124](https://github.com/Adonis80/how-we-build/pull/124)), in his words *"Lift the 10 October freeze for this one change only"*; both pull requests quote his rulings whole. He lifted it again on 29 September for the items of [decision 0010](consensuses/juku-os/DECISION-0010-REVIEW-SPEND-AND-PLAN-MAP.md) only, its owner table naming each; his ruling reached the code session that filed it as *"the Chairman lifted the 10 October freeze for its items only"*. He lifted it once more the same day for [#118](https://github.com/Adonis80/how-we-build/pull/118) alone: asked which parked pull request to move, his words to the session that moved it were *"move 118"*, quoted on that pull request. His ruling that evening on who reviews (no reader is the lead's own model; Sonnet 5.5 at max wherever GLM does not read) is a ruling of his own, and lands on its own pull request, which quotes it whole. The week's measure is product: one agreed Hemz OS journey usable and accepted by him by 3 October, within his spending ceiling, with spend on the journey and spend on anything else reported as two numbers. The word cap is in `library/changing-the-rulebook.md`; the queue, the gate and the merge in `library/changing-the-rulebook-merge.md`.
