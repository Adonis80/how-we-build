# The max subagent

Scope: every product repository. Open when: a lead hands its max piece on, or a product sets up or checks its max subagent file.

The effort ladder is library/two-stacks.md's. This page holds only what carries out its top step (R-2026-09-28a).

**The file.** Every product carries `.claude/agents/max-subagent.md`, exactly as below, and makes itself current in its next pull request. `<model>` and `<effort>` are what the registry's `max-subagent` role resolves to, printed from a checkout of this repository by `python3 model-registry/resolve.py model-registry/registry.json max-subagent model`, and then `effort`. So a switch is one edit to the registry, and each product's file follows in its next pull request.

```markdown
---
name: max-subagent
description: The max step of the rulebook's effort ladder (Adonis80/how-we-build, library/two-stacks.md): one bounded piece the lead hands over, never a whole slice. The lead briefs it fully, since it starts with no context.
model: <model>
effort: <effort>
tools: Read, Grep, Glob, Edit, Write
---
You are the max step of the effort ladder in Adonis80/how-we-build (library/two-stacks.md). The lead of a slice, working at high, has handed you one bounded piece of it. You start with no context, so the brief is all you have. If it lacks something you need, say exactly what, rather than guess.

Do that piece and nothing else. You may read the code and change the files the brief names. The lead keeps the pull request and the tests: you do not commit, push, open or merge anything, and you run no checks.

Answer with what you did, what you checked, what you did not, and how sure you are.
```

**What stops it running at max** (Claude Code's docs, read 28 September 2026). `CLAUDE_CODE_EFFORT_LEVEL`, wherever it is set, outranks the file's `effort`, so no product sets it. A managed `maxEffortLevel` caps it. `CLAUDE_CODE_SUBAGENT_MODEL_FORCE`, or a `model` the lead passes when it hands over, replaces its model. `CLAUDE_EFFORT`, which a cloud session's host sets from the session's own effort, does not cap it: shown below.

**Shown in a real session** (29 September 2026, a cloud container on his account). A lead at high (`--effort high`, and `CLAUDE_EFFORT=high` as the host sets it for a session at high) handed this file, resolved from the role as above, one bounded piece. The transcripts recorded the lead's turns at high and the subagent's at max, on the same model. With `CLAUDE_CODE_EFFORT_LEVEL=high` added, the subagent's turns ran at high, so the check tells the two apart.

**Checking a run.** The lead reads the subagent's transcript, `subagents/agent-*.jsonl` under the session's folder in `~/.claude/projects/`: each turn's `perTurnEffort` and `message.model`. It records on the pull request what ran and, if anything but max, why.
