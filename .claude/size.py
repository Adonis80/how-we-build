#!/usr/bin/env python3
"""The size hook: a session's real size, read from its own transcript.

His rulings of 5 November 2026 (issue #363, "Locks, not reminders"): "Hard stop
at 350,000 tokens, by machine. A hook reads the session's own transcript usage
(the real figure, not an estimate) after every tool call: at 300,000 it
requires the handover checkpoint; at 350,000 it blocks every action except
writing that checkpoint. Every checkpoint carries a size line."

`.claude/settings.json` runs this file before (PreToolUse) and after
(PostToolUse) every tool call. The size is the context of the newest
main-thread model turn in the transcript: its input, cache-write, cache-read
and output tokens, as the model's own usage reports them.

- After a call, at 300,000 or more with no checkpoint written since the line
  was crossed: the session is told, on every call until it writes one, to write
  its handover checkpoint now.
- Before a call, at 350,000 or more, or once that checkpoint is written past
  300,000: every call is refused but the checkpoint itself, loading a tool
  (ToolSearch), and, once the checkpoint is written, starting the successor
  (`library/session-changeover.md`, *A session starts its own successor*).
- Before a call, at any size: a checkpoint comment without a `Size:` line
  whose `end`/`now` figure is within 20k of the real one is refused, with the
  real figure. Head office's `Checkpoint: released` carries none (that page).

An unreadable transcript blocks nothing and says so: a lock that cannot see
must not brick the session that would write the handover.

`--now [transcript]` prints the real size (newest transcript of this
directory's project when none is named). `--selftest` runs the cases below and
checks `.claude/settings.json` still wires both events to this file.
"""
import json
import os
import re
import sys
import tempfile

LINE = 300_000      # the handover checkpoint is required
HARD = 350_000      # everything but the checkpoint is refused
SLACK_K = 20        # a Size: line's figure may sit this many k off the real one

COMMENT_TOOLS = ("__add_issue_comment", "__update_issue_comment")
SUCCESSOR_TOOLS = ("__create_trigger", "__update_trigger", "__fire_trigger", "__list_triggers")
ALWAYS = ("ToolSearch",)

CHECKPOINT_RE = re.compile(r"(?m)^\W*Checkpoint:")
RELEASED_RE = re.compile(r"(?m)^\W*Checkpoint:\s*released")
SIZE_RE = re.compile(r"(?m)^\W*Size:.*$")
FIGURE_RE = re.compile(r"\b(?:end|now)\s*~?\s*(\d+(?:\.\d+)?)\s*k\b")


def _ends(name, suffixes):
    return any(name.endswith(s) for s in suffixes)


def checkpoint_body(tool_name, tool_input):
    """The body if this call posts a checkpoint (not a release), else None."""
    if not _ends(tool_name or "", COMMENT_TOOLS):
        return None
    body = (tool_input or {}).get("body") or ""
    if not CHECKPOINT_RE.search(body) or RELEASED_RE.search(body):
        return None
    return body


def read(transcript_path):
    """(size, checkpointed_past_line, tool_uses) or None when unreadable."""
    try:
        f = open(transcript_path, encoding="utf-8")
    except (OSError, TypeError):
        return None
    size = 0
    seen = False
    checkpointed = False
    tool_uses = 0
    with f:
        for raw in f:
            try:
                d = json.loads(raw)
            except ValueError:
                continue
            if d.get("type") != "assistant" or d.get("isSidechain"):
                continue
            m = d.get("message")
            if not isinstance(m, dict):
                continue
            u = m.get("usage")
            if isinstance(u, dict):
                n = sum(int(u.get(k) or 0) for k in
                        ("input_tokens", "cache_creation_input_tokens",
                         "cache_read_input_tokens", "output_tokens"))
                if n:
                    size, seen = n, True
            content = m.get("content")
            if not isinstance(content, list):
                continue
            for c in content:
                if not isinstance(c, dict) or c.get("type") != "tool_use":
                    continue
                tool_uses += 1
                if size >= LINE and checkpoint_body(c.get("name"), c.get("input")) is not None:
                    checkpointed = True
    if not seen:
        return None
    return size, checkpointed, tool_uses


