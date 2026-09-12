# How we build

**Rulebook v1.8 · 12 September 2026.** This page governs delivery; product `AGENTS.md` adds domain rules; `CHARTER.md` explains why. Provider setup lives in `README.md`.

**Authority.** Dhayan owns product outcomes, business figures, visual acceptance, spending, permissions and irreversible decisions. The active CTO makes technical decisions and implements them. Claude, Codex or ChatGPT Work may lead when their actual tools support the task. One active builder per slice; transfer only at a stopped, pushed checkpoint.

**Communication.** Default: short summary and actions, no technical-choice questions. Disagree and propose better solutions when warranted. Only when Dhayan requests dialogue with Claude, return replies as downloadable Markdown until consensus. Report an unavoidable human approval only at the actual approval screen, naming the action.

**Truth.** GitHub is canonical. Read current global `main` and relevant open PRs, then product instructions, relevant product truth, roadmap and open PRs. Record source SHAs in the PR. Open proposals are not policy. Respect explicit current user rulings; resolve contradictions by replacing superseded rules. Never invent business figures; unknown is valid. One implementation per business rule; machines verify calculations.

**`build`.** Resume the applicable approved slice before starting another. Otherwise implement the first approved roadmap item. In Juku OS itself, implement the requested system change through its existing PR; there is no product roadmap here. No approved work means stop with the missing outcome, not invent a roadmap. README defines takeover and bootstrap.

**Delivery loop.**
1. State objective, acceptance and non-goals in a draft PR. New work starts from current `main`; resumed work reconciles `main` without overwriting another builder. Material UI follows README's **How a screen gets designed** before implementation.
2. Build the smallest coherent change; replace rather than wrap. Run the repository's checks and meaningful regression tests.
3. Prove product work with build/tests, a **Playwright journey on phone and desktop**, and a preview. Screenshots alone are insufficient. Rulebook-only work uses its deterministic checks; no fictitious app preview.
4. Obtain independent cold review of the current head. Ask once per round, batch fixes, at most two rounds; then park unresolved work and continue an independent approved slice. Never waive a blocking finding. Prefer another vendor; require one for pricing, database/schema, authentication, trust boundaries, deployment or review-gate changes.
5. Present material visuals for Dhayan's acceptance. Merge only after required checks and review; never self-merge additions to this rulebook. Deploy the accepted artifact, smoke-test, roll back failure; update product roadmap status and next action.

**PR handover.** Objective, acceptance, done, remaining, checks, preview, next action, rollback; active lead, source/head SHAs, reviewer and ownership state. No necessary state only in chat.

**Recovery.** Reproduce, repair the cause, test; change method after two identical failures. Checkpoint when blocked. No polling, scheduled builders or extra coordination machinery. Read rules fully before editing; replace conflicts rather than adding exceptions. Keep `main` protected and access narrowly scoped.
