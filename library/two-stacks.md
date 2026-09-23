# The two stacks

Scope: every product and this repository. Open when: choosing the lead or its effort, handing work between stacks, a job needs hands, or telling code from words.

**One lead owns a slice at a time.** The pull request is the handover; a replacement lead rebuilds from GitHub, never from a chat. *build* in the other stack transfers ownership only at a clean checkpoint: when the pull request's latest entry is the outgoing lead's checkpoint. Otherwise the incoming lead leaves that pull request alone and takes the next item. Nothing is built to manage this: no switch file, lock, registry or orchestrator.

**Who leads is his ruling.** While a Claude Opus model is the strongest available to him, Claude leads and the OpenAI path stays configured. The rules are written by role, so the swap costs nothing. **Effort:** the lead builds at medium, and steps to high after one failed attempt. Max is kept for reviews of the risky classes: pricing, schema, authentication and authorisation, deploy machinery. A product holds the default as `effortLevel` in its `.claude/settings.json` (*What every product carries*), and a session steps it up with `/effort`. The reviewer still reads at max on every read.

**Code and words.** Anything that runs (code, tests, a database change, a deploy) is built in the lead's workshop: a session attached to the repo, meaning a Claude code session or a Codex cloud task. Only a workshop can prove it: the build, the tests, the Playwright journey on phone and desktop, the preview. Words may change from a Cowork session through the Mac, by the same branch, pull request and review. Words: this rulebook, and a product's `AGENTS.md`, `PRODUCT.md`, `NAMES.md`, `roadmap.json`, screen specs, README. Size is not the line. One session reaches one product's repository: one key, one product.

**Anthropic.** Building happens in a code session started attached to the repository. A Cowork or chat session advises, and may change words by pull request. The product's `.claude/settings.json` enforces the hard stop. Its hands are Claude's own, used from a Cowork session (his rulings): the Chrome extension, computer use on the Mac, and the Claude app's built-in browser, which opens `claude.ai` pages the extension refuses.

A code session at `claude.ai/code` has none of them. It puts the job in CI; where CI cannot do it, it writes the job on its pull request under **Hands needed:** with every choice made. Its reply names only the room: a Cowork session in the product's Project, where *build* reads the open pull requests and does the job. It says on the pull request what was done, never a secret. Such a job keeps its pull request open until done: the slice waits, or before the merge the job moves to one that stays open. He types *build* and nothing else (his ruling); anything more is a fault in the line.

**OpenAI.** Codex cloud is the development surface, local only when the work needs the Mac. ChatGPT advises: it reads GitHub, writes nothing. A Codex cloud environment is built from the repository's own toolchain:
- the setup script installs what the lockfiles name and clones this rulebook to `~/.juku/how-we-build`;
- the maintenance script refreshes that clone and fails closed;
- agent internet stays off unless needed, and then is a named allowlist (the package registry and GitHub, GET, HEAD and OPTIONS only);
- no secret is added until a product proves it needs one.

One line in the product's `AGENTS.md` points a lead working offline at the local rulebook. Schedules, automations and polling are forbidden in the build loop. It has no hands: a manual job goes to CI, or the slice checkpoints and transfers.

**His part is only a tap no hand may make**: signing in, a password or secret typed into a web page, an are-you-human check, paying, approving a sign-in key. A session takes such a job to that one tap and hands him the tap alone: the link, what he will see, the words to reply. Never the job, and never a choice of how.
