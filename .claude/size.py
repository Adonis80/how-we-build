#!/usr/bin/env python3
"""The size hook: a session's real size, read from its own transcript.

His rulings of 5 November 2026 (issue #363, "Locks, not reminders"): "Hard stop
at 350,000 tokens, by machine. A hook reads the session's own transcript usage
(the real figure, not an estimate) after every tool call: at 300,000 it
requires the handover checkpoint; at 350,000 it blocks every action except
writing that checkpoint. Every checkpoint carries a size line." His word of
12 November 2026, 00:19:58 UTC, agreeing the lead builder's fixes for a monitor
that "sometimes fires and sometimes doesn't fire" (Adonis80/Hemz-OS#333, comment
6810454648, item 4): "I agree with all of your suggestions": the checkpoint line
at 280k, a warn band from 250k, a look at the end of every turn, and blind fails
closed.

`.claude/settings.json` runs this file before (PreToolUse) and after
(PostToolUse) every tool call, and at the end of every turn (Stop), so a turn
that makes no tool call is measured too. The size is the context of the newest
main-thread model turn in the transcript: its input, cache-write, cache-read
and output tokens, as the model's own usage reports them.

- After a call, from 250,000: the session is warned, on every call, that the
  line is near. At 280,000 or more with no checkpoint written since the line
  was crossed: the session is told, on every call until it writes one, to write
  its handover checkpoint now.
- At the end of a turn, the same: past 280,000 with no checkpoint the turn is
  kept going to write it (once: a turn already kept going ends, so a checkpoint
  that cannot be posted never loops), and from 250,000 the person is warned.
- The successor lock (his word, 12 November 2026, about 09:25 UTC: "Yes, I agree
  to all of your fixes implement them now while I evaluate the app", after a
  session checkpointed at 280k on Adonis80/Hemz-OS#333 and ended starting none):
  once a checkpoint has gone through past 280,000, a turn's end is kept going,
  once, until a successor start has gone through after it (`fire_trigger`, or
  `create_session`) or a checkpoint past the line carrying
  `Successor: none — <reason>` has, the reason being nothing ready, the platform
  refused (naming what), or blind. Before a call, at any size, a checkpoint
  whose `Successor:` line gives any other reason is refused.
- Each of the two is asked once in a run of kept-going ends, by the hook's own
  record of what it asked there (`~/.claude/size-hook-stops`, per transcript),
  not by the platform's `stop_hook_active`, which is one flag for every stop
  hook: a turn kept going to write its checkpoint, or by another hook, is still
  asked for its successor (Adonis80/Hemz-OS#363's read: the shared flag let a
  checkpoint first written in a kept-going turn end with no successor). Kept
  going, it asks only what it has first recorded, so nothing is asked twice;
  where the record cannot be read or kept, a turn already kept going ends.
- Before a call, at 350,000 or more: every call is refused but the checkpoint
  itself, loading a tool (ToolSearch), and, once a checkpoint has gone through
  past 280,000, starting the successor (`library/session-changeover.md`,
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
one start page plus only what its job names"; "Locks, not reminders"), only where
the rulebook's `product-reads/ticket.py` is reachable: in this rulebook, or in a
product whose session has the rulebook cloned beside it as `how-we-build`. It
knows a product's clone by the name the README's map gives it (a `hemz-os`
directory is `Hemz-OS`), beside this repository or the rulebook's clone:

- Before a call, a `create_trigger` or `update_trigger` whose words' ticket
  fails `ticket.py check` is refused, with its faults; a `fire_trigger` is
  refused until such words have gone through in this session.
- Before a call, while a session whose first message carries a `Ticket:` is
  booting (until its `Resumed:`, `Continued:` or `Checkpoint:` comment has gone
  through), a read off the ticket is refused: a `Read` or `Grep` of a file in
  a clone it knows other than the rulebook's `HOW-WE-BUILD.md` and `README.md`
  or a whole-file piece, and a shell command naming a rule page (`library/`,
  `juku-library/`, `CHARTER.md`, `AGENTS.md`, `RICH-DATA.md`) or a product's
  `PRODUCT.md`, `roadmap.json` or `MAP.md` that is neither a whole-file piece
  nor, inside a `ticket.py` command, a piece's file. It does not see a
  recursive search or a read dressed as a ticket read.

The clock lock (#378, agreed on #371, 6 November 2026; his root on #363, "Locks,
not reminders"; library/session-changeover.md: "A task with a repeat or a run
time is a clock and never wakes a session"), wherever this file runs:

- Before a call, a `create_trigger` or `update_trigger` carrying a
  `cron_expression` or `run_once_at` is refused.
- Before a call, a `fire_trigger` is refused unless the newest thing this
  session saw of that task shows it with neither: a `create_trigger` that went
  through (its input, or its result where that reports the fields), an
  `update_trigger` whose result reports both fields empty, or a
  `list_triggers` entry for it with both empty. An update's input is never
  evidence, since an update that omits the fields can leave an old schedule
  standing; one whose result is silent on them leaves the task unknown.

The boot measured (his ruling, 5 November 2026, 18:15, on #363, "I agree to
your upgrade": every fresh session, before any work, posts one line on its
issue, its starting size split into what the platform loads and what we made
it read, ours under 30k; over target, the line names the three heaviest
pieces), in the same repositories as the guard:

- Before a call, the session's first `Resumed:` or `Continued:` comment is
  refused unless it carries a `Boot:` line whose figures are the hook's own:
  `ours` is every tool result the session read before it (bytes / 4, a
  loaded tool's schema excepted), `platform` the rest of its real size; past
  30k ours, the line names its three heaviest reads. The refusal hands the
  line to paste, so no session rounds or skips it. A hook cannot post a
  comment itself; it holds the one the session must post.

The size is read from the transcript the platform names in each call's own
`transcript_path`, never found by the working directory, which a session can
leave. A session it cannot measure (no `transcript_path`, a file that will not
open, one with no usage in it, or a hook that raises) fails closed: before a call,
everything is refused until it can see but the checkpoint, loading a tool, and
the repair of the hook itself (reading or editing `.claude/size.py` or
`.claude/settings.json`, or a command that is a run of `.claude/size.py` and
nothing else; the hook runs from the working tree, so a repair there lets the
same session see again). A hook that cannot run at all (a file that will not
compile, or input that is not a JSON object) fails open: the platform runs the
call, so a broken repair is caught by `--selftest` before anything is pushed. Starting a successor is refused too: it would
be as blind, so a blindness every session shares stops at one checkpoint for the
person to see, never a chain. After every call and at the end of a turn it tells
the session, and the person, that it is blind and why. A call's own turn is in
the transcript before its hook runs (shown on 12 November 2026), so a fresh
session's first call is measured, not blind. The words of a
`create_trigger` or `update_trigger` are checked all the same: they are in
the call, not the transcript.

`--install` wires this file at user level (a link at `~/.claude/size.py`, the three events in `~/.claude/settings.json`), for the environment's setup script, so it runs whatever the working directory; `--user` is that wiring's run, quiet where the project already wires the hook. `--now [transcript]` prints the real size (when none is named, the transcript
the hook was last given, which the hook's own call for that command records);
when it cannot measure, it says why and exits 1. `--selftest` runs the cases below and
checks `.claude/settings.json` still wires all three events to this file.
"""
import importlib.util
import json
import os
import re
import sys
import tempfile

WARN = 250_000      # the session and the person are warned
LINE = 280_000      # the handover checkpoint is required
HARD = 350_000      # everything but the checkpoint is refused
SLACK_K = 20        # a Size: line's figure may sit this many k off the real one

COMMENT_TOOLS = ("__add_issue_comment", "__update_issue_comment")
START_TOOLS = ("__fire_trigger", "__create_session")   # a successor start, for the successor lock
SUCCESSOR_TOOLS = ("__create_trigger", "__update_trigger", "__fire_trigger", "__list_triggers")
ALWAYS = ("ToolSearch",)
WORDS_TOOLS = ("__create_trigger", "__update_trigger")
LIST_TOOLS = ("__list_triggers",)
FIRE_TOOLS = ("__fire_trigger",)
CLOCK_KEYS = ("cron_expression", "run_once_at")
TRIG_RE = re.compile(r"\btrig_[A-Za-z0-9]+")

