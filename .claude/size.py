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
- Before a call, at 350,000 or more: every call is refused but the checkpoint
  itself, loading a tool (ToolSearch), and, once a checkpoint has gone through
  past 300,000, starting the successor (`library/session-changeover.md`,
  *A session starts its own successor*).
- A checkpoint counts as written only when its call went through: a refused
  or failed call (its result an error) does not. It is a comment whose first
  line opens `Checkpoint:`, posted by a comment tool. A shell command is never
  a checkpoint, so past 350k the shell is refused like everything else and the
  refusal names the comment tool.
- Before a call, at any size: a checkpoint comment without a `Size:` line
  whose `end`/`now` figure is within 20k of the real one is refused, with the
  real figure. Head office's `Checkpoint: released` carries none (that page).

The guard (his rulings of 5 November 2026 on #363: "Slim boot. A session loads
one start page plus only what its job names"; "Locks, not reminders"), only in
a repository that carries `product-reads/ticket.py` (this rulebook):

- Before a call, a `create_trigger` or `update_trigger` whose words' ticket
  fails `ticket.py check` is refused, with its faults; a `fire_trigger` is
  refused until such words have gone through in this session.
- Before a call, while a session whose first message carries a `Ticket:` is
  booting (until its `Resumed:`, `Continued:` or `Checkpoint:` comment has gone
  through), a read off the ticket is refused: a `Read` or `Grep` of a file in
  this repository other than `HOW-WE-BUILD.md`, `README.md` or a whole-file
  piece, and a shell command naming a rule page (`library/`, `juku-library/`,
  `CHARTER.md`, `AGENTS.md`, `RICH-DATA.md`) that is neither a whole-file
  piece nor, inside a `ticket.py` command, a piece's file. It does not see a
  recursive search or a read dressed as a ticket read.

An unreadable transcript blocks nothing and says so: a lock that cannot see
must not brick the session that would write the handover. The words of a
`create_trigger` or `update_trigger` are checked all the same: they are in
the call, not the transcript.

`--now [transcript]` prints the real size (newest transcript of this
directory's project when none is named). `--selftest` runs the cases below and
checks `.claude/settings.json` still wires both events to this file.
"""
import importlib.util
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
WORDS_TOOLS = ("__create_trigger", "__update_trigger")
FIRE_TOOLS = ("__fire_trigger",)

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BOOT_OPEN = ("HOW-WE-BUILD.md", "README.md")
BOOT_END_RE = re.compile(r"\A\W*(?:Resumed|Continued|Checkpoint):")
RULE_PAGE_RE = re.compile(r"(?<![\w.-])(?:\./)?((?:juku-library|library)/[\w./-]*|CHARTER\.md|AGENTS\.md|RICH-DATA\.md)")

CHECKPOINT_RE = re.compile(r"\A\W*Checkpoint:")
RELEASED_RE = re.compile(r"\A\W*Checkpoint:\s*released")
SIZE_RE = re.compile(r"(?m)^\W*Size:.*$")
FIGURE_RE = re.compile(r"\b(?:end|now)\s*~?\s*(\d+(?:\.\d+)?)\s*k\b")


def _ends(name, suffixes):
    return any(name.endswith(s) for s in suffixes)


def checkpoint_body(tool_name, tool_input):
    """The body if this call posts a checkpoint (not a release), else None."""
    tool_input = tool_input if isinstance(tool_input, dict) else {}
    if not _ends(tool_name or "", COMMENT_TOOLS):
        return None
    body = (tool_input.get("body") or "").lstrip()
    if not CHECKPOINT_RE.search(body) or RELEASED_RE.search(body):
        return None
    return body


def _text(content):
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        return "\n".join(c.get("text") or "" for c in content
                         if isinstance(c, dict) and c.get("type") == "text")
    return ""


def read(transcript_path):
    """(size, checkpointed_past_line, tool_uses, guard) or None when unreadable;
    guard = {"first": the first message's text, "booted": its boot line went
    through, "words": the newest trigger words that went through}."""
    try:
        f = open(transcript_path, encoding="utf-8")
    except (OSError, TypeError):
        return None
    size = 0
    seen = False
    checkpointed = False
    tool_uses = 0
    pending = set()   # checkpoint calls made past the line, awaiting their result
    guard = {"first": None, "booted": False, "words": None}
    boot_calls, word_calls = set(), {}
    with f:
        for raw in f:
            try:
                d = json.loads(raw)
            except ValueError:
                continue
            if d.get("isSidechain"):
                continue
            m = d.get("message")
            if not isinstance(m, dict):
                continue
            if d.get("type") == "user":
                content = m.get("content")
                if guard["first"] is None and _text(content):
                    guard["first"] = _text(content)
                for c in content if isinstance(content, list) else []:
                    if not (isinstance(c, dict) and c.get("type") == "tool_result") or c.get("is_error"):
                        continue
                    t = c.get("tool_use_id")
                    checkpointed = checkpointed or t in pending
                    guard["booted"] = guard["booted"] or t in boot_calls
                    if t in word_calls:
                        guard["words"] = word_calls[t]
                continue
            if d.get("type") != "assistant":
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
                name, inp = c.get("name") or "", c.get("input") if isinstance(c.get("input"), dict) else {}
                if _ends(name, COMMENT_TOOLS) and BOOT_END_RE.search((inp.get("body") or "").lstrip()):
                    boot_calls.add(c.get("id"))
                if _ends(name, WORDS_TOOLS) and inp.get("prompt"):
                    word_calls[c.get("id")] = inp["prompt"]
                if size >= LINE and checkpoint_body(c.get("name"), c.get("input")) is not None:
                    pending.add(c.get("id"))
    if not seen:
        return None
    return size, checkpointed, tool_uses, guard


# ---- the guard --------------------------------------------------------------

def _ticket():
    """This repository's ticket.py, or None where it carries none (a product)."""
    p = os.path.join(ROOT, "product-reads", "ticket.py")
    if not os.path.isfile(p):
        return None
    sys.dont_write_bytecode = True   # check.sh admits no __pycache__ beside it
    try:
        spec = importlib.util.spec_from_file_location("ticket", p)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return mod
    except Exception:
        return None


def words_faults(words, tk):
    faults, _ = tk.check(words or "", {tk.RULEBOOK: ROOT})
    return faults


def _rel(path):
    """A path's place in this repository, or None outside it."""
    if not path:
        return None
    full = os.path.realpath(path if os.path.isabs(path) else os.path.join(os.getcwd(), path))
    if full != ROOT and os.path.commonpath([ROOT, full]) != ROOT:
        return None
    return os.path.relpath(full, ROOT)


def off_ticket(tool_name, tool_input, entries, tk):
    """Why this call reads off the ticket at boot, or None."""
    pieces = [tk.split(e) for e in entries if tk.split(e)[0] == tk.RULEBOOK]
    whole = {os.path.normpath(p) for _, p, a in pieces if not a}
    files = {os.path.normpath(p) for _, p, _ in pieces}
    open_ = whole | set(BOOT_OPEN)
    if tool_name == "Read":
        r = _rel(tool_input.get("file_path"))
        if r is not None and os.path.normpath(r) not in open_:
            return r
    elif tool_name == "Grep":
        r = _rel(tool_input.get("path") or os.getcwd())
        if r is not None and os.path.normpath(r) not in open_:
            return r
    elif tool_name == "Bash":
        cmd = tool_input.get("command") or ""
        for m in RULE_PAGE_RE.finditer(cmd):
            p = os.path.normpath(m.group(1).rstrip("/.") or m.group(1))
            if p in whole or ("ticket.py" in cmd and p in files):
                continue
            return m.group(1)
    return None


def guard(event, tool_name, tool_input, state, tk):
    """The guard's refusal, or None."""
    if tk is None or event != "PreToolUse":
        return None
    name = tool_name or ""
    if _ends(name, WORDS_TOOLS) and "prompt" in tool_input:
        faults = words_faults(tool_input.get("prompt"), tk)
        if faults:
            return _deny("size hook: these task words' ticket fails `product-reads/ticket.py check` "
                         "(library/session-changeover.md, *The ticket*): " + "; ".join(faults))
        return None
    if state is None:
        return None
    g = state[3]
    if _ends(name, FIRE_TOOLS):
        if g["words"] is None or words_faults(g["words"], tk):
            return _deny("size hook: a successor is fired only after `update_trigger` has gone through in this "
                         "session with words whose ticket passes `product-reads/ticket.py check` "
                         "(library/session-changeover.md, *The ticket*)")
        return None
    entries = tk.ticket_lines(g["first"] or "")
    if entries is None or g["booted"]:
        return None
    what = off_ticket(name, tool_input, entries, tk)
    if what is None:
        return None
    return _deny(f"size hook: `{what}` is off this session's ticket. At boot it reads `HOW-WE-BUILD.md`, the README "
                 f"and its ticket's pieces (`python3 product-reads/ticket.py --repo how-we-build=. read <address>`); "
                 f"post `Resumed:` first, then take the read and name it in your next checkpoint as "
                 f"`Added: <address> — <why>` (library/session-changeover.md, *The ticket*)")


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


def decide(event, tool_name, tool_input, state, tk=None):
    """The hook's JSON answer, or None to stay silent."""
    tool_input = tool_input if isinstance(tool_input, dict) else {}
    refused = guard(event, tool_name, tool_input, state, tk)
    if refused:
        return refused
    if state is None:
        if event == "PostToolUse":
            return {"hookSpecificOutput": {"hookEventName": "PostToolUse",
                    "additionalContext": "size hook: the transcript could not be read; size unknown, nothing blocked"}}
        return None
    size, checkpointed, tool_uses = state[:3]
    k = f"{round(size / 1000)}k"
    if event == "PreToolUse":
        body = checkpoint_body(tool_name, tool_input)
        if body is not None:
            why = size_problem(body, size)
            return _deny(why) if why else None
        if size < HARD or tool_name in ALWAYS:
            return None
        if checkpointed and _ends(tool_name or "", SUCCESSOR_TOOLS):
            return None
        if checkpointed:
            return _deny(f"size hook: {k}, past the hard stop of 350k with the checkpoint written; the only "
                         f"actions left are starting the successor (create/update/fire_trigger) and ending the turn")
        return _deny(f"size hook: {k}, past the hard stop of 350k; every action is refused but writing "
                     f"the handover checkpoint, posted with the issue-comment tool (`add_issue_comment`), its first line `Checkpoint:`, with its `Size:` line")
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

def _turn(n, tool=None, body=None, sidechain=False, id=None):
    content = []
    if tool:
        content.append({"type": "tool_use", "id": id or "t" + str(n), "name": tool,
                        "input": {"body": body} if body is not None else {}})
    return json.dumps({"type": "assistant", "isSidechain": sidechain, "message": {
        "content": content,
        "usage": {"input_tokens": 2, "cache_creation_input_tokens": 1000,
                  "cache_read_input_tokens": n - 1002 - 10, "output_tokens": 10}}})


def _result(id, error=False):
    return json.dumps({"type": "user", "message": {"content": [
        {"type": "tool_result", "tool_use_id": id, "is_error": error, "content": "x"}]}})


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
    cases += [
        ("a comment quoting the format is not a checkpoint",
         decide("PreToolUse", C, {"body": "Round 2.\n- `Checkpoint: boundary — …` is the shape"}, s) is None),
        ("a shell command is never a checkpoint, even one naming one", decide("PreToolUse", "Bash",
         {"command": "gh api repos/x/y/issues/363/comments --jq 'Checkpoint:'"}, s) is None),
    ]
    s = _state([_turn(96_000, "Bash"), _turn(305_000, "Bash"), _turn(310_000, C, good, id="cp"), _result("cp")])
    cases += [
        ("a checkpoint past the line stops the demand", decide("PostToolUse", "Bash", {}, s) is None),
        ("after it, below 350k, work is not refused", decide("PreToolUse", "Bash", {}, s) is None),
    ]
    s = _state([_turn(96_000, "Bash"), _turn(305_000, "Bash"), _turn(310_000, C, good, id="cp"), _result("cp", error=True)])
    cases.append(("a refused or failed checkpoint is not written", s[1] is False and
                  bool(decide("PostToolUse", "Bash", {}, s))))
    s = _state([_turn(96_000, "Bash"), _turn(310_000, C, good, id="cp"), _result("cp"), _turn(351_000, "Bash")])
    cases += [
        ("past 350k after it, work is refused", _denied(decide("PreToolUse", "Bash", {}, s))),
        ("past 350k a shell command that posts a checkpoint is still refused", _denied(decide("PreToolUse", "Bash",
         {"command": "make && gh issue comment 363 --body 'Checkpoint: x\nSize: end 351k'"}, s))),
        ("past 350k after it, the successor may start", decide("PreToolUse", "mcp__claude-code-remote__fire_trigger", {}, s) is None),
        ("past 350k after it, a tool may be loaded", decide("PreToolUse", "ToolSearch", {}, s) is None),
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
    ok = _guard_cases(cases)
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


def _first(text):
    return json.dumps({"type": "user", "isMeta": True, "message": {"content": text}})


def _call(n, tool, inp, id):
    return json.dumps({"type": "assistant", "message": {
        "content": [{"type": "tool_use", "id": id, "name": tool, "input": inp}],
        "usage": {"input_tokens": n, "output_tokens": 0}}})


def _guard_cases(cases):
    """The guard's cases, on this repository's own ticket.py and pages; True when it holds them."""
    tk = _ticket()
    if tk is None:
        cases.append(("this repository carries product-reads/ticket.py for the guard", False))
        return True
    U, F, C = "mcp__claude-code-remote__update_trigger", "mcp__claude-code-remote__fire_trigger", "mcp__github__add_issue_comment"
    good = "Words.\nTicket:\n- " + tk.OWN + "\n- how-we-build:.claude/size.py\n\nMore words.\n"
    bad = "Words.\nTicket:\n- " + tk.OWN + "\n- how-we-build:library/session-changeover.md#No such piece\n"
    s0 = _state([_turn(96_000, "Bash")])
    cases += [
        ("task words whose ticket passes go through", decide("PreToolUse", U, {"prompt": good}, s0, tk) is None),
        ("task words whose ticket fails are refused", _denied(decide("PreToolUse", U, {"prompt": bad}, s0, tk))),
        ("task words with no ticket are refused", _denied(decide("PreToolUse", U, {"prompt": "Build."}, s0, tk))),
        ("and refused with an unreadable transcript too", _denied(decide("PreToolUse", U, {"prompt": bad}, None, tk))),
        ("a trigger change without words is not checked", decide("PreToolUse", U, {"enabled": False}, s0, tk) is None),
        ("a fire with no words gone through is refused", _denied(decide("PreToolUse", F, {}, s0, tk))),
        ("a product, carrying no ticket.py, is not guarded", decide("PreToolUse", U, {"prompt": bad}, s0, None) is None),
    ]
    s = _state([_turn(96_000, "Bash"), _call(97_000, U, {"prompt": good}, "u1"), _result("u1")])
    cases.append(("a fire after checked words went through passes", decide("PreToolUse", F, {}, s, tk) is None))
    s = _state([_turn(96_000, "Bash"), _call(97_000, U, {"prompt": good}, "u1"), _result("u1", error=True)])
    cases.append(("a fire after a refused rewrite is refused", _denied(decide("PreToolUse", F, {}, s, tk))))
    boot = [_first("Do the job.\n" + good), _turn(96_000, "Bash")]
    s = _state(boot)
    lib = os.path.join(ROOT, "library", "reviewer.md")
    piece = "python3 product-reads/ticket.py --repo how-we-build=. read '" + tk.OWN + "'"
    cases += [
        ("at boot a library page off the ticket is refused to Read", _denied(decide("PreToolUse", "Read", {"file_path": lib}, s, tk))),
        ("at boot the start page is read", decide("PreToolUse", "Read", {"file_path": os.path.join(ROOT, "HOW-WE-BUILD.md")}, s, tk) is None),
        ("at boot a whole-file piece is read", decide("PreToolUse", "Read", {"file_path": os.path.join(ROOT, ".claude", "size.py")}, s, tk) is None),
        ("at boot a file outside the repository is read", decide("PreToolUse", "Read", {"file_path": "/tmp/x.txt"}, s, tk) is None),
        ("at boot a search of the repository is refused", _denied(decide("PreToolUse", "Grep", {"pattern": "x"}, s, tk))),
        ("at boot a shell read of a rule page is refused", _denied(decide("PreToolUse", "Bash", {"command": "sed -n 1,9p library/reviewer.md"}, s, tk))),
        ("at boot the archive is refused", _denied(decide("PreToolUse", "Bash", {"command": "cat juku-library/DECISION-0021.md"}, s, tk))),
        ("at boot a ticket piece is read with ticket.py", decide("PreToolUse", "Bash", {"command": piece}, s, tk) is None),
        ("at boot ticket.py off the ticket is refused", _denied(decide("PreToolUse", "Bash",
         {"command": "python3 product-reads/ticket.py read how-we-build:library/reviewer.md#Who"}, s, tk))),
        ("at boot a shell read of the start page passes", decide("PreToolUse", "Bash", {"command": "cat HOW-WE-BUILD.md README.md"}, s, tk) is None),
    ]
    s = _state(boot + [_call(97_000, C, {"body": "Resumed: clean"}, "r1"), _result("r1")])
    cases.append(("after Resumed: went through, a read off the ticket passes", decide("PreToolUse", "Read", {"file_path": lib}, s, tk) is None))
    s = _state(boot + [_call(97_000, C, {"body": "Resumed: clean"}, "r1"), _result("r1", error=True)])
    cases.append(("a refused Resumed: does not end the boot", _denied(decide("PreToolUse", "Read", {"file_path": lib}, s, tk))))
    s = _state([_first("Do the job, no ticket."), _turn(96_000, "Bash")])
    cases.append(("a session with no ticket is not guarded at boot", decide("PreToolUse", "Read", {"file_path": lib}, s, tk) is None))
    return True


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
    a = decide(h.get("hook_event_name"), h.get("tool_name"), h.get("tool_input"),
               read(h.get("transcript_path")), _ticket())
    if a:
        print(json.dumps(a))


if __name__ == "__main__":
    main()
