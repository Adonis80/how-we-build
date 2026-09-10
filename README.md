# how-we-build

The global operating system for Dhayan's AI-built products. This repository says **how** products are built. Each product repository says **what** that product is and what comes next.

## What matters

- `HOW-WE-BUILD.md` — the short operating rule. A working session reads this first.
- `CHARTER.md` — why the system is shaped this way. It is not normal working context.
- `AGENTS.md` — instructions for reviewing changes to this repository.
- `design/` — shared screen law, interaction-architect role and design forms.
- `LEGACY-ROADMAP.md` — non-authoritative ideas rescued from retired repositories. It never drives work.

GitHub is the only durable project truth. Chats, provider memory and copied Project files are not.

## Products under this rulebook

- **Hemz OS** — `Adonis80/Hemz-OS` (private). Alterations-business operating system.
- **Juku Perfume** — `Adonis80/juku-perfume` (private). Fragrance intelligence, discovery and exchange.

A repository not listed here is not automatically governed by this rulebook.

# New product bootstrap

A new product has **one shared bootstrap contract** and **provider-specific adapters**. Do not duplicate the common rules inside each provider setup.

## Shared contract

The active CTO does this agentically; Dhayan only supplies permissions, money, irreversible decisions or product truth that cannot be derived.

1. Create or normalise the private product repository.
2. Give it the canonical product files required by `HOW-WE-BUILD.md`: `AGENTS.md`, `PRODUCT.md`, `NAMES.md`, `roadmap.json`, `README.md`; add only product files the product genuinely needs.
3. Put product-specific truth in that repo. Do not copy the global rulebook into it.
4. Register the product in **Products under this rulebook** above.
5. Install the standard deterministic checks and independent-review gate, adapted only where the product's toolchain requires it.
6. Configure both provider adapters below.
7. From a completely fresh session in each provider, send only `build`. Bootstrap is complete only when each provider can identify the right repo, read the global rule, inspect open PRs and the roadmap, and continue the correct work without Dhayan explaining state.

A setup difference belongs in a provider adapter. A product difference belongs in the product repo. A global rule belongs in `HOW-WE-BUILD.md`. Never maintain the same truth in two places.

## OpenAI adapter — ChatGPT + Codex

**ChatGPT is the thinking/advisory surface. Codex is the development surface.**

### ChatGPT Project

Create one lightweight ChatGPT Project named for the product. Its instructions identify the product repo and this rulebook. Keep copied project files and project-state handovers out of it. When current product state matters, read GitHub live.

ChatGPT may research, challenge architecture, resolve product/UI questions and update durable decisions through GitHub. Normal software implementation belongs in Codex.

### Codex

Create a Codex project attached to the product repository. Normal execution uses **Codex Cloud**; local execution is chosen only when the task genuinely needs the Mac.

Configure the cloud environment from the repository's actual toolchain rather than from a universal template:

- detect runtimes and package managers from lockfiles, manifests and existing scripts;
- install only what the repository needs;
- make `how-we-build` reachable at startup, normally by cloning it to `~/.juku/how-we-build` or reading the live raw file;
- enable container caching and workspace sharing;
- allow common development internet access;
- add a system browser only when the repository's tests or UI work require it;
- add no secret or environment variable until the product proves it needs one, then use the platform secret store rather than repository files.

Codex may use its automatic environment detection, but the repository's explicit setup and test commands remain authoritative. The final test is a fresh Codex thread receiving only `build`.

**Proven autonomous bootstrap route.** When the Codex project/environment does not yet exist, the active CTO may use **ChatGPT for Chrome** against an already-open Codex Cloud tab to create it rather than asking Dhayan to configure it manually. The proven Hemz OS instruction was:

> Use my open Codex Cloud tab in Chrome. Create the Hemz OS environment for `Adonis80/Hemz-OS` using the agreed setup. Configure it fully, but do not start a build.

For a new product, substitute the product name and repository, and derive "the agreed setup" from this adapter plus the repository's real toolchain. Configure and save the environment, but do not start product work during bootstrap. If the Codex UI changes, preserve the outcome rather than the old click sequence. Ask Dhayan only when the platform itself requires a human permission or authentication action.

**Current proven example — Hemz OS:** Ubuntu 24.04, Node 22, `npm ci`, system Chrome, no redundant Playwright browser install, `how-we-build` cloned to `~/.juku/how-we-build`, caching on, workspace sharing on, common-development internet on, and no secrets by default. Copy the method, not blindly these dependencies.

## Anthropic adapter — Claude

Create one Claude Project named for the product. It contains routing instructions, not a second copy of product truth. Its instructions identify this rulebook and the private product repository.

Use the provider's current attached-repo/code environment when it can read and write the private repository reliably. If that path is unavailable, use the product's checked-out Mac folder as the working route. The route may change; GitHub does not.

Claude reads the live global rule first, then the product repo and open PRs. It uses the repository's actual setup/test commands and adds only permissions or secrets the task requires. A fresh Claude working session must also succeed from `build` alone.

# Switching CTO

Only one provider owns a slice at a time. The PR is the handover.

At a checkpoint, starting `build` in the other provider transfers CTO ownership. The incoming provider reads the global rule, global open PRs, product open PRs and current product truth before acting. Dhayan does not relay the previous provider's reasoning.

Do not switch providers while the outgoing provider is still modifying the same slice.

# The independent reviewer

Every product uses cold review according to `HOW-WE-BUILD.md`. A review clears only the commit it actually read; a later push requires the new head to be reviewed. Review requests are batched, never used as a polling mechanism.

The reviewer checks the diff, tests, product truth and roadmap independently. It looks for wrong, missing, duplicated, untested or quietly expanded work and states what it did and did not check. Cross-vendor review is mandatory for the protected changes named in `HOW-WE-BUILD.md`.

# Context and documentation hygiene

Canonical files contain **current truth, not history**. Git history preserves old truth.

When changing a canonical file:

1. find the existing owner of the subject;
2. read enough surrounding material to understand the current rule;
3. replace, consolidate or delete superseded wording;
4. search other active files and code for conflicting copies;
5. update tests where the truth is executable.

Small always-read instruction files carry hard size limits. Large product documents are not given arbitrary size caps; they are searched and edited at the relevant section rather than reread in full for every task.

Temporary reasoning, status and handover prose belongs in the PR and disappears when the PR closes. Do not create standalone handover, restart, review, context or status files. Historical evidence may exist where a product genuinely needs evidence, but it is excluded from normal execution context and is not rewritten as current truth.

# Design

Shared interaction rules live once in `design/`. A product carries only its own domain constitution, design system and screen specifications.

For materially new UI: brief the real user problem, reduce concepts, settle the interaction model, create the visual, obtain Dhayan's material visual acceptance, then build it into the real product. A polished mockup never overrides business truth.

# Changing this repository

Changes use a branch and pull request against protected `main`. Before changing `HOW-WE-BUILD.md`, read it in full and replace or remove what the change supersedes.

Do not answer development-system friction by creating another control plane, scheduler, memory system, agent hierarchy or instruction layer. Prefer deletion, ordinary GitHub state and deterministic checks.

A fresh product session normally needs only `HOW-WE-BUILD.md` plus the relevant product files. This README is setup/reference material, not recurring build context.
