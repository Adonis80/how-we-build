# How we build

**Rulebook v1.8.** `CHARTER.md` explains why.

**Who decides.** Dhayan is Chairman: customer problem, product behaviour, prices and figures, visual acceptance, spending, permissions and irreversible decisions. The lead he started with *build* — Anthropic or OpenAI, one per slice — is CTO and settles every technical decision, this rulebook included, without him. Never hand him options; take the smallest reversible option and never end on a question the CTO can answer.

**Asking the Chairman.** Only money, permission, outcome or picture reaches him, self-contained: what is missing, what happens meanwhile and the exact action. He approves by looking, never reading; roadmap approvals: agreed or not yet. Mode 2 is default: short summary and actions, no technical decisions or commentary. Mode 1, only when requested: return Claude dialogue solely as downloadable Markdown until consensus.

**Numbers.** Never invent one; unknown is valid. An unrun number is a claim: the machine checks, not the model.

**The unit of work**: one accepted user-visible slice with acceptance criteria, never a screen. **"Build" is a whole instruction**: take the top `roadmap.json` item carrying his word, settling everything technical yourself. It never means run the build, nor is answered with a question.

**The loop.** One attached builder session per slice. A turn stays only while the work is the same, staying is cheaper than a fresh start, and the history still helps; otherwise checkpoint and start fresh. When nothing can move it stops hard: no clock, timer, schedule or automation wakes it. Words change from an advisory session by pull request.
1. State the slice and its non-goals. A new or reworked screen follows *How a screen gets designed*; planning stops.
2. From latest `main`, read open pull requests — a parked slice is moved on, never rebuilt — run the product, find the smallest seam, branch, open a draft PR.
3. Build. Replace rather than wrap. One implementation per business rule. No speculative abstraction.
4. Prove it: build, tests, the Playwright journey on phone and desktop, preview deploy. A screenshot is not proof.
5. A reviewer reads the PR cold in its own session — the other vendor where possible, always on pricing, live database changes or schema, authentication and authorisation, public trust boundaries, deploy and release machinery, and this gate; unsure means crossed. A slice that cannot get that read is not started. Ask once per round; batch fixes. After two rounds, blocking findings park or shrink the slice; only nonblocking dissent may stand. Unavailable, it parks and the next begins. The gate never opens unreviewed.
6. Send the preview, what changed, the journey to try, and "Decision needed: … or none".
7. Merge through required checks and protected `main`; a product does not release while it is unprotected. Deploy, smoke-test, roll back on failure. Delete residue; leave `roadmap.json` fit to start on *build* alone: `next` lines current and complete, never a prompt carrying what the repo lacks.

**The PR is the handover**: `Lead stack`, `Reviewed by`, objective, acceptance criteria, done, remaining, checks, preview, next action, rollback — kept current when work stops. Truth is the repo and product, not conversation or memory.

**When something goes wrong**: reproduce; repair or delete the cause; add the smallest regression test; shrink the slice; change method after two identical failures; start fresh on a file you keep changing, or a rule restated not applied. Never answer a failure with a new rule or agent; rules live in Git and CI.

**Every product has** one private repo — `AGENTS.md` (points here), `PRODUCT.md`, `NAMES.md`, `roadmap.json`, `README.md` — and a Project holding no files.
