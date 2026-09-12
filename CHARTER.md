# Systems Blueprint v2.2

**Status:** Current charter, 12 September 2026. Read for rationale, not as routine build context.
**Primary outcome:** Dhayan can move between interchangeable AI development stacks while GitHub preserves the work, and each stack can ship accepted software with minimal founder coordination.
**Supersedes:** Earlier development-system blueprints, control planes, orchestration proposals, permanent model assignments and instruction stacks.

`HOW-WE-BUILD.md` is the short operating rule. This Charter explains **why**. Product repositories define **what** each product is.

## 1. Authority

Dhayan is Chairman. He owns product purpose and behaviour, commercial truth, prices and business figures, material visual acceptance, spending, permissions, legal commitments and irreversible decisions.

The active AI lead is CTO for one bounded slice. It owns routine technical decisions: implementation, architecture inside approved product boundaries, dependencies, testing, branches, pull requests, previews, release and reversible recovery.

The CTO must not turn technical uncertainty into work for Dhayan. Choose the smallest safe reversible option unless the unresolved decision genuinely belongs to him.

## 2. What the system optimises for

The measure is **accepted product output**, not prompts, agent activity, documents, commits or architectural sophistication.

The system should make four things easy:

1. start from current truth;
2. build one bounded outcome;
3. prove it works;
4. stop or hand over without losing state.

Everything else must justify its cognitive, token and maintenance cost.

## 3. Lessons from the systems we rejected

Earlier Juku systems repeatedly converted reasonable ideas into permanent machinery. More agents, handovers, memory layers, schedulers and governance increased complexity faster than useful product output.

The replacements are deliberately ordinary:

| Rejected pattern | Replacement |
|---|---|
| Custom control planes, task databases, event buses and heartbeats | GitHub branches, pull requests, CI and deployment history |
| Swarms and default parallel agents | One active lead per slice |
| Large persistent instruction stacks | Small canonical files; replace obsolete text |
| Chat memory and prose handovers as project state | Repository + PR as handover |
| Nightly or timed agents rereading the system | Event/user-started bounded sessions; no polling |
| Permanent “best” model or vendor | Provider adapters around the same GitHub truth |
| Screenshot or model explanation as proof | Tests, real journey, preview, smoke test and rollback |
| Building governance before product | Add system machinery only for a demonstrated need |

Useful ideas retained from the older work: fresh sessions are disposable; deterministic checks outrank model confidence; one concern has one current owner; changes stay reversible; successful workflows are proven before automation; Git history preserves history so current files do not have to.

## 4. Minimum architecture

The active development system is:

Dhayan defines product outcomes. One active CTO implements a bounded slice in the product repository, proves it with deterministic checks and a preview, obtains acceptance and independent review, then merges through protected `main`, deploys, smoke-tests and rolls back failure.

`Adonis80/how-we-build` contains only global development rules and shared design method. Each product has its own private repository. Products do not depend on one another for project truth.

Do not introduce a general orchestrator, memory database, model registry, scheduler, context compiler, policy engine or autonomous-company layer merely because several providers or products exist.

## 5. Interchangeable providers

OpenAI and Anthropic are **adapters**, not separate development systems.

The shared contract is GitHub: current product truth, open PRs, branch state, checks and the roadmap. Provider-specific setup exists only where the products genuinely differ in how they reach and execute that contract.

OpenAI work uses a verified capable surface: ChatGPT Work or Codex for implementation, and dialogue where helpful. The requested model and available tools decide the route. Provider capability details live in README.md; neither a Project attachment nor a model name proves repository write access.

Anthropic development uses Claude/Cowork/Code through the best current route to the same repository.

Only one lead owns a slice at a time, including sessions in different accounts of the same provider. The outgoing lead stops and pushes a checkpoint before the incoming lead claims the PR and verifies its live head. A new chat cannot implicitly stop another process. README.md owns the takeover procedure.

A new provider in future earns one adapter. It does not justify another roadmap, state store, handover format or copy of the global rules.

## 6. Canonical truth and context

Normal execution starts from:

- `HOW-WE-BUILD.md`;
- the product's `AGENTS.md`;
- the relevant current sections of `PRODUCT.md`;
- `roadmap.json`;
- the product README when setup/test/deploy commands are needed;
- source, tests and live runtime;
- relevant open pull requests.

Provider memory, old chats, old model explanations, copied project files, standalone handovers, restart notes and superseded specifications are not sources of truth.

A fresh session reads progressively and stops when it knows enough. Large product documents are searched for the subject being changed; they are not reread in full by default.

## 7. Documentation must resist accumulation

Canonical files describe **current truth, not the history of truth**.

When a rule, requirement or design changes:

1. find the existing owner of the subject;
2. understand the current relevant wording;
3. replace, consolidate or delete what is superseded;
4. search active files and code for conflicting copies;
5. update executable tests where applicable.

