# TO CLAUDE — GLOBAL OPEN-WEIGHT MODEL REGISTRY AND ROUTING IMPLEMENTATION

**From:** GPT Astra, technical adviser  
**To:** Claude, CTO and implementation owner  
**Date:** 18 September 2026  
**Subject:** Implement a global, provider-independent system for assigning the best open-weight LLM to each task  
**Primary global repository:** `Adonis80/how-we-build`

## Executive decision

Please implement a single global record of the approved open-weight LLMs used across the Juku development system. Every present and future project must be able to determine which model to use for each role without hard-coding a model or inference provider in application code.

The model market is changing too quickly for a permanent choice. We intend to review and update the approved model list **every week**. The architecture must therefore make a role change—such as replacing the main reviewer or front-end specialist—a small, central, version-controlled configuration change rather than a refactor across repositories.

Use your authenticated Chrome extension and GitHub access to inspect the existing global and product repositories, implement the smallest robust version of this design, test it, and open the necessary pull request or pull requests. Do not stop at a proposal if the available access permits implementation.

## Current recommendation snapshot

These assignments are the starting policy as of **18 September 2026**, subject to your verification immediately before implementation:

| Stable global role | Initial model | Intended use | Suggested fallback |
|---|---|---|---|
| `reviewer-main` | **GLM-5.3 Max** | Primary code review, architecture review, difficult debugging, large refactors, and escalation after a weaker model fails | Kimi K3 Max |
| `reviewer-frontend` | **Kimi K3 Max** | Final front-end and design review, UI quality, React/web work, screenshot-aware review, and human-preference judgement | GLM-5.3 Max |
| `coder-fast` | **GLM-5.3 Flash** | Default high-volume implementation model and inexpensive autonomous coding | DeepSeek V4.1 Flash |
| `coder-max` | **GLM-5.3 Max** | High-value or difficult implementation that needs flagship open-weight reasoning | Kimi K3 Max |
| `frontend-fast` | **Qwen3.8 Flash Next** | Low-cost front-end generation and rapid visual iteration | GLM-5.3 Flash |
| `frontend-max` | **Kimi K3 Max** | Final/high-value UI generation and design-sensitive implementation | GLM-5.3 Max |
| `agent-fast` | **DeepSeek V4.1 Flash** | Fast terminal, tool-use, and long-horizon agent work where throughput and cache economics matter | GLM-5.3 Flash |

The main operating pattern should be:

1. Use **GLM-5.3 Flash** for most routine coding work.
2. Escalate difficult engineering and final general review to **GLM-5.3 Max**.
3. Use **Kimi K3 Max** for front-end work where visual quality and human preference matter, especially final review.
4. Use **Qwen3.8 Flash Next** for cheap front-end iteration before final review.
5. Use **DeepSeek V4.1 Flash** for high-throughput terminal and agent work.

No product should depend on these literal model names. Products request a stable role; the global registry resolves that role to the currently approved model and provider policy.

## Why this is the present recommendation

There is no honest single winner across every coding benchmark. The leading open-weight models have different strengths:

- **GLM-5.3 Max** is currently the best all-round recommendation for difficult repository engineering and general code review. The supplied research placed it marginally ahead on broad independent intelligence/agent measures, with materially higher generation speed than Kimi K3.
- **Kimi K3 Max** leads current open-weight human-preference coding and WebDev results, making it the strongest specialist for front-end design and final UI review.
- **GLM-5.3 Flash** offers unusually strong coding performance at very low current pricing and is therefore the recommended default worker.
- **DeepSeek V4.1 Flash** combines low pricing, high throughput, native vision, and a strong terminal/agent profile.
- **Qwen3.8 Flash Next** is close to the leading WebDev score at a small fraction of Kimi K3's reference price, making it a strong front-end iteration model.

The supplied point-in-time WebDev comparison was:

| Model | WebDev score | Approximate API input/output price per million tokens shown by Arena |
|---|---:|---:|
| Kimi K3 Max | 1674 | $3.00 / $15.00 |
| Qwen3.8 Flash Next | 1635 | $0.16 / $0.47 |
| Tencent HY4 Preview | 1624 | $0.83 / $2.50 |
| GLM-5.3 Max | 1614 | $1.40 / $4.40 |
| DeepSeek V4.1 Flash Max | 1614 | $0.30 / $1.20 |
| GLM-5.3 Flash | 1607 | $0.07 / $0.25 |

Prices, promotions, benchmark positions, context limits, and provider availability are volatile. Treat this table as the initial evidence snapshot, not permanent configuration.

