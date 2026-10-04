#!/usr/bin/env python3
"""The asker: which of a product's pull requests are ready to be read, and the ask (decision 0013, #148).

    ask.py OWNER/NAME [--dispatch]
    ask.py --selftest

Environment: PRODUCT_TOKEN, a token that reads this one product (contents, pull
requests and checks, read alone); REVIEWER_APP_ID; and GH_TOKEN, this
repository's own token, which reads the runs asked for already and, with
--dispatch, may start a workflow here.

It lists the product's open pull requests and picks out each whose head is the
builder's ready mark, whose own `verify` passed on it, and which has never been
read. Those are the very three things review-product.yml checks again before it
pays for a read, and they are asked of the same rules in reads.py, so the asker
cannot ask for what the reviewer would refuse. Anything else is left: a draft, a
fork, work still moving, a check that has not passed, a commit already read or
being read, and a read that began and never finished, which nothing retries by
itself: a builder looks, and asks with `again`. Without --dispatch it only says
what it would ask, which is how it is tried before anything runs by itself.

It is run on a timer (every ten minutes, the Chairman's ruling of 4 October
2026), so two more things hold. A commit is asked about once: review-product.yml
names each run for its pull request and commit, so a commit a run was already
started for is left, whatever became of that run. And a question GitHub does not
answer is a failed run (exit 3), never read as "nothing is ready": a token that
lost a right would otherwise look like a product with no work.

The log is public: it names a product, a pull request's number and a commit,
which point at the work without holding any of it, and counts. Nothing else.
"""
import os
import sys
from datetime import datetime, timezone

# The scripts import one another; a cache written beside them would be a file no list names.
sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import reads  # noqa: E402

HERE_REPO = "Adonis80/how-we-build"
WORKFLOW = "review-product.yml"
PAGES = 3          # of 100 open pull requests: more than that is a product to look at by hand


class Unanswered(Exception):
    """GitHub did not answer a question the asker needed answered. Not a rule's refusal."""


class Trouble(Exception):
    """The run asked what it could and some question went unanswered: the run is red for it."""


def _list(call, path):
    """Every page of a list, up to three; a failed answer is a refusal, never an empty list."""
    out = []
    for page in range(1, PAGES + 1):
        status, batch = call("GET", "%s%sper_page=100&page=%d" % (path, "&" if "?" in path else "?", page))
        if status != 200 or not isinstance(batch, list):
            raise reads.Refused("GitHub answered %s to %s" % (status, path.split("?")[0]))
        out += batch
        if len(batch) < 100:
            break
    return out


def ready_to_read(call, repo, sha, app_id, now):
    """None if this commit may be asked for now, else the rule's own words for why not."""
    def get(path):
        status, body = call("GET", "/repos/%s/%s" % (repo, path))
        if status != 200:
            raise Unanswered("GitHub answered %s to %s" % (status, path.split("?")[0]))
        return body

    try:
        commit = get("commits/%s" % sha)
        parents = commit.get("parents") or []
        parent = get("commits/%s" % parents[0]["sha"]) if len(parents) == 1 else {}
        reads.ready(commit, parent, sha)
        reads.verified(get("commits/%s/check-runs?check_name=%s&filter=all&per_page=100" % (sha, reads.VERIFY)), sha)
        reads.unread(get("commits/%s/check-runs?check_name=%s&app_id=%s&filter=all&per_page=100"
                         % (sha, reads.REVIEWER_CHECK, app_id)), app_id, sha, now)
    except reads.Refused as why:
        return str(why)
    except (KeyError, TypeError, IndexError):
        raise Unanswered("an answer in a shape the asker does not read")
    return None