Git history is the archive. Temporary reasoning belongs in the pull request and disappears when the work closes.

Small always-read files may have hard size limits because their context cost is constant. Large product documents should not receive arbitrary size caps; semantic duplication is the problem, not legitimate product complexity.

A new document is justified only when it owns durable information that cannot live clearly in an existing canonical owner.

## 8. The unit of work

Product work uses one accepted **vertical slice**: a bounded user-visible outcome with observable acceptance criteria, or a necessary cross-cutting change inseparable from that outcome. Juku OS itself uses an explicitly requested system repair and its PR, not an invented product roadmap.

A screen is not automatically a slice. A slice can touch several screens. The boundary follows behaviour and proof.

`build` is intentionally a complete instruction. The repository and open PRs must contain enough current state that a fresh session can determine what should happen next without Dhayan reconstructing technical context.

## 9. Proof before completion

A slice is not complete because an agent says so.

Use deterministic evidence appropriate to the product: install/build, type/lint checks, unit/domain/integration tests, a Playwright journey at phone and desktop sizes for web products, preview deployment, production smoke and rollback capability.

Business invariants such as pricing, permissions or transformations should be executable tests wherever practical.

Material user-facing design is accepted by Dhayan by looking at the working result. He is not asked to inspect code.

Independent cold review is required where `HOW-WE-BUILD.md` says so. Review is a check on the change, not a second permanent CTO.

## 10. PR as handover

The PR carries objective state: objective, acceptance criteria, done, remaining, checks, preview, next action, rollback, active lead, ownership state, source/head SHAs and reviewer. Rulebook-only changes mark product preview and deployment not applicable, with a reason.

If a session stops mid-slice, it pushes a coherent checkpoint and leaves the PR sufficient for a fresh session. No necessary continuation state may live only in conversation.

This makes sessions disposable and provider switching cheap.

## 11. Failure and recovery

Handle failure in this order:

1. reproduce;
2. inspect current evidence;
3. repair or delete the faulty cause;
4. add the smallest regression test;
5. shrink the slice if needed;
6. change method after two materially identical failures;
7. restore the last safe state if completion is no longer credible.

Do not answer an isolated failure by inventing a new agent, document or rule.

When no allowed action can move the slice, checkpoint and stop. Do not poll, sleep, schedule wakeups or burn tokens reporting that nothing changed.

## 12. Permissions, internet and secrets

Autonomy is the default inside reversible technical work. Restrict authority, not usefulness.

Development agents may use the internet needed for ordinary dependencies and development services. Prefer scoped/common-development access to unrestricted access where the provider supports it.

Secrets belong in provider or repository secret stores, never ordinary repository files or prompts. Add them only when a real product need requires them. Use least-privilege repository access and protected `main`.

Dhayan must approve new spending, wider permissions, destructive production-data changes, domains/DNS/legal commitments and other irreversible/high-consequence actions. Existing explicit authorisation remains valid; do not ask again for routine technical work. Do not expose raw secrets as an approval shortcut. This global repository is public: private product/customer facts and account-specific authentication evidence remain private.

## 13. Changing the development system

System changes are expensive because they affect every product. A change is justified by either:

- Dhayan's explicit ruling about how he wants the system to work; or
- a measured repeated delivery failure, or one severe security/data-loss incident, where ordinary product repair is insufficient.

Prefer the smallest reversible intervention. Compare it with doing nothing. Define what success would look like.

Most importantly: **change the existing system, do not layer around it.** Read the canonical owner, replace or remove superseded rules, and check the surrounding architecture still makes sense.

Changes go through protected main and independent review. The CTO never merges its own additions to this rulebook. The explicit 12 September 2026 audit/build ruling authorises the bounded provider, bootstrap and check repairs; it is not blanket authority to bypass review.

A provider-specific problem should normally change only that provider adapter. A product-specific problem should normally stay in that product. Global rules should remain genuinely global.

## 14. New-product test

A product can ship once the shared repository contract and its selected provider route are configured and tested. Each additional provider/account is independently verified; an unavailable secondary account must not block the working route. The exact setup and instruction drift check live in `README.md`, because provider configuration changes faster than this Charter.

The acceptance test is deliberately simple:

> In a completely fresh working session for either provider, with the product selected, Dhayan sends `build` and the CTO finds the correct current work without further technical context from him.

If that fails, that route is unverified. Do not claim synchronisation or readiness beyond the accounts and capabilities actually tested. Stable Project launch instructions read the latest GitHub rulebook; no automatic cross-account mirror is assumed.

## 15. Final constraint

The development system is scaffolding, not the product.

If maintaining Juku OS begins consuming attention comparable to building the products, simplify it. The strongest system is the smallest one that reliably lets interchangeable agents ship correct software and lets Dhayan remain focused on product judgement.
