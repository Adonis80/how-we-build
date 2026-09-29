# The max subagent

Scope: every product, in the Anthropic stack. Open when: a lead hands its max piece on, or a product sets up or checks its max subagent file.

The effort ladder is library/two-stacks.md's. This page holds only what carries out its top step (his ruling, 28 September 2026, quoted whole on [#124](https://github.com/Adonis80/how-we-build/pull/124)).

**The file.** Every product carries `.claude/agents/max-subagent.md`, exactly as below with `<id>` replaced by the id `model-registry/registry.json` gives Claude Opus 5.5, and makes itself current in its next pull request. It has no shell, so it cannot commit, push or run a check: the lead keeps the pull request and the tests.

```markdown
---
name: max-subagent
description: Claude Opus 5.5 at effort max, for the one bounded piece the rulebook's effort ladder sends to max (Adonis80/how-we-build, library/two-stacks.md), never a whole slice. The lead briefs it fully, since it starts with no context.
model: <id>
effort: max
tools: Read, Grep, Glob, Edit, Write
---
You are the max step of the effort ladder in Adonis80/how-we-build (library/two-stacks.md). The lead of a slice, working at high, has handed you one bounded piece of it. You start with no context, so the brief is all you have. If it lacks something you need, say exactly what, rather than guess.

Do that piece and nothing else. You may read the code and change the files the brief names. The lead keeps the pull request and the tests: you do not commit, push, open or merge anything, and you run no checks.

Answer with what you did, what you checked, what you did not, and how sure you are.
```

**What stops it running at max** (Claude Code's docs, read 28 September 2026). `CLAUDE_CODE_EFFORT_LEVEL`, wherever it is set, outranks the file's `effort`, so no product sets it. A managed `maxEffortLevel` caps it. `CLAUDE_CODE_SUBAGENT_MODEL_FORCE`, or a `model` the lead passes when it hands over, replaces its model.

**Shown in a real session** late on 28 September 2026 (UTC): Claude Code 2.1.284, in a cloud container on his account. A lead on Claude Opus 5.5 at high, with the host's effort variable at high as a product session at high has it, handed this file, exactly as above, one bounded piece. The transcripts record each turn's effort: the lead's 3 turns ran at high and the subagent's 4 at max, both on Claude Opus 5.5; the session cost $0.21 and took 70 s. With `CLAUDE_CODE_EFFORT_LEVEL=high` added, the subagent's turns ran at high ($0.11, 25 s), so the check tells the two apart.

**Checking a run.** The lead reads the subagent's transcript, `subagents/agent-*.jsonl` under the session's folder in `~/.claude/projects/`: each turn's `perTurnEffort` and `message.model`. It records on the pull request what ran and, if anything but max, why.
