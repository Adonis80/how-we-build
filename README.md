# Juku OS — how we build

The shared operating system for Dhayan's products. This repository owns **how** we work; private product repositories own **what** we build. GitHub holds current truth and PRs hold unfinished work. Chats are disposable.

`HOW-WE-BUILD.md` is the short operating page. `CHARTER.md` gives rationale. `design/` owns the shared screen method. `LEGACY-ROADMAP.md` is an inactive idea bank, never approved work. `scripts/` implements checks and Project instruction rendering; it is not an orchestrator.

## Projects and source routing

This is the canonical registry used by the instruction generator. Register a new product here once. Routing grants no repository permission.

<!-- juku-projects:start -->
| Key | Project | Repository | Scope |
|---|---|---|---|
| juku-os | Juku OS | Adonis80/how-we-build | global |
| hemz-os | Hemz OS | Adonis80/Hemz-OS | product |
| juku-perfume | Juku Perfume | Adonis80/juku-perfume | product |
<!-- juku-projects:end -->

Juku OS reads the global repository and reads registered products only when the task needs them. A product Project reads its own private repository plus the global rulebook, never another product by default. Verify each account's access independently. Private product content, customer data, credentials and account identifiers must not be copied into this public repository or its PRs.

## Start and switch CTO

`build` is an instruction to complete approved work, not a shell command. Resolve the selected repository, read current global `main`, then its `AGENTS.md` and relevant canonical files. Read open PRs before choosing work. A proposed global change is context, not merged policy; unrelated global PRs do not block product delivery. A session uses its recorded rulebook revision until a user ruling or relevant safety fix requires re-reading it.

For a product, resume an approved unfinished slice; otherwise take the first approved roadmap item. Do not reorder the owner's roadmap. For Juku OS, use the user's explicit system request and the relevant open PR. No `PRODUCT.md` or `roadmap.json` is required in this rulebook repository, and its inactive idea bank never supplies work.

One lead owns a slice. Its PR records `Lead: provider / surface`, `Ownership: active | checkpointed | blocked`, the full head SHA, checks, remaining work and next action. On a user-requested switch, the outgoing session stops and pushes first. The incoming CTO checks that checkpoint against the live branch, records its ownership and resumes that branch. Starting another chat alone does not stop the outgoing process or grant a lock. If the PR still says active and no stop is evidenced, do useful independent work but do not concurrently edit that slice. Never force-push another lead's work. Before any push, compare the remote head with the checkpoint; reconcile changed work rather than overwriting it.

Keep one PR per slice. A handover must contain objective, acceptance criteria, done, remaining, commands/results, preview (or why not applicable), source SHAs, next action and rollback. Record the reviewer and the commit reviewed separately from the lead. Source SHAs belong in PR metadata; a PR cannot contain its own final commit hash in that same commit.

## What every product carries

One private repository with `AGENTS.md` (under 500 words), `PRODUCT.md`, `NAMES.md`, `roadmap.json`, `README.md`, source and tests. Product `AGENTS.md` points to this rulebook and holds only domain invariants. Product README owns exact install, check, preview, deployment, smoke and rollback commands. Keep one implementation for each business calculation. Roadmap order and product/business truth belong to Dhayan; status, proof and technical implementation belong to the CTO.

Preserve existing product safeguards and constraints when refreshing an adapter. A stale access recipe is not a domain rule: verify the available connector or execution route before requiring a Mac. Fix that recipe in the product's own PR; never duplicate it here. Do not use a global rewrite to silently relax product checks.

## Project instructions and synchronisation

Use one Project per product **within each account or workspace actually needed**. Reuse existing Projects and Cloud environments after verifying their repository mapping; names alone are insufficient. Do not copy source files or handover notes into Project knowledge. Projects are launch points, not mirrors of GitHub.

Generate instructions from this README, normally on merged `main`. Record the source revision when preparing a routing change in a PR; the rendered instructions always load operating rules from merged `main`:

```sh
python3 -B scripts/project_bootstrap.py --list
python3 -B scripts/project_bootstrap.py juku-os
python3 -B scripts/project_bootstrap.py hemz-os
python3 -B scripts/project_bootstrap.py juku-perfume
```

