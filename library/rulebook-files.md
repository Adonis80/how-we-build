# What each file here is for

Scope: this repository. Open when: asking what a root file or a decision issue is for, or why this repository is public.

The rulebook for every product Dhayan's AI studio builds. This repository says **how** we work. Each product's own repository says **what** we build.

**Three files matter.**

- `HOW-WE-BUILD.md` — the operating page, short and machine-checked; the cap lives in `check.sh`. The first thing a working session loads, with *What every product carries* in the README.
- `CHARTER.md` — the Systems Blueprint, the reasoning behind the page. Read once, never loaded into a working session.
- `RICH-DATA.md` — the method for what a product learns from and how we know its AI got smarter. Read on the trigger in *What every product carries*, and not otherwise.

A fourth, `AGENTS.md`, is not for sessions at all: it carries the reviewer's brief for changes to this repository, because the reviewing tool loads only a file of that name.

**And `library/`, indexed under *Where each topic lives* below.** It is where a topic goes when it leaves this README: one page per topic, or a named few where a topic is over the cap, opened only when a task touches it, each named here with when to open it (his ruling, 23 September 2026, [decision 0005](https://github.com/Adonis80/how-we-build/issues/75): *"a lesson learned in one product reaches every product at once; the fault is loading, not sharing"*). `check.sh` holds the shape: each page named here, at most 4000 bytes and carrying a `Scope: … Open when: …` line, each index row opening the first page it names on that page's own words, and every link to one resolving.

**And the `decision` issues in this repository: why a rule is what it is, rather than the obvious alternative.** They hold the one thing he has ruled worth keeping from a conversation (his ruling, 22 September 2026, [decision 0003](https://github.com/Adonis80/how-we-build/issues/59): *"The only thing that we should be storing that is valuable is the architecture consensus that we reach with two intelligent AI models"*) — a consensus two capable models reached after genuinely disagreeing, each carrying the question, what was rejected, who was overruled on what evidence, and what is still unproved. **Read like `CHARTER.md`, not like the operating page:** when a rule is about to change or its reason is in question, and never loaded into a working session. Nothing executable depends on them — delete them all and the system behaves identically, and only the reasoning is lost. A record is never edited to stay current; a later one supersedes it and the earlier stands as history.

**Why it is public.** It holds no secrets, prices or customer data — only the way we work — and a public repository is the one thing every session, in either stack, can read directly, with no extra setup. Product repositories stay private.