def candidates(call, repo, app_id, now):
    """([(pull request, head commit)] to ask for, how many were left and why in brief, what went unanswered)."""
    chosen, left, trouble = [], {}, []
    for pr in _list(call, "/repos/%s/pulls?state=open" % repo):
        number, head = pr.get("number"), (pr.get("head") or {})
        sha = head.get("sha")
        if not isinstance(number, int) or not isinstance(sha, str):
            left["a pull request in a shape the asker does not read"] = left.get("a pull request in a shape the asker does not read", 0) + 1
            continue
        if pr.get("draft") is not False:
            why = "a draft"
        elif (head.get("repo") or {}).get("full_name") != repo:
            why = "a fork's pull request"
        else:
            try:
                why = ready_to_read(call, repo, sha, app_id, now)
            except Unanswered as unanswered:
                trouble.append("#%s: %s" % (number, unanswered))
                continue
        if why is None:
            chosen.append((number, sha))
        else:
            left[why.split(";")[0].split(",")[0]] = left.get(why.split(";")[0].split(",")[0], 0) + 1
    return chosen, left, trouble


def asked_titles(send):
    """The names of the latest hundred runs of review-product.yml that a person or a timer started.

    A run is named `Review OWNER/NAME#PR at SHA`, so what was already asked about is a list of
    names. A list that cannot be had is no list: the caller asks for nothing."""
    status, body = send("GET", "/repos/%s/actions/workflows/%s/runs?event=workflow_dispatch&per_page=100" % (HERE_REPO, WORKFLOW))
    if status != 200 or not isinstance(body, dict) or not isinstance(body.get("workflow_runs"), list):
        raise Unanswered("GitHub answered %s to the list of reads already asked for" % status)
    return {r.get("display_title") for r in body["workflow_runs"] if isinstance(r, dict)}


def dispatch(call, repo, number, sha):
    """Start review-product.yml on main for one commit. 204 is the only yes."""
    status, _ = call("POST", "/repos/%s/actions/workflows/%s/dispatches" % (HERE_REPO, WORKFLOW),
                     {"ref": "main", "inputs": {"repo": repo, "pr": str(number), "sha": sha}})
    if status != 204:
        raise reads.Refused("GitHub answered %s to the dispatch for %s#%s" % (status, repo, number))


def run(call, send, repo, app_id, now, do_dispatch, say=print):
    """Ask for what is ready and not asked about before; return how many. Raises Trouble, after
    asking what it safely could, if any question went unanswered."""
    reads.listed(open(os.path.join(HERE, "..", "README.md"), encoding="utf-8").read(), repo)
    chosen, left, trouble = candidates(call, repo, app_id, now)
    asked = set()
    if chosen:
        try:
            asked = asked_titles(send)
        except Unanswered as unanswered:
            # Not knowing what was asked, nothing is asked: a commit would be asked about twice.
            trouble.append(str(unanswered))
            left["not asked: it could not be told what was asked already"] = len(chosen)
            chosen = []
    fresh = []
    for number, sha in chosen:
        if "Review %s#%s at %s" % (repo, number, sha) in asked:
            left["already asked, and not read yet"] = left.get("already asked, and not read yet", 0) + 1
        else:
            fresh.append((number, sha))
    for number, sha in fresh:
        say("%s %s#%s at %s" % ("ask:" if do_dispatch else "would ask:", repo, number, sha))
        if do_dispatch:
            dispatch(send, repo, number, sha)
    say("%s: %d to ask, %d left%s" % (repo, len(fresh), sum(left.values()),
                                     "".join("; %d %s" % (n, why) for why, n in sorted(left.items()))))
    if trouble:
        raise Trouble("%d question(s) GitHub did not answer: %s" % (len(trouble), "; ".join(trouble)))
    return len(fresh)


# ---------------------------------------------------------------- the selftest