NOTE = os.path.join(os.path.expanduser("~"), ".claude", "size-hook-transcript")   # the last transcript_path given
STOPS = os.path.join(os.path.expanduser("~"), ".claude", "size-hook-stops")   # per transcript, what its run of kept-going ends was asked
ROOT = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
BOOT_OPEN = ("HOW-WE-BUILD.md", "README.md")
TICKET_RE = re.compile(r"(?m)^\s*Ticket:\s*$")
BOOT_END_RE = re.compile(r"\A\W*(?:Resumed|Continued|Checkpoint):")
BOOT_LINE_RE = re.compile(r"\A\W*(?:Resumed|Continued):")
BOOT_RE = re.compile(r"(?m)^\W*Boot:.*$")
OURS_TARGET = 30_000   # what we make a fresh session read (his ruling, 5 November 2026, 18:15)
OURS_SLACK = 3_000     # a Boot: line's ours figure may sit this far off the hook's
NOT_OURS = ("ToolSearch",)   # a loaded tool's schema is the platform's
RULE_PAGE_RE = re.compile(r"(?<![\w.-])(?:\./)?((?:[\w]+(?:-[\w]+)*-library|library)/[\w./-]*|CHARTER\.md|AGENTS\.md|RICH-DATA\.md"
                          r"|PRODUCT\.md|roadmap\.json|MAP\.md)")

CHECKPOINT_RE = re.compile(r"\A\W*Checkpoint:")
RELEASED_RE = re.compile(r"\A\W*Checkpoint:\s*released")
SIZE_RE = re.compile(r"(?m)^\W*Size:.*$")
SUCCESSOR_RE = re.compile(r"(?m)^\W*Successor:.*$")
NONE_RE = re.compile(r"\A\W*Successor:\s*none\s*[—–-]+\s*(?:nothing ready\b|(?:the )?platform refused\s+\w|blind\b)", re.I)
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


def successor_problem(body):
    """Why a checkpoint body's Successor: line fails, or None (no line, or a good one)."""
    line = SUCCESSOR_RE.search(body)
    if line is None or NONE_RE.search(line.group(0)):
        return None
    return ("size hook: a checkpoint's `Successor:` line says why none starts: `Successor: none — nothing ready`, "
            "`Successor: none — the platform refused <what>`, or `Successor: none — blind` "
            "(library/session-changeover.md, *A session starts its own successor*); a started successor needs no line")


def names_none(body):
    """True when a checkpoint body carries a good `Successor: none — <reason>` line."""
    line = SUCCESSOR_RE.search(body or "")
    return line is not None and NONE_RE.search(line.group(0)) is not None


def _text(content):
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        return "\n".join(c.get("text") or "" for c in content
                         if isinstance(c, dict) and c.get("type") == "text")
    return ""


def read(transcript_path):
    """(size, checkpointed_past_line, tool_uses, guard, succeeded) or None when unreadable;
    succeeded: after that checkpoint, a successor start went through, or a checkpoint past the line
    carrying `Successor: none — <reason>` did;
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
    succeeded = False
    starts = set()    # successor starts after it, and checkpoints naming none, awaiting their result
    guard = {"first": None, "booted": False, "words": None, "reads": [], "tasks": {}}
    boot_calls, word_calls, labels, task_calls = set(), {}, {}, {}
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
                # the task's words: the first message before any reply that carries a Ticket: line,
                # so a note or caveat the surface puts first does not hide it
                if guard["first"] is None and not tool_uses and not seen and TICKET_RE.search(_text(content)):
                    guard["first"] = _text(content)
                for c in content if isinstance(content, list) else []:
                    if not (isinstance(c, dict) and c.get("type") == "tool_result"):
                        continue
                    if c.get("is_error"):
                        labels.pop(c.get("tool_use_id"), None)
                        continue
                    t = c.get("tool_use_id")
                    if not guard["booted"] and t in labels:
                        body = _text(c.get("content")) or json.dumps(c.get("content"))
                        guard["reads"].append(((len(body.encode("utf-8")) + 3) // 4, labels.pop(t)))
                    checkpointed = checkpointed or t in pending
                    succeeded = succeeded or t in starts
                    guard["booted"] = guard["booted"] or t in boot_calls
                    if t in word_calls:
                        guard["words"] = word_calls[t]
                    if t in task_calls:
                        _task_state(guard["tasks"], task_calls.pop(t), _text(c.get("content")) or json.dumps(c.get("content")))
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
                if not guard["booted"] and name not in NOT_OURS:
                    labels[c.get("id")] = _label(name, inp)
                if _ends(name, COMMENT_TOOLS) and BOOT_END_RE.search((inp.get("body") or "").lstrip()):
                    boot_calls.add(c.get("id"))
                if _ends(name, WORDS_TOOLS + LIST_TOOLS):
                    task_calls[c.get("id")] = dict(inp, _tool=name)
                if _ends(name, WORDS_TOOLS) and inp.get("prompt"):
                    word_calls[c.get("id")] = inp["prompt"]
                if size >= LINE and checkpoint_body(c.get("name"), c.get("input")) is not None:
                    pending.add(c.get("id"))
                    if names_none(checkpoint_body(c.get("name"), c.get("input"))):
                        starts.add(c.get("id"))
                if (checkpointed or pending) and _ends(name, START_TOOLS):   # after the checkpoint, or beside it in one turn
                    starts.add(c.get("id"))
    if not seen:
        return None
    return size, checkpointed, tool_uses, guard, succeeded


def clock_in(inp):
    """The clock fields a trigger call's input sets."""
    return [k for k in CLOCK_KEYS if inp.get(k)]


def _own(text, tid):
    """The task's own object in a trigger call's result, when the result is JSON and has one with any clock field."""
    try:
        data = json.loads(text)
    except ValueError:
        return None
    stack = [data]
    while stack:
        x = stack.pop()
        if isinstance(x, dict):
            if x.get("id") == tid and any(k in x for k in CLOCK_KEYS):
                return x
            stack.extend(x.values())
        elif isinstance(x, list):
            stack.extend(x)
    return None


def _clock_in_result(text, tid=None):
    """The clock fields a trigger call's result reports set; [] when it reports both, empty; else None.
    The task's own object, where the result has one, decides alone: a field it reports is read, and one it
    omits is unset, since the platform's result leaves an unset field out (update_trigger, 6 November 2026:
    `"cron_expression": ""` and no `run_once_at`)."""
    own = _own(text, tid) if tid else None
    if own is not None:
        return [k for k in CLOCK_KEYS if own.get(k)]
    try:
        found = {}
        def walk(x):
            if isinstance(x, dict):
                for k, v in x.items():
                    if k in CLOCK_KEYS:
                        found[k] = found.get(k) or bool(v)
                    walk(v)
            elif isinstance(x, list):
                for v in x:
                    walk(v)
        walk(json.loads(text))
    except ValueError:
        found = {}
        for k, v in re.findall(r'"?(cron_expression|run_once_at)"?\s*[:=]\s*("[^"]*"|[^,}\s]+)', text):
            found[k] = found.get(k) or v.strip('"') not in ("", "null", "None")
    set_ = sorted(k for k, v in found.items() if v)
    # a clock reported set is a clock; clear only when both are reported, and empty
    return set_ if set_ or len(found) == len(CLOCK_KEYS) else None


def _listed(tasks, result):
    """Each task a list_triggers result shows, with the clock fields it reports."""
    try:
        data = json.loads(result)
    except ValueError:
        return
    def walk(x):
        if isinstance(x, dict):
            if isinstance(x.get("id"), str) and x["id"].startswith("trig_") and all(k in x for k in CLOCK_KEYS):
                tasks[x["id"]] = [k for k in CLOCK_KEYS if x.get(k)]
            for v in x.values():
                walk(v)
        elif isinstance(x, list):
            for v in x:
                walk(v)
    walk(data)


def _task_state(tasks, inp, result):
    """Record a trigger call that went through: its task's clock where the call shows it, else unknown (None).
    A create's input is the whole task; an update's is not, so only its result counts."""
    tool = inp.get("_tool") or ""
    if _ends(tool, LIST_TOOLS):
        _listed(tasks, result)
        return
    tid = inp.get("trigger_id")
    if not tid:
        try:
            tid = json.loads(result).get("trigger", {}).get("id")
        except (ValueError, AttributeError):
            tid = None
        m = None if tid else TRIG_RE.search(result)
        tid = tid or (m.group(0) if m else None)
    if tid:
        shown = _clock_in_result(result, tid)
        if shown is None and _ends(tool, ("__create_trigger",)):
            shown = clock_in(inp)
        tasks[tid] = shown


def clock(tool_name, tool_input, state):
    """The clock lock's refusal, or None."""
    name = tool_name or ""
    if _ends(name, WORDS_TOOLS):
        set_ = clock_in(tool_input)
        if set_:
            return _deny(f"size hook: a standing task never carries a clock (`{'`, `'.join(set_)}`): no repeat, no run "
                         f"time; it is fired with `fire_trigger` (library/session-changeover.md, *A session starts its own "
                         f"successor*; #378). Drop the field")
        return None
    if not _ends(name, FIRE_TOOLS) or state is None:
        return None
    tid = tool_input.get("trigger_id")
    known = state[3]["tasks"].get(tid)
    if known is None:
        return _deny(f"size hook: `{tid}` is fired only once this session has seen it carry no `cron_expression` or "
                     f"`run_once_at`: an `update_trigger` result reporting both empty, or a `list_triggers` entry for it "
                     f"showing both empty (an update's own words are no evidence: one that omits them leaves an old "
                     f"schedule standing; #378)")
    if known:
        return _deny(f"size hook: `{tid}` still carries a clock (`{'`, `'.join(known)}`), and a task with one never "
                     f"wakes a session (library/session-changeover.md; #378). Clear it with `update_trigger` first")
    return None


