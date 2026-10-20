# Decision 0021: the rulebook audit, and the checks that keep it clean

**His ruling, 20 October 2026, given in the Juku OS Project, word for word.** It overrides "standalone cleanup only from first revenue", and it asks for the checks below as well as the cut.

```
Juku OS: full audit of the rulebook and every product's rule pages — delete stale, duplicated and conflicting text; leave a much smaller, easier-to-follow rulebook — AND build the checks that keep it clean on every change. My ruling, 20 Oct 2026: do it now (this overrides the "standalone cleanup only from first revenue" line).

Why: Hemz round 1 (19 Oct) ignored most of HyperSolid, not just the distillation step. Cause found: conflicting instructions.
- Hemz's own constitution/design-system (Sept) says no spatial layer, five motions/nothing loops, "private bank statement" — and HyperSolid's Palette rule defers looks to the product constitution, so the old house rules beat the reworked HyperSolid (how-we-build#240/#242).
- Same Hemz file holds --signal as both #4DFFA3 and #5FD3C4; HEMZ-VOICE still says things overruled 11 Oct.
- The rulebook is 56,568 words (library 24,356 in 31 pages; juku-library 21,410 in 16 decision files; RICH-DATA 4,716; CHARTER 2,231; README 2,042) — too heavy to read before working.
- How it rotted: every lesson became a new paragraph and nothing left; rules copied into several places drifted apart; decision records sat in the reading path; my memory preferences became a second, partly stale rulebook.

PART A — THE AUDIT
Scope: Adonis80/how-we-build; the rule pages of Adonis80/Hemz-OS, Adonis80/myst, Adonis80/phena (AGENTS.md, PRODUCT.md, NAMES.md, design constitutions, design-system, voice pages); this Project's instructions; this Project's memory (list any stale lines in my account-level memory for me to clear — don't edit them).
1. One home per rule. Duplicates go or become one-line pointers.
2. Superseded or contradicted text is deleted, not reworded. Git history is the archive.
3. Decision and consensus records leave the reading path (archive folder no session reads by default); only the live rule they produced stays.
4. HyperSolid alone owns the look standard. A product's pages keep only its tokens, units, money/domain law, and exceptions I approved by picture (each with date). Anything else in them about looks goes.
5. Target: everything a session must read before working fits in a few minutes. Report before/after word counts.
6. Nothing changes what a product does, any price, permission or money rule. If deleting something would, list it for me instead.

PART B — KEEP IT CLEAN (machine checks, on every change, in every repo)
1. The exam: a fixed set of about 20 questions with expected answers on who decides what and which rule wins (e.g. "On a Hemz screen, does HyperSolid or Hemz's own pages decide the look?"). Every rulebook or product-rule change: a fresh model with no memory reads the reading path and sits the exam; a wrong answer or a contradiction it reports blocks the change. A deleted rule takes its question with it.
2. One in, one out: a word budget for the reading path in check.sh; a change that adds words names the matching cut. A real repair over budget is allowed only with its cut stated.
3. Every PR touching a rule has a "Replaces:" line; the old text leaves in the same change; a new rule with nothing replaced must say why it can't be a machine check instead of words.
4. One home, enforced: CI fails a product repo that copies rulebook text, or holds a looks line without a dated picture-approved exception. A rulebook change lists the product pages that lean on it and updates them in the same change.
5. Memory holds who I am and how I like to be spoken to, never how we build. Add this to the rulebook and Project instructions.

LIGHTNESS — A HARD REQUIREMENT FOR EVERY SOLUTION
Whatever is agreed must cost little time, money and tokens, every day, forever. Specifically:
- Free checks first (word counts, text matching, file rules in check.sh); a paid model read only when they pass, and only on changes that touch a rule — never on ordinary product work, never on a timer.
- The exam uses the cheapest model that reliably passes it, reads only the reading path (which the audit makes small), and stays short. Each run's cost goes on one line in the PR.
- No new standing agents, schedules, ledgers or extra review rounds. Reuse the existing reviewer and check.sh wherever possible.
- A check that costs more than the mess it prevents is cut. Say the expected cost per change and per month in the agreed answer.

PROCESS
Read whole, list every conflict found (file, both texts, which wins and why), propose the cut and the checks, settle it with Astra (three rounds, fourth only if the third changed something). Tell Astra up front: every proposal from either side is judged first on whether it keeps the system light — little time, few tokens, little money — and a heavy solution loses to a lighter one that does the job. Then PRs — rulebook first, then each product — through the Mac (~/Documents/Claude/Projects, key in .alma-secrets/github-token, never printed), check.sh green, independent reviewer read, merge. Update the Project instructions from the new template and set them yourself.

BRING ME
The agreed answer from Astra, with the expected running cost; before/after word counts; one simple box drawing (Mermaid) of the new rulebook and its checks to approve by looking; the list of stale memory lines for me to clear. Then write me the paste for Hemz HyperSolid round 2 (Hemzy and Price a job; rounds used 1 of 3; R1 failed: inventory map, HyperSolid not applied, garbled lettering — next time words and figures go in by machine).
```

**The debate** (GPT-6.1 Sol high against Claude Opus 5.5 high, two rounds, 20 October 2026):

`AGREED: One rulebook PR removes conflicting and duplicated instructions and installs measured budgets, brief-embedded counterexamples and the single Replaces declaration; product PRs follow with pinned checks — changed by: the protected-main brief placement resolved the consultant's exam objection, and his explicit B3 and the dependency argument resolved the declaration and PR split — strongest objection left: semantic omissions still depend on the existing reviewer; size and shape checks cannot prove that every live requirement survived.`

**What was rejected, and why.** A twelve-word copy check for product pages: it cannot tell duplication from a needed quotation, paraphrase defeats it, and the products' own Review guidelines legitimately repeat the brief. Separate `Cut:` and `Products affected:` lines: declarations prove nothing the count does not. A budget escape for a declared cut: a declared cut removes no words, so the cut must land and be counted. An exam on its own page: delivery to the reader was unproven, and a change could delete its own question; inside the reviewer's brief, read from `main`, it is always delivered and cannot be removed by the change it judges.

**Unproved.** That the counts and shapes catch what the reviewer would miss; the first rule change after this is the first evidence. That a product runs the check from a pinned commit; no product does yet.

**Split.** The first pull request carrying the whole audit (#246) spent its two reads; per the two-round rule it was shrunk: the machinery first, the word cut after.
