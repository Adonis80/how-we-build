# What each file here is for

Scope: this repository. Open when: asking what a root file or a decision issue is for, or why this repository is public.

The rulebook for every product Dhayan's AI studio builds. This repository says **how** we work. Each product's own repository says **what** we build.

**Three files matter.**

- `HOW-WE-BUILD.md` — the operating page, short, with no word limit: it routes, and the README's index sends a session on (decision 0026). The first thing a working session loads, then the README.
- `CHARTER.md` — the Systems Blueprint, the reasoning behind the page. Read once, never loaded into a working session.
- `RICH-DATA.md` — the method for what a product learns from and how we know its AI got smarter. Read on its row in the README's index, and not otherwise.

A fourth, `AGENTS.md`, is not for sessions at all: it carries the reviewer's brief for changes to this repository, because the reviewing tool loads only a file of that name.

**And `library/`, indexed under *Where each topic lives* in the README.** It is where a topic goes when it leaves this README: one page per topic, or a named few where a topic is large, opened only when a task touches it, each named in the README's index with when to open it. One library serves every product, so a lesson reaches them all at once; what is kept small is what a session loads (R-2026-09-23a). `check.sh` holds the shape (the only things beside a page: a screen's approved picture, a PNG named for its page, and the look's stylesheet, `library/juku-style.css`, beside its page): each page named in that index with a `Scope: … Open when: …` line, its words never counted (`library/changing-the-rulebook.md`), each index row opening the first page it names on that page's own words, and every link to one resolving.

**And the `decision` issues in this repository: why a rule is what it is, rather than the obvious alternative.** They hold the one thing he has ruled worth keeping from a conversation (R-2026-09-22d): a consensus two capable models reached after genuinely disagreeing, each carrying the question, what was rejected, who was overruled on what evidence, and what is still unproved. **Read like `CHARTER.md`, not like the operating page:** when a rule is about to change or its reason is in question, and never loaded into a working session. Nothing executable depends on them: delete them all and only the reasoning is lost. A record is never edited to stay current; a later one replaces it and the earlier stands as history.

**And `model-registry/`, `product-reads/` and `juku-library/`.** The registry is the one place a model is named ([decision 0008](https://github.com/Adonis80/how-we-build/issues/103)): `library/model-registry.md`. `juku-library/` is the rulebook's own library: papers only, directly inside it (R-2026-10-02a). It holds the paper a consensus was built on, committed verbatim, when a build must read it from GitHub, and the frozen record a consensus ends on, the same words as its decision issue (R-2026-09-25d); where the agreement itself was reached is its decision issue. Each product keeps its own `<product>-library/` in its private repo, created with its first paper and never here, since a product's papers hold its prices and strategy; `NAMES.md` lists each library's name. It is read like the decision issues, never loaded into a working session. `product-reads/`: the product read's rules, setup script and starter kit, `rules-check.py`, the rules' own guard (`library/changing-the-rulebook.md`), `brief-check.py`, the design brief's (`library/hypersolid.md`), and `ticket.py`, a successor's ticket and its section reader (`library/session-changeover.md`), and `coherence.py`, the guard of one home per ruling (`library/changing-the-rulebook.md`, *Coherence*). Not `library/`, the rule pages; his rulings' one register is `library/rulings.md`.

**Why it is public.** It holds no secrets, prices or customer data — only the way we work — and a public repository is the one thing every session, in either stack, can read directly, with no extra setup. Product repositories stay private.