def _label(name, inp):
    """A read's name in a Boot: line: its command, file or tool and target."""
    if name == "Bash":
        return "`" + (inp.get("command") or "").strip().split("\n")[0][:60] + "`"
    if inp.get("file_path"):
        return name + " " + (_rel(inp["file_path"]) or inp["file_path"])
    short = name.split("__")[-1]
    target = [str(inp[k]) for k in ("method", "issue_number", "pullNumber") if inp.get(k) is not None]
    return " ".join([short] + target)


def boot_line(state):
    """The Boot: line the hook's own figures make."""
    size, reads = state[0], state[3]["reads"]
    ours = sum(n for n, _ in reads)
    k = lambda n: f"{round(n / 1000)}k"
    line = f"Boot: platform {k(size - ours)}, ours {k(ours)} (transcript; ours = what we made it read)"
    if ours > OURS_TARGET:
        top = sorted(reads, key=lambda r: -r[0])[:3]
        line += "; over 30k, heaviest: " + ", ".join(f"{l} {k(n)}" for n, l in top)
    return line


def boot_problem(body, state):
    """Why a first Resumed:/Continued: comment's Boot: line fails, or None."""
    want = boot_line(state)
    line = BOOT_RE.search(body)
    fig = lambda w, t: re.search(w + r"\s*~?\s*(\d+(?:\.\d+)?)\s*k\b", t)
    ours = sum(n for n, _ in state[3]["reads"])
    if line:
        p, o = fig("platform", line.group(0)), fig("ours", line.group(0))
        if (p and o and abs(float(p.group(1)) * 1000 - (state[0] - ours)) <= SLACK_K * 1000
                and abs(float(o.group(1)) * 1000 - ours) <= OURS_SLACK
                and (ours <= OURS_TARGET or "heaviest" in line.group(0))):
            return None
    return ("size hook: a fresh session's first `Resumed:` or `Continued:` carries its boot measured, split "
            "into the platform's share and ours (his ruling, 5 November 2026, 18:15, #363; "
            "library/session-changeover.md, *The ticket*). Put this line in it as it stands: " + want)


# ---- the guard --------------------------------------------------------------

def _rulebook_root():
    """The rulebook's clone: this repository when it carries ticket.py, else a how-we-build
    clone beside it (a product's session with the rulebook attached), else None."""
    has = lambda d: os.path.isfile(os.path.join(d, "product-reads", "ticket.py"))
    if has(ROOT):
        return ROOT
    up = os.path.dirname(ROOT)
    try:
        names = sorted(os.listdir(up))
    except OSError:
        return None
    return next((os.path.join(up, n) for n in names if n.lower() == "how-we-build" and has(os.path.join(up, n))), None)


def _ticket():
    """The rulebook's ticket.py, or None where none is reachable (a product without the rulebook beside it)."""
    rb = _rulebook_root()
    if rb is None:
        return None
    p = os.path.join(rb, "product-reads", "ticket.py")
    sys.dont_write_bytecode = True   # check.sh admits no __pycache__ beside it
    try:
        spec = importlib.util.spec_from_file_location("ticket", p)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return mod
    except Exception:
        return None


def _repos(tk):
    """Each clone the guard can see, by the name a ticket gives it: the rulebook's, and each
    product on its README's map cloned beside this repository or the rulebook's clone."""
    rb = _rulebook_root() or ROOT
    repos = {tk.RULEBOOK: rb}
    names = {p.lower(): p for p in tk.products(rb)}
    if os.path.realpath(ROOT) != os.path.realpath(rb) and os.path.basename(ROOT).lower() in names:
        repos[names[os.path.basename(ROOT).lower()]] = ROOT
    for up in (os.path.dirname(ROOT), os.path.dirname(rb)):
        try:
            found = sorted(os.listdir(up))
        except OSError:
            continue
        for n in found:
            if n.lower() in names and os.path.isdir(os.path.join(up, n)):
                repos.setdefault(names[n.lower()], os.path.join(up, n))
    return repos


def words_faults(words, tk):
    faults, _ = tk.check(words or "", _repos(tk))
    return faults


def _rel(path, root=None):
    """A path's place in a clone (this repository by default), or None outside it."""
    root = os.path.realpath(root or ROOT)
    if not path:
        return None
    full = os.path.realpath(path if os.path.isabs(path) else os.path.join(os.getcwd(), path))
    if full != root and os.path.commonpath([root, full]) != root:
        return None
    return os.path.relpath(full, root)


def _where(path, repos):
    """(the clone's name, the path inside it) for a path in one of the session's clones, or None."""
    for name, root in repos.items():
        r = _rel(path, root)
        if r is not None:
            return name, os.path.normpath(r)
    return None


def off_ticket(tool_name, tool_input, entries, tk):
    """Why this call reads off the ticket at boot, or None."""
    repos = _repos(tk)
    pieces = [tk.split(e) for e in entries if tk.split(e)[0] in repos]
    open_ = {name: {os.path.normpath(p) for r, p, a in pieces if r == name and not a} for name in repos}
    open_[tk.RULEBOOK] |= set(BOOT_OPEN)
    whole = set().union(*open_.values()) - set(BOOT_OPEN)
    files = {os.path.normpath(p) for _, p, _ in pieces}
    if tool_name in ("Read", "Grep"):
        w = _where(tool_input.get("file_path") if tool_name == "Read" else (tool_input.get("path") or os.getcwd()), repos)
        if w is not None and w[1] not in open_[w[0]]:
            return w[0] + ":" + w[1]
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
                 f"and its ticket's pieces (the rulebook's `python3 product-reads/ticket.py --repo <name>=<clone> read <address>`); "
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


def owed(state, kept=False, asked=None):
    """What a turn's end is kept going for: "checkpoint", "successor" or None. Each is asked once in a
    run of kept-going ends, by the hook's own record of what it has asked there (`asked`), never by
    the platform's one flag for every stop hook (`kept`): a turn kept going to write its checkpoint,
    or by another hook, has not yet been asked for its successor. Kept going with no record,
    everything counts as asked, so nothing loops."""
    size, checkpointed = state[:2]
    want = "checkpoint" if size >= LINE and not checkpointed else "successor" if checkpointed and not state[4] else None
    return None if kept and (not isinstance(asked, list) or want in asked) else want


def asked_at(path, stops=STOPS):
    """What the hook has asked in the run of kept-going ends this transcript is in, or None with no record."""
    try:
        with open(stops, encoding="utf-8") as f:
            a = json.load(f).get(path)
    except (OSError, ValueError, AttributeError):
        return None
    return a if isinstance(a, list) else None


def keep_asked(path, asked, stops=STOPS):
    """Record it, newest last, twenty transcripts at most; False when it could not be kept."""
    try:
        with open(stops, encoding="utf-8") as f:
            d = json.load(f)
    except (OSError, ValueError):
        d = {}
    d = {p: a for p, a in d.items() if p != path} if isinstance(d, dict) else {}
    d[path] = asked
    try:
        with open(stops + ".new", "w", encoding="utf-8") as f:
            json.dump(dict(list(d.items())[-20:]), f)
        os.replace(stops + ".new", stops)
    except OSError:
        return False
    return True


