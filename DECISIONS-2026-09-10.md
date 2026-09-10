# Decisions — 10 September 2026

This page records the agreements reached between Claude and ChatGPT while moving Juku to interchangeable Anthropic and OpenAI lead stacks. `HOW-WE-BUILD.md` carries the compact operating rules; this page preserves the fuller decision context.

## One system, interchangeable lead stacks

- Anthropic stack: Claude/Cowork lead, Claude Code builder.
- OpenAI stack: ChatGPT/Work lead, Codex builder.
- One active lead per slice.
- GitHub is the brain and the pull request is the handover.
- A replacement lead reads the repository, open PR and current slice; it does not reconstruct state from old chats.
- The builder is replaceable.
- Dhayan retains product truth, commercial truth, spending, permissions, visual acceptance and irreversible decisions.
- No AI CEO, second roadmap, shared AI memory database, orchestration/control plane or model registry unless repeated measured failure later proves one is needed.

## Independent review

Review is separate and cold. Use the other vendor whenever practical. Cross-vendor review is mandatory for:

- pricing logic;
- live database mutation or schema changes;
- authentication or authorisation;
- public trust-boundary changes;
- deploy/release machinery;
- the review gate itself.

If it is unclear whether a trust boundary is crossed, treat it as crossed.

Every PR handover identifies `Lead stack:` and `Reviewed by:`.

## Session changeover

At every turn decide whether the next turn stays here or starts fresh. Stay only while all three hold:

- **Same work:** the same slice or bounded question continues.
- **Cheaper to stay:** useful unresolved context here costs less than rebuilding it from the small canonical boot.
- **Clear:** history still helps more than it hurts, with no material stale truth, contradiction, looping, irrelevant output or lost detail.

Otherwise checkpoint and start fresh. Provider caches and compaction can inform that judgement but are never rules themselves.

Before leaving, every durable fact goes to GitHub and the PR/roadmap handover must be sufficient. If the opening words for the next session would need to carry project state, the handover is incomplete.

A fresh session reads progressively from canonical truth and stops when it knows enough. It never rebuilds repository state from old chats. Tool output stays targeted; no polling.

For Codex, a fresh task starts each slice and a thread continues only within that slice while the three checks hold.

For non-repository advisory work only, one temporary `START-HERE.md` may hold the bounded question, agreed points, next action and relevant files. It is superseded when the result lands in GitHub.

## Autonomy

The development system should minimise manual relay by Dhayan. Repository-backed handovers belong in GitHub, not downloadable chat files or copy/paste between sessions. Agent internet access may remain enabled where it materially reduces manual work, subject to the product's security boundaries and least necessary access.

## Hemz OS OpenAI pilot

Hemz OS is the first OpenAI-led pilot. The pilot succeeds if Dhayan only needs to:

1. type `build`;
2. inspect the preview;
3. answer `agreed` or `not yet`.

The Hemz Codex Cloud environment has been created. No build task had started at the time of this decision record.