def size_problem(body, size):
    """Why a checkpoint body's Size: line fails, or None."""
    line = SIZE_RE.search(body)
    real = f"{round(size / 1000)}k"
    if not line:
        return (f"a checkpoint carries a `Size:` line (his ruling, 5 November 2026, #363); "
                f"this session's real size is {real} (transcript)")
    fig = FIGURE_RE.search(line.group(0))
    if not fig or abs(float(fig.group(1)) - size / 1000) > SLACK_K:
        return (f"the `Size:` line's `end`/`now` figure must be the real one: "
                f"this session is at {real} (transcript), so write `end {real} (transcript)`")
    return None


def decide(event, tool_name, tool_input, state):
    """The hook's JSON answer, or None to stay silent."""
    if state is None:
        if event == "PostToolUse":
            return {"hookSpecificOutput": {"hookEventName": "PostToolUse",
                    "additionalContext": "size hook: the transcript could not be read; size unknown, nothing blocked"}}
        return None
    size, checkpointed, tool_uses = state
    k = f"{round(size / 1000)}k"
    if event == "PreToolUse":
        body = checkpoint_body(tool_name, tool_input)
        if body is not None:
            why = size_problem(body, size)
            return _deny(why) if why else None
        finished = size >= HARD or (size >= LINE and checkpointed)
        if not finished or tool_name in ALWAYS:
            return None
        if checkpointed and _ends(tool_name or "", SUCCESSOR_TOOLS):
            return None
        if checkpointed:
            return _deny(f"size hook: {k}, handover checkpoint written; the only actions left are "
                         f"starting the successor (create/update/fire_trigger) and ending the turn")
        return _deny(f"size hook: {k}, past the hard stop of 350k; every action is refused but writing "
                     f"the handover checkpoint (an issue comment opening `Checkpoint:`, with its `Size:` line)")
    if event == "PostToolUse":
        if size >= LINE and not checkpointed:
            return {"decision": "block",
                    "reason": (f"size hook: {k}, past the 300k line. Write the handover checkpoint now "
                               f"(`Checkpoint:`, `Size: ... end {k} (transcript) ...`, `Planned:`, the session's link), "
                               f"then start the successor. At 350k every other action is refused.")}
        if tool_uses <= 1:
            return {"hookSpecificOutput": {"hookEventName": "PostToolUse",
                    "additionalContext": f"size hook: live; boot {k} (transcript)"}}
    return None


def _deny(reason):
    return {"hookSpecificOutput": {"hookEventName": "PreToolUse",
            "permissionDecision": "deny", "permissionDecisionReason": reason}}


def newest_transcript():
    slug = re.sub(r"[^A-Za-z0-9]", "-", os.getcwd())
    d = os.path.join(os.path.expanduser("~"), ".claude", "projects", slug)
    try:
        files = [os.path.join(d, f) for f in os.listdir(d) if f.endswith(".jsonl")]
    except OSError:
        return None
    return max(files, key=os.path.getmtime) if files else None


# ---- selftest ---------------------------------------------------------------

def _turn(n, tool=None, body=None, sidechain=False):
    content = []
    if tool:
        content.append({"type": "tool_use", "name": tool, "input": {"body": body} if body is not None else {}})
    return json.dumps({"type": "assistant", "isSidechain": sidechain, "message": {
        "content": content,
        "usage": {"input_tokens": 2, "cache_creation_input_tokens": 1000,
                  "cache_read_input_tokens": n - 1002 - 10, "output_tokens": 10}}})


def _state(lines):
    fd, p = tempfile.mkstemp(suffix=".jsonl")
    with os.fdopen(fd, "w") as f:
        f.write("\n".join(lines) + "\n")
    try:
        return read(p)
    finally:
        os.unlink(p)


def _denied(a):
    return bool(a) and a.get("hookSpecificOutput", {}).get("permissionDecision") == "deny"


