#!/usr/bin/env python3
"""Set a new product up for the independent reviewer (decision 0013, #148).

    setup.py NAME --commit SHA [--apply] [--replace-gate] [--display NAME] [--about LINE]
    setup.py --selftest

NAME is the product's repository under Adonis80. SHA is a commit of the rulebook
(Adonis80/how-we-build) that is on main, which is where the starter kit is copied
from: one reviewed commit, never "the latest". It is on main when the merge base of
it and main is itself, which is asked of GitHub's compare and decided from the merge
base, not from the word `status`, which describes main's position and not the
commit's. Before the first real use, run it without --apply twice: once with an old
commit of main, which must be accepted, and once with the head of an unmerged pull
request, which must be refused. Without --apply it only reads, and says what it
would do. With --apply it makes the repository if there is none,
or takes over the one that is, and opens one pull request in it, on the branch
`juku-kit`, that carries the kit: the gate, the wake, `verify`, and a starter
AGENTS.md and roadmap.json where it has none. It never merges anything, and it is
safe to run again: what is already there is left alone, what is on the branch is
not written twice, and an open pull request is reused.

It needs SETUP_TOKEN in the environment: one token that can create a repository
and write code and workflow files into it. It sits on the machine the script is
run from and is never printed, and the script prints no answer GitHub gives it,
only the status and the endpoint, so a private repository's words never reach a
log. The session that built this has no such token; that is why a person runs it.

WHAT IT DOES NOT DO: join the rulebook's map. The README's line, the board's row
and the board's product list are one pull request in the rulebook, and the board
draws four rows today (decision 0007 §1, board/build.py's own fixtures), so a
fifth product's row needs the board to change first. The script prints the lines
that pull request carries, from --display and --about, and changes nothing there.

KIT FILES. `owned` ones are the gate, and are made to match the kit exactly: a
gate that differs from the rulebook's is not the rulebook's gate. But a product that
already has a gate of its own, with its own command line, would be broken by having
it replaced, so a differing file stops the script before anything is written, and
`--replace-gate` is the word that it should be replaced. `starter` ones become the
product's own after the first install, so they are written only where there is no
file, and a product's own `verify` is never overwritten.
"""
import base64
import json
import os
import re
import sys

# The scripts import one another; a cache written beside them would be a file no list names.
sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from reads import github  # noqa: E402  one client, said once

OWNER = "Adonis80"
RULEBOOK = "%s/how-we-build" % OWNER
BRANCH = "juku-kit"
NAME = re.compile(r"^[A-Za-z0-9_][A-Za-z0-9._-]{0,99}$")
SHA = re.compile(r"^[0-9a-f]{40}$")
# (source in product-reads/kit/, target in the product, kind)
KIT = (
    ("review-gate.py", "review-gate.py", "owned"),
    ("gate.yml", ".github/workflows/gate.yml", "owned"),
    ("wake.yml", ".github/workflows/wake.yml", "owned"),
    ("verify.yml", ".github/workflows/verify.yml", "starter"),
    ("AGENTS.starter.md", "AGENTS.md", "starter"),
    ("roadmap.starter.json", "roadmap.json", "starter"),
)


class Refused(Exception):
    pass


def _need(status, path, ok=(200,)):
    if status not in ok:
        raise Refused("GitHub answered %s to %s" % (status, path))


def _text(entry):
    return base64.b64decode(entry["content"]).decode("utf-8")


def kit_from(call, sha):
    """The kit's files at one rulebook commit, which must be on main."""
    if not SHA.match(sha):
        raise Refused("the commit must be named in full: forty lower-case hex characters")
    status, cmp = call("GET", "/repos/%s/compare/%s...main" % (RULEBOOK, sha))
    _need(status, "the rulebook's compare")
    # A commit is on main exactly when the merge base of it and main is itself. The
    # `status` word is main's position relative to the commit, so an old commit of main
    # says `ahead` and an unmerged one that descends from main says `behind`.
    if ((cmp or {}).get("merge_base_commit") or {}).get("sha") != sha:
        raise Refused("that commit is not on the rulebook's main; the kit is copied from a "
                      "commit that has passed its gate, never a branch's")
    files = {}
    for source, _, _ in KIT:
        path = "/repos/%s/contents/product-reads/kit/%s?ref=%s" % (RULEBOOK, source, sha)
        status, entry = call("GET", path)
        _need(status, "the kit's %s" % source)
        files[source] = _text(entry)
    return files