def decide(event, tool_name, tool_input, state, tk=None, blind=None):
    """The hook's JSON answer, or None to stay silent."""
    tool_input = tool_input if isinstance(tool_input, dict) else {}
    refused = clock(tool_name, tool_input, state) if event == "PreToolUse" else None
    if refused:
        return refused
    refused = guard(event, tool_name, tool_input, state, tk)
    if refused:
        return refused
    if state is None:
        msg = blind_message(blind or "the transcript could not be read")
        if event == "PreToolUse":
            return None if blind_allows(tool_name, tool_input) else _deny(msg)
        if event == "PostToolUse":
            return {"decision": "block", "reason": msg, "systemMessage": msg}
        return {"systemMessage": msg} if event == "Stop" else None
    size, checkpointed, tool_uses = state[:3]
    k = f"{round(size / 1000)}k"
    if (event == "PreToolUse" and tk is not None and not state[3]["booted"]
            and _ends(tool_name or "", COMMENT_TOOLS)
            and BOOT_LINE_RE.search((tool_input.get("body") or "").lstrip())):
        why = boot_problem(tool_input.get("body") or "", state)
        if why:
            return _deny(why)
    if event == "PreToolUse":
        body = checkpoint_body(tool_name, tool_input)
        if body is not None:
            why = size_problem(body, size) or successor_problem(body)
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
    demand = (f"size hook: {k}, past the 280k line. Write the handover checkpoint now "
              f"(`Checkpoint:`, `Size: ... end {k} (transcript) ...`, `Planned:`, the session's link), "
              f"then start the successor. At 350k every other action is refused.")
    warn = f"size hook: {k}, in the warn band from 250k; the checkpoint is due at 280k: bring the work to a boundary."
    if event == "Stop":
        ask = owed(state, tool_input.get("stop_hook_active"), tool_input.get("asked"))
        if ask == "checkpoint":
            return {"decision": "block", "reason": demand}
        if ask == "successor":
            return {"decision": "block", "reason": (
                f"size hook: {k}, the checkpoint is written but no successor has started. Start it now "
                f"(`update_trigger` with its words, then `fire_trigger`, or `create_session` where the surface allows it: "
                f"library/session-changeover.md, *A session "
                f"starts its own successor*), or post a checkpoint whose `Successor:` line says why none starts: "
                f"`Successor: none — nothing ready`, `— the platform refused <what>`, or `— blind`")}
        return {"systemMessage": warn} if WARN <= size < LINE else None
    if event == "PostToolUse":
        if size >= LINE and not checkpointed:
            return {"decision": "block", "reason": demand}
        if size >= WARN and not checkpointed:
            return {"hookSpecificOutput": {"hookEventName": "PostToolUse", "additionalContext": warn}}
        if tool_uses <= 1:
            return {"hookSpecificOutput": {"hookEventName": "PostToolUse",
                    "additionalContext": f"size hook: live; boot {k} (transcript)"}}
    return None


def blind_message(why):
    return (f"size hook: blind, {why}; this session's size is unknown, so every call is refused but a `Checkpoint:` "
            f"comment (its Size: source `unknown`, naming the blindness), loading a tool, and repairing the hook "
            f"(reading or editing `.claude/size.py` or `.claude/settings.json`, or a command that only runs `.claude/size.py`). No successor: it would be blind too.")


HOOK_FILES = (".claude/size.py", ".claude/settings.json")


# A run of the hook and nothing else: `python3 [dir/].claude/size.py [args]`, no second
# command, redirect, substitution or comment riding along on it.
RUN_HOOK = re.compile(r"python3? +(?:[\w./~-]*/)?\.claude/size\.py(?: +[\w./=~-]+)*")


def blind_allows(tool_name, tool_input):
    """What a blind session may still do: the checkpoint, loading a tool, and repairing the hook."""
    tool_input = tool_input if isinstance(tool_input, dict) else {}
    tool_name = tool_name if isinstance(tool_name, str) else ""
    body = tool_input.get("body")
    return (tool_name in ALWAYS or repairs(tool_input) or (
        _ends(tool_name, COMMENT_TOOLS) and CHECKPOINT_RE.search((body if isinstance(body, str) else "").lstrip()) is not None))


def repairs(tool_input):
    """True when a call edits or reads the hook's own files, or runs the hook itself: the one way out of a blindness."""
    path = tool_input.get("file_path") or ""
    cmd = tool_input.get("command")
    return (isinstance(path, str) and path.endswith(HOOK_FILES)) or (
        isinstance(cmd, str) and RUN_HOOK.fullmatch(cmd.strip()) is not None)


def _deny(reason):
    return {"hookSpecificOutput": {"hookEventName": "PreToolUse",
            "permissionDecision": "deny", "permissionDecisionReason": reason}}


def failed(h, e):
    """A hook that raised: blind, refusing all but what blind lets through."""
    msg = blind_message(f"the hook failed ({type(e).__name__})")
    return (_deny(msg) if h.get("hook_event_name") == "PreToolUse" and not blind_allows(h.get("tool_name"), h.get("tool_input"))
            else {"systemMessage": msg})


def answer(h, note=NOTE, stops=STOPS):
    """The hook's answer to one call's input, measured from the call's own transcript_path."""
    path = h.get("transcript_path")
    state, why = None, "the hook was given no transcript_path"
    if isinstance(path, str) and path:
        try:
            with open(note, "w", encoding="utf-8") as f:
                f.write(path)
        except OSError:
            pass
        state = read(path)
        why = f"{path} could not be opened" if not os.path.isfile(path) else f"{path} carries no usage"
    event = h.get("hook_event_name")
    if event != "Stop":
        return decide(event, h.get("tool_name"), h.get("tool_input"), state, _ticket(), why)
    kept = bool(h.get("stop_hook_active"))
    asked = [] if not kept else asked_at(path, stops) if state else None   # a turn's first end opens a new run
    a = decide(event, None, {"stop_hook_active": kept, "asked": asked}, state, _ticket(), why)
    if state is None or asked is None:
        return a
    ask = owed(state, kept, asked)
    recorded = keep_asked(path, asked + [ask] if ask else asked, stops)
    # kept going, a turn is asked only what the record now holds, so an ask that cannot be kept is never made twice
    return None if kept and ask and not recorded else a


