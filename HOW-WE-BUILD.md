# How we build

**Rulebook v1.7, 12 September 2026.** How we build; `CHARTER.md`, why.

**Who decides.** Dhayan is Chairman: the customer problem, what the product does, prices and figures, visual acceptance, spending, permissions, anything irreversible. The lead — the model he started with *build*, Anthropic or OpenAI, one per slice — is CTO: every other technical decision, this rulebook included, settled and merged without him. Never hand him options. When unsure, take the smallest reversible option; no turn ends on a question the CTO could answer.

**Asking the Chairman.** Only money, a permission, an outcome or a picture reaches him, self-contained: what is missing, what happens meanwhile, the taps, the words to reply. He approves by looking, never reading; roadmap approvals: agreed or not yet. Plain English always: summaries and actions, never technical commentary. Every reply ends "continue to build here", or "ready to start fresh session" naming where and the words to send.

**Numbers.** Never invent one; unknown is valid. An unrun number is a claim: the machine checks, not the model.

**The unit of work**: one accepted slice, a user-visible outcome with acceptance criteria, never a screen. **"Build" is a whole instruction**: take the top `roadmap.json` item carrying his word, settling everything technical yourself. It never means run the build, nor is answered with a question.

**The loop.** One builder session per slice, attached to the repo. A turn stays only while the work is the same, staying is cheaper than a fresh start from GitHub, and the history still helps; otherwise checkpoint and start fresh. When nothing can move it stops hard: no clock, timer, schedule or automation wakes it. Words change from an advisory session by pull request.
1. State the slice and its non-goals. A new or reworked screen follows *How a screen gets designed*; planning stops.
2. From latest `main`, read open pull requests — a parked slice is moved on, never rebuilt — run the product, find the smallest seam, branch, open a draft PR.
3. Build. Replace rather than wrap. One implementation per business rule. No speculative abstraction.
4. Prove it: build, tests, the Playwright journey on phone and desktop, preview deploy. A screenshot is not proof.
5. A reviewer reads the PR cold in its own session — the other vendor where it can be, and always on pricing, live database changes, authentication, public trust boundaries, deploy machinery and this gate; unsure means crossed. Asked once per round, fixes batched into one push; unavailable, the slice parks and the next begins — the gate never opens unreviewed.
6. Send the preview link, what changed, the journey to try, and "Decision needed: … or none".
7. Merge to protected `main`, deploy, smoke-test, roll back on failure. Delete residue; leave `roadmap.json` fit to start on *build* alone: `next` lines current and complete, never a prompt carrying what the repo lacks.

**The PR is the handover**: `Lead stack`, `Reviewed by`, objective, acceptance criteria, done, remaining, checks, preview, next action, rollback — kept current whenever work stops. Truth is the repo and the product, not conversation or memory.

**When something goes wrong**: reproduce; repair or delete the cause; add the smallest regression test; shrink the slice; change method after two identical failures; start fresh on a file you keep changing, or a rule restated not applied. Never answer a failure with a new rule or agent; rules live in Git and CI, never in memory.

**Every product has** one private repo — `AGENTS.md` (points here; under 500 words, machine-checked), `PRODUCT.md`, `NAMES.md`, `roadmap.json`, `README.md` — and a Project holding no files.