def product_repo(call, name):
    """The repository's record, or None if there is none. Refuses one that is not
    this owner's, not private, archived, or not on `main`."""
    status, repo = call("GET", "/repos/%s/%s" % (OWNER, name))
    if status == 404:
        return None
    _need(status, "the repository")
    if (repo.get("owner") or {}).get("login") != OWNER or repo.get("full_name", "").lower() != ("%s/%s" % (OWNER, name)).lower():
        raise Refused("that repository is not %s's" % OWNER)
    if not repo.get("private"):
        raise Refused("a product's repository is private, and this one is public")
    if repo.get("archived"):
        raise Refused("that repository is archived")
    if repo.get("default_branch") != "main":
        raise Refused("the kit's workflows name `main`, and this repository's default branch is not")
    return repo


def wanted(call, name, kit, ref):
    """What must be written, as [(target, text, why)], against `ref` of the product."""
    changes = []
    for source, target, kind in KIT:
        status, entry = call("GET", "/repos/%s/%s/contents/%s?ref=%s" % (OWNER, name, target, ref))
        if status == 404:
            changes.append((target, kit[source], "missing"))
        else:
            _need(status, "the product's %s" % target)
            if kind == "owned" and _text(entry) != kit[source]:
                changes.append((target, kit[source], "differs from the kit"))
    return changes


def join_lines(name, display, about, today):
    """The README lines the rulebook's join pull request carries. Printed, never applied."""
    return [
        "README, under *Products under this rulebook*:",
        "- **%s** — `https://github.com/%s/%s` (private; joining since %s). %s Open `AGENTS.md`, "
        "then `roadmap.json`." % (display, OWNER, name, today, about),
        "README, under *Where each product's plan lives*:",
        "- **%s** — [`roadmap.json`](https://github.com/%s/%s/blob/main/roadmap.json) on `main`. "
        "On the board: its row, from that file's items." % (display, OWNER, name),
        "build-board.yml's product list: %s/%s=%s" % (OWNER, name, display),
        "board/build.py: %r added to ROWS" % display,
        "All four go in one pull request: the board's selftest holds ROWS to the README, so a "
        "pull request with only some of them turns check.sh red.",
    ]


def settled(call, name, pause, tries=6):
    """The repository just made, once GitHub shows it with a `main`: it makes the two a moment
    apart. Refuses a repository that does not turn out private, on `main`, and its own."""
    import time
    for attempt in range(tries):
        repo = product_repo(call, name)
        status, _ = call("GET", "/repos/%s/%s/git/ref/heads/main" % (OWNER, name))
        if repo is not None and status == 200:
            return repo
        if attempt < tries - 1:
            time.sleep(pause)
    raise Refused("the repository was made, but GitHub did not show it with a main; run this again")


def today():
    import datetime
    d = datetime.date.today()
    return "%d %s %d" % (d.day, d.strftime("%B"), d.year)