## Required architecture

### 1. One canonical global registry

Place the source of truth in `Adonis80/how-we-build`, following that repository's existing conventions. If no suitable convention exists, use a clearly named area such as:

```text
model-registry/
  open-weight-models.yaml
  role-routing.yaml
  provider-policy.yaml
  evaluation-policy.md
  CHANGELOG.md
  schema/
  scripts/
```

The precise filenames may change to fit the repository, but there must be one authoritative registry—not separately maintained lists in each product repository.

For every approved or watched model, record at least:

- canonical model family, version, and release date;
- exact provider model identifiers;
- licence/open-weight status and any usage restrictions;
- supported modalities, tools, structured output, and context length;
- best-fit task categories and known weaknesses;
- current input, cached-input, and output prices;
- provider, region, measured speed, uptime, and data-retention/privacy policy;
- relevant external and internal benchmark results;
- evidence URLs and the date each fact was checked;
- status: `candidate`, `canary`, `active`, `fallback`, `deprecated`, or `blocked`;
- date approved, approving decision, superseded model, and reason for any change.

### 2. Stable role aliases

All agents and projects must call stable aliases such as `reviewer-main`, `reviewer-frontend`, `coder-fast`, `coder-max`, `frontend-fast`, `frontend-max`, and `agent-fast`.

The registry should resolve each alias to:

- primary model;
- ordered fallback models;
- allowed and preferred providers;
- maximum acceptable cost and latency where appropriate;
- required capabilities;
- escalation conditions;
- registry version and last-reviewed date.

Do not scatter literal model IDs through prompts, workflows, source code, or project-specific agent definitions. Add validation that rejects or flags unapproved hard-coded model identifiers where practical.

### 3. Provider-independent gateway

Use a provider-neutral OpenAI-compatible interface. The recommended arrangement is:

```text
Juku project or coding agent
          ↓ stable role alias
LiteLLM-compatible gateway/router
          ↓ provider policy
OpenRouter and/or direct first-party provider
          ↓
approved open-weight model
```

Recommended commercial policy:

- Use **OpenRouter initially** as the broad marketplace, unified API, provider failover layer, and convenient way to compare multiple hosts for the same weights.
- Keep **LiteLLM or an equivalent provider-neutral router** as Juku's own abstraction boundary. Product code must not depend on OpenRouter-specific SDK calls.
- Permit direct providers when they offer a material advantage in price, prompt caching, latency, reliability, privacy, or model fidelity.
- Make provider preference a configuration choice, independently switchable from the model assigned to a role.
- Support provider allowlists/denylists, retry, timeout, circuit breaking, and ordered failover.
- Keep API keys and provider secrets in the existing secret-management mechanism; never commit them to the registry.

OpenRouter currently appears attractive because it offers a large multi-provider catalogue, can route the same model across several inference hosts, and supports provider selection/failover. Its current pay-as-you-go platform fee and all displayed inference prices must be verified before implementation.

### 4. Preserve model-specific advantages

Provider independence must not erase useful model-specific behaviour. Allow per-model settings for prompt format, tool support, cache policy, context retention, temperature/reasoning controls, and session affinity.

For example, the supplied research reports that Kimi K3 benefits from sustained sessions and very high prompt-cache reuse when complete assistant messages are retained. The registry/router should be able to express that policy without forcing it upon other models.

### 5. Global availability to every project

Choose the lightest mechanism consistent with the existing Juku repositories so that every project consumes the same registry. Prefer, in order:

1. a small versioned internal configuration package or service generated from the canonical registry;
2. a shared configuration artifact pinned by registry version and updated automatically by pull request;
3. a generated, hash-stamped local projection when a project cannot consume the central source directly.

Do not rely on developers manually copying the table into each repository. Each consumer must expose which registry version it is using, and updating or rolling back that version must be straightforward.

Project-level overrides should be rare, explicit, schema-validated, and documented with an owner, reason, and expiry date. A project override must not silently redefine a global role.

## Weekly model review and update process

Build a scheduled weekly process that prepares a review but does **not** silently replace production models.

Every week it should:

1. Refresh model releases, licence status, benchmark results, prices, provider availability, context limits, speed, uptime, caching, and privacy terms.
2. Compare candidate models against the active role-holder using both external evidence and a small representative Juku evaluation suite.
3. Produce a readable Markdown report showing proposed promotions, demotions, unchanged roles, cost effects, quality effects, and evidence links.
4. Open a pull request for any proposed registry change.
5. Require human approval before promoting a candidate to an active role.
6. Run schema validation, routing tests, provider smoke tests where safe, and consumer compatibility checks.
7. Update the changelog and retain the previous mapping for immediate rollback.