def selftest():
    ok = True
    C = "mcp__github__add_issue_comment"
    good = "**Checkpoint: boundary — slice complete.**\n- `Size: cloud boot 96k end 310k (transcript) items #1 S`"
    cases = []
    s = _state([_turn(96_000, "ToolSearch")])
    cases += [
        ("the real size is read", s[0] == 96_000),
        ("a first call reports the hook live", "live" in json.dumps(decide("PostToolUse", "ToolSearch", {}, s))),
        ("below the line nothing is refused", decide("PreToolUse", "Bash", {}, s) is None),
    ]
    s = _state([_turn(96_000, "Bash"), _turn(250_000, "Bash"), _turn(120_000, "Bash", sidechain=True)])
    cases.append(("a subagent's turn is not the session's size", s[0] == 250_000))
    s = _state([_turn(96_000, "Bash"), _turn(305_000, "Bash")])
    post = decide("PostToolUse", "Bash", {}, s)
    cases += [
        ("past 300k without a checkpoint, the checkpoint is demanded", bool(post) and post.get("decision") == "block"),
        ("between the lines work is not refused", decide("PreToolUse", "Bash", {}, s) is None),
        ("a checkpoint with no Size: line is refused", _denied(decide("PreToolUse", C, {"body": "Checkpoint: boundary"}, s))),
        ("a guessed Size: figure is refused", _denied(decide("PreToolUse", C, {"body": good.replace("310k", "200k")}, s))),
        ("a Size: line with no figure is refused", _denied(decide("PreToolUse", C, {"body": "Checkpoint: x\nSize: as at 01:45"}, s))),
        ("a true checkpoint passes", decide("PreToolUse", C, {"body": good}, s) is None),
        ("the Size: line is the one that opens with it, not a mention in prose",
         decide("PreToolUse", C, {"body": "Checkpoint: x\n- a `Size:` figure is refused\n- `Size: boot 96k now 305k (transcript)`"}, s) is None),
        ("a release needs no Size: line", decide("PreToolUse", C, {"body": "Checkpoint: released — link"}, s) is None),
        ("an ordinary comment is not a checkpoint", decide("PreToolUse", C, {"body": "Resumed: clean"}, s) is None),
    ]
    s = _state([_turn(96_000, "Bash"), _turn(305_000, "Bash"), _turn(310_000, C, good)])
    cases += [
        ("a checkpoint past the line stops the demand", decide("PostToolUse", "Bash", {}, s) is None),
        ("after it, work is refused", _denied(decide("PreToolUse", "Bash", {}, s))),
        ("after it, the successor may start", decide("PreToolUse", "mcp__claude-code-remote__fire_trigger", {}, s) is None),
        ("after it, a tool may be loaded", decide("PreToolUse", "ToolSearch", {}, s) is None),
    ]
    s = _state([_turn(96_000, C, good), _turn(200_000, "Bash"), _turn(352_000, "Bash")])
    cases += [
        ("a checkpoint before the line does not count", s[1] is False),
        ("past 350k every action is refused", _denied(decide("PreToolUse", "Bash", {}, s))),
        ("past 350k an edit is refused", _denied(decide("PreToolUse", "Edit", {}, s))),
        ("past 350k the successor waits on the checkpoint", _denied(decide("PreToolUse", "mcp__claude-code-remote__fire_trigger", {}, s))),
        ("past 350k the checkpoint itself passes", decide("PreToolUse", C, {"body": good.replace("310k", "352k")}, s) is None),
    ]
    cases += [
        ("an unreadable transcript blocks nothing", decide("PreToolUse", "Bash", {}, read("/nonexistent")) is None),
        ("and says so", "unknown" in json.dumps(decide("PostToolUse", "Bash", {}, None))),
    ]
    here = os.path.dirname(os.path.abspath(__file__))
    try:
        hooks = json.load(open(os.path.join(here, "settings.json"))).get("hooks", {})
        wired = all(any(h.get("matcher", "") in ("", "*") and
                        any("size.py" in (x.get("command") or "") for x in h.get("hooks", []))
                        for h in hooks.get(ev, [])) for ev in ("PreToolUse", "PostToolUse"))
    except (OSError, ValueError, AttributeError):
        wired = False
    cases.append((".claude/settings.json runs this file before and after every tool call", wired))
    for name, passed in cases:
        print(("ok: " if passed else "FAIL: ") + "size hook: " + name)
        ok = ok and passed
    return ok


def main():
    if sys.argv[1:2] == ["--selftest"]:
        sys.exit(0 if selftest() else 1)
    if sys.argv[1:2] == ["--now"]:
        p = sys.argv[2] if len(sys.argv) > 2 else newest_transcript()
        st = read(p) if p else None
        print("unknown" if st is None else f"{round(st[0] / 1000)}k (transcript)")
        return
    try:
        h = json.load(sys.stdin)
    except ValueError:
        return
    a = decide(h.get("hook_event_name"), h.get("tool_name"), h.get("tool_input"), read(h.get("transcript_path")))
    if a:
        print(json.dumps(a))


if __name__ == "__main__":
    main()
