# How we build

**Rulebook v1.7, 10 September 2026.** How we build; a product's `AGENTS.md`, what it builds; `CHARTER.md`, why.

**Who decides.** Dhayan is Chairman: customer problem, product behaviour, business figures and prices, visual acceptance, spending, permissions, anything irreversible. The active lead is CTO for one slice and settles other technical decisions. The lead may be Anthropic or OpenAI; one owns a slice at a time. OpenAI development runs in Codex; Anthropic development in Claude/Cowork/Code; ChatGPT is advisory. When unsure, take the smallest reversible option.

**Asking the Chairman.** Only money, permission, an outcome or a picture reaches him. Plain English: summaries and actions, no technical commentary. Roadmap approvals: `agreed` or `not yet`. Every reply ends `continue to build here` or `ready to start fresh session`, naming where and the short words to send.

**Numbers.** Never invent one; unknown is valid. An unrun number is a claim: the machine checks, not the model.

**The unit of work:** one accepted slice, a user-visible outcome with acceptance criteria, never a screen. **`build` is a whole instruction:** build the top `roadmap.json` item carrying his approval, settling technical decisions yourself.

**The loop.** One builder task per slice, attached to the repo. Each turn stays only while the work is the same, staying costs less than a fresh start from GitHub, and its history still helps; otherwise checkpoint and start fresh. No schedules, polling or timed wake-ups in the build loop.
1. State slice and non-goals.
2. Before project work, read the latest global rulebook and its open PRs; record any agreed global change there first. Then from latest product `main`, read open PRs, run the product, branch, open a draft PR.
3. Build the smallest coherent change. Replace rather than wrap. No speculative abstraction.
4. Prove it: build, tests, phone and desktop journey, preview deploy.
5. Independent cold review. Prefer the other vendor where practical; cross-vendor review is mandatory for pricing logic, live database mutation/schema, authentication/authorisation, public trust-boundary changes, deploy/release machinery, and the review gate itself. If unclear whether a trust boundary is crossed, count it as crossed.
6. Send preview, what changed, journey to try, and `Decision needed: … or none`.
7. Merge to protected `main`, deploy, smoke-test, roll back on failure. Leave `roadmap.json` fit to start from `build` alone.

**The PR is the handover:** `Lead stack:`, `Reviewed by:`, objective, acceptance criteria, done, remaining, checks, preview, next action, rollback. No necessary project state may live only in chat or memory.

**When something goes wrong:** reproduce; repair or delete the cause; add the smallest regression test; shrink the slice; change method after two identical failures. Never answer a failure with a new rule or agent.

**Changing this system:** before changing `HOW-WE-BUILD.md`, read that file in full. Replace or remove what the change supersedes; never stack exceptions.

**Every product has** one private repo with `AGENTS.md`, `PRODUCT.md`, `NAMES.md`, `roadmap.json`, `README.md`. GitHub is the only project truth. Provider caches, compaction and model memory may help a session but are never sources of truth.