def run(call, name, sha, apply, say=print, pause=2, replace_gate=False, display=None, about=None):
    """Do it, or say what would be done. Returns the number of writes made."""
    if not NAME.match(name) or name.endswith(".git"):
        raise Refused("a product's name is letters, digits, dots, dashes and underscores")
    kit = kit_from(call, sha)
    writes = 0
    repo = product_repo(call, name)
    if repo is None:
        say("no repository %s/%s: it would be created, private, with a README on main" % (OWNER, name))
        if apply:
            status, _ = call("POST", "/user/repos", {"name": name, "private": True, "auto_init": True,
                                                     "description": "A Juku product."})
            _need(status, "creating the repository", (201,))
            writes += 1
            say("created %s/%s" % (OWNER, name))
            settled(call, name, pause)
    else:
        say("%s/%s exists, private, on main: it is taken over, nothing in it is replaced "
            "except the gate" % (OWNER, name))
    # Against main. A repository this script has just made is read the same way; one
    # a dry run only imagines has nothing, so every file is listed as missing.
    changes = [(t, kit[s], "missing") for s, t, _ in KIT] if repo is None and not apply \
        else wanted(call, name, kit, "main")
    for target, _, why in changes:
        say("  %s: %s" % (target, why))
    foreign = [t_ for t_, _, why in changes if why == "differs from the kit"]
    if foreign and not replace_gate:
        raise Refused("%s already has its own %s, which differs from the kit's; replacing a gate "
                      "can break the check that uses it, so nothing was written. If it should be "
                      "replaced, say so with --replace-gate" % (name, " and ".join(foreign)))
    if not changes:
        say("the kit is already on main; nothing to open")
        for line in join_lines(name, display or name, about or "<one line on what it is for>", today()):
            say(line)
        return writes
    if not apply:
        say("nothing was written (without --apply)")
        for line in join_lines(name, display or name, about or "<one line on what it is for>", today()):
            say(line)
        return writes
    status, main_ref = call("GET", "/repos/%s/%s/git/ref/heads/main" % (OWNER, name))
    _need(status, "main's head")
    status, _ = call("GET", "/repos/%s/%s/git/ref/heads/%s" % (OWNER, name, BRANCH))
    if status == 404:
        status, _ = call("POST", "/repos/%s/%s/git/refs" % (OWNER, name),
                         {"ref": "refs/heads/%s" % BRANCH, "sha": main_ref["object"]["sha"]})
        _need(status, "the branch", (201,))
        writes += 1
    else:
        _need(status, "the branch")
    for target, text, why in changes:
        status, entry = call("GET", "/repos/%s/%s/contents/%s?ref=%s" % (OWNER, name, target, BRANCH))
        if status == 200 and _text(entry) == text:
            say("  %s is already on %s" % (target, BRANCH))
            continue
        body = {"message": "Juku kit: %s" % target, "branch": BRANCH,
                "content": base64.b64encode(text.encode("utf-8")).decode("ascii")}
        if status == 200:
            body["sha"] = entry["sha"]
        else:
            _need(status, "the file on the branch", (404,))
        status, _ = call("PUT", "/repos/%s/%s/contents/%s" % (OWNER, name, target), body)
        _need(status, "writing %s" % target, (200, 201))
        writes += 1
    status, open_prs = call("GET", "/repos/%s/%s/pulls?head=%s:%s&state=open" % (OWNER, name, OWNER, BRANCH))
    _need(status, "the open pull requests")
    if open_prs:
        say("pull request %s is open already" % open_prs[0]["number"])
    else:
        status, made = call("POST", "/repos/%s/%s/pulls" % (OWNER, name), {
            "title": "Juku kit: the reviewer's gate, and the product's own check",
            "head": BRANCH, "base": "main",
            "body": "Installs the starter kit from %s at %s: a gate that is green only on a "
                    "commit the independent reviewer read clean, the wake that re-runs it when a "
                    "verdict lands, `verify`, and a starter AGENTS.md and roadmap.json where "
                    "there were none. Nothing here is merged by the script that opened it." % (RULEBOOK, sha)})
        _need(status, "opening the pull request", (201,))
        writes += 1
        say("opened pull request %s" % made["number"])
    for line in join_lines(name, display or name, about or "<one line on what it is for>", today()):
        say(line)
    return writes


# ---------------------------------------------------------------- the selftest

