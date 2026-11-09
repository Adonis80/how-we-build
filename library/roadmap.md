# The Roadmap

Scope: the Roadmap at roadmap.juku.pro. Open when: working on the Roadmap.

**Its name is the Roadmap** (R-2026-10-17a), singular, as its address is: every name he sees or reads says Roadmap. A product's `roadmap.json` is what it reads, never its name. Its internal names (`board/`, `build-board.yml`, the host project `juku-build-board`) stay until a change of their own.

## What it shows

**The Roadmap** (R-2026-09-25c) is one plain-English page showing where every product and this rulebook are and how much is left, at `roadmap.juku.pro`: the one place he goes for all of it, behind the Juku OS directors' PIN and never meant to be found by search. What it shows and may claim is [decision 0007](https://github.com/Adonis80/how-we-build/issues/97).

It is one page per project, swiped or stepped with ‹ › (R-2026-10-01b), each a timeline: done folded into one line, in hand open at its sentence, a second tap for the detail, a swipe to the next product; it all still opens without script. Above the projects sit OpenRouter's spend this month against $40 (R-2026-10-01b), from its daily activity, then the proposals card he approved (`library/board-proposals-card.md`): this repository's open `proposal` issues and every product's suggested ideas in one queue (decision 0020). Both sit closed, as two tiles side by side, each its headline, a word on its state and a thin bar; a tap opens the full card in place, so the projects start on the first screen (R-2026-10-17d).

The page shows each product's `roadmap.json` (`id`, `title`, `plain`, `status`, `gate`, `proof`, `next`, `decided_on`, `decided_by`, and any money milestone's sentence and whether it is reached), this repository's pull requests (the open ones with their review check, and the last ten merged), and its open `proposal` issues (each one's title, stage, priority, age and one sentence).

**What lives here is its gate and its build, never its data**: `board/` holds the gate's three files and `build.py`, which reads and renders the page, its selftest and the list held by `check.sh`. The page carries text from private product roadmaps, and this repository is public.

## How it reads

**It reads live when opened and uses no deploys for activity** (R-2026-10-15b). What is deployed is a frame: the PIN gate, and `board/build.py` as the function `api/build.py`. On each open, behind the PIN, it reads every product's roadmap, this repository's pull requests and open `proposal` issues, and OpenRouter's spend, there and then, with GETs alone, and keeps the page a minute. A source it cannot read is said on its page, and the rest still show. The live read is held by `build.py`'s selftest; a read behind the PIN is not yet shown here.

**Its keys** are the project's own two: `ROADMAP_READ_TOKEN`, a read-only GitHub token over every repository he owns (his choice, R-2026-10-17f), and the spend card's `OPENROUTER_KEY`. Their one home is the `reviewer` environment; the deploy stores them on the project, sensitive, before it makes the frame, and makes none while the read key is missing. The host gives a key only to a deployment made after it, so a new or changed key reaches the Roadmap by a production dispatch, which passes over the unchanged frame but not the ceiling; a key taken out of the environment stays on the project until it is removed there. The read key reaches every repository he owns, whole, not roadmaps alone, so it is read-only; the redirect it might follow to another host is refused.

## Its deploy

`.github/workflows/build-board.yml` deploys the frame only on main's push of the Roadmap's own code (`board/`, or the workflow), or a dispatch: no pull request, verdict, product or clock wakes it, it wears no App and reads nothing. A push deploys only when the frame's fingerprint, riding as `board.sha`, differs from what the domain serves, or that fails a stranger's smoke.

Before it makes anything, a push or a dispatch, it counts the account's deployments in the last 24 hours and makes none at 60 or more, so it can never starve a product (R-2026-10-15c), unless a production run finds a stranger shown the Roadmap; it goes red on a day it cannot count. A run held at the ceiling is not yet seen. The frame's proof is in `library/upgrade-log.md`.

After a production run whose domain is confirmed live and gated, the deploy deletes the project's old previews, as `library/deploy.md` gives, keeping what the domain and the fixed address serve, the preview waiting at the fixed address, the rollback target and what each was copied from. The newest smoked preview takes one fixed address, `next.roadmap.juku.pro`, overwriting the last, as every product's does (`library/deploy.md`). A dispatch deploys a preview unless production is chosen, and production is a copy of a smoked preview, asked for only after its smoke and given the domain once ready, as it will not promote a preview.

## The PIN gate

No cookie or a forged one gets only the PIN screen, `noindex` and `private, no-store`; a wrong PIN gets 401; the right one sets the cookie and serves the Roadmap; an anonymous request after an authorised one gets none of it; the firewall refuses the eleventh wrong PIN in a minute with 403. The domain is a DNS-only CNAME at Cloudflare to Vercel, verified on the project.
