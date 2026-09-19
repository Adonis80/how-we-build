# how-we-build

The rulebook for every product Dhayan's AI studio builds. This repository says **how** we work. Each product's own repository says **what** we build.

**Three files matter.**

- `HOW-WE-BUILD.md` — the operating page, short and machine-checked; the cap lives in `check.sh`. The first thing a working session loads, with *What every product carries* below.
- `CHARTER.md` — the Systems Blueprint, the reasoning behind the page. Read once, never loaded into a working session.
- `RICH-DATA.md` — the method for what a product learns from and how we know its AI got smarter. Read on the trigger in *What every product carries*, and not otherwise.

A fourth, `AGENTS.md`, is not for sessions at all: it carries the reviewer's brief for changes to this repository, because the reviewing tool loads only a file of that name.

**Why it is public.** It holds no secrets, prices or customer data — only the way we work — and a public repository is the one thing every session, in either stack, can read directly, with no extra setup. Product repositories stay private.

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

## The independent reviewer

Step 5 of the loop — an independent reviewer reads every pull request cold — is done, until further notice, by the reviewer named in *What every product carries*, with Codex on GitHub reading as well wherever it is available, in every repository under this rulebook; where the list below requires the other stack, Codex reads Claude's work and a Claude session reads OpenAI's. It reviews the *change*: the diff, the tests, what regressed, and whether the pull request's claims match its code. It does not challenge a design; that is the consultant's lane below. Once code review is switched on for a repository, `@codex review` written on a pull request makes Codex read the current commit and post its findings on that pull request, where the CTO answers them. Nothing is pasted between models, and nothing passes through the Chairman. Codex is one reviewer for every repository under this rulebook, this one included — which is why this repository, though not a product, carries an `AGENTS.md` of its own. Which repositories it can reach is decided by the GitHub app's repository access, set once for all of them; no other setup is needed.

**Cold, and cross-vendor where it counts.** Independent means a session of its own, forming its view from the diff and the tests before reading the pull request's own account. The same vendor is acceptable; the other vendor is preferred; and on pricing logic, live database mutation or schema, authentication and authorisation, public trust-boundary changes, deploy and release machinery, and this review gate itself, the other vendor is required. If it is unclear whether a change crosses a trust boundary, it does. Every pull request carries `Lead stack:` and `Reviewed by:`, so the pair is visible without asking. The machine has counted one reviewer identity until now: `check.sh` turned green on a read by the Codex bot and nothing else. So while a reviewer identity for the other stack does not exist on GitHub that the check can count, **an OpenAI-led slice in any of those classes does not start** — Claude leads it and Codex reads it, and the gate means what it says. A Codex read of OpenAI's own work never satisfies that list, because no such pull request is opened. Everything outside the list is open to either lead, with the same cold read. What would change this is *the badge* below, and it is half built: the identity exists, this repository's gate counts it, and it has never signed a verdict, because its key is not sealed yet. The restriction therefore stands exactly as written until a run shows the badge answering — a rule lifted on machinery nobody has watched work is the failure this whole section keeps paying for.

**A review clears only the commit it read.** A later push voids it: a round's fixes land as one push and the CTO asks once, and a repository's check goes green only when the reviewer has read the current commit — by itself, with no hand re-run, whichever shape the answer takes. Codex's findings arrive as a submitted review and its clean pass as a plain comment naming the commit, and both count as a read (fixed 9 September, after a clean pass left a pull request red overnight); the badge's verdict is one check run, whose commit and conclusion are fields rather than sentences, so there is no shape to miss. This repository goes further, because here the proposer may not clear its own addition: its gate tells the two shapes apart and opens on a clean read alone, so a head the reviewer left findings on stays red until the push that answers them. A report to the Chairman names the commit that was reviewed.