def remembered(note=NOTE):
    try:
        with open(note, encoding="utf-8") as f:
            return f.read().strip() or None
    except OSError:
        return None


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
        ("past the line without a checkpoint, the checkpoint is demanded", bool(post) and post.get("decision") == "block"),
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
    U, F = "mcp__claude-code-remote__update_trigger", "mcp__claude-code-remote__fire_trigger"
    CLEAR = json.dumps({"trigger": {"id": "trig_X", "cron_expression": None, "run_once_at": None}})
    T = {"trigger_id": "trig_X"}
    s = _state([_turn(96_000, "Bash"), _turn(310_000, C, good, id="cp"), _result("cp"),
                _call(312_000, U, T, "u"), _trig_result("u", CLEAR), _turn(351_000, "Bash")])
    cases += [
        ("past 350k after it, work is refused", _denied(decide("PreToolUse", "Bash", {}, s))),
        ("past 350k a shell command that posts a checkpoint is still refused", _denied(decide("PreToolUse", "Bash",
         {"command": "make && gh issue comment 363 --body 'Checkpoint: x\nSize: end 351k'"}, s))),
        ("past 350k after it, the successor may start", decide("PreToolUse", F, T, s) is None),
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
    _clock_cases(cases, U, F, T)
    cases += [
        ("blind, a call is refused until it can see", _denied(decide("PreToolUse", "Bash", {}, read("/nonexistent")))),
        ("blind, an edit is refused", _denied(decide("PreToolUse", "Edit", {}, None))),
        ("blind, the checkpoint goes through", decide("PreToolUse", C, {"body": "Checkpoint: x\nSize: source unknown"}, None) is None),
        ("blind, an ordinary comment is refused", _denied(decide("PreToolUse", C, {"body": "Round 2."}, None))),
        ("blind, a tool may be loaded", decide("PreToolUse", "ToolSearch", {}, None) is None),
        ("blind, no successor starts: it would be blind too", _denied(decide("PreToolUse", "mcp__claude-code-remote__fire_trigger", {"trigger_id": "trig_X"}, None))),
        ("blind, the hook may be read", decide("PreToolUse", "Read", {"file_path": "/r/.claude/size.py"}, None) is None),
        ("blind, the hook may be edited", decide("PreToolUse", "Edit", {"file_path": "/r/.claude/size.py"}, None) is None),
        ("blind, its wiring may be edited", decide("PreToolUse", "Edit", {"file_path": "/r/.claude/settings.json"}, None) is None),
        ("blind, the hook may be run", decide("PreToolUse", "Bash", {"command": "python3 .claude/size.py --selftest"}, None) is None),
        ("blind, the hook may be run by its path", decide("PreToolUse", "Bash", {"command": "python3 /r/.claude/size.py --now"}, None) is None),
        ("blind, a command that only mentions the hook is refused",
         _denied(decide("PreToolUse", "Bash", {"command": "gh pr merge 1 # .claude/size.py"}, None))),
        ("blind, a command chained after a run of the hook is refused",
         _denied(decide("PreToolUse", "Bash", {"command": "python3 .claude/size.py --selftest; gh pr merge 1"}, None))),
        ("blind, a command that reads the hook through the shell is refused",
         _denied(decide("PreToolUse", "Bash", {"command": "cat .claude/settings.json"}, None))),
        ("blind, a substitution riding on a run of the hook is refused",
         _denied(decide("PreToolUse", "Bash", {"command": "python3 .claude/size.py $(gh pr merge 1)"}, None))),
        ("blind, another file may not be edited", _denied(decide("PreToolUse", "Edit", {"file_path": "/r/.claude/size.py.bak"}, None))),
        ("and says so, loud, to the session and the person", (lambda a: a.get("decision") == "block" and
         "blind" in a.get("reason", "") and "blind" in a.get("systemMessage", ""))(decide("PostToolUse", "Bash", {}, None))),
        ("and at a turn's end", "blind" in json.dumps(decide("Stop", None, {}, None))),
    ]
    _band_cases(cases, C, good)
    _successor_cases(cases, C, good)
    _path_cases(cases)
    ok = _guard_cases(cases)
    here = os.path.dirname(os.path.abspath(__file__))
    try:
        hooks = json.load(open(os.path.join(here, "settings.json"))).get("hooks", {})
        wired = all(any(h.get("matcher", "") in ("", "*") and
                        any("size.py" in (x.get("command") or "") for x in h.get("hooks", []))
                        for h in hooks.get(ev, [])) for ev in ("PreToolUse", "PostToolUse", "Stop"))
    except (OSError, ValueError, AttributeError):
        wired = False
    cases.append((".claude/settings.json runs this file before and after every tool call, and at every turn's end", wired))
    for name, passed in cases:
        print(("ok: " if passed else "FAIL: ") + "size hook: " + name)
        ok = ok and passed
    return ok


def _trig_result(id, text):
    return json.dumps({"type": "user", "message": {"content": [
        {"type": "tool_result", "tool_use_id": id, "content": [{"type": "text", "text": text}]}]}})


def _clock_cases(cases, U, F, T):
    """The clock lock (#378): no standing task carries a repeat or a run time, and none with one is fired."""
    Cr, L = "mcp__claude-code-remote__create_trigger", "mcp__claude-code-remote__list_triggers"
    s0 = _state([_turn(96_000, "Bash")])
    up = lambda inp, res: _state([_turn(96_000, "Bash"), _call(97_000, U, dict(T, **inp), "u"), _trig_result("u", res)])
    clear = json.dumps({"trigger": {"id": "trig_X", "cron_expression": None, "run_once_at": None}})
    cases += [
        ("a create carrying a repeat is refused", _denied(decide("PreToolUse", Cr, {"name": "x", "prompt": "p", "cron_expression": "0 * * * *"}, s0))),
        ("a create carrying a run time is refused", _denied(decide("PreToolUse", Cr, {"name": "x", "prompt": "p", "run_once_at": "2026-11-07T09:00:00Z"}, s0))),
        ("an update carrying a repeat is refused", _denied(decide("PreToolUse", U, dict(T, cron_expression="0 9 * * *"), s0))),
        ("and refused with an unreadable transcript too", _denied(decide("PreToolUse", U, dict(T, run_once_at="2026-11-07T09:00:00Z"), None))),
        ("a create with neither passes", decide("PreToolUse", Cr, {"name": "x", "prompt": "p"}, s0) is None),
        ("a fire of a task this session has not updated is refused", _denied(decide("PreToolUse", F, T, s0))),
        ("a fire after an update whose result shows no clock passes", decide("PreToolUse", F, T, up({"prompt": "p"}, clear)) is None),
        ("a fire after an update that left an old repeat standing is refused",
         _denied(decide("PreToolUse", F, T, up({"prompt": "p"}, json.dumps({"trigger": {"id": "trig_X", "cron_expression": "0 9 * * *"}}))))),
        ("a fire after an update that left an old run time standing is refused, read from prose",
         _denied(decide("PreToolUse", F, T, up({"prompt": "p"}, "updated trig_X: run_once_at: 2026-11-07T09:00:00Z, enabled")))),
        ("a fire of another task than the one updated is refused", _denied(decide("PreToolUse", F, {"trigger_id": "trig_Y"}, up({}, clear)))),
        ("a fire after a refused update is refused", _denied(decide("PreToolUse", F, T, _state(
            [_turn(96_000, "Bash"), _call(97_000, U, dict(T, prompt="p"), "u"), _result("u", error=True)])))),
        ("a created task is known by the id its result names", decide("PreToolUse", F, T, _state(
            [_turn(96_000, "Bash"), _call(97_000, Cr, {"name": "x", "prompt": "p"}, "c"), _trig_result("c", clear)])) is None),
        ("the newest update decides", decide("PreToolUse", F, T, _state(
            [_turn(96_000, "Bash"), _call(97_000, U, T, "u"), _trig_result("u", json.dumps({"cron_expression": "0 9 * * *"})),
             _call(98_000, U, T, "v"), _trig_result("v", clear)])) is None),
        ("an unreadable transcript refuses a fire: its successor would be blind too", _denied(decide("PreToolUse", F, T, None))),
        ("the platform's own update result (6 November 2026: an empty repeat, no run time) clears the task",
         decide("PreToolUse", F, T, up({"prompt": "p"}, json.dumps({"trigger": {"id": "trig_X", "cron_expression": "", "enabled": True}}))) is None),
        ("the task's own object decides, not another one in the result",
         _denied(decide("PreToolUse", F, T, up({"prompt": "p"}, json.dumps({"trigger": {"id": "trig_X", "cron_expression": "0 9 * * *"},
                                                                        "previous": {"id": "trig_Y", "cron_expression": None, "run_once_at": None}}))))),
        ("an update whose result is silent on the fields leaves the task unknown, and its fire refused",
         _denied(decide("PreToolUse", F, T, up({"prompt": "p"}, json.dumps({"trigger": {"id": "trig_X", "name": "x"}}))))),
        ("a list_triggers entry with both empty clears it", decide("PreToolUse", F, T, _state(
            [_turn(96_000, "Bash"), _call(97_000, L, {}, "l"), _trig_result("l", json.dumps({"triggers": [
                {"id": "trig_X", "cron_expression": None, "run_once_at": None}]}))])) is None),
        ("a list_triggers entry with a repeat is refused", _denied(decide("PreToolUse", F, T, _state(
            [_turn(96_000, "Bash"), _call(97_000, L, {}, "l"), _trig_result("l", json.dumps({"triggers": [
                {"id": "trig_X", "cron_expression": "0 9 * * *", "run_once_at": None}]}))])))),
        ("a list after a clearing update decides", _denied(decide("PreToolUse", F, T, _state(
            [_turn(96_000, "Bash"), _call(97_000, U, T, "u"), _trig_result("u", clear),
             _call(98_000, L, {}, "l"), _trig_result("l", json.dumps([{"id": "trig_X", "cron_expression": None, "run_once_at": "2026-11-07T09:00:00Z"}]))])))),
    ]


def _first(text):
    return json.dumps({"type": "user", "isMeta": True, "message": {"content": text}})


def _call(n, tool, inp, id):
    return json.dumps({"type": "assistant", "message": {
        "content": [{"type": "tool_use", "id": id, "name": tool, "input": inp}],
        "usage": {"input_tokens": n, "output_tokens": 0}}})


def _guard_cases(cases):
    """The guard's cases, on the rulebook's own ticket.py and pages, run with ROOT and the working
    directory at the rulebook's clone, so a product's copy with the rulebook beside it runs them as the rulebook does; True when
    it holds them."""
    global ROOT
    home, cwd = ROOT, os.getcwd()
    rb = _rulebook_root()
    try:
        if rb is not None:
            ROOT = os.path.realpath(rb)
            os.chdir(ROOT)
        return _guard_cases_here(cases)
    finally:
        ROOT = home
        os.chdir(cwd)


def _guard_cases_here(cases):
    tk = _ticket()
    if tk is None:
        # a product's copy: no ticket.py, so the guard is off, and its selftest stays green
        cases.append(("a repository carrying no ticket.py has no guard",
                      decide("PreToolUse", "mcp__claude-code-remote__update_trigger", {"prompt": "Build."},
                             _state([_turn(96_000, "Bash")]), None) is None))
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
        # words are checked against the clones the hook knows: with no product's clone beside it, a product's ticket is refused, never passed unchecked
        ("a product's ticket written here is refused", _denied(decide("PreToolUse", U, {"prompt": good.replace("\n\nMore", "\n- Hemz-OS:AGENTS.md\n\nMore")}, s0, tk))),
    ]
    s = _state([_turn(96_000, "Bash"), _call(97_000, U, {"prompt": good, "trigger_id": "trig_X"}, "u1"),
                _trig_result("u1", json.dumps({"cron_expression": None, "run_once_at": None}))])
    cases.append(("a fire after checked words went through passes", decide("PreToolUse", F, {"trigger_id": "trig_X"}, s, tk) is None))
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
        ("at boot a product's whole-file piece opens no file of this repository",
         _denied(decide("PreToolUse", "Read", {"file_path": os.path.join(ROOT, "AGENTS.md")},
                        _state([_first("Do the job.\nTicket:\n- " + tk.OWN + "\n- Hemz-OS:AGENTS.md\n"), _turn(96_000, "Bash")]), tk))),
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
    s = _state([_first("A note the surface puts first."), _first("Do the job.\n" + good), _turn(96_000, "Bash")])
    cases.append(("a note before the task's words does not hide its ticket", _denied(decide("PreToolUse", "Read", {"file_path": lib}, s, tk))))
    s = _state([_first("Do the job, no ticket."), _turn(96_000, "Bash"), _first("Pasted later.\n" + good)])
    cases.append(("a ticket pasted after the first reply arms nothing", decide("PreToolUse", "Read", {"file_path": lib}, s, tk) is None))
    s = _state([_first("Do the job, no ticket."), _turn(96_000, "Bash")])
    cases.append(("a session with no ticket is not guarded at boot", decide("PreToolUse", "Read", {"file_path": lib}, s, tk) is None))
    _product_cases(cases, tk, U, F, C)
    return _boot_cases(cases, tk, C)


