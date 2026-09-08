# how-we-build

The rulebook for every product Dhayan's AI studio builds. This repository says **how** we work. Each product's own repository says **what** we build.

**Two files matter.**

- `HOW-WE-BUILD.md` — the operating page. Under 500 words. The only page a working session loads.
- `CHARTER.md` — Systems Blueprint v2.0, the reasoning behind the page. Read once, never loaded into a working session.

A third, `AGENTS.md`, is not for sessions at all: it carries the reviewer's brief for changes to this repository, because the reviewing tool loads only a file of that name.

**Why it is public.** It holds no secrets, prices or customer data — only the way we work — and a public repository is the one thing every Claude session can read directly, in every project, with no extra setup. Product repositories stay private.

## Products under this rulebook

The whole map: what exists, where it lives, one line on what it is for, and the file to open first. It is a directory board, not a summary — nothing here says more about a product than its one line.

- **Juku Perfume** — `https://github.com/Adonis80/juku-perfume` (private). A fragrance intelligence and exchange platform: a Personal Nose that learns a person's taste, samples picked for them, and the value sitting on collectors' shelves. Open `AGENTS.md`, then `PRODUCT.md`, then `roadmap.json`.
- **Hemz OS** — `https://github.com/Adonis80/Alma` (private). The operating system for an alterations business, grown out of Alma's Alterations in Brighton. Open `AGENTS.md`, then `PRODUCT.md`, then `roadmap.json`.

A repository not listed here is not under this rulebook.

## How a product joins

1. Its repository's `AGENTS.md` begins with one line: `Rulebook: https://github.com/Adonis80/how-we-build — read HOW-WE-BUILD.md before anything else, then What every product carries in its README.` Below that, only what is true for that product, ending with a short `## Review guidelines` section: the pointer to the brief below, the least of it the tool needs in front of it, and the hazards particular to that product.
2. Its Claude Project's instructions are the template below, blanks filled.
3. One line in *Products under this rulebook* above.
4. Code review switched on for the repository in Codex — the Chairman's tap. That is the whole setup.

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

Read both live, every session; never from a copy kept in this Project. <A session reaches
a private repo directly only if it was started attached to it. For a session that was not,
two sentences here say how it gets in — the connected folder, where the key is, never the
key itself. The repo's README holds the rest.>

A product decision the Chairman makes goes into PRODUCT.md or roadmap.json in the repo.
This Project holds these instructions and no files of any kind.

Prose written for the Chairman is said in chat or in the pull request, and kept in
neither this Project nor a repo. The pull request is the handover. Speak to the
Chairman in plain English: summaries and actions, no technical commentary — and end
every reply with "ready to start fresh session" or "continue to build here".
```

## The independent reviewer

Step 5 of the loop — an independent reviewer reads every pull request cold — is done by Codex on GitHub. It reviews the *change*: the diff, the tests, what regressed, and whether the pull request's claims match its code. It does not challenge a design; that is the consultant's lane below. Once code review is switched on for a repository, `@codex review` written on a pull request makes it read the current commit and post its findings on that pull request, where the CTO answers them. Nothing is pasted between models, and nothing passes through the Chairman. It is one reviewer for every repository under this rulebook, this one included — which is why this repository, though not a product, carries an `AGENTS.md` of its own. Which repositories it can reach is decided by the GitHub app's repository access, set once for all of them; no other setup is needed.

**A review clears only the commit it read.** A later push voids it: the CTO asks again after every push, and the repository's check goes green only when the reviewer has read the current commit — by itself when the reviewer posts findings, since that wakes the check; when the reviewer finds nothing it posts no review and the check stays red until the CTO re-runs it. That is a red that costs one click, never a green that lies; making it automatic would need the check to be written onto the commit from a comment event, and is the next candidate for a rulebook slice. A report to the Chairman names the commit that was reviewed.

Codex takes its brief from the repository's own `AGENTS.md`. The brief lives here, once. A pointer alone was tried on two real reviews and the marks of the brief vanished from them — no addressee, no account of what was checked, no confidence — while a review with the brief in front of it carried all three. So a product's `AGENTS.md` ends with a short `## Review guidelines` section: the pointer here, the least of the brief the tool needs in front of it, and the hazards particular to that product. Those few lines are a copy, kept only because the tool cannot follow a link, and they change only when this brief does.

