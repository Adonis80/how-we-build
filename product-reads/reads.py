#!/usr/bin/env python3
"""The product read's rules, said once (decision 0013, #148).

    reads.py product OWNER/NAME [README]          a product this rulebook lists?
    reads.py list [README]                         every product it lists, one a line
    reads.py ready COMMIT PARENT SHA               is that commit the ready mark?
    reads.py verify CHECKRUNS                      did the product's own check pass?
    reads.py state CHECKRUNS SHA APPID [--again]   has that commit been read?
    reads.py marked REPO BASE HEAD CHANGED_NUL     does the change leave its marked spans alone?
    reads.py --selftest

Each answers by its exit status: 0 go ahead, 1 refused with one line, 2 a
mistake in how it was called. A refusal says why in fixed words and prints
nothing a product holds: the log it lands in is public and the product is not.
review-product.yml asks before any read is paid for, the asker asks before it
dispatches one, and the setup script writes what these read, so a rule is
changed here and nowhere else. Standard library only: it runs on a bare runner,
beside the key.

THE READY MARK. A builder that has finished a round adds one commit that changes
no file. Its message carries `Review-Ready: yes` and `Review-Parent: <the full
id of the commit beneath it>`, each alone on a line. That commit is the one a
read is asked for. A builder that pushes half its fixes and goes quiet has not
marked anything ready, so a timer never buys a read of work that is still
moving; and a push on top of the mark moves the head off it, so a read is never
asked for work the mark does not describe. A second round is a fix and a new mark
on top of the old one, which stays in the pull request's history: the head must be
a valid mark, and a commit already read is stopped by its own read state, so no
rule about earlier commits is needed and one would make a second round impossible.
It is a signal between a builder and the asker, not a boundary: whoever can push
can write it, and the check that matters is the reviewer's own, on the commit it
read. The same is true of the product's `verify`: it is the product's, so whoever
can push there can make it pass, and a name is all this checks.

THREE KINDS OF "NOT READ". A commit with a verdict on it has been read. One whose
check run is still opening or reading is being read. One whose run ended
without a verdict, or was left in progress past the job's own hour, did not get
a read, and whether it was paid for is not something a run can say. So nothing
retries that by itself: a builder looks, and asks again with `again`. The asker
never does. One kind is not that: a run the spending check refused before any
request was sent, signed "Did not read: budget refused, nothing spent". It cost
nothing and read nothing, so it is no read at all, and asking again needs no
`again` (9 October 2026: Adonis80/myst#29 was refused five times at 0 USD, and
each re-ask needed the word).
"""
import json
import os
import re
import subprocess
import sys
import tempfile
import types
import urllib.error
import urllib.request
from datetime import datetime, timedelta, timezone

OWNER = "Adonis80"
REPO = re.compile(r"^%s/[A-Za-z0-9._-]+$" % OWNER)
SECTION = "## Products under this rulebook"
LISTED = re.compile(r"`https://github\.com/(%s/[A-Za-z0-9._-]+)`" % OWNER)
# The product's own check, and the reviewer's. A new product's kit names its
# job `verify`; the reviewer signs under this name, and review-gate.py holds the
# two spellings of it to one.
VERIFY = "verify"
REVIEWER_CHECK = "juku-reviewer"
# The reviewer's job is held to 55 minutes. A run still in progress an hour
# after it started has lost its runner and will not sign.
STALE = timedelta(minutes=60)
# The title both reviewers sign a read with when the spending check refused every
# request before it was sent: review.yml's and review-product.yml's why(), held
# to this by review-gate.py.
FREE = "Did not read: budget refused, nothing spent"

SHA = re.compile(r"^[0-9a-f]{40}$")
READY = re.compile(r"(?m)^Review-Ready: yes\r?$")
PARENT = re.compile(r"(?m)^Review-Parent: ([0-9a-f]{40})\r?$")
ANY_MARK = re.compile(r"(?mi)^[ \t]*review-(?:ready|parent)[ \t]*:")


class Refused(Exception):
    pass


class Malformed(Refused):
    """GitHub answered, but not in a shape a rule reads: no rule's refusal, so the asker
    fails its run on it (decision 0013's amendment), while review-product.yml refuses it."""


def github(token):
    """`call(method, path, body=None) -> (status, json or None)`. No body is ever kept
    from an error, and nothing about a request is printed."""
    def call(method, path, body=None):
        req = urllib.request.Request(
            "https://api.github.com" + path, method=method,
            data=json.dumps(body).encode() if body is not None else None,
            headers={"Authorization": "Bearer " + token, "Accept": "application/vnd.github+json",
                     "X-GitHub-Api-Version": "2022-11-28", "User-Agent": "juku-product-reads"})
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                text = r.read().decode("utf-8")
                return r.status, json.loads(text) if text else None
        except urllib.error.HTTPError as e:
            return e.code, None
    return call