class Fake:
    """GitHub, in memory, for the calls this script makes. Counts every write."""

    # The rulebook's history, as a graph of commits and their parents. main's tip is "2".
    # `a` is an old commit of main; `9` is an unmerged commit that descends from main's tip
    # (a pull request's head, say); `8` branched off long ago and main has moved on since.
    GRAPH = {"a" * 40: None, "1" * 40: "a" * 40, "2" * 40: "1" * 40, "9" * 40: "2" * 40, "8" * 40: "a" * 40}
    TIP = "2" * 40

    def compare(self, sha):
        """GitHub's compare of `sha...main`: `status` is where MAIN stands against `sha`, the
        base, so an old commit of main is answered `ahead`, and an unmerged one that descends
        from main is answered `behind`: the opposite of how it reads."""
        if sha not in self.GRAPH:
            return 404, None

        def up(commit):
            chain = []
            while commit:
                chain.append(commit)
                commit = self.GRAPH[commit]
            return chain

        on_main, mine = up(self.TIP), up(sha)
        if sha == self.TIP:
            status, base = "identical", sha
        elif sha in on_main:
            status, base = "ahead", sha
        elif self.TIP in mine:
            status, base = "behind", self.TIP
        else:
            status, base = "diverged", next(c for c in mine if c in on_main)
        return 200, {"status": status, "merge_base_commit": {"sha": base}}

    def __init__(self, kit_dir, repo=None, files=None, late=0, made_as=None):
        self.kit_dir, self.repo = kit_dir, repo
        self.late, self.made_as = late, made_as          # looks before it shows; the shape it is made in
        self.files = dict(files or {})          # product main: path -> text
        self.branch = None                      # None, or {path: text}
        self.prs, self.writes, self.created = [], [], False

    def _kit(self, source):
        with open(os.path.join(self.kit_dir, source), encoding="utf-8") as f:
            return f.read()

    @staticmethod
    def _entry(text, sha="s"):
        return {"content": base64.b64encode(text.encode()).decode(), "sha": sha + str(hash(text) % 997)}

    def __call__(self, method, path, body=None):
        path, _, query = path.partition("?")
        owned = "/repos/%s/" % OWNER
        if path.startswith("/repos/%s/compare/" % RULEBOOK):
            return self.compare(path.split("/compare/", 1)[1].split("...", 1)[0])
        if path.startswith("/repos/%s/contents/product-reads/kit/" % RULEBOOK):
            return 200, self._entry(self._kit(path.rsplit("/", 1)[1]))
        if method == "GET" and re.match(r"^/repos/%s/[^/]+$" % OWNER, path):
            if self.created and self.late > 0:
                self.late -= 1
                return 404, None
            return (200, self.repo) if self.repo else (404, None)
        if method == "POST" and path == "/user/repos":
            self.writes.append("repo")
            self.created, self.made = True, body
            self.repo = dict({"owner": {"login": OWNER}, "full_name": "%s/%s" % (OWNER, body["name"]),
                              "private": True, "archived": False, "default_branch": "main"}, **(self.made_as or {}))
            return 201, {}
        m = re.match(r"^/repos/%s/[^/]+/contents/(.+)$" % OWNER, path)
        if m and method == "GET":
            target, ref = m.group(1), query.split("ref=")[-1]
            store = self.files if ref == "main" else (self.branch or {})
            return (200, self._entry(store[target])) if target in store else (404, None)
        if m and method == "PUT":
            self.writes.append("put " + m.group(1))
            self.branch[m.group(1)] = base64.b64decode(body["content"]).decode()
            return 201, {}
        if path.endswith("/git/ref/heads/main"):
            return 200, {"object": {"sha": "m" * 40}}
        if path.endswith("/git/ref/heads/" + BRANCH):
            return (200, {}) if self.branch is not None else (404, None)
        if path.endswith("/git/refs") and method == "POST":
            self.writes.append("branch")
            self.branch = {}
            return 201, {}
        if path.endswith("/pulls") and method == "GET":
            return 200, list(self.prs)
        if path.endswith("/pulls") and method == "POST":
            self.writes.append("pr")
            self.prs.append({"number": 7})
            return 201, {"number": 7}
        return 500, None