def _product_cases(cases, tk, U, F, C):
    """A product's copy of this hook, with the rulebook cloned beside it: the same locks on its ticket."""
    global ROOT
    home, cwd = ROOT, os.getcwd()
    with tempfile.TemporaryDirectory() as up:
        prod = os.path.join(up, "hemz-os")
        os.makedirs(prod)
        for name, text in (("AGENTS.md", "# Agents\n"), ("README.md", "# Hemz\n"),
                           ("PRODUCT.md", "# Product\n\n## 1. What it is\n\nOne.\n\n## 2. Other\n\nTwo.\n"),
                           ("roadmap.json", json.dumps({"_what_this_is": "order", "items": [{"id": "P62"}]}))):
            with open(os.path.join(prod, name), "w") as f:
                f.write(text)
        alone = os.path.join(up, "alone", "hemz-os")
        os.makedirs(alone)
        os.symlink(home, os.path.join(up, "how-we-build"))
        words = ("Words.\nTicket:\n- " + tk.OWN + "\n- how-we-build:library/carries-sessions.md\n- Hemz-OS:AGENTS.md\n- Hemz-OS:PRODUCT.md#1\n"
                 "- Hemz-OS:roadmap.json#_what_this_is\n- Hemz-OS:roadmap.json#P62\n\nBuild.\n")
        try:
            ROOT = alone
            cases.append(("a product with no rulebook beside it has no guard", _ticket() is None))
            ROOT = prod
            os.chdir(prod)
            ptk = _ticket()
            cases.append(("a product's copy finds the rulebook's ticket.py beside it", ptk is not None))
            if ptk is None:
                return
            s0 = _state([_turn(96_000, "Bash")])
            boot = _state([_first("Do the job.\n" + words), _turn(96_000, "Bash")])
            rd = lambda path: decide("PreToolUse", "Read", {"file_path": path}, boot, ptk)
            sh = lambda cmd: decide("PreToolUse", "Bash", {"command": cmd}, boot, ptk)
            cases += [
                ("in a product, words with decision 0015's reads go through", decide("PreToolUse", U, {"prompt": words}, s0, ptk) is None),
                ("in a product, words reading PRODUCT.md whole are refused",
                 _denied(decide("PreToolUse", U, {"prompt": words.replace("PRODUCT.md#1", "PRODUCT.md")}, s0, ptk))),
                ("in a product, words with no ticket are refused", _denied(decide("PreToolUse", U, {"prompt": "Build."}, s0, ptk))),
                ("in a product, a fire with no words gone through is refused", _denied(decide("PreToolUse", F, {}, s0, ptk))),
                ("at a product's boot PRODUCT.md is refused to Read", _denied(rd(os.path.join(prod, "PRODUCT.md")))),
                ("at a product's boot its own README is refused", _denied(rd(os.path.join(prod, "README.md")))),
                ("at a product's boot its AGENTS.md, a whole piece, is read", rd(os.path.join(prod, "AGENTS.md")) is None),
                ("at a product's boot the rulebook's start page is read", rd(os.path.join(up, "how-we-build", "HOW-WE-BUILD.md")) is None),
                ("at a product's boot a rulebook page off the ticket is refused",
                 _denied(rd(os.path.join(up, "how-we-build", "library", "reviewer.md")))),
                ("at a product's boot a search of it is refused", _denied(decide("PreToolUse", "Grep", {"pattern": "x"}, boot, ptk))),
                ("at a product's boot a shell read of roadmap.json is refused", _denied(sh("head -c 4000 roadmap.json"))),
                ("at a product's boot a shell read of PRODUCT.md is refused", _denied(sh("cat PRODUCT.md"))),
                ("at a product's boot a shell read of its -library/ paper is refused", _denied(sh("cat hemz-library/x.md"))),
                ("at a product's boot a piece is read with ticket.py", sh(
                    "python3 ../how-we-build/product-reads/ticket.py --repo Hemz-OS=. read 'Hemz-OS:PRODUCT.md#1'") is None),
                ("at a product's boot a Resumed: is held to its Boot: line",
                 _denied(decide("PreToolUse", C, {"body": "Resumed: clean"}, boot, ptk))),
            ]
        finally:
            ROOT = home
            os.chdir(cwd)


def _band_cases(cases, C, good):
    """The warn band from 250k, the line at 280k, and the end of a turn (his word, 12 November 2026)."""
    s = _state([_turn(96_000, "Bash"), _turn(240_000, "Bash")])
    cases += [("below 250k no warning", decide("PostToolUse", "Bash", {}, s) is None),
              ("below 250k a turn ends quietly", decide("Stop", None, {}, s) is None)]
    s = _state([_turn(96_000, "Bash"), _turn(260_000, "Bash")])
    post = decide("PostToolUse", "Bash", {}, s) or {}
    cases += [
        ("from 250k every call is warned", "warn band" in json.dumps(post) and post.get("decision") is None),
        ("from 250k a turn's end warns the person", "warn band" in decide("Stop", None, {}, s).get("systemMessage", "")),
        ("from 250k nothing is refused", decide("PreToolUse", "Bash", {}, s) is None),
    ]
    s = _state([_turn(96_000, "Bash"), _turn(285_000, "Bash")])
    cases += [
        ("past 280k the checkpoint is demanded after a call", (decide("PostToolUse", "Bash", {}, s) or {}).get("decision") == "block"),
        ("past 280k a turn with no checkpoint is kept going to write it", (decide("Stop", None, {}, s) or {}).get("decision") == "block"),
        ("but only once, so it never loops", decide("Stop", None, {"stop_hook_active": True}, s) is None),
        ("a checkpoint at 285k carries its figure", decide("PreToolUse", C, {"body": good.replace("310k", "285k")}, s) is None),
    ]
    s = _state([_turn(96_000, "Bash"), _turn(285_000, C, good.replace("310k", "285k"), id="cp"), _result("cp"), _turn(290_000, "Bash")])
    cases += [("after the checkpoint a turn ends once it has said so", decide("Stop", None, {"stop_hook_active": True}, s) is None),
              ("after the checkpoint no call is nagged", decide("PostToolUse", "Bash", {}, s) is None)]