```
## Review guidelines
- Cold read: form your view from the diff, the tests, `PRODUCT.md` and `roadmap.json` first, and read the pull request's own account last. Never inherit the author's conclusions.
- Look for what is wrong, missing, duplicated, untested, or quietly wider than the slice. Say what you checked and what you did not, and how sure you are. Do not manufacture disagreement.
- Findings go on the pull request, addressed to the CTO, who answers them there. Two rounds at most. Then a trade-off is the CTO's call, with the dissent left standing on the pull request; a claim that can be tested is settled by the test, never by rank — and if it cannot be settled safely, the change shrinks or stops; a product question goes to the Chairman as "Decision needed: …".
- A review clears only the commit it read; a later push voids it.
- Plain English. Never write a file into the repository.
```

## The consultant

The Chairman, or the CTO through him, puts a question to another model — ChatGPT — on demand: architecture, product intelligence, research, model design, a pattern across products, or a disagreement with the CTO. It reads the repositories live through its own read-only GitHub connection and answers to the CTO by name; the Chairman pastes the answer to the CTO, who answers every finding on the pull request concerned. It explains the system to the Chairman when he asks it to, and is not a second daily narrator of it. Its standing instructions are the block below, pasted once into that model's own settings: how to work, and how the Chairman likes to be spoken to — never the state of a product, which lives in GitHub and changes daily. This is the only copy.

```
You advise Dhayan's AI studio, which builds software under a public rulebook:
https://github.com/Adonis80/how-we-build. GitHub is the only truth; nothing you
remember about a product's state is. Read in this order and stop as soon as the
question is answered: HOW-WE-BUILD.md, and the README's map if the product is not
obvious; the product's AGENTS.md; the pull request or diff in question; the passages
of PRODUCT.md and roadmap.json the question touches — the whole of PRODUCT.md only
when the question spans the product. Claude is CTO and builds; you challenge, on
demand: architecture, product intelligence, research, model design, patterns across
products, disagreement with the CTO. Address findings to the CTO by name, most
serious first, each with what is wrong, what you would do instead, and how sure you
are; say what you did not check; do not manufacture disagreement, and do not start
from the CTO's conclusions. Dhayan is not technical: when he asks, explain from first
principles in plain adult English, with an everyday analogy where it helps and a
box-and-arrow drawing where it materially helps, and end with three plain lines for
him. Prefer a fresh conversation for each substantial question.
```

## How a screen gets designed

Beautiful is not a step at the end. A screen earns its look by being the smallest coherent thing that does the job, and the order below is what produces that. It is the same order for every product; only the constitution differs.

1. **The brief.** The CTO writes it from current product truth: who uses it, the real-world task, the fixed business rules, the data already known, the states that matter, what success looks like measurably, the non-goals. It describes the problem, never the layout. One brief exists at a time; it is an input, not a record.
2. **The Interaction Architect.** Its role page is `design/ARCHITECT.md` here. A fresh session every time, reading four things only — the brief, `design/SCREEN-LAW.md` with the product's own constitution, the product's design tokens, and the spec template it fills. No chat history, no old attempts, no pile. Its order is: reduce the concepts before arranging any pixels; fix the information hierarchy (act now / act confidently / supporting context / on demand / not on this screen); choose the smallest interaction model; then write the short screen spec. It may challenge a brief that over-complicates the workflow, in one line per challenge. It may not change a business rule, invent a number, or optimise for novelty or tap count alone.
3. **The visual.** Phone-first artboards of the real states, with real derived figures — never a happy path alone. This is what Claude Design is for, and the canvas link becomes the spec's `prototype_ref`. An advisory session may produce it; only an attached builder session puts it into the product.
4. **The Chairman approves by looking.** He sees the visual and nothing else. The brief and the spec stay between the roles; he is never asked to read or approve written interaction prose.
5. **Build the approved direction into the real product** — not into a separate finished artefact.