def products(readme):
    """The repositories the README's map of products lists, or Refused.

    The list is the whole allowance: a product is read because it is on it. A
    list that cannot be read exactly stops everything, since guessing at a
    broken list is how a repository nobody listed gets read. So: the section
    must exist, every bullet in it names exactly one repository of this owner,
    none is named twice (case aside, as GitHub reads names), and there is at
    least one.
    """
    _, found, rest = readme.partition("\n" + SECTION + "\n")
    if not found:
        raise Refused("the README has no '%s' section" % SECTION[3:])
    names = []
    for line in rest.split("\n## ", 1)[0].splitlines():
        if not line.startswith("- "):
            continue
        urls = LISTED.findall(line)
        if len(urls) != 1:
            raise Refused("a line of the product list names %d repositories, not one" % len(urls))
        names.append(urls[0])
    if not names:
        raise Refused("the product list names no repository")
    if len(set(n.lower() for n in names)) != len(names):
        raise Refused("the product list names a repository twice")
    return names


def listed(readme, repo):
    """Refused unless `repo` is, exactly as written, a product on the list."""
    if not isinstance(repo, str) or not REPO.match(repo):
        raise Refused("the product must be named OWNER/NAME")
    if repo not in products(readme):
        raise Refused("%s is not a product this rulebook lists" % repo)


def ready(commit, parent, sha):
    """Refused unless `sha` is a ready mark: one commit, with one parent, that changes no file.

    `commit` and `parent` are the API's answers for it and for the commit beneath it.
    That it is the pull request's head is the caller's to have checked.
    """
    try:
        if not SHA.match(sha) or commit.get("sha") != sha:
            raise Refused("the commit fetched is not the commit asked for")
        parents = commit.get("parents") or []
        if len(parents) != 1:
            raise Refused("the ready mark must be a commit with exactly one parent")
        message = commit["commit"]["message"]
        marks = ANY_MARK.findall(message)
        said, beneath = READY.findall(message), PARENT.findall(message)
        if len(said) != 1 or len(beneath) != 1 or len(marks) != 2:
            raise Refused("the commit does not carry exactly one `Review-Ready: yes` and one "
                          "`Review-Parent: <full id>`, each alone on a line")
        if parents[0].get("sha") != beneath[0] or parent.get("sha") != beneath[0]:
            raise Refused("the commit's Review-Parent is not the commit beneath it")
        if commit["commit"]["tree"]["sha"] != parent["commit"]["tree"]["sha"]:
            raise Refused("the ready mark changes files; it must change none")
    except (KeyError, TypeError, AttributeError):
        raise Malformed("the commit's answer was not in the shape the ready check reads")


def _runs(answer):
    runs = answer.get("check_runs") if isinstance(answer, dict) else answer
    if not isinstance(runs, list):
        raise Malformed("the check runs were not in the shape the check reads")
    return [r for r in runs if isinstance(r, dict)]