The generator fills the single template below from the registry and adds a content fingerprint. To verify a saved Project, read its actual instructions back through the provider UI/tool and compare the complete text, not just its fingerprint:

```sh
python3 -B scripts/project_bootstrap.py hemz-os --check /temporary/path/actual-instructions.txt
```

Exit zero means the text matches this checkout; it does **not** mean an account is authenticated or a fresh build has succeeded. These commands render and compare text; they do not log into accounts or write provider settings. Use a temporary file outside the repository for readback.

The CTO updates reachable Project settings during authorised setup work and verifies the saved text. Reconcile the installed text with merged `main` when the routing/template PR lands; installing a launch instruction does not make its unmerged policy proposals authoritative. Other accounts require their own permitted login and repository connection; a shared Project does not prove GitHub write access. Record account-specific setup evidence in the relevant private setup PR or chat, never here. Never share cookies, credentials or customer content between accounts. If authentication is required, use the real sign-in/approval screen; do not invent a handed-off screen.

Routine rule changes need no Project rewrite: the instructions load the latest rulebook at session start. **This is live source loading plus explicit instruction drift checking, not an automatic cross-account sync service.** Missing secondary accounts do not stop an already verified CTO from shipping.

<!-- juku-instructions:start -->
```text
You are the CTO for ${project_name}. Canonical repository: https://github.com/${repository}.
Global operating rule: https://github.com/Adonis80/how-we-build/blob/main/HOW-WE-BUILD.md.
At session start, fetch the current global rule from GitHub and follow it. Read this repository's AGENTS.md and relevant current files, open PRs and their live heads before continuing work. Treat open proposals and prior chats as context, not current policy.
${source_scope}
Make technical decisions and complete authorized work. Use the tools actually available: verify repository read access, execution, branch writes and PR capability separately. A Project name, a model choice or a successful read does not prove write access. Never claim to control the Mac or select a Cloud model unless verified.
For build, follow the operating rule and README's Start and switch CTO section. Resume the checkpointed approved slice before starting another; never overlap an active builder. Keep main protected, use branches and PRs, and leave a complete handover there.
Fetch README's Project instructions and synchronisation section when setup or routing changes. Do not copy rules, product files, credentials or handover notes into this Project. If live access fails, report the exact blocker without inventing repository state.
```
<!-- juku-instructions:end -->

## Provider adapters

Choose a route by **verified capabilities and the requested model**, not the provider label. A successful read proves reading; a successful branch push and PR update prove those operations. Use real authorized work to verify writes, not dummy commits on `main`.

### OpenAI: ChatGPT Projects, Work and Codex

ChatGPT Projects can hold dialogue and Work chats. Work may implement, test and publish changes when its execution and GitHub tools support them. An ordinary chat without those tools cannot claim the same capabilities. The desktop app is optional for repository work; use it when a local device or installed tool is actually needed.

Codex Cloud is another execution route. Reuse the environment attached to the exact repository. Derive runtime, package manager, installation and tests from the repository; install a browser only when required. Grant only needed network destinations, repository access and secret-store entries. Sharing and caching depend on the workspace's needs and data, not a universal switch-on rule.