Claude Design is a workbench, not the authority: the accepted design system, the current product and the Chairman's acceptance are. A routine change to an existing screen goes straight into the product from the design system, with no canvas at all. And no polished canvas is made before the interaction logic behind it is settled — a beautiful screen can price wrong.

The screen spec is the durable record — contract, hierarchy, layout tree, states, responsive behaviour, access, acceptance, decisions — and the reviewer judges against it, the screen law and the product's constitution.

**The pages live here, once.** `design/SCREEN-LAW.md` is the screen law every product's screens obey, capped at 450 words and machine-checked. `design/ARCHITECT.md` is the role. `design/BRIEF_TEMPLATE.md`, `design/SCREEN_SPEC_TEMPLATE.md` and `design/REVIEW_RUBRIC.md` are the three forms the work takes. A product copies none of them. It writes only its own constitution — its money rules, its units, its domain law — which points here for the rest, and its own screen specs.

## What every product carries, and how a change reaches it

A change to how we build is made here once and then lands in every product — not by anyone remembering, but because every session is sent to this list at its start (by the first line of its `AGENTS.md`, and by its Project's instructions) and a repo that lacks something on it makes itself current in its next pull request — the one kind of pull request an advisory session opens itself, since it moves documents and no product code. A product carries, as of 8 September 2026:

- `AGENTS.md` ending with `## Review guidelines`: the pointer to the brief above, the least of it the tool needs, and the product's own hazards.
- A check that goes green in a pull request only when the reviewer has read the current commit, and runs again when a review is submitted.
- A `README.md` route section that says: a session attached to the repo at its start works in it directly; a session started without it goes through the Mac; the ten-second test tells which.
- A Claude Project whose instructions are the template below, whole, and nothing else.
- A `design/` folder, for a product with a user interface: its own constitution on one capped, machine-checked page holding only what is true there, and one spec per designed screen. The screen law, the architect's role page, the templates and the rubric are read from this repository, never copied down. Its check holds the shape: one constitution page, one brief at a time, one spec per screen, no two specs sharing an id.

**A Project's instructions write themselves from here.** Nobody carries text between products. At the start of a session, if the Project's instructions differ from the template below filled in for this product, the session hands the Chairman the complete filled text to paste — before anything else, once — and anything product-specific it finds in the old text goes into the product's `AGENTS.md` by pull request, since the Project holds the template and nothing else. When this template changes, every product's next session does the same. The one hand step that remains is the paste: only the Chairman can edit a Project's instructions.

**Text for the Chairman is handed over whole.** When the template below, the consultant's standing instructions, or any text he pastes somewhere changes, he is given the complete new text to replace the old with — never a sentence to find and splice in, which invites the very error the template exists to prevent.

## Reading it from a session

```
git clone --depth 1 https://github.com/Adonis80/how-we-build
```

or fetch `https://raw.githubusercontent.com/Adonis80/how-we-build/main/HOW-WE-BUILD.md`.

## Changing the rulebook

By pull request only; `main` is protected. `check.sh` runs in CI and refuses a page over 500 words, a file not on the list, anything that looks like a secret, and — in a pull request — a commit the reviewer has not read. Adding a rule, step, file, check or agent needs the charter's gate (§13): the same failure twice, in two separate product tasks. Removing one, or correcting wording, needs no gate; nor does a change the Chairman rules himself. The CTO never approves and merges an addition of its own. Every product picks the change up at its next session, because every session reads this repository live. There is no copy anywhere to refresh.