def _successor_cases(cases, C, good):
    """The successor lock (his word, 12 November 2026): a checkpoint past the line is followed by a start, or says why none."""
    F, S = "mcp__claude-code-remote__fire_trigger", "mcp__claude-code-remote__create_session"
    cp = [_turn(96_000, "Bash"), _turn(285_000, C, good.replace("310k", "285k"), id="cp"), _result("cp")]
    none = lambda why: good.replace("310k", "286k") + "\nSuccessor: none — " + why
    end = lambda lines, **i: (decide("Stop", None, i, _state(lines)) or {}).get("decision") == "block"
    cases += [
        ("a checkpoint past the line with no successor keeps the turn going", end(cp)),
        ("and says how to end it", "Successor: none" in json.dumps(decide("Stop", None, {}, _state(cp)))),
        ("but only once, so it never loops", not end(cp, stop_hook_active=True)),
        ("a fire after the checkpoint lets the turn end", not end(cp + [_call(286_000, F, {"trigger_id": "trig_X"}, "f"), _result("f")])),
        ("a create_session after it lets the turn end", not end(cp + [_call(286_000, S, {"prompt": "p"}, "n"), _result("n")])),
        ("a refused fire does not", end(cp + [_call(286_000, F, {"trigger_id": "trig_X"}, "f"), _result("f", error=True)])),
        ("a fire beside the checkpoint in one turn lets the turn end, whichever result comes first",
         all(not end(cp[:1] + [_pair(285_000, C, good.replace("310k", "285k"), F)] + r) for r in
             ([_result("cp"), _result("f")], [_result("f"), _result("cp")]))),
        ("a fire beside a refused checkpoint still leaves the checkpoint owed",
         end(cp[:1] + [_pair(285_000, C, good.replace("310k", "285k"), F), _result("cp", error=True), _result("f")])),
        ("a fire before the checkpoint does not", end(cp[:1] + [_call(282_000, F, {"trigger_id": "trig_X"}, "f"), _result("f")] + cp[1:])),
        ("`Successor: none — nothing ready` lets the turn end",
         not end(cp + [_turn(286_000, C, none("nothing ready"), id="n"), _result("n")])),
        ("`Successor: none — the platform refused <what>` lets the turn end",
         not end(cp + [_turn(286_000, C, none("the platform refused fire_trigger (no task tools)"), id="n"), _result("n")])),
        ("`Successor: none — blind` lets the turn end", not end(cp + [_turn(286_000, C, none("blind"), id="n"), _result("n")])),
        ("the line in the first checkpoint itself lets the turn end",
         not end(cp[:1] + [_turn(286_000, C, none("nothing ready"), id="n"), _result("n")])),
        ("a refused checkpoint naming none does not", end(cp + [_turn(286_000, C, none("nothing ready"), id="n"), _result("n", error=True)])),
        ("a checkpoint naming another reason is refused",
         _denied(decide("PreToolUse", C, {"body": none("the next session takes over")}, _state(cp)))),
        ("the platform refused, unnamed, is refused", _denied(decide("PreToolUse", C, {"body": none("the platform refused")}, _state(cp)))),
        ("a checkpoint naming a good reason passes", decide("PreToolUse", C, {"body": none("nothing ready")}, _state(cp)) is None),
        ("below the line a checkpoint does not hold the turn",
         not end([_turn(96_000, "Bash"), _turn(150_000, C, good.replace("310k", "150k"), id="cp"), _result("cp")])),
        # Adonis80/Hemz-OS#363's read: the two asks shared the platform's one flag, so the first used up the second
        ("a turn kept going for the checkpoint, which then writes it, is still asked for its successor",
         end(cp, stop_hook_active=True, asked=["checkpoint"])),
        ("a turn kept going by another hook is still asked for its successor", end(cp, stop_hook_active=True, asked=[])),
        ("and for its checkpoint", end(cp[:1] + [_turn(285_000, "Bash")], stop_hook_active=True, asked=[])),
        ("each is asked once in a run: the successor", not end(cp, stop_hook_active=True, asked=["checkpoint", "successor"])),
        ("each is asked once in a run: the checkpoint",
         not end(cp[:1] + [_turn(285_000, "Bash")], stop_hook_active=True, asked=["checkpoint"])),
    ]
    with tempfile.TemporaryDirectory() as d:
        t, stops = os.path.join(d, "s.jsonl"), os.path.join(d, "stops")
        say = lambda lines: open(t, "w").write("\n".join(lines) + "\n")
        stop = lambda kept=False, s=stops: (answer({"hook_event_name": "Stop", "transcript_path": t, "stop_hook_active": kept},
                                                   os.path.join(d, "note"), s) or {}).get("decision") == "block"
        say(cp[:1] + [_turn(285_000, "Bash")])
        first = stop()
        say(cp)   # the checkpoint is first written in the turn the hook kept going
        second, third = stop(kept=True), stop(kept=True)
        say(cp[:1] + [_turn(285_000, "Bash")])
        nowhere = os.path.join(d, "gone", "stops")   # a record that cannot be kept
        stuck = os.path.join(d, "stuck")             # one that can be read and no longer written
        keep_asked(t, [], stuck)
        os.mkdir(stuck + ".new")
        cases += [
            ("through the hook: past the line a turn's end is kept going for its checkpoint", first),
            ("through the hook: the checkpoint first written in that kept-going turn, its end is kept going for the successor", second),
            ("through the hook: and then it ends, so it never loops", not third),
            ("through the hook: with no record a turn already kept going ends", stop() and not stop(kept=True, s=os.path.join(d, "other"))),
            ("through the hook: a record that cannot be kept asks at a turn's first end and never after",
             stop(s=nowhere) and not stop(kept=True, s=nowhere)),
            ("through the hook: kept going, an ask that cannot be recorded is not made, so it cannot be made twice",
             asked_at(t, stuck) == [] and not stop(kept=True, s=stuck)),
            ("through the hook: one transcript's record is not another's", asked_at(os.path.join(d, "else.jsonl"), stops) is None),
        ]


def _pair(n, C, body, F):
    """One model turn that posts a checkpoint (id cp) and fires a successor (id f) together."""
    return json.dumps({"type": "assistant", "message": {"content": [
        {"type": "tool_use", "id": "cp", "name": C, "input": {"body": body}},
        {"type": "tool_use", "id": "f", "name": F, "input": {"trigger_id": "trig_X"}}],
        "usage": {"input_tokens": n, "output_tokens": 0}}})


def _path_cases(cases):
    """The size is read from the call's own transcript_path, whatever the working directory; blind is loud."""
    import subprocess
    with tempfile.TemporaryDirectory() as d:
        t, note = os.path.join(d, "s.jsonl"), os.path.join(d, "note")
        with open(t, "w") as f:
            f.write(_turn(96_000, "Bash") + "\n" + _turn(305_000, "Bash") + "\n")
        cwd = os.getcwd()
        os.chdir(d)   # a working directory with no project of its own, as after a session's cd
        try:
            post = lambda **h: answer(dict(hook_event_name="PostToolUse", tool_name="Bash", tool_input={}, **h), note) or {}
            hit = post(transcript_path=t)
            cases += [
                ("the size is the transcript_path's, whatever the cwd", "305k, past the 280k line" in hit.get("reason", "")),
                ("the hook records the transcript_path it was given", remembered(note) == t),
                ("no transcript_path is blind, and says so", "blind, the hook was given no transcript_path" in post().get("reason", "")),
                ("a transcript_path that will not open is blind, naming it",
                 "blind, %s could not be opened" % os.path.join(d, "gone") in post(transcript_path=os.path.join(d, "gone")).get("reason", "")),
            ]
            with open(os.path.join(d, "empty.jsonl"), "w") as f:
                f.write("{}\n")
            cases.append(("a transcript with no usage is blind, not a silent pass",
                          "carries no usage" in post(transcript_path=os.path.join(d, "empty.jsonl")).get("reason", "")))
            env = dict(os.environ, HOME=d)
            os.makedirs(os.path.join(d, ".claude"))
            me = os.path.realpath(__file__)
            now = lambda: subprocess.run([sys.executable, "-I", me, "--now"], env=env, capture_output=True, text=True)
            r = now()
            cases.append(("--now with nothing recorded says why and fails", r.returncode == 1 and "recorded none" in r.stderr))
            with open(os.path.join(d, ".claude", "size-hook-transcript"), "w") as f:
                f.write(t)
            r = now()
            cases.append(("--now reads the transcript the hook was last given", (r.returncode, r.stdout) == (0, "305k (transcript)\n")))
            r = subprocess.run([sys.executable, "-I", me], input="not json", env=env, capture_output=True, text=True)
            cases.append(("input that is not JSON is blind, and says so", "blind" in r.stdout))
            pre = lambda **h: answer(dict(hook_event_name="PreToolUse", **h), note)
            cases += [("blind through the real ticket, a call is refused", _denied(pre(tool_name="Bash", tool_input={"command": "ls"}))),
                      ("blind through the real ticket, a task's words are still checked, not a crash",
                       _denied(pre(tool_name="mcp__claude-code-remote__update_trigger", tool_input={"trigger_id": "trig_X", "prompt": "x"})))]
            r = subprocess.run([sys.executable, "-I", me], input=json.dumps({"hook_event_name": "PreToolUse", "tool_name": 5,
                               "tool_input": {"command": "ls"}, "transcript_path": t}), env=env, capture_output=True, text=True)
            cases.append(("a hook that fails refuses the call, never a silent pass",
                          _denied(json.loads(r.stdout or "{}")) and "the hook failed" in r.stdout))
            boom = lambda name, inp: failed({"hook_event_name": "PreToolUse", "tool_name": name, "tool_input": inp}, ValueError())
            cases += [
                ("a hook that fails lets the checkpoint through",
                 not _denied(boom("mcp__github__add_issue_comment", {"body": "Checkpoint: x\nSize: source unknown"}))),
                ("a hook that fails lets a tool be loaded", not _denied(boom("ToolSearch", {}))),
                ("a hook that fails lets the hook be run", not _denied(boom("Bash", {"command": "python3 .claude/size.py --selftest"}))),
                ("a hook that fails still refuses an ordinary comment", _denied(boom("mcp__github__add_issue_comment", {"body": "Round 2."}))),
                ("a hook that fails, given input that is not an object, refuses rather than crashing", _denied(boom("Bash", ["ls"]))),
                ("a hook that fails, given a name that is not a string, refuses rather than crashing", _denied(boom(5, "x"))),
            ]
            stop = lambda **h: answer(dict(hook_event_name="Stop", **h), note, os.path.join(d, "stops")) or {}
            cases += [
                ("a turn's end with no tool call is measured from its transcript_path", stop(transcript_path=t).get("decision") == "block"),
                ("a turn already kept going is let end", stop(transcript_path=t, stop_hook_active=True) == {}),
            ]
        finally:
            os.chdir(cwd)
    _user_cases(cases)