def _when(text):
    try:
        return datetime.strptime(text, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
    except (TypeError, ValueError):
        return None


def verified(answer, sha):
    """Refused unless the product's `verify` check passed on `sha`.

    The latest run by when it started decides, so a re-run that is still going
    or has failed is not hidden behind an older green one.
    """
    mine = [r for r in _runs(answer) if r.get("name") == VERIFY and r.get("head_sha") == sha]
    if not mine:
        raise Refused("the product's own check, %s, has not run on this commit" % VERIFY)
    last = max(mine, key=lambda r: str(r.get("started_at") or ""))
    if last.get("status") != "completed":
        raise Refused("the product's own check, %s, is still running on this commit" % VERIFY)
    if last.get("conclusion") != "success":
        raise Refused("the product's own check, %s, did not pass on this commit" % VERIFY)


def read_state(answer, app_id, sha, now):
    """One of: none, running, read, failed. Never the verdict's words."""
    states = set()
    for r in _runs(answer):
        app = r.get("app") if isinstance(r.get("app"), dict) else {}
        if r.get("name") != REVIEWER_CHECK or app.get("id") != app_id or r.get("head_sha") != sha:
            continue
        if r.get("status") == "completed":
            title = (r.get("output") or {}).get("title") if isinstance(r.get("output"), dict) else None
            if r.get("conclusion") == "neutral" and isinstance(title, str) and title.startswith(FREE):
                continue  # refused before anything was sent: no read, and nothing to look at
            states.add("read" if r.get("conclusion") in ("success", "failure") else "failed")
        else:
            began = _when(r.get("started_at"))
            states.add("running" if began and now - began < STALE else "failed")
    for state in ("read", "running", "failed"):
        if state in states:
            return state
    return "none"


def unread(answer, app_id, sha, now, again=False):
    """Refused unless this commit may be read now. `again` lets a builder re-ask
    a commit whose earlier read did not finish; nothing else does."""
    state = read_state(answer, app_id, sha, now)
    if state == "read":
        raise Refused("this commit has already been read; a verdict is on it")
    if state == "running":
        raise Refused("a read of this commit is already running; asking again would pay twice")
    if state == "failed" and not again:
        raise Refused("an earlier read of this commit did not finish, and whether it was paid for "
                      "is unclear, so nothing retries it by itself; a builder who has looked asks "
                      "again with `again`")


# THE MARKED SPANS (#218, agreed 17 October 2026). Names alone missed a product's
# pricing: Hemz-OS#159 changed what feeds a price in a page no name calls
# pricing, and was read as ordinary code. A product marks what decides a price,
# in the file itself, around the lines: `RISK: pricing — START` and
# `RISK: pricing — END`, each on a line of its own, in a comment; Hemz OS's
# older `PRICING CORE — START` / `— END` band counts the same. A change is risky
# when a line it adds falls in a span of the head, or a line it deletes in a
# span of the base (never the diff's context lines), a marker line being in
# its own span, so adding, removing or editing one is a change in a span; or
# when the markers of a file it touches cannot be read: a
# `RISK:` line that is no such marker, a START inside an open span, an END
# with no START of its kind, a START never ended, or a file git cannot give.
# A page (`.md`) decides no price and may quote the markers, so it is not read
# for them. Never a downgrade: the names stay the floor, and this only adds.
MARK = re.compile(r"(RISK:[ \t]*pricing|PRICING CORE)[ \t]*[\u2014\u2013-]+[ \t]*(START|END)\b")
HUNK = re.compile(r"^@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@")


def spans(text):
    """[(first line, last line)], counted from 1, both marker lines in: a file's marked spans.

    Refused when its markers cannot be read.
    """
    out, at, kind = [], None, None
    for n, line in enumerate(text.splitlines(), 1):
        m = MARK.search(line)
        if not m:
            if "RISK:" in line:
                raise Refused("a RISK: line that is no pricing START or END marker, line %d" % n)
            continue
        k = m.group(1)[:4]
        if m.group(2) == "START":
            if at is not None:
                raise Refused("a marker START inside an open span, line %d" % n)
            at, kind = n, k
        else:
            if at is None or kind != k:
                raise Refused("a marker END with no START of its kind, line %d" % n)
            out.append((at, n))
            at = None
    if at is not None:
        raise Refused("a marker START never ended, line %d" % at)
    return out


def touches(diff, base, head):
    """Refused when one file's zero-context diff touches a marked span of its base or head.

    `diff` is `git diff -U0` of one file; `base` and `head` its text before and
    after, empty where it did not exist.
    """
    inside = lambda n, s: any(a <= n <= b for a, b in s)
    was, now = spans(base), spans(head)
    for line in diff.splitlines():
        m = HUNK.match(line)
        if m:
            old, olds, new, news = int(m.group(1)), int(m.group(2) or 1), int(m.group(3)), int(m.group(4) or 1)
            if any(inside(n, was) for n in range(old, old + olds)) or any(inside(n, now) for n in range(new, new + news)):
                raise Refused("a line it changes is inside a marked span")


def marked(repo, base, head, changed):
    """`reads.py marked REPO BASE HEAD CHANGED_NUL`: ok when no file the change touches has a marked line changed.

    Read as review-product.yml's diff is, from where BASE and HEAD meet to HEAD.
    """
    def git(*args):
        return subprocess.run(["git", "--literal-pathspecs", "-C", repo, "-c", "core.quotePath=false"] + list(args),
                              capture_output=True, check=True, timeout=120).stdout

    def blob(rev, f):
        if subprocess.run(["git", "-C", repo, "cat-file", "-e", "%s:%s" % (rev, f)], capture_output=True,
                          timeout=60).returncode:
            return ""
        return git("show", "%s:%s" % (rev, f)).decode("utf-8", "replace")
    since = git("merge-base", base, head).decode().strip()
    with open(changed, "rb") as f:
        files = [p.decode("utf-8") for p in f.read().split(b"\0") if p]
    for f in files:
        if f.lower().endswith(".md"):
            continue
        diff = git("diff", "-U0", "--no-renames", "--no-color", "--no-ext-diff", since, head, "--", f)
        diff = diff.decode("utf-8", "replace")
        if "@@" not in diff:
            continue
        touches(diff, blob(since, f), blob(head, f))


def _load(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def main(argv):
    now = datetime.now(timezone.utc)
    try:
        if argv[1:2] == ["--selftest"] and len(argv) == 2:
            return _selftest()
        if argv[1:2] == ["product"] and len(argv) in (3, 4):
            with open(argv[3] if len(argv) == 4 else "README.md", encoding="utf-8") as f:
                listed(f.read(), argv[2])
        elif argv[1:2] == ["list"] and len(argv) in (2, 3):
            with open(argv[2] if len(argv) == 3 else "README.md", encoding="utf-8") as f:
                print("\n".join(products(f.read())))
            return 0
        elif argv[1:2] == ["ready"] and len(argv) == 5:
            ready(_load(argv[2]), _load(argv[3]), argv[4])
        elif argv[1:2] == ["verify"] and len(argv) == 4:
            verified(_load(argv[2]), argv[3])
        elif argv[1:2] == ["marked"] and len(argv) == 6:
            marked(*argv[2:6])
        elif argv[1:2] == ["state"] and len(argv) in (5, 6) and (len(argv) == 5 or argv[5] == "--again"):
            if not argv[4].isdigit():
                raise ValueError("the App's id is a number")
            unread(_load(argv[2]), int(argv[4]), argv[3], now, again=len(argv) == 6)
        else:
            print("\n\n".join(__doc__.split("\n\n")[:2]))
            return 2
    except Refused as why:
        print("refused: %s" % why)
        return 1
    except (OSError, ValueError, subprocess.SubprocessError) as why:
        # The mistake is named by its kind, never quoted: a file's own words
        # could be a product's.
        print("could not be asked: %s" % type(why).__name__)
        return 2
    print("ok")
    return 0


# ---------------------------------------------------------------- the selftest

APP = 5000405
HEAD = "a" * 40
BENEATH = "b" * 40
NOW = datetime(2026, 10, 3, 15, 0, 0, tzinfo=timezone.utc)


def _stamp(minutes_ago):
    return (NOW - timedelta(minutes=minutes_ago)).strftime("%Y-%m-%dT%H:%M:%SZ")


def _run(name=REVIEWER_CHECK, app=APP, sha=HEAD, status="completed", conclusion="success", ago=5):
    return {"name": name, "app": {"id": app}, "head_sha": sha, "status": status,
            "conclusion": conclusion, "started_at": _stamp(ago)}


def _mark(parent=BENEATH, extra=""):
    return "Ready for a read\n\nReview-Ready: yes\nReview-Parent: %s\n%s" % (parent, extra)


def _commit(message, sha=HEAD, parents=(BENEATH,), tree="t1"):
    return {"sha": sha, "parents": [{"sha": p} for p in parents],
            "commit": {"message": message, "tree": {"sha": tree}}}


def _asks(fn, *args):
    try:
        fn(*args)
        return "ok"
    except Refused as why:
        return str(why)


# A cut-down Hemz-OS#159: its page, the pricing core's band, and the run-choice
# code and handlers #159 changed, marked as the agreed RISK: pricing span.
MARK_PAGE = ("<style>\n.chip{color:#333}\n</style>\n<script>\n"
             "/* ══════════ PRICING CORE — START ══════════\n   the price, from minutes */\n"
             "function minutesFor(f){ return 1; }\n/* ══════════ PRICING CORE — END ══════════ */\n"
             "function render(){ return 'x'; }\n"
             "/* RISK: pricing — START: the run a formula's price travels along */\n"
             "function seatRun(f){\n  if(f.lenIdx==null) f.lenIdx=0;\n}\n"
             "function pickOp(f,id){ f.ops.push(id); seatRun(f); }\n/* RISK: pricing — END */\n</script>\n")
# (what, the head's files as each change leaves them, None for gone; refused?)
MARK_CASES = (
    ("Hemz-OS#159's change, to the run a price travels along",
     {"page.html": MARK_PAGE.replace("if(f.lenIdx==null) f.lenIdx=0;", "if(f.lenIdx==null) f.lenIdx=f.fields.length-1;")},
     True),
    ("a line deleted from a marked span", {"page.html": MARK_PAGE.replace("  if(f.lenIdx==null) f.lenIdx=0;\n", "")}, True),
    ("a line added just inside a span's start",
     {"page.html": MARK_PAGE.replace("travels along */\n", "travels along */\nconst RUN=1;\n")}, True),
    ("a change inside the pricing core's band", {"page.html": MARK_PAGE.replace("return 1; }", "return 2; }")}, True),
    ("a CSS change elsewhere in the same page", {"page.html": MARK_PAGE.replace("#333", "#444")}, False),
    ("a change to unmarked code in the same page", {"page.html": MARK_PAGE.replace("'x'", "'y'")}, False),
    ("a line added just outside a span's start",
     {"page.html": MARK_PAGE.replace("/* RISK: pricing — START", "const NEAR=1;\n/* RISK: pricing — START")}, False),
    ("the line after a span, never its context", {"page.html": MARK_PAGE.replace("</script>", "</script >")}, False),
    ("a marker edited", {"page.html": MARK_PAGE.replace("/* RISK: pricing — END */", "/* RISK: pricing — END. */")},
     True),
    ("a marker removed", {"page.html": MARK_PAGE.replace("/* RISK: pricing — END */\n", "")}, True),
    ("a marker added", {"page.html": MARK_PAGE.replace("function render(){ return 'x'; }\n",
                                                       "/* RISK: pricing — START */\nfunction render(){ return 'x'; }\n"
                                                       "/* RISK: pricing — END */\n")}, True),
    ("the marked page deleted", {"page.html": None}, True),
    ("the marked page renamed, unchanged", {"page.html": None, "the-page.html": MARK_PAGE}, True),
    ("a page whose span never ends, changed elsewhere",
     {"page.html": MARK_PAGE.replace("/* RISK: pricing — END */\n", "").replace("#333", "#444")}, True),
    ("an unmarked file", {"other.js": "let b = 2;\n"}, False),
    ("a new file with no markers", {"new.js": "let c = 3;\n"}, False),
    ("a page that quotes the markers", {"notes.md": "Mark it from RISK: pricing — START to RISK: pricing — END.\n"},
     False),
)
MARK_BASE = {"page.html": MARK_PAGE, "other.js": "let a = 1;\n"}
# Each a file's text and whether its markers can be read.
MARK_SHAPES = (
    ("no markers", "a\nb\n", []),
    ("one span", "RISK: pricing — START\nx\nRISK: pricing — END\n", [(1, 3)]),
    ("the band and a span", "PRICING CORE — START\nx\nPRICING CORE — END\nRISK: pricing - START\ny\nRISK: pricing - END\n",
     [(1, 3), (4, 6)]),
    ("a line off the core is no marker", "PRICING CORE — START\n/* ── OFF THE PRICING CORE ── */\nPRICING CORE — END\n",
     [(1, 3)]),
    ("a RISK: line that is no marker", "RISK: pricing begins\n", None),
    ("a START inside an open span", "RISK: pricing — START\nRISK: pricing — START\nRISK: pricing — END\n", None),
    ("an END with no START", "RISK: pricing — END\n", None),
    ("an END of the other kind", "PRICING CORE — START\nRISK: pricing — END\n", None),
    ("a START never ended", "RISK: pricing — START\n", None),
)


# Each must turn some case above: applied to a copy of this file, its cases run.
MARK_LOOSENINGS = (
    ("a deleted line never read", "if any(inside(n, was) for n in range(old, old + olds)) or ", "if "),
    ("an added line never read", " or any(inside(n, now) for n in range(new, new + news)):", ":"),
    ("the pricing core's band not counted", "(RISK:[ \\t]*pricing|PRICING CORE)", "(RISK:[ \\t]*pricing)"),
    ("a START never ended let through", 'raise Refused("a marker START never ended, line %d" % at)', "pass"),
    ("the diff's context read as changed", '"-U0"', '"-U3"'),
)


def _mark_cases(mod):
    """The marked spans' cases, run on `mod` (this module or a loosened copy): what each got wrong."""
    wrong = []
    for what, text, expected in mod.MARK_SHAPES:
        try:
            got = mod.spans(text)
        except mod.Refused:
            got = None
        if got != expected:
            wrong.append("marks: %s: expected %r, got %r" % (what, expected, got))
    for what, head, refused in mod.MARK_CASES:
        with tempfile.TemporaryDirectory() as d:
            sha, changed = mod._mark_repo(d, head)
            if (mod._asks(mod.marked, d, "origin/main", sha, changed) != "ok") != refused:
                wrong.append("marked: %s: expected %s" % (what, "risky" if refused else "ordinary"))
    return wrong


def _mark_repo(d, head):
    """A product's repository in d: MARK_BASE on main, `head` committed on top. Returns (head sha, changed file)."""
    def git(*args):
        return subprocess.run(["git", "-C", d, "-c", "user.name=t", "-c", "user.email=t@t"] + list(args),
                              capture_output=True, text=True, check=True, timeout=60).stdout.strip()
    git("init", "-q", "-b", "main")
    for files in (MARK_BASE, head):
        for f, text in files.items():
            if text is None:
                os.remove(os.path.join(d, f))
            else:
                with open(os.path.join(d, f), "w", encoding="utf-8") as fh:
                    fh.write(text)
        git("add", "-A")
        git("commit", "-qm", "x")
        if files is MARK_BASE:
            git("update-ref", "refs/remotes/origin/main", "HEAD")
    changed = os.path.join(d, ".changed")
    with open(changed, "wb") as fh:
        fh.write(subprocess.run(["git", "-C", d, "diff", "-z", "--name-only", "--no-renames", "origin/main...HEAD"],
                                capture_output=True, check=True, timeout=60).stdout)
    return git("rev-parse", "HEAD"), changed


def _selftest():
    bad = []

    def want(what, got, expected):
        if got != expected:
            bad.append("%s: expected %r, got %r" % (what, expected, got))

    def refuses(what, fn, *args):
        got = _asks(fn, *args)
        if got == "ok":
            bad.append("%s: was let through" % what)
        return got

    # The README's list, on made-up shapes and then on the real README, which
    # is the one the workflows read: a README edit that breaks the list fails
    # this build rather than a read.
    line = "- **X** — `https://github.com/Adonis80/%s` (private). One line.\n"
    page = "# t\n\n## Products under this rulebook\n\nProse.\n\n" + line + "\n## Next\n- `https://github.com/Adonis80/other`\n"
    want("a listed product", _asks(listed, page % "alpha", "Adonis80/alpha"), "ok")
    want("a product not listed", "not a product" in refuses("unlisted", listed, page % "alpha", "Adonis80/beta"), True)
    want("a name the owner does not have", "OWNER/NAME" in refuses("elsewhere", listed, page % "alpha", "Evil/alpha"), True)
    want("a name with a path in it", "OWNER/NAME" in refuses("path", listed, page % "alpha", "Adonis80/alpha/../x"), True)
    want("a name by prefix only", "not a product" in refuses("prefix", listed, page % "alpha", "Adonis80/alph"), True)
    want("a name by case only", "not a product" in refuses("case", listed, page % "alpha", "Adonis80/Alpha"), True)
    want("a repository named after the list ends", "not a product" in refuses("later section", listed, page % "alpha", "Adonis80/other"), True)
    want("no section", "no 'Products" in refuses("no section", listed, "# t\n", "Adonis80/alpha"), True)
    refuses("an empty list", listed, "# t\n\n## Products under this rulebook\n\nProse only.\n", "Adonis80/alpha")
    broken = "# t\n\n## Products under this rulebook\n\n- **X** no link here\n" + line % "alpha"
    want("a bullet naming none", "names 0" in refuses("a bullet naming none", listed, broken, "Adonis80/alpha"), True)
    twice = "# t\n\n## Products under this rulebook\n\n- `https://github.com/Adonis80/a` and `https://github.com/Adonis80/b`\n"
    want("a bullet naming two", "names 2" in refuses("a bullet naming two", listed, twice, "Adonis80/a"), True)
    dup = "# t\n\n## Products under this rulebook\n\n" + line % "alpha" + line % "ALPHA"
    want("a repository twice", "twice" in refuses("a duplicate", listed, dup, "Adonis80/alpha"), True)
    import os
    here = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(here, "..", "README.md"), encoding="utf-8") as f:
        real = products(f.read())
    want("the real README lists Hemz OS", "Adonis80/Hemz-OS" in real, True)
    want("the real README's list is not empty or doubled", len(real) == len(set(real)) >= 1, True)

    # The ready mark.
    parent = _commit("x", sha=BENEATH, parents=())
    want("a ready mark", _asks(ready, _commit(_mark()), parent, HEAD), "ok")
    # A second round: the first mark is still in the pull request's history beneath a fix,
    # and the new mark names the fix. Nothing about the earlier commits is asked.
    fix = _commit("a fix", sha="f" * 40, parents=(BENEATH,))
    again = _commit(_mark(parent="f" * 40), parents=("f" * 40,))
    want("a second mark, above a fix, above the first mark", _asks(ready, again, fix, HEAD), "ok")
    for what, commit, parent_json in (
        ("another commit than asked", _commit(_mark(), sha="c" * 40), parent),
        ("no mark", _commit("fix things"), parent),
        ("ready without a parent", _commit("Review-Ready: yes\n"), parent),
        ("a parent without ready", _commit("Review-Parent: %s\n" % BENEATH), parent),
        ("ready said no", _commit(_mark().replace("yes", "no")), parent),
        ("ready said twice", _commit(_mark() + "Review-Ready: yes\n"), parent),
        ("a different case of the key", _commit(_mark().replace("Review-Ready", "review-ready")), parent),
        ("the mark indented", _commit(_mark().replace("Review-Ready", "  Review-Ready")), parent),
        ("a variant line beside the real two", _commit(_mark(extra="review-ready: yes\n")), parent),
        ("a spaced variant beside the real two", _commit(_mark(extra="Review-Parent : %s\n" % BENEATH)), parent),
        ("the parent id short", _commit(_mark(parent="b" * 39)), parent),
        ("the parent id upper case", _commit(_mark(parent="B" * 40)), parent),
        ("the wrong parent named", _commit(_mark(parent="d" * 40)), parent),
        ("a merge commit", _commit(_mark(), parents=(BENEATH, "e" * 40)), parent),
        ("a root commit", _commit(_mark(), parents=()), parent),
        ("the parent fetched is another", _commit(_mark()), _commit("x", sha="f" * 40, parents=())),
        ("files changed", _commit(_mark(), tree="t2"), parent),
        ("an answer in another shape", {"sha": HEAD}, parent),
    ):
        refuses(what, ready, commit, parent_json, HEAD)
    want("a CRLF message", _asks(ready, _commit(_mark().replace("\n", "\r\n")), parent, HEAD), "ok")

    # The product's own check.
    green = {"check_runs": [_run(name=VERIFY, ago=9)]}
    want("verify green", _asks(verified, green, HEAD), "ok")
    refuses("verify absent", verified, {"check_runs": []}, HEAD)
    refuses("another check's name", verified, {"check_runs": [_run(name="check", ago=9)]}, HEAD)
    refuses("verify on another commit", verified, {"check_runs": [_run(name=VERIFY, sha="c" * 40)]}, HEAD)
    refuses("verify running", verified, {"check_runs": [_run(name=VERIFY, status="in_progress", conclusion=None)]}, HEAD)
    for conclusion in ("failure", "neutral", "cancelled", "skipped", "timed_out", None):
        refuses("verify " + str(conclusion), verified, {"check_runs": [_run(name=VERIFY, conclusion=conclusion)]}, HEAD)
    refuses("a re-run that failed after a pass", verified,
            {"check_runs": [_run(name=VERIFY, ago=20), _run(name=VERIFY, conclusion="failure", ago=2)]}, HEAD)
    want("a re-run that passed after a failure", _asks(verified, {"check_runs": [
        _run(name=VERIFY, conclusion="failure", ago=20), _run(name=VERIFY, ago=2)]}, HEAD), "ok")
    refuses("not a list", verified, {"check_runs": "none"}, HEAD)

    # Has it been read: every state, and who may ask again.
    def state(*runs):
        return read_state({"check_runs": list(runs)}, APP, HEAD, NOW)

    want("no runs", state(), "none")
    want("a clean verdict", state(_run()), "read")
    want("findings", state(_run(conclusion="failure")), "read")
    want("a read in progress", state(_run(status="in_progress", conclusion=None, ago=10)), "running")
    want("a read just queued", state(_run(status="queued", conclusion=None, ago=0)), "running")
    want("a read lost past the hour", state(_run(status="in_progress", conclusion=None, ago=61)), "failed")
    want("an hour exactly is lost", state(_run(status="in_progress", conclusion=None, ago=60)), "failed")
    want("a run with no start time", state({**_run(status="in_progress", conclusion=None), "started_at": None}), "failed")
    for conclusion in ("neutral", "cancelled", "timed_out", "skipped", "stale", "action_required"):
        want("a run closed " + conclusion, state(_run(conclusion=conclusion)), "failed")
    want("a verdict beats a failed run", state(_run(conclusion="neutral", ago=30), _run(ago=3)), "read")
    want("running beats failed", state(_run(conclusion="neutral", ago=30), _run(status="in_progress", conclusion=None, ago=2)), "running")
    want("a verdict beats running", state(_run(status="in_progress", conclusion=None), _run(conclusion="failure")), "read")
    want("someone else's App", state(_run(app=1)), "none")
    want("the right App, another name", state(_run(name="juku-review")), "none")
    want("another commit", state(_run(sha="c" * 40)), "none")
    want("no App at all", state({"name": REVIEWER_CHECK, "head_sha": HEAD, "status": "completed", "conclusion": "success"}), "none")
    want("an App id as text", state(_run(app=str(APP))), "none")
    free = dict(_run(conclusion="neutral"), output={"title": FREE + ": the weekly limit admits no read now"})
    want("a budget park that sent nothing is no read", state(free), "none")
    want("a free park beside a verdict", state(free, _run()), "read")
    want("a budget park that spent", state(dict(free, output={"title": "Did not read: budget refused: the key's own limit"})), "failed")
    want("the free words on a run that did not end neutral", state(dict(free, conclusion="cancelled")), "failed")
    want("the free words in the summary, not the title", state(dict(free, output={"summary": FREE})), "failed")
    want("the free words from another App", state(dict(free, app={"id": 1})), "none")
    for runs, again, expected in (
        ([], False, "ok"), ([_run()], False, "read"), ([_run()], True, "read"),
        ([_run(status="in_progress", conclusion=None)], True, "running"),
        ([_run(conclusion="neutral")], False, "did not finish"), ([_run(conclusion="neutral")], True, "ok"),
        ([dict(_run(conclusion="neutral"), output={"title": FREE + ": x"})], False, "ok"),
    ):
        got = _asks(unread, {"check_runs": runs}, APP, HEAD, NOW, again)
        want("asking %s again=%s" % (len(runs), again), expected in got or got == expected, True)

    # The command line: its exit statuses are what the workflows read.
    import contextlib
    import io

    def cli(*args):
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            code = main(["reads.py", *args])
        return code, out.getvalue()

    with tempfile.TemporaryDirectory() as d:
        def put(name, value):
            path = os.path.join(d, name)
            with open(path, "w", encoding="utf-8") as f:
                f.write(value if isinstance(value, str) else json.dumps(value))
            return path

        readme = put("README.md", page % "alpha")
        want("cli: a listed product", cli("product", "Adonis80/alpha", readme), (0, "ok\n"))
        want("cli: an unlisted product", cli("product", "Adonis80/beta", readme)[0], 1)
        want("cli: a missing file", cli("product", "Adonis80/alpha", os.path.join(d, "none"))[0], 2)
        want("cli: the list names each product once", cli("list", readme)[1].split(), ["Adonis80/alpha"])
        want("cli: a broken list is a refusal, not an empty one", cli("list", put("bad.md", "# t\n"))[0], 1)
        want("cli: ready", cli("ready", put("c", _commit(_mark())), put("p", parent), HEAD)[0], 0)
        want("cli: not ready", cli("ready", put("c", _commit("x")), put("p", parent), HEAD)[0], 1)
        want("cli: verified", cli("verify", put("v", green), HEAD)[0], 0)
        want("cli: not verified", cli("verify", put("v2", {"check_runs": []}), HEAD)[0], 1)
        want("cli: unread", cli("state", put("s", {"check_runs": []}), HEAD, str(APP))[0], 0)
        want("cli: read", cli("state", put("s2", {"check_runs": [_run(ago=0)]}), HEAD, str(APP))[0], 1)
        # The command line reads the real clock, so these stamp their runs by it: one
        # begun years ago and never closed has lost its runner, which `--again` lets a
        # builder re-ask; one begun a moment ago is being read, which nothing lets through.
        lost = dict(_run(status="in_progress", conclusion=None), started_at="2020-01-01T00:00:00Z")
        going = dict(lost, started_at=datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"))
        stale = put("s3", {"check_runs": [lost]})
        want("cli: lost run refused", cli("state", stale, HEAD, str(APP))[0], 1)
        want("cli: lost run, asked again", cli("state", stale, HEAD, str(APP), "--again")[0], 0)
        want("cli: running run, asked again", cli("state", put("s4", {"check_runs": [going]}), HEAD, str(APP), "--again")[0], 1)
        want("cli: an App id that is not a number", cli("state", stale, HEAD, "x")[0], 2)
        want("cli: an unknown word after the id", cli("state", stale, HEAD, str(APP), "--force")[0], 2)
        want("cli: not json", cli("verify", put("junk", "{"), HEAD)[0], 2)
        want("cli: no arguments", cli()[0], 2)
        want("cli: no arguments prints the usage, not only the title", "reads.py product" in cli()[1] and "reads.py ready" in cli()[1], True)
        # A refusal prints fixed words only, never what the product's JSON held.
        secret = _commit("a private message " + _mark())
        code, said = cli("ready", put("c2", secret), put("p2", _commit("x", sha="f" * 40, parents=())), HEAD)
        want("cli: a refusal quotes nothing", (code, "private" in said), (1, False))

    # The marked spans (#218): each shape read or refused, each change replayed
    # on a real repository, and the command line's three answers.
    bad.extend(_mark_cases(sys.modules[__name__]))
    with open(__file__, encoding="utf-8") as f:
        source = f.read()
    # The rules above the list of loosenings, which names their words too.
    cut = source.index("# Each must turn some case above")
    for what, old, new in MARK_LOOSENINGS:
        if source[:cut].count(old) != 1:
            bad.append("the loosening '%s' no longer applies; rewrite it against the file" % what)
            continue
        copy = types.ModuleType("loosened")
        copy.__file__ = __file__
        exec(compile(source[:cut].replace(old, new, 1) + source[cut:], __file__, "exec"), copy.__dict__)
        if not _mark_cases(copy):
            bad.append("with %s every marked-span case still passes: the guard for it is gone" % what)
    for what, head, refused in MARK_CASES:
        with tempfile.TemporaryDirectory() as d:
            sha, changed = _mark_repo(d, head)
            if what.startswith("Hemz-OS#159"):
                want("cli: a marked change is a refusal", cli("marked", d, "origin/main", sha, changed)[0], 1)
                want("cli: an unreadable change is a mistake", cli("marked", d, "origin/main", "f" * 40, changed)[0], 2)
            if what.startswith("an unmarked file"):
                want("cli: an unmarked change goes ahead", cli("marked", d, "origin/main", sha, changed)[0], 0)

    if bad:
        for b in bad:
            print("  reads selftest: %s" % b)
        print("reads selftest failed: %d case(s)" % len(bad))
        return 1
    print("ok: the product read's rules — the README's list read exactly (and the real one read), the "
          "ready mark, the product's own check, the three kinds of not read, and a change to a product's "
          "marked spans (%d changes replayed, %d loosenings refused) — refuse every case put to them and quote "
          "nothing a product holds" % (len(MARK_CASES), len(MARK_LOOSENINGS)))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
