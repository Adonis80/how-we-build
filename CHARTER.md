# Systems Blueprint v2.1

**Status:** Current charter, 12 September 2026. Read for rationale, not as routine build context.
**Primary outcome:** Dhayan can move between interchangeable AI development stacks while GitHub preserves the work, and each stack can ship accepted software with minimal founder coordination.
**Supersedes:** Earlier development-system blueprints, control planes, orchestration proposals, permanent model assignments and instruction stacks.

`HOW-WE-BUILD.md` is the short operating rule. This Charter explains **why**. Product repositories define **what** each product is. Where they disagree, `HOW-WE-BUILD.md`'s *Which rule wins* settles it; this document governs only why.

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

Dhayan gives intent and acceptance; one active CTO stack (OpenAI or Anthropic) works in the product repository, whose pull request is the durable state and handover; deterministic checks and a preview prove it; a protected merge deploys, smokes and rolls back if needed.

`Adonis80/how-we-build` contains only global development rules and shared design method. Each product has its own private repository. Products do not depend on one another for project truth.

Do not introduce a general orchestrator, memory database, scheduler, context compiler, policy engine or autonomous-company layer merely because several providers or products exist. A registry naming which model fills each role is the one exception, and it is his (22 September 2026: switching a model must be easy): role, adapter and exact model id, for roles something consumes.

## 5. Interchangeable providers

OpenAI and Anthropic are **adapters**, not separate development systems. The shared contract is GitHub: current product truth, open PRs, branch state, checks and the roadmap. Only one provider owns a slice at a time, and the PR, not a prose explanation, carries it across. Which model leads is the Chairman's; because the rules are written by role, that swap costs nothing. How each stack works today lives in `library/two-stacks.md`, which changes faster than this Charter. A new provider earns one adapter, never another roadmap, state store, handover format or copy of the rules.

## 6. Canonical truth and context

Normal execution starts from the reading path the README names, then the product's own pages, source, tests, live runtime and open pull requests.

Memory, old chats, copied files, standalone handovers and superseded specifications are not sources of truth.

A fresh session reads progressively and stops when it knows enough; large product documents are searched, not reread whole.

## 7. Documentation must resist accumulation

Canonical files describe **current truth, not the history of truth**.

When a rule, requirement or design changes, its one owner changes and what it supersedes is deleted (`library/changing-the-rulebook.md`).

Git history is the archive. Temporary reasoning belongs in the pull request and disappears when the work closes.

Operating instructions and design rules carry hard word budgets, because every session pays for them: one in, one out, counted by machine (`library/changing-the-rulebook.md`). A product's requirements, roadmap and locked figures carry none; semantic duplication and stale text are the problem there, not legitimate product complexity.

A new document is justified only when it owns durable information that cannot live clearly in an existing canonical owner.

## 8. The unit of work

The slice (`HOW-WE-BUILD.md`) follows behaviour and proof, not screens, and may be a cross-cutting change inseparable from its outcome. `build` is a complete instruction because the repository and open PRs carry enough state that Dhayan never reconstructs technical context.

## 9. Proof before completion

A slice is not complete because an agent says so: the evidence is deterministic (build, checks, tests, the real journey on phone and desktop, a preview, a production smoke and a rollback). Business invariants such as pricing, permissions or transformations are executable tests wherever practical.

**One path for business logic.** Pricing, rates, permissions, calculations and other protected rules have one canonical implementation. Interfaces import it; they never carry their own figures. For pricing the minimum is: staff and customer surfaces import the same function and the same rate source; contract tests prove matching totals, rate propagation and VAT exactly once; and tests prove a customer sees only locked lines, with no internal working exposed. Critical journeys are covered by a real browser suite — Playwright, where the product has one — not by a screenshot.

Material user-facing design is accepted by Dhayan by looking at the working result. He is not asked to inspect code.

Independent cold review is required where `HOW-WE-BUILD.md` says so. Review is a check on the change, not a second permanent CTO.

## 10. PR as handover

The PR carries objective state: the handover fields `HOW-WE-BUILD.md` names. The list lives there once — this page says why it exists, not what is on it, so the two cannot drift.

If a session stops mid-slice, it pushes a coherent checkpoint and leaves the PR sufficient for a fresh session. No necessary continuation state may live only in conversation.

This makes sessions disposable and provider switching cheap.

## 11. Failure and recovery

The order is `HOW-WE-BUILD.md`'s (*When something goes wrong*); the reason is that an isolated failure answered with a new agent, document or rule is how earlier systems grew. When completion is no longer credible, restore the last safe state. When no allowed action can move the slice, checkpoint and stop: polling, sleeping or reporting that nothing changed burns tokens for nothing.

## 12. Permissions, internet and secrets

Autonomy is the default inside reversible technical work. Restrict authority, not usefulness.

Development agents may use the internet needed for ordinary dependencies and development services. Prefer scoped/common-development access to unrestricted access where the provider supports it.

Secrets belong in provider or repository secret stores, never ordinary repository files or prompts. Add them only when a real product need requires them. Use least-privilege repository access and protected `main`.

Dhayan must approve new spending, wider permissions, raw-secret exposure, destructive production-data changes, domains/DNS/legal commitments and other irreversible/high-consequence actions.

The lead may never: write directly to protected `main` or force-push it; disable, weaken or skip a required check to make work pass; quarantine or delete a test to go green; expose a secret in a prompt, a log or a repository file; delete a repository, an archive or production data; grant itself wider permissions; or merge a material user-facing change before the Chairman has accepted it.

## 13. Changing the development system

System changes are expensive because they affect every product. A change is justified by either:

- Dhayan's explicit ruling about how he wants the system to work; or
- the same material failure in two separate product tasks, or one severe security or data-loss incident, where ordinary product repair is insufficient.

The case is made where the change is made — in the pull request — and carries the evidence of the failure, a cause that could be proved wrong, and why repairing the product would not do. Prefer the smallest reversible intervention; compare it with doing nothing; say what success would look like. One system experiment runs at a time. The lead proposing a major change does not clear it: the independent cold review does. A change that fails is reverted and deleted, never left standing as a dormant layer.

Removing a rule, or correcting wording, needs none of this.

Most importantly: **change the existing system, do not layer around it.** Read the canonical owner, replace or remove superseded rules, and check the surrounding architecture still makes sense.

A provider-specific problem should normally change only that provider adapter. A product-specific problem should normally stay in that product. Global rules should remain genuinely global.

## 14. New-product test

A product is integrated only when the shared repository contract and both provider adapters are configured and tested. The exact setup lives in `README.md` and the library pages its index names, because provider configuration changes faster than this Charter.

The acceptance test is deliberately simple:

> In a completely fresh working session for either provider, with the product selected, Dhayan sends `build` and the CTO finds the correct current work without further technical context from him.

If that fails, the bootstrap is incomplete.

## 15. Final constraint

The development system is scaffolding, not the product.

If maintaining Juku OS begins consuming attention comparable to building the products, simplify it. The strongest system is the smallest one that reliably lets interchangeable agents ship correct software and lets Dhayan remain focused on product judgement.

## 16. Rich data

Every product is built to capture rich, granular evidence that raises its own AI's intelligence in its domain, and to measure that honestly. The method is `RICH-DATA.md`, read only when a slice changes what a product learns from, shows about a person, or claims about its own accuracy. Three decisions stay the Chairman's: Hemz retention beyond the documentation clearing, commercial reuse of staff expertise, and reuse of Myst contributions.