**The badge: what a read has to be, and why it is not a comment.** [#34](https://github.com/Adonis80/how-we-build/pull/34) closed at round ten having settled the bar, and [#38](https://github.com/Adonis80/how-we-build/pull/38) was built without reading it and failed both halves. A read must arrive **under a login a branch cannot wear, as a signal a branch cannot erase**. A verdict posted as a comment by `github-actions[bot]` is neither: that login belongs to every workflow token in the repository, including one on a throwaway branch that is never opened as a pull request, and an issue comment can be edited or deleted by anyone with write access — which is exactly the population a review gate defends against. Both halves come from one fact: **only a GitHub App can create a check run**, and nobody with write access can forge, edit or delete one. So the reviewer signs as an App — `juku-reviewer`, created on the Chairman's account 19 September 2026 and installed on this repository alone — and its verdict is that check run's own `conclusion`, on that check run's own `head_sha`. Nothing is parsed out of prose. The comment the workflow also posts is the same words where people can read them, and the gate reads none of it, which is why it does not matter who can edit that. A GitHub App is free; the managed alternative costs a Team plan and $15–25 a review, and does not let the model or the effort be chosen, which is the Chairman's ruling broken at the moment of purchase.

**The door, and why it is proved rather than stated.** The App's private key is what a branch would need to sign with, so it lives in a repository **environment** named `reviewer` whose deployment branch policy admits `main` and nothing else, and the reviewer workflow's job names that environment. A run whose ref is a branch is refused the job before it starts. The reviewer reaches `main` because it triggers on `issue_comment` alone, and an `issue_comment` run's ref is the default branch — proved on #38, run `35343442166`, `head_branch: main`. GitHub documents the environment half, but documentation is not this standard: `.github/workflows/door.yml` is a standing, re-runnable proof — push a branch named `proof/door-*` and watch the job refused, or run it on `main` and watch it read the key — because a protection rule nobody has watched refuse anything is a claim. A green door run on a branch means the badge is forgeable and nothing should merge until the policy is back.

**A product copies four files and one tap, not a paragraph.** `review-gate.py` holds the register, the door in the gate and the wiring checks; `.github/workflows/` holds the reviewer, the wake it calls and the door's proof; `check.sh` runs the lot. The Chairman's part is installing the App on the repository. This repository proves the route first, being public and holding no secrets, prices or customer data; the product repositories follow once a run here has shown a badge answering end to end.

**The session asks once and stops; two rounds is the limit for the CTO too.** After a push, ask the reviewer and stop there. The check turns green by itself when the review lands, so nothing is gained by watching it, and a session that reports "nothing to do" is spending the Chairman's attention on its own idling. Two rounds binds the CTO as well as the reviewer: answer what the first and second rounds raise, then land the slice with any remaining dissent left standing on the pull request. A third round means the slice is too big — shrink it and ship what is proved. None of this reaches the Chairman; he gets the preview, what changed, and "Decision needed: … or none".

**The reviewer's budget is finite and shared.** One allowance serves every repository under this rulebook: spent on one product, it is spent for all, and a words-only pull request draws on the same pool. That is why the ask comes once per round, with the round's fixes batched into one push — an ask per small push reads the same code many times over and empties the allowance. Learned the expensive way on 9 September: nine asks on nine small pushes to one Juku Perfume pull request ended reviews by mid-afternoon, and within minutes the same wall refused Hemz OS on two pull requests — the same failure, twice, in two products, which is what clears the charter's gate for this rule.

**When the gate can count no read** — Codex out, its allowance spent or the service down — the gate does not open and is not waived; the named reviewer alone being out holds nothing up, as *What every product carries* says. The slice parks: one comment on the pull request names the blocker, then no further pushes and no further asks, which only deepen the hole. Nothing watches for the reviewer's return, on any clock: a watch cannot see it, since only an ask can tell and a parked slice makes none. The return is found by the next session to start, whose ask on the oldest parked pull request either lands or is refused. Parked work never stops the line: the next slice starts from `main` in its own session — but `main` still names the parked slice as the top roadmap item, so a session starting on *build* alone would rebuild it. When the reviewer returns, parked pull requests re-enter review oldest first, one ask each. None of this reaches the Chairman: a parked slice is the CTO's wait, not his problem, and he hears of it only when it moves something he was promised.

**A change here reaches a session at its start, never mid-flight.** A running session keeps the page it read when it began, so a rule landed at noon does not bind a session that started at eleven. Nothing is done about this: a session that re-read its rules mid-slice would be a session whose ground moved under it. The consequence is only that a new rule shows up in the next session, not the one in front of you.

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

The Chairman, or the CTO through him, puts a question to the chat surface of the stack that is **not** leading — ChatGPT while Claude leads, a Claude chat session while OpenAI leads — on demand: architecture, product intelligence, research, model design, a pattern across products, or a disagreement with the CTO. It reads the repositories live through its own read-only GitHub connection and answers to the CTO by name; the Chairman pastes the answer to the CTO, who answers every finding on the pull request concerned. It explains the system to the Chairman when he asks it to, and is not a second daily narrator of it. On the OpenAI side, its strongest model is reachable only from cloud work mode, so an architecture question is asked there; Codex builds, and does not challenge a design. **When the consultant cannot be reached, the work does not wait** (the Chairman's ruling, 16 September 2026): what the lead does then is in *What every product carries*, where every product session reads it. The Chairman may still carry a question to another account of his by hand, if he chooses. A Claude session with the Chrome extension can also ask the consultant itself, in the Chairman's own browser, so his hands are not needed when it is reachable. The standing instructions are the block below, pasted once into that model's own settings — and written by role, so the same text serves whichever stack is consulting: how to work, and how the Chairman likes to be spoken to — never the state of a product, which lives in GitHub and changes daily. This is the only copy.

```
You are the consultant to Dhayan's AI studio, which builds software under a public rulebook:
https://github.com/Adonis80/how-we-build. GitHub is the only truth; nothing you
remember about a product's state is. Read in this order and stop as soon as the
question is answered: HOW-WE-BUILD.md, and the README's map if the product is not
obvious; the product's AGENTS.md; the pull request or diff in question; the passages
of PRODUCT.md and roadmap.json the question touches — the whole of PRODUCT.md only
when the question spans the product. The lead — the model he started with *build* — is CTO and builds;
you challenge, on demand: architecture, product intelligence, research, model design, patterns across
products, disagreement with the CTO. Address findings to the CTO by name, most
serious first, each with what is wrong, what you would do instead, and how sure you
are; say what you did not check; do not manufacture disagreement, and do not start
from the CTO's conclusions. Dhayan is not technical: when he asks, explain from first
principles in plain adult English, with an everyday analogy where it helps and a
box-and-arrow drawing where it materially helps, and end with three plain lines for
him. Prefer a fresh conversation for each substantial question, and end one when the bounded
question is settled, when the next turn is materially a new question, or when reloading the
small source set would be cheaper and clearer than carrying the thread.
```

## Session changeover

His ruling, 10 September 2026: at every turn, weigh whether it is cheaper to stay in this session or start a fresh one, and when starting fresh, leave the next session what it needs. What follows is that ruling, worked out with the consultant and written down.

At every turn, decide whether the next turn stays here or starts fresh. Stay only while all three hold:

- **Same work:** the same slice or bounded question continues.
- **Cheaper to stay:** the useful unresolved context here costs less than rebuilding it from the small canonical boot.
- **Clear:** the history still helps more than it hurts, with no material stale truth, contradiction, looping, irrelevant output or lost detail.

Otherwise, checkpoint and start fresh. Provider caches and compaction can inform that judgement but are never rules in themselves.

Before leaving, put every durable fact in GitHub and make the pull request and roadmap handover sufficient on their own. If the opening words for the next session would have to carry project state, the handover is not finished. Advisory work that has no repository yet gets one temporary `START-HERE.md` — the bounded question, what is agreed, the next action, the files that matter — superseded the moment the result lands in GitHub.

**And say so, as a claim that can be wrong.** A turn that ends "ready to start fresh session" also states that the next session has full context: the repository carries what it needs, and nothing has to be pasted. The saying is the mechanism. The obligation above — the handover sufficient on its own — is invisible until somebody checks it, and a session can satisfy the phrase while failing the substance. Stating it turns the phrase into a claim, and a claim gets checked before it is made. On 14 September 2026 a Juku Perfume session ended eight replies "ready to start fresh session" while `roadmap.json` still pointed at code that session had just deleted, still said a blocker had gone when it had not, and named no next action at all. The Chairman had to ask whether the slice was even finished; the check that question forced found six wrong lines. Nothing was concealed — the phrase had become a sign-off rather than a statement about the repository, and a sign-off costs nothing to say.

A fresh session reads progressively from canonical truth and stops when it knows enough. It never rebuilds repository state from old chats. Keep tool output targeted, and never poll. For Codex, a fresh task starts each slice and a thread is continued only inside that slice, while the three above hold.

## The two stacks

One lead owns a slice at a time. The pull request is the handover, and a replacement lead rebuilds what it needs from GitHub, never from a chat. At a clean checkpoint, *build* in the other stack transfers ownership — and only then: ownership moves when the pull request's latest entry is the outgoing lead's checkpoint. Otherwise the incoming lead leaves that pull request alone and takes the next item. Nothing is built to manage this: no switch file, no lock service, no registry, no orchestrator.

**Anthropic.** Building happens in a code session started attached to the repository. A Cowork or chat session advises, and may change words through the Mac by pull request. The hard stop is enforced by the product's `.claude/settings.json`. **Its hands are Claude's own, used from a Cowork session: the Chrome extension, computer use on the Mac, and the Claude app's built-in browser** — for a console, a dashboard, a setting no pipeline can reach (his rulings: 14 September 2026, *you should do all manual tasks with chrome extension*; 17 September 2026, *make sure that in future all manual tasks are done through Claude chrome extension and or computer use*, and later that day, *i want you to be autonomous and independent, so use Claude app's own built-in browser for manual jobs*). Claude's own pages at `claude.ai` go to the built-in browser: on 17 September 2026 the extension refused them (*Navigation to this domain is not allowed*). A code session started at `claude.ai/code` has none of these hands. It puts the job in CI; where CI cannot do it, it writes the job on its pull request under **Hands needed:** with every choice already made, and tells him only where to take it: a Cowork session in the product's Project, and the word *build* — the only word he types to start work, in either stack and in Cowork or code mode, because the reply names the room and the session works out the job. That session reads the open pull requests for the line, sees whether the job in front of it is hands or code, does the work, and says so on the pull request — what was done, never a secret — so the next code session on *build* carries the slice on rather than asking again. **Such a job keeps an open pull request until it is done**, and the slice carrying it does not merge out from under it: either the pull request waits, or the job moves to one that stays open before the merge. The queue here is the open pull requests, so a job on a merged one is a job *build* will never find — which is the same thing as handing him the job, and on 19 September it ended with a session telling him to type a sentence instead of the word. He types *build*. Anything that needs more than that is a fault in the line, not an instruction for him. Neither is a second lead; advising is not owning.

**OpenAI.** Codex is the development surface — cloud by default, local only when the work needs the Mac — and ChatGPT is the advisory surface, reading GitHub and writing nothing. The Chairman's finding of 11 September 2026: the strongest OpenAI model is reachable only from ChatGPT's cloud work mode, and the ChatGPT desktop app cannot work in a repository at all. So an OpenAI-led build runs as a Codex cloud task, and an OpenAI architecture review is asked in cloud work mode. A Codex cloud environment is built from the repository's own toolchain, not from a template: the setup script installs what the lockfiles name and clones this rulebook to `~/.juku/how-we-build`; the maintenance script refreshes that clone and fails closed, so a cached environment never starts on stale rules; agent internet stays off unless the repository genuinely needs it, and then as a named allowlist — its package registry and GitHub — restricted to GET, HEAD and OPTIONS, because the broad preset has a published prompt-injection route out; and no secret is added until a product proves it needs one. One line in the product's `AGENTS.md` points a lead working offline at the local rulebook. Schedules, automations and polling are forbidden in the build loop, as the hard stop forbids them on the other side. **It has no hands**: ChatGPT writes nothing and Codex has no browser, so an OpenAI-led slice puts a manual action in CI, and where it cannot, checkpoints and transfers by the route above rather than borrowing another stack's. Nothing here pretends otherwise, and nothing reaches the Chairman instead.

**Whichever stack leads, his part is only a tap no hand may make.** The hands may not sign in for him, type a password or a secret into a web page, get past an are-you-human check, pay, or approve a sign-in key on his account by themselves. A session takes such a job to that one tap and hands him the tap alone — the link, what he will see, the words to reply — never the job, and never a choice of how. Learned 17 September 2026: a Hemz OS code session handed him *add one credential — an Anthropic API key or a Claude subscription token*, a job with a choice attached. The Cowork session that took it over chose the subscription token, since it needs no new spending, made it, and put it into the repository's secrets through GitHub's API, sealed, where no person or model saw it. Its own safety guard refused to approve the key without him, which is right, and Claude's approval page, after stalling twice in his Chrome, went through at once in the built-in browser. All he did was sign in and tap *Authorize*.

**The Chairman's ruling, 11 September 2026.** While Claude Opus 5 at maximum effort is the strongest model available to him, it leads, and the OpenAI path stays configured and used for review. The rules are written by role, so the swap costs nothing the day that changes.

## How a screen gets designed

Beautiful is not a step at the end. A screen earns its look by being the smallest coherent thing that does the job, and the order below is what produces that. It is the same order for every product; only the constitution differs.

1. **The brief.** The CTO writes it from current product truth: who uses it, the real-world task, the fixed business rules, the data already known, the states that matter, what success looks like measurably, the non-goals. It describes the problem, never the layout. One brief exists at a time; it is an input, not a record.
2. **The Interaction Architect.** Its role page is `design/ARCHITECT.md` here. A fresh session every time, reading four things only — the brief, `design/SCREEN-LAW.md` with the product's own constitution, the product's design system (tokens and approved patterns), and the spec template it fills. No chat history, no old attempts, no pile. Its order is: reduce the concepts before arranging any pixels; fix the information hierarchy (act now / act confidently / supporting context / on demand / not on this screen); choose the smallest interaction model; then write the short screen spec. It may challenge a brief that over-complicates the workflow, in one line per challenge. It may not change a business rule, invent a number, or optimise for novelty or tap count alone.
3. **The visual.** Phone-first artboards of the real states, with real derived figures — never a happy path alone. This is what Claude Design is for, and the canvas link becomes the spec's `prototype_ref`. An advisory session may produce it; only an attached builder session puts it into the product.
4. **The Chairman approves by looking.** He sees the visual and nothing else. The brief and the spec stay between the roles; he is never asked to read or approve written interaction prose.
5. **Build the approved direction into the real product** — not into a separate finished artefact.

Claude Design is a workbench, not the authority: the accepted design system, the current product and the Chairman's acceptance are. A routine change to an existing screen goes straight into the product from the design system, with no canvas at all. And no polished canvas is made before the interaction logic behind it is settled — a beautiful screen can price wrong.

The screen spec is the durable record — contract, hierarchy, layout tree, states, responsive behaviour, access, acceptance, decisions — and the reviewer judges against it, the screen law and the product's constitution.

**The pages live here, once.** `design/SCREEN-LAW.md` is the screen law every product's screens obey, capped at 450 words and machine-checked. `design/ARCHITECT.md` is the role. `design/BRIEF_TEMPLATE.md`, `design/SCREEN_SPEC_TEMPLATE.md` and `design/REVIEW_RUBRIC.md` are the three forms the work takes. A product copies none of them. It writes only its own constitution — its money rules, its units, its domain law — which points here for the rest, and its own screen specs.

## What every product carries

How a change reaches every product: it is made here once and then lands everywhere — a change to how we build not by anyone remembering, but because every session is sent to this list at its start (by the first line of its `AGENTS.md`, and by its Project's instructions) and a repo that lacks something on it makes itself current in its next pull request. One line each, as of 17 September 2026; the why of each lives in the pull request that added it.

- `AGENTS.md` ending with `## Review guidelines`: the pointer to the brief above, the least of it the tool needs in front of it, and the product's own hazards — under 500 words, machine-checked.
- A check that goes green in a pull request only when the reviewer has read the current commit, counting both shapes of answer — a submitted review, and a plain comment naming the commit.
- The reviewer, until further notice: Claude Sonnet 5 at maximum effort (his ruling, 18 September 2026, replacing that day's earlier word for Claude Fable 5.1). It is named in one place per repository — here, `review-gate.py`'s `REVIEWER_MODEL` — so a change is one line, and the workflow that runs it is held against that line by the check. It reads every pull request cold at that effort, from the committed diff and the pages the diff does not touch, before the pull request's own account. Codex also reads wherever it is available, and is always asked on the classes in *Cold, and cross-vendor where it counts*. When the named reviewer is the one out, nothing is held up: Codex's clean read turns the check green by the ordinary route. The other way round is what *the badge* below is for, and until a run shows it answering, a repository's check still counts only Codex — so when Codex cannot read, the slice parks as it always has. What is never the answer is a sentence permitting a merge while the check is red: one check carries the word caps, the file lists and the secret scan too, so any such permission waives those with it. Powerful open-weight models join as reviewers next, by the same route (his ruling, 18 September 2026).
- Open pull requests read before starting: a slice parked only for review, or waiting under **Hands needed:**, is moved on rather than rebuilt or restarted — its findings answered, its fixes pushed, its ask made, its hands asked for, and that is the session's work — while a stale or abandoned one is closed or taken over, and anything else is left alone and the next roadmap item taken. An open pull request defers a slice; it never blocks every slice.
- A session that cannot move says so once on the pull request and stops hard (his ruling, 10 September 2026). No clock wakes it — no check-in, timer, loop, scheduled task or background watch, and no shell left waiting past the work in hand, which still allows the waits a slice needs, such as the deploy's couple of minutes. Something happening may wake it: a review landing, a check failing, the Chairman writing. `.claude/settings.json` denies the clock tools — `ScheduleWakeup`, `CronCreate`, `RemoteTrigger`, `mcp__*__send_later`, `mcp__*__create_trigger`, `mcp__*__update_trigger`, `mcp__*__fire_trigger` — and the check fails if one goes missing; a shell left sleeping is forbidden by the rule, which no file can catch. On the OpenAI side the same rule forbids Codex automations, schedules and polling in the build loop.
- A consultant that cannot be reached never holds up a slice (his ruling, 16 September 2026). A Claude lead puts the question to a Claude Fable subagent at its highest effort, as a cold read of the committed text, and carries on; an OpenAI lead has no Claude subagent to call, so it carries on and leaves the question standing on the pull request until the consultant is back. Running out of the other stack's allowance is never put to the Chairman as a purchase — his words: "dont tell me to buy GPT credits again".
- A `roadmap.json` left fit for a one-word start (his ruling, 9 September 2026: *make sure the session has all the context it needs so all I have to do is say "build"*): every `next` line current, self-sufficient, and in the order the work will be taken up, so that *build* alone is enough and he is never handed a paragraph to paste. Words still waiting in an unmerged pull request are the one exception, and the session that opened them says so and carries the difference meanwhile.
- Money milestones in `roadmap.json` (his ruling, 17 September 2026): each revenue figure he gives, and what he is reminded of when it is reached — at least *revenue passes £1,000 a month: a real business, so move the host to its paid plan*. Never build work. The slice that first counts a product's revenue shows it where he can see it and checks the milestones every time it counts, so a reminder fires on its own.
- Evidence recorded with its origin (his ruling, 17 September 2026): for anything the product learns from, whether it is a person's statement, a recorded observation or a derived result, along with where it came from, who recorded it and when, and under which notice. Kept only for a permitted purpose and period, with personal records and anything identifiable derived from them provably deletable, and any justified exception written down. The proof is the product's own test in the slice that changes the behaviour; a line in this list is not a machine gate.
- The handover's `evidence` field, which `HOW-WE-BUILD.md` names with the rest: what evidence this slice captures, or deliberately does not capture; which decision it can improve; and what cost or retention obligation it adds. "None, because ..." is a valid answer, which is what stops it becoming a box everyone ticks.
- `PRODUCT.md` and `NAMES.md`: what the product is, and the words it uses for its own things.
- `RICH-DATA.md` read whole by any slice that changes what the product learns from, shows about a person, or claims about its own accuracy — and not otherwise. `PRODUCT.md` carries the five-heading section that page's §10 names and says how to fill; the headings are written there, once. "Unknown" and "deliberately not captured" are valid answers.
- A `README.md` route section saying that a session attached to the repo at its start works in it directly, a session started without it goes through the Mac, and the ten-second test tells which.
- A Project whose instructions are the template above, whole, and nothing else.
- A `design/` folder, for a product with a user interface: its own constitution on one capped, machine-checked page holding only what is true there, and one spec per designed screen. The screen law, the architect's role page, the templates and the rubric are read from this repository, never copied down; whoever draws a screen, or a prototype or picture of one for the Chairman, reads the screen law and the constitution first. Its check holds the shape: one constitution page, one brief at a time, one spec per screen, no two specs sharing an id.

**The deploy, in shape.** Deploys run from CI with the deploy key held as a repository secret, so no session of any kind ever holds it — and this says what is built, because no product can read another product's repository to find out. CI builds the app, deploys it as a preview and smoke-tests that exact deployment; a merge to `main` promotes the same deployment — never a rebuild, never "whatever is newest" — then smokes the live addresses and, if they are red, promotes the previous production deployment straight back and fails loudly. The previous deployment is recorded before anything moves. The host's own Git integration stays off on purpose: it would put every push into production untested. Four things cost Hemz OS real runs and need cost the next product none: the deploy tool reads GitHub-flavoured environment variables and a `github.com` remote as an integration deploy, which a private repo on the free plan refuses outright with no visible error, so both are put out of its sight for the deploy call; a team-scoped key works where a project-scoped one authenticates and then dies with a misleading missing-project message; promoting a preview-built deployment mints a production copy rather than repointing production, so the check passes on the smoked id **or** on a deployment whose original is the smoked id; and the edge serves the new build a little after the control plane calls it live, so ask again for a couple of minutes before calling it red.
**The host's plan (his ruling, 17 September 2026).** No product is a real business until its revenue passes £1,000 a month. Until then it stays on the host's free plan and deploys there as normal: production is promoted, never held back waiting for a paid plan. The free plan's terms reserve it for non-commercial use; he was told, and the call is his. The paid plan is his to buy when a product's milestone fires, and no session buys it.
**Code and words.** Anything that runs — code, tests, a database change, a deploy — is built in the lead's workshop, a session attached to the repo: a Claude code session, or a Codex cloud task. Only a workshop can prove it: the build, the tests, the Playwright journey on phone and desktop, the preview. Words — this rulebook, a product's `AGENTS.md`, `PRODUCT.md`, `NAMES.md`, `roadmap.json`, its screen specs, its README — may change from a Cowork session, through the Mac, by the same branch, pull request and review as everything else. Size is not the line: a one-line change to code still needs the workshop; a long change to words does not. One session reaches one product's repository — one key, one product — reads the rulebook, and writes down:

```mermaid
flowchart LR
  RB["Rulebook · how-we-build<br/>public — every session reads it, no key"]
  H["Hemz-OS · private"]
  P["myst · private"]
  C1["Builder on Hemz-OS<br/>Claude code, or Codex cloud — code and words"]
  C2["Builder on myst<br/>Claude code, or Codex cloud — code and words"]
  W["Cowork session<br/>through the Mac — words only"]
  RB -. reads .-> C1
  RB -. reads .-> C2
  RB -. reads .-> W
  C1 -->|writes| H
  C2 -->|writes| P
  W -->|writes words| H
  W -->|writes words| P
  W -->|writes words| RB
```

**A Project's instructions write themselves from here.** Nobody carries text between products. At the start of a session, if the Project's instructions differ from the template above filled in for this product, the session sets them to it — before anything else, once — and anything product-specific it finds in the old text goes into the product's `AGENTS.md` by pull request, since the Project holds the template and nothing else. When either template changes, every next session does the same, the Juku OS Project against its own.

**The session sets them; the Chairman is handed no paste (his ruling, 14 September 2026).** It works in the Claude app's built-in browser (*The two stacks*), signed in to `claude.ai` by him: `claude.ai/projects` → *New project* → the name and one line saying what it is → *Create project* → *Instructions* → *Edit instructions* → the template, whole → *Save instructions*. An existing Project is the same route from its own page. Nothing is ever added to a Project's *Context*: it holds instructions and no files. The session then reloads the page, reopens the instructions, reads them back and says what it set — a Project is not reported as done on the strength of having typed into it. If that browser is not signed in, he is handed that one tap and nothing else. The text whole is for a session with no Mac connected, and that is the exception, not the route.

**Text for the Chairman is handed over whole.** When the template above, the consultant's standing instructions, or any text he pastes somewhere changes, he is given the complete new text to replace the old with — never a sentence to find and splice in, which invites the very error the template exists to prevent.

## Reading it from a session

```
git clone --depth 1 https://github.com/Adonis80/how-we-build
```

or fetch `https://raw.githubusercontent.com/Adonis80/how-we-build/main/HOW-WE-BUILD.md`.

## Changing the rulebook

**A word cap is paid for in wording, never in requirements.** Twice on 9 September a trim to fit the 500 words changed what the page required: *the Playwright journey* became *the journey*, letting a manual walkthrough pass as proof, and *it never means run the build* became *never run the build*, forbidding the very step that proves a slice. Both were caught by the reviewer, neither by the machine — a word count cannot tell a shorter sentence from a weaker one. So: compress phrasing first, and if a change cannot fit without removing something the page requires, say so in the pull request and let the cap be the thing that is argued about, rather than quietly spending a rule to buy space.


**The cap gave once, in the open, and 600 is the ceiling.** The page was capped at 500 words from 28 August to 12 September 2026. The two-lead rules — the lead is CTO, cold review with the cross-vendor list, session changeover, a hard stop that names schedules and automations — would not fit under it without spending a rule, which the paragraph above forbids. So it moved to 600 in `check.sh`, in the pull request that needed it and for that reason, said out loud. That is the last rise. From here a rule in means a rule out: an addition pays in wording, or by removing a rule that has stopped earning its place — never with another number. A change that genuinely cannot fit argues about the cap in its own pull request and waits there; it does not raise it in passing.

**15 September: an addition was paid for in punctuation, and that slack is now spent.** Putting *and that the next session has full context* into *Asking the Chairman* cost five words on a page already sitting at exactly 600. They came from five standalone em dashes, which the counter treats as words because `split()` does: the parenthetical in *Who decides* took brackets instead, two in the loop took a colon and a full stop, one in *the PR is the handover* took a semicolon. No word was deleted, no requirement changed, and the page is shorter in characters as well as in count. It is written down because the page now holds no standalone em dash at all — there is no punctuation left to sell, so the next addition pays in wording or in a rule out, exactly as the paragraph above says.

**"Build" here means the oldest open pull request.** This repository has no `roadmap.json`; its queue is its open pull requests. A session started on *build* with this repository chosen reads them oldest first and moves one on — answers its findings, pushes the round's fixes as one push, asks once — or closes one that is stale. With none open, there is nothing to build here: say so and stop.

By pull request only; `main` is protected. `check.sh` runs in CI and refuses a page over 600 words, a file not on the list, anything that looks like a secret, and — in a pull request — a commit the reviewer has not read clean: unread, or read and left findings on. Adding a rule, step, file, check or agent needs the charter's gate (§13): the same failure twice, in two separate product tasks. Removing one, or correcting wording, needs no gate; nor does a change the Chairman rules himself. **The CTO settles and merges changes to this page and this repository, without the Chairman** (his ruling, 9 September 2026: "you are the CTO — don't ask me about such things in future"). He is asked for money, a permission, a product outcome or a picture, and nothing else. The reviewer still reads every change cold, and the gate above still applies. Every product picks the change up at its next session, because every session reads this repository live. There is no copy anywhere to refresh.