def _selftest():
    import contextlib
    import io
    import re
    bad = []
    now = reads.NOW
    app, repo = reads.APP, "Adonis80/Hemz-OS"

    def want(what, got, expected):
        if got != expected:
            bad.append("%s: expected %r, got %r" % (what, expected, got))

    class Product:
        """A product's API, in memory: open pull requests and what each commit says."""

        def __init__(self, prs, runs=()):
            self.prs, self.dispatched, self.check_queries = prs, [], []
            self.runs, self.runs_status = list(runs), 200

        def __call__(self, method, path, body=None):
            if method == "POST":
                self.dispatched.append(body)
                if self.sent == 204:
                    i = body["inputs"]
                    self.runs.append("Review %s#%s at %s" % (i["repo"], i["pr"], i["sha"]))
                return self.sent, None
            path, _, query = path.partition("?")
            # Whatever repository is asked of, the same answers: so only the README's list,
            # and not a 404 from this fake, can stop a product that is not on it.
            path = re.sub(r"^/repos/[^/]+/[^/]+", "", path)
            sha_of = {p["sha"]: p for p in self.prs}
            if path == "/actions/workflows/review-product.yml/runs":
                return self.runs_status, {"workflow_runs": [{"display_title": t} for t in self.runs]}
            if path == "/pulls":
                return 200, [p["api"] for p in self.prs]
            tail = path.split("/commits/", 1)[-1]
            if tail == reads.BENEATH:
                return 200, reads._commit("x", sha=reads.BENEATH, parents=())
            if tail.endswith("/check-runs"):
                self.check_queries.append(query)
                sha = tail.split("/")[0]
                name = query.split("check_name=")[1].split("&")[0]
                return 200, {"check_runs": [r for r in sha_of[sha][name]]}
            if tail in sha_of:
                return 200, sha_of[tail]["commit"]
            return 404, None

        sent = 204

    def make(number, **kw):
        sha = ("%040x" % number)
        marked = dict(message=reads._mark(), tree="t1")
        marked.update(kw.get("commit", {}))
        pr = {"number": number, "sha": sha,
              "api": {"number": number, "draft": kw.get("draft", False),
                      "head": {"sha": sha, "repo": {"full_name": kw.get("fork", repo)}}},
              "commit": reads._commit(marked["message"], sha=sha, tree=marked["tree"]),
              reads.VERIFY: kw.get("verify", [reads._run(name=reads.VERIFY, sha=sha, ago=9)]),
              reads.REVIEWER_CHECK: kw.get("read", [])}
        return pr

    def go(prs, dispatch_=False, runs=()):
        api = Product(prs, runs)
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            n = run(api, api, repo, app, now, dispatch_)
        return n, api, out.getvalue()

    n, api, said = go([make(1)])
    want("a ready commit is asked for", (n, api.dispatched), (1, []))
    want("every check-run question asks for all of them, never the latest of each name",
         bool(api.check_queries) and all("filter=all" in q for q in api.check_queries), True)
    want("without --dispatch it only says", "would ask: %s#1 at %040x" % (repo, 1) in said, True)
    n, api, said = go([make(1)], dispatch_=True)
    want("with --dispatch it asks once, exactly", api.dispatched,
         [{"ref": "main", "inputs": {"repo": repo, "pr": "1", "sha": "%040x" % 1}}])
    want("and never asks for `again`", "again" in str(api.dispatched), False)

    left_alone = (
        ("a draft", make(2, draft=True)),
        ("a fork's pull request", make(3, fork="Evil/x")),
        ("a head that is no ready mark", make(4, commit={"message": "just a fix"})),
        ("files changed under the mark", make(5, commit={"tree": "t9"})),
        ("verify never ran", make(6, verify=[])),
        ("verify still running", make(7, verify=[reads._run(name=reads.VERIFY, sha="%040x" % 7, status="in_progress", conclusion=None)])),
        ("verify failed", make(8, verify=[reads._run(name=reads.VERIFY, sha="%040x" % 8, conclusion="failure")])),
        ("already read clean", make(9, read=[reads._run(sha="%040x" % 9)])),
        ("already read with findings", make(10, read=[reads._run(sha="%040x" % 10, conclusion="failure")])),
        ("being read now", make(11, read=[reads._run(sha="%040x" % 11, status="in_progress", conclusion=None, ago=3)])),
        ("a read that ended without a verdict", make(12, read=[reads._run(sha="%040x" % 12, conclusion="neutral")])),
        ("a read lost past the hour", make(13, read=[reads._run(sha="%040x" % 13, status="in_progress", conclusion=None, ago=90)])),
    )
    for what, pr in left_alone:
        n, api, said = go([pr], dispatch_=True)
        want("%s is left alone" % what, (n, api.dispatched), (0, []))
    n, api, said = go([make(20, draft=True), make(21), make(22, verify=[]), make(23)], dispatch_=True)
    want("only the ready ones among several", [d["inputs"]["pr"] for d in api.dispatched], ["21", "23"])
    want("the log counts what it left, by reason", "2 to ask, 2 left" in said and "a draft" in said, True)
    # A second round: the first mark was read and left findings, on another commit, and a fix and a
    # new mark followed. The new mark is asked for; nothing about earlier commits stands in its way.
    n, api, said = go([make(40, read=[reads._run(sha="e" * 40, conclusion="failure")])], dispatch_=True)
    want("a second round is asked for", [d["inputs"]["pr"] for d in api.dispatched], ["40"])
    # No pull requests at all is not an error.
    n, api, said = go([], dispatch_=True)
    want("no pull requests", (n, api.dispatched), (0, []))
    # A dispatch GitHub refuses is a failed run, not a quiet one.
    api = Product([make(30)])
    api.sent = 403
    try:
        run(api, api, repo, app, now, True, say=lambda *_: None)
        bad.append("a refused dispatch passed in silence")
    except reads.Refused:
        pass
    # A product the README does not list is never looked at.
    api = Product([make(31)])
    try:
        run(api, api, "Adonis80/elsewhere", app, now, True, say=lambda *_: None)
        bad.append("a product the README does not list was read")
    except reads.Refused:
        pass
    want("and nothing was asked of it", api.dispatched, [])
    # An answer that is an error is a refusal, never an empty list of work.
    class Down(Product):
        def __call__(self, method, path, body=None):
            return 500, None
    try:
        run(Down([]), Down([]), repo, app, now, True, say=lambda *_: None)
        bad.append("a failing GitHub read as no work")
    except reads.Refused:
        pass

    # A commit a run was already started for is not asked about again, whatever became of that run.
    n, api, said = go([make(70)], dispatch_=True, runs=["Review %s#70 at %040x" % (repo, 70)])
    want("a commit already asked about is left", (n, api.dispatched), (0, []))
    want("and the log says so", "already asked" in said, True)
    n, api, said = go([make(71)], dispatch_=True, runs=["Review %s#71 at %040x" % (repo, 72)])
    want("another commit's run is no reason to leave this one", (n, len(api.dispatched)), (1, 1))

    # THE TIMER (the Chairman's ruling of 4 October 2026). This program comes back every ten
    # minutes, so what it did last time is never done again and what went wrong is never retried.
    # Seven ticks over four pull requests: each asked exactly once; a request not yet begun, a
    # request that never became a read, a read begun, a read that ended without a verdict, a
    # read lost past the hour and a read with findings are each left alone; a second round, on a
    # new commit, is asked for once.
    p50, p51 = make(50), make(51)
    p52 = make(52, read=[reads._run(sha="d" * 40, conclusion="failure")])
    world = Product([p50, p51, p52])

    def tick():
        before = len(world.dispatched)
        with contextlib.redirect_stdout(io.StringIO()):
            run(world, world, repo, app, now, True)
        return [d["inputs"]["pr"] for d in world.dispatched[before:]]

    want("tick 1 asks for all three, once each", tick(), ["50", "51", "52"])
    want("tick 2, the asks not yet begun, asks for nothing", tick(), [])
    p50[reads.REVIEWER_CHECK] = [reads._run(sha=p50["sha"], status="in_progress", conclusion=None, ago=3)]
    want("tick 3, one read begun and one that never became a read, asks for nothing", tick(), [])
    p50[reads.REVIEWER_CHECK] = [reads._run(sha=p50["sha"], conclusion="neutral")]
    want("tick 4, a read that ended without a verdict is not retried", tick(), [])
    p50[reads.REVIEWER_CHECK] = [reads._run(sha=p50["sha"], status="in_progress", conclusion=None, ago=90)]
    p52[reads.REVIEWER_CHECK] = [reads._run(sha=p52["sha"], conclusion="failure")]
    want("tick 5, a read lost past the hour and a read with findings are not retried", tick(), [])
    world.prs.append(make(55, read=[reads._run(sha="e" * 40, conclusion="failure")]))
    want("tick 6, a second round on a new commit is asked for", tick(), ["55"])
    want("tick 7, and not again", tick(), [])
    want("over the whole life, each commit was asked about once and `again` never",
         ([d["inputs"]["pr"] for d in world.dispatched], "again" in str(world.dispatched)),
         (["50", "51", "52", "55"], False))

    # A question GitHub does not answer is a failed run, not "nothing to ask": a token that lost
    # a right would otherwise look like a product with no work. What could be asked is still asked.
    class Flaky(Product):
        """GitHub refuses the commit read of pull request 60 and the check-run read of 62."""
        def __call__(self, method, path, body=None):
            if method == "GET" and ("/commits/%040x" % 60 in path or "/commits/%040x/check-runs" % 62 in path):
                return 403, None
            return Product.__call__(self, method, path, body)

    api = Flaky([make(60), make(61), make(62)])
    try:
        run(api, api, repo, app, now, True, say=lambda *_: None)
        bad.append("two unanswered questions ended a run green")
    except Trouble as why:
        want("both unanswered questions are named", "#60" in str(why) and "#62" in str(why), True)
    want("the pull request that could be read was still asked", [d["inputs"]["pr"] for d in api.dispatched], ["61"])
    # A list of what was asked already that cannot be had: nothing is asked, for fear of asking twice.
    api = Product([make(63)])
    api.runs_status = 500
    try:
        run(api, api, repo, app, now, True, say=lambda *_: None)
        bad.append("a list of reads asked that GitHub would not give was read as empty")
    except Trouble:
        pass
    want("and nothing was asked", api.dispatched, [])
    # And a rule's refusal is not that: every case above that was left alone left the run green.

    if bad:
        for b in bad:
            print("  ask selftest: %s" % b)
        print("ask selftest failed: %d case(s)" % len(bad))
        return 1
    print("ok: the asker asks, once and exactly, only for a commit that is the ready mark with its own "
          "check passed and no read begun, leaves a draft, a fork, a read begun or lost, never asks "
          "about a commit twice or retries a read that went wrong across seven timed runs, and fails "
          "the run when GitHub will not answer")
    return 0


def main(argv):
    if argv[1:] == ["--selftest"]:
        return _selftest()
    args = [a for a in argv[1:] if a != "--dispatch"]
    do_dispatch = "--dispatch" in argv[1:]
    if len(args) != 1:
        print(__doc__.split("\n\n")[0])
        return 2
    token, app, here = os.environ.get("PRODUCT_TOKEN", ""), os.environ.get("REVIEWER_APP_ID", ""), os.environ.get("GH_TOKEN", "")
    if not token or not app.isdigit() or not here:
        print("PRODUCT_TOKEN, REVIEWER_APP_ID (a number) and GH_TOKEN (to read what was asked already, "
              "and to dispatch) are read from the environment")
        return 2
    try:
        run(reads.github(token), reads.github(here), args[0], int(app), datetime.now(timezone.utc), do_dispatch)
    except reads.Refused as why:
        print("refused: %s" % why)
        return 1
    except Trouble as why:
        print("trouble: %s" % why)
        return 3
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