def _selftest():
    here = os.path.dirname(os.path.abspath(__file__))
    kit_dir = os.path.join(here, "kit")
    bad = []
    sha = "a" * 40

    def want(what, got, expected):
        if got != expected:
            bad.append("%s: expected %r, got %r" % (what, expected, got))

    def attempt(fake, name="alpha", commit=sha, apply=True, **kw):
        said = []
        try:
            n = run(fake, name, commit, apply, say=said.append, pause=0, **kw)
            return n, " | ".join(said)
        except Refused as why:
            return None, str(why)

    # The manifest and the folder are the same list, so a file added to one is
    # not left out of the other.
    on_disk = sorted(f for f in os.listdir(kit_dir))
    want("every kit file is in the manifest, and the other way", sorted(s for s, _, _ in KIT), on_disk)
    want("no target is named twice", len(set(t for _, t, _ in KIT)), len(KIT))
    want("every kind is owned or starter", set(k for _, _, k in KIT) <= {"owned", "starter"}, True)

    # A new product: the repository, the branch, six files, one pull request.
    fake = Fake(kit_dir)
    n, said = attempt(fake)
    want("a new product is created and a pull request opened", (n, fake.created, len(fake.prs)), (9, True, 1))
    want("the repository is made private", fake.made.get("private"), True)
    want("all six files are on the branch", sorted(fake.branch), sorted(t for _, t, _ in KIT))
    want("each is the kit's own", all(fake.branch[t] == fake._kit(s) for s, t, _ in KIT), True)
    # GitHub shows a new repository late: the script looks again, and goes on.
    slow = Fake(kit_dir, late=2)
    n, said = attempt(slow)
    want("a repository that shows late is waited for", (n is not None, len(slow.prs)), (True, 1))
    # One that never shows, or comes out public or on another branch, stops it before any file is written.
    for what, odd in (("never shows", dict(late=99)), ("comes out public", dict(made_as={"private": False})),
                      ("comes out on another branch", dict(made_as={"default_branch": "trunk"}))):
        odd_fake = Fake(kit_dir, **odd)
        n, said = attempt(odd_fake)
        want("a repository that %s stops it" % what, (n, [w for w in odd_fake.writes if w != "repo"]), (None, []))
    # Run again against what it made: nothing is written twice.
    fake.writes.clear()
    n, said = attempt(fake)
    want("a second run writes nothing", (n, fake.writes), (0, []))
    # Dry run, for a product that does not exist and for one that does.
    fake = Fake(kit_dir)
    n, said = attempt(fake, apply=False)
    want("a dry run of a new product writes nothing", (n, fake.writes, fake.created), (0, [], False))
    want("and lists every file", all(t in said for _, t, _ in KIT), True)

    repo = {"owner": {"login": OWNER}, "full_name": "%s/alpha" % OWNER, "private": True, "archived": False,
            "default_branch": "main"}
    # Taken over, with a gate of its own that differs from the kit's, and a verify and an
    # AGENTS.md of its own. Replacing the gate could break the check that runs it, so the
    # script stops before it writes anything, and says which file.
    mine = {"review-gate.py": "its own gate\n", ".github/workflows/verify.yml": "name: verify  # theirs\n",
            "AGENTS.md": "Rulebook: x\n", "roadmap.json": "{}"}
    fake = Fake(kit_dir, repo=repo, files=mine)
    n, said = attempt(fake)
    want("a product with a gate of its own is not given another", (n, fake.writes, fake.branch), (None, [], None))
    want("and is told which file", "review-gate.py" in said and "--replace-gate" in said, True)
    n, said = attempt(Fake(kit_dir, repo=repo, files=mine), apply=False)
    want("the dry run says so too", n, None)
    # With the word, the gate is replaced and the product's own verify, AGENTS.md and roadmap are not.
    fake = Fake(kit_dir, repo=repo, files=mine)
    n, said = attempt(fake, replace_gate=True)
    want("told to replace it, the gate is replaced and the missing gate files written",
         sorted(fake.branch), [".github/workflows/gate.yml", ".github/workflows/wake.yml", "review-gate.py"])
    want("the product's own verify, AGENTS.md and roadmap are untouched",
         [t for t in fake.branch if t in ("AGENTS.md", "roadmap.json", ".github/workflows/verify.yml")], [])
    # A product with no gate yet is taken over without the word.
    bare = {k: v for k, v in mine.items() if k != "review-gate.py"}
    fake = Fake(kit_dir, repo=repo, files=bare)
    n, said = attempt(fake)
    want("a product with no gate yet is taken over", (n is not None, sorted(fake.branch)),
         (True, [".github/workflows/gate.yml", ".github/workflows/wake.yml", "review-gate.py"]))
    # Everything already on main: nothing to open.
    full = {t: Fake(kit_dir)._kit(s) for s, t, _ in KIT}
    fake = Fake(kit_dir, repo=repo, files=full)
    n, said = attempt(fake)
    want("a product that has the kit gets no pull request", (n, fake.writes, fake.prs), (0, [], []))
    # An open pull request is reused, not doubled.
    fake = Fake(kit_dir, repo=repo, files=bare)
    fake.branch, fake.prs = {}, [{"number": 3}]
    n, said = attempt(fake)
    want("an open pull request is reused", (len(fake.prs), "pull request 3 is open already" in said), (1, True))

    # What it refuses, each before anything is written.
    refusals = (
        ("a name with a slash", attempt(Fake(kit_dir), name="a/b")),
        ("a name with a space", attempt(Fake(kit_dir), name="a b")),
        ("a name that is only dots", attempt(Fake(kit_dir), name="..")),
        ("a name ending .git", attempt(Fake(kit_dir), name="a.git")),
        ("an empty name", attempt(Fake(kit_dir), name="")),
        ("a short commit", attempt(Fake(kit_dir), commit="abc123")),
        ("a branch name as the commit", attempt(Fake(kit_dir), commit="main")),
        ("an unmerged commit that descends from main, which GitHub answers `behind`", attempt(Fake(kit_dir), commit="9" * 40)),
        ("a commit that branched off and diverged", attempt(Fake(kit_dir), commit="8" * 40)),
        ("a commit GitHub does not know", attempt(Fake(kit_dir), commit="7" * 40)),
        ("another owner's repository", attempt(Fake(kit_dir, repo=dict(repo, owner={"login": "Evil"})))),
        ("a public repository", attempt(Fake(kit_dir, repo=dict(repo, private=False)))),
        ("an archived repository", attempt(Fake(kit_dir, repo=dict(repo, archived=True)))),
        ("a default branch that is not main", attempt(Fake(kit_dir, repo=dict(repo, default_branch="trunk")))),
    )
    for what, (n, said) in refusals:
        if n is not None:
            bad.append("%s was let through" % what)
    fakes = [Fake(kit_dir), Fake(kit_dir, repo=dict(repo, private=False))]
    attempt(fakes[0], commit="9" * 40)
    attempt(fakes[1])
    want("a refusal writes nothing", [f.writes for f in fakes], [[], []])
    # A commit that IS on main is accepted, old or new, however GitHub words the compare.
    for what, commit in (("an old commit of main", "a" * 40), ("a commit in the middle of main", "1" * 40),
                         ("main's tip", "2" * 40)):
        n, said = attempt(Fake(kit_dir), commit=commit)
        want("%s is accepted" % what, n is not None, True)
    want("the fake answers as GitHub does: `ahead` for an old commit of main, `behind` for an unmerged one",
         (Fake(kit_dir).compare("a" * 40)[1]["status"], Fake(kit_dir).compare("9" * 40)[1]["status"],
          Fake(kit_dir).compare("2" * 40)[1]["status"], Fake(kit_dir).compare("8" * 40)[1]["status"]),
         ("ahead", "behind", "identical", "diverged"))

    # The join lines are printed, on every road that succeeds, and carry what it was given.
    for what, kwargs in (("a dry run", dict(apply=False)), ("an install", {}), ("a repeat", {})):
        f = Fake(kit_dir)
        if what == "a repeat":
            attempt(f)
        n, said = attempt(f, display="Alpha", about="A thing for people.", **kwargs)
        want("%s prints the join lines" % what,
             "build-board.yml's product list: Adonis80/alpha=Alpha" in said and "A thing for people." in said
             and "board/build.py: 'Alpha' added to ROWS" in said, True)
    # Asked without a name or a line, it says what is missing and does not invent one.
    n, said = attempt(Fake(kit_dir), apply=False)
    want("without a display name or a line it prints placeholders, not inventions",
         "<one line on what it is for>" in said, True)

    # The command line: a usage that is a usage, and no token is no run.
    import contextlib
    import io
    out = io.StringIO()
    try:
        with contextlib.redirect_stdout(out):
            main(["setup.py", "--help"])
    except SystemExit as stop:
        want("--help exits 0", stop.code, 0)
    want("the usage names the commit and the word for replacing a gate",
         "--commit" in out.getvalue() and "--replace-gate" in out.getvalue() and "--apply" in out.getvalue(), True)
    err = io.StringIO()
    try:
        with contextlib.redirect_stderr(err):
            main(["setup.py"])
        bad.append("no arguments ran")
    except SystemExit as stop:
        want("no arguments is an error, not a run", stop.code, 2)
    saved = os.environ.pop("SETUP_TOKEN", None)
    try:
        with contextlib.redirect_stdout(io.StringIO()):
            want("no token is no run", main(["setup.py", "alpha", "--commit", "a" * 40]), 2)
    finally:
        if saved is not None:
            os.environ["SETUP_TOKEN"] = saved

    # The lines for the rulebook's join are exactly what the product reviewer's own
    # rules read, so a product joined by them is one it will read.
    sys.path.insert(0, here)
    import reads
    lines = join_lines("zed", "Zed", "A thing for people.", "3 October 2026")
    with open(os.path.join(here, "..", "README.md"), encoding="utf-8") as f:
        readme = f.read()
    entry = lines[1] + "\n"
    joined = readme.replace("\nA repository not listed here is not under this rulebook.", "\n" + entry + "\nA repository not listed here is not under this rulebook.", 1)
    try:
        reads.listed(joined, "Adonis80/zed")
        listed = True
    except reads.Refused:
        listed = False
    want("the join line puts a product on the list the reviewer reads", listed, True)
    sys.path.pop(0)

    if bad:
        for b in bad:
            print("  setup selftest: %s" % b)
        print("setup selftest failed: %d case(s)" % len(bad))
        return 1
    print("ok: the setup script makes or takes over a private repository, opens one pull request "
          "with the kit, replaces a gate only when told, writes nothing twice, merges nothing, prints "
          "the lines the rulebook's join carries, accepts a commit that is on main and refuses one that "
          "is not (the fake answers from a commit graph, as GitHub's compare does), and refuses a bad "
          "name and a repository that is not Adonis80's private main")
    return 0


def main(argv):
    if argv[1:] == ["--selftest"]:
        return _selftest()
    import argparse
    ap = argparse.ArgumentParser(prog="setup.py", description=__doc__.split("\n\n")[0])
    ap.add_argument("name", help="the product's repository under %s" % OWNER)
    ap.add_argument("--commit", required=True, help="a commit of the rulebook that is on main, in full")
    ap.add_argument("--apply", action="store_true", help="write; without it, only read and say")
    ap.add_argument("--replace-gate", action="store_true", help="replace a gate the product already has")
    ap.add_argument("--display", help="the product's name as the board shows it")
    ap.add_argument("--about", help="one line on what the product is for")
    args = ap.parse_args(argv[1:])
    token = os.environ.get("SETUP_TOKEN", "")
    if not token:
        print("SETUP_TOKEN is not set; it is read from the environment and never printed")
        return 2
    try:
        run(github(token), args.name, args.commit, args.apply, replace_gate=args.replace_gate,
            display=args.display, about=args.about)
    except Refused as why:
        print("refused: %s" % why)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