def _user_cases(cases):
    """Wired at user level by the environment's setup: measured whatever the working directory (#408's checkpoint:
    a session restarted at /home/user ran to 453k unmeasured, the project's wiring unloaded)."""
    import subprocess
    with tempfile.TemporaryDirectory() as d:
        t = os.path.join(d, "s.jsonl")
        with open(t, "w") as f:
            f.write(_turn(96_000, "Bash") + "\n" + _turn(305_000, "Bash") + "\n")
        link, settings = os.path.join(d, ".claude", "size.py"), os.path.join(d, ".claude", "settings.json")
        os.makedirs(os.path.dirname(settings))
        other = {"type": "command", "command": "other.sh"}
        with open(settings, "w") as f:
            json.dump({"keep": 1, "hooks": {"Stop": [{"hooks": [other]}]}}, f)
        install(link, settings)
        install(link, settings)
        cfg = json.load(open(settings))
        runs = lambda ev: sum("size.py" in x.get("command", "") for h in cfg["hooks"].get(ev, []) for x in h.get("hooks", []))
        cases += [
            ("--install wires all three events once, run twice", all(runs(ev) == 1 for ev in EVENTS)),
            ("--install keeps the settings it found", cfg.get("keep") == 1 and any(other in h["hooks"] for h in cfg["hooks"]["Stop"])),
            ("--install's stable path is this file", os.path.realpath(link) == os.path.realpath(__file__)),
        ]
        out = os.path.join(d, "out")   # a working directory outside any repository
        os.makedirs(out)
        hook = lambda project, inp: subprocess.run(
            [sys.executable, "-I", link, "--user"], input=json.dumps(inp), cwd=out, capture_output=True, text=True,
            env=dict(os.environ, HOME=d, CLAUDE_PROJECT_DIR=project))
        post = {"hook_event_name": "PostToolUse", "tool_name": "Bash", "tool_input": {}, "cwd": out, "transcript_path": t}
        r = hook(out, post)
        cases += [
            ("a hook input whose cwd is outside any repo, with transcript_path given, is still measured",
             "305k, past the 280k line" in r.stdout),
            ("the user-level run is quiet where the project already wires the hook", hook(ROOT, post).stdout == ""),
            # a product's copy with no rulebook beside it (its CI) reaches no ticket.py and so has no guard: there the
            # same call goes through, and the selftest stays green (Hemz-OS#362: it was red on every such run)
            ("through the stable path the guard still finds ticket.py, where one is reachable", _denied(json.loads(hook(out, {
                "hook_event_name": "PreToolUse", "tool_name": "mcp__claude-code-remote__update_trigger",
                "tool_input": {"trigger_id": "trig_X", "prompt": "x"}, "cwd": out, "transcript_path": t}).stdout or "{}"))
             == (_ticket() is not None)),
        ]


def _read_result(id, tokens):
    return json.dumps({"type": "user", "message": {"content": [
        {"type": "tool_result", "tool_use_id": id, "content": "x" * (tokens * 4)}]}})


def _boot_cases(cases, tk, C):
    """The boot measured: the first Resumed:/Continued: carries the hook's own Boot: line."""
    small = [_turn(96_000, "Bash", id="a"), _read_result("a", 5_000),
             _call(1, "ToolSearch", {}, "ts"), _read_result("ts", 9_000),
             _call(112_000, "Read", {"file_path": os.path.join(ROOT, "README.md")}, "b"), _read_result("b", 2_000)]
    s = _state(small)
    line = boot_line(s)
    cases += [
        ("ours is what the session read, a loaded tool's schema excepted", "ours 7k" in line),
        ("platform is the rest of the real size", "platform 105k" in line),
        ("under 30k no heaviest list is asked", "heaviest" not in line),
        ("a Resumed: with no Boot: line is refused, and handed the line",
         _denied(decide("PreToolUse", C, {"body": "Resumed: clean"}, s, tk)) and
         line in json.dumps(decide("PreToolUse", C, {"body": "Resumed: clean"}, s, tk))),
        ("a Resumed: with the hook's line passes", decide("PreToolUse", C, {"body": "Resumed: clean\n" + line}, s, tk) is None),
        ("a Continued: is held the same", _denied(decide("PreToolUse", C, {"body": "Continued: x"}, s, tk))),
        ("a guessed ours figure is refused", _denied(decide("PreToolUse", C,
         {"body": "Resumed: clean\nBoot: platform 105k, ours 1k"}, s, tk))),
        ("a product, carrying no ticket.py, is not held", decide("PreToolUse", C, {"body": "Resumed: clean"}, s, None) is None),
    ]
    big = small[:-2] + [_call(150_000, "Bash", {"command": "cat a"}, "c"), _read_result("c", 20_000),
                        _call(151_000, "mcp__github__issue_read", {"method": "get_comments", "issue_number": 363}, "d"),
                        _read_result("d", 9_000)]
    s = _state(big)
    line = boot_line(s)
    cases += [
        ("over 30k the line names the three heaviest", "heaviest: `cat a` 20k, issue_read get_comments 363 9k" in line),
        ("over 30k a line without them is refused", _denied(decide("PreToolUse", C,
         {"body": "Resumed: clean\nBoot: platform 116k, ours 34k"}, s, tk))),
        ("over 30k the hook's line passes", decide("PreToolUse", C, {"body": "Resumed: clean\n" + line}, s, tk) is None),
    ]
    s = _state(big + [_call(152_000, C, {"body": "Resumed: clean\n" + line}, "r"), _result("r"),
                      _call(153_000, "Bash", {"command": "cat b"}, "e"), _read_result("e", 50_000)])
    cases += [
        ("reads after the boot are not ours at boot", sum(n for n, _ in s[3]["reads"]) < 35_000),
        ("a later Resumed: is not held again", decide("PreToolUse", C, {"body": "Resumed: x"}, s, tk) is None),
    ]
    return True


USER_LINK = os.path.join(os.path.expanduser("~"), ".claude", "size.py")
USER_SETTINGS = os.path.join(os.path.expanduser("~"), ".claude", "settings.json")
EVENTS = ("PreToolUse", "PostToolUse", "Stop")


def install(link=USER_LINK, settings=USER_SETTINGS):
    """Wire the hook at user level, so it runs whatever the working directory (his word, 12 November 2026,
    Hemz-OS#333 item 4: "in the environment's setup"). The stable path is a link to this checkout's file, so
    the hook still finds the rulebook (and ticket.py) beside the file it really is; other settings are kept."""
    os.makedirs(os.path.dirname(link), exist_ok=True)
    tmp = link + ".new"
    if os.path.lexists(tmp):
        os.unlink(tmp)
    os.symlink(os.path.realpath(__file__), tmp)
    os.replace(tmp, link)
    try:
        with open(settings, encoding="utf-8") as f:
            cfg = json.load(f)
    except (OSError, ValueError):
        cfg = {}
    cfg = cfg if isinstance(cfg, dict) else {}
    hooks = cfg.setdefault("hooks", {})
    cmd = f'python3 -I "{link}" --user'
    for ev in EVENTS:
        kept = [h for h in hooks.get(ev, []) if not any("size.py" in (x.get("command") or "") for x in h.get("hooks", []))]
        entry = {"hooks": [{"type": "command", "command": cmd}]}
        if ev != "Stop":
            entry = {"matcher": "", **entry}
        hooks[ev] = kept + [entry]
    with open(settings + ".new", "w", encoding="utf-8") as f:
        json.dump(cfg, f, indent=2)
    os.replace(settings + ".new", settings)


def project_wires(project):
    """True when a project's own .claude/settings.json already runs size.py, so the user-level run stays quiet."""
    try:
        with open(os.path.join(project or "", ".claude", "settings.json"), encoding="utf-8") as f:
            hooks = json.load(f).get("hooks", {})
        return all(any("size.py" in (x.get("command") or "") for h in hooks.get(ev, []) for x in h.get("hooks", []))
                   for ev in EVENTS)
    except (OSError, ValueError, AttributeError, TypeError):
        return False


def main():
    if sys.argv[1:2] == ["--selftest"]:
        sys.exit(0 if selftest() else 1)
    if sys.argv[1:2] == ["--install"]:
        install()
        print(f"size hook: wired at user level, {USER_LINK} -> {os.path.realpath(__file__)}")
        return
    if sys.argv[1:2] == ["--user"] and project_wires(os.environ.get("CLAUDE_PROJECT_DIR")):
        return   # the project's own wiring runs it; once is enough
    if sys.argv[1:2] == ["--now"]:
        p = sys.argv[2] if len(sys.argv) > 2 else remembered()
        st = read(p) if p else None
        if st is None:
            sys.exit("size hook: unknown, " + (f"{p} could not be read" if p else "no transcript named, and the hook has recorded none"))
        print(f"{round(st[0] / 1000)}k (transcript)")
        return
    try:
        h = json.load(sys.stdin)
    except ValueError:
        h = None
    if not isinstance(h, dict):
        print(json.dumps({"systemMessage": blind_message("its input was not a JSON object, so no call can be named or refused")}))
        return
    try:
        a = answer(h)
    except Exception as e:   # a hook that raises is blind and refuses; one that cannot run fails open
        a = failed(h, e)
    if a:
        print(json.dumps(a))


if __name__ == "__main__":
    main()