**Model constraint, checked 12 September 2026:** OpenAI's [model documentation](https://learn.chatgpt.com/docs/models#choose-a-model-for-cloud-chats) says the default model for Codex Cloud chats cannot currently be changed. Do not promise “any model,” assume the chat's selector controls delegated Cloud work, or block on making Cloud environments appear as desktop folders. For an explicitly requested Astra level, use a capable surface that actually exposes it; record a user-selected setting as user-reported unless directly verifiable. [Project documentation](https://learn.chatgpt.com/docs/projects?surface=app) describes shared Project instructions across Chat and Work, not automatic GitHub permission grants.

Keep GitHub App access selected to required repositories, with contents and PR write capability for building; no administration or branch-protection bypass. Account, workspace, ChatGPT connector and Codex installation access are distinct and must be checked where used.

### Anthropic: Claude

Use the same generated routing instructions in the existing Claude Project. Choose its available coding environment or repository connector after proving capabilities. A read-only Project attachment cannot push a branch. Use an authorized local checkout only if the work or available execution route needs it. Verify provider-specific setup against current provider documentation when changing it; do not assume another provider's instructions or permissions apply.

### New product or additional account

Normalise the canonical product files, register it, install its checks, configure the selected provider's existing Project/environment and apply generated routing instructions. Do not create a duplicate because another account cannot see an existing workspace. Reconnect the correct account or use its own deliberately separate Project.

Verify each configured route with a fresh session: identify repository and global SHA, read relevant product truth and open PRs, select the right approved slice from `build` alone, then execute its real checks and publish its authorized branch/PR. Bootstrap inspection alone must not start product work if the user asked only for setup. A second provider is an independent acceptance test, not a prerequisite to shipping with the first. Mark untested routes unverified; never claim all accounts are configured.

## The independent reviewer

Cold review starts from the diff, tests and canonical truth before the PR's narrative. Address the CTO, state evidence, omissions and confidence. Resolve important findings in a batch, then request at most one review of that new head. Two rounds is a coordination limit, never permission to ship a known blocking bug. If the reviewer is unavailable or blocking issues remain, checkpoint and park; take independent approved work if available. No polling or repeated asks.

Prefer another provider; the operating page names changes that require one. An OpenAI builder's own audit is not independent review, and another OpenAI session does not satisfy a cross-vendor requirement. A reviewer unable to post directly may supply findings, but the lead must attribute them honestly with the exact reviewed SHA and preserve the evidence in the PR. Never manufacture a bot review or an approval.

This repository's required `check` includes a **Codex review receipt**, preserving the existing GitHub gate. It recognises a submitted bot review on the exact head or the bot's known completed-comment formats with a commit identifier resolved to that full SHA. Pending/dismissed reviews and changes-requested reviews cannot clear it. API failure or ambiguous/stale commit fails closed. A receipt says a review happened, not that findings are resolved or that cross-vendor review occurred; those remain explicit merge requirements. Reaction-only responses without a verifiable commit do not clear the gate.

PR pushes and submitted reviews run CI. A plain issue comment does **not** trigger this workflow. After a clean completed bot comment, rerun the failed `check` workflow on that PR once using an available GitHub action. Do not repeatedly ask for another review to wake CI. The gate needs only repository and PR read permission; do not add an elevated comment-triggered workflow that executes PR code.

## How a screen gets designed

For materially new or reworked UI, use `design/BRIEF_TEMPLATE.md` to state the real user problem and fixed domain rules. The fresh Interaction Architect follows `design/ARCHITECT.md` and `design/SCREEN-LAW.md` with the product's constitution and design system. Reduce concepts, settle the interaction model, write the screen spec, then show phone-first real states and desktop where composition differs. Use real derived values, truthful unknown/error/empty states, accessible controls and existing approved patterns.

Dhayan accepts the visual before material UI implementation. Review against `design/REVIEW_RUBRIC.md`; a pretty mockup cannot override business truth. Routine changes to an already accepted pattern do not need another design ceremony. The implemented Playwright journey, preview and acceptance must still agree. Keep one active brief; delete it when its durable contract and decisions reach the spec. Specifications remain in the product, not global Project knowledge.

## Checks and changes to this repository

Run `bash check.sh` from any directory. Python 3 and Bash are the only dependencies. It validates the fixed file tree, the 500-word operating page, the 450-word screen law, registry/template rendering and secret patterns, then runs the regression suite. It reports suspected secrets by location without printing values. Pattern checks are not a comprehensive secret audit. Local success makes no claim of independent review or provider access; CI adds the receipt check on PR events.

A global change needs the Charter §13 gate or Dhayan's explicit ruling, recorded in the PR. The 12 September 2026 instruction to audit/build Juku OS and implement interchangeable CTOs and Project synchronisation authorises this bounded repair. It does not authorise weakening protected `main`, merging one's own system additions, exposing private data or bypassing review.

Read the canonical owner fully; replace obsolete text, search active files for contradictions, and test executable rules. Do not create another memory database, scheduler or handover file. Product-specific fixes stay in their own repositories. Open proposals are not active policy. Saved launch instructions still read merged policy, even while a routing repair is under review. After this repair, return to approved product delivery; measure released, accepted customer outcomes rather than OS maintenance. Revenue is a product result to validate, not a guarantee a rulebook can make.
