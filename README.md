# how-we-build

The rulebook for every product Dhayan's AI studio builds. This repository says **how** we work. Each product's own repository says **what** we build.

**Two files matter.**

- `HOW-WE-BUILD.md` — the operating page. Under 500 words. The only page a working session loads.
- `CHARTER.md` — Systems Blueprint v2.0, the reasoning behind the page. Read once, never loaded into a working session.

**Why it is public.** It holds no secrets, prices or customer data — only the way we work — and a public repository is the one thing every Claude session can read directly, in every project, with no extra setup. Product repositories stay private.

## How a product joins

1. Its repository's `AGENTS.md` begins with one line: `Rulebook: https://github.com/Adonis80/how-we-build — read HOW-WE-BUILD.md before anything else.` Below that, only what is true for that product.
2. Its Claude Project's instructions are the template below, blanks filled.
3. In the Project's knowledge, add this repository from GitHub (`HOW-WE-BUILD.md` and `CHARTER.md`) so chats on the phone read it too. Tap **Sync** when the rulebook changes.

### Project instructions template

```
# <Product> — how this project works

Rulebook: https://github.com/Adonis80/how-we-build. At the start of every working
session, read HOW-WE-BUILD.md from it (clone the repo, or fetch the raw file). It says
who decides, the loop, and when a slice is done. Nothing below overrides it.

This project builds <Product>. Its repo is https://github.com/Adonis80/<repo> (private).
The repo's AGENTS.md holds the rules true only for this product; PRODUCT.md is what we
are building; roadmap.json is what comes next.

No repo access from the cloud? Read claude/infrastructure-status.md in this Project's
docs before anything else.

Prose for the Chairman lives in this Project's docs, never in a repo. The pull request
is the handover. Speak to the Chairman in plain English: summaries and actions, no
technical commentary.
```

## Reading it from a session

```
git clone --depth 1 https://github.com/Adonis80/how-we-build
```

or fetch `https://raw.githubusercontent.com/Adonis80/how-we-build/main/HOW-WE-BUILD.md`.

## Changing the rulebook

By pull request only; `main` is protected. `check.sh` runs in CI and refuses a page over 500 words, a file not on the list, or anything that looks like a secret. A change to *how we build* needs the charter's gate (§13): the same failure twice, in two separate product tasks. Fixing wording needs no gate. Every product picks the change up at its next session; Projects that synced the rulebook into their knowledge pick it up on **Sync**.