The weekly evaluation should not crown a winner from one benchmark. Weight at least:

- repository-level coding and repair;
- terminal/agent task completion;
- tool-call and structured-output reliability;
- front-end visual and human-preference quality;
- regression rate and review accuracy;
- latency and throughput;
- uncached, cached, and output-token cost;
- effective whole-task cost, including retries and failures;
- context handling and cache behaviour;
- provider reliability, privacy, and licence constraints.

Use task-specific evidence. A model can become `reviewer-frontend` without displacing `reviewer-main`, and a cheap worker can lead `coder-fast` without being trusted for final review.

## Sensible promotion controls

Implement simple safeguards:

- `candidate` models are measured but receive no production work.
- `canary` models receive a small, reversible share of suitable work.
- `active` models own a role after approval.
- `fallback` models are tested sufficiently to take over when the primary fails.
- Automatic failover may move a request to an approved fallback, but it must not permanently rewrite the role mapping.
- Permanent role changes occur only through the version-controlled registry and an approved change record.
- Rollback must be possible by restoring the preceding registry version.

Where possible, capture anonymised operational metrics by role, model, and provider: success, retries, latency, token use, estimated cost, evaluator score, and fallback frequency. Do not capture customer data, secrets, or raw prompts merely for this purpose.

## Minimum implementation acceptance criteria

The work is complete when:

- [ ] `Adonis80/how-we-build` contains one schema-validated canonical open-weight model registry.
- [ ] The seven initial role aliases above are defined with primary and fallback mappings.
- [ ] At least one real Juku project resolves a role through the shared mechanism end to end.
- [ ] Application code can switch a role's model and its provider without a code change.
- [ ] No secrets are stored in the registry or repository.
- [ ] A weekly scheduled workflow produces a dated comparison report and, when warranted, a proposed pull request.
- [ ] Production role changes require human review and are recorded in a changelog/decision record.
- [ ] Schema, resolution, fallback, invalid-role, and rollback behaviour have automated tests.
- [ ] Documentation tells every project and agent how to request a role, inspect the resolved model/provider, pin a registry version, and apply an approved override.
- [ ] The implementation has an emergency rollback path and does not leave OpenRouter—or any other provider—as an irreplaceable dependency.

## Implementation sequence

Please use the Chrome extension and authenticated GitHub session to:

1. Inspect `Adonis80/how-we-build` and the relevant product repositories for existing model, agent, provider, secrets, CI, and configuration conventions.
2. Reconcile this design with any existing global architecture rather than creating a duplicate system.
3. Verify the current model names, identifiers, benchmark evidence, prices, licence terms, and provider capabilities.
4. Implement the canonical schema, initial registry, stable aliases, resolver/router configuration, validation, tests, documentation, and weekly review workflow.
5. Integrate one representative product first, then provide a controlled migration path for the remaining projects.
6. Create focused pull requests with a reversible migration; do not mix unrelated changes.
7. Return a Markdown implementation report with links to the pull requests, files changed, tests run, current role table, any deviations from this recommendation, risks, and decisions that still require Chairman approval.

If repository evidence shows that LiteLLM or the proposed distribution mechanism is a poor fit, choose the smallest equivalent that preserves the non-negotiable properties: **one global source of truth, stable roles, provider independence, weekly evidence-based review, human-approved promotion, and rapid rollback**.

## Sources to verify during implementation

- Artificial Analysis model evidence: <https://artificialanalysis.ai/models/glm-5-3/>
- Arena coding leaderboard: <https://arena.ai/leaderboard/text/coding?license=open-source>
- Arena WebDev/open-weight leaderboard: <https://arena.ai/leaderboard/code?license=open-source>
- Arena WebDev cost/performance frontier: <https://arena.ai/leaderboard/code/pareto?license=open-source>
- OpenRouter pricing: <https://openrouter.ai/pricing>
- OpenRouter GLM-5.3: <https://openrouter.ai/z-ai/glm-5.3>
- OpenRouter DeepSeek V4.1 Flash: <https://openrouter.ai/deepseek/deepseek-v4.1-flash>
- DeepSeek pricing: <https://api-docs.deepseek.com/quick_start/pricing/>
- LiteLLM documentation: <https://docs.litellm.ai/>

Because this is a fast-moving market, the implementation should record the verification date beside every external fact and should make stale evidence visible during the weekly review.
