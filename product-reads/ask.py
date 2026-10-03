#!/usr/bin/env python3
"""The asker: which of a product's pull requests are ready to be read, and the ask (decision 0013, #148).

    ask.py OWNER/NAME [--dispatch]
    ask.py --selftest

Environment: PRODUCT_TOKEN, a token that reads this one product (contents, pull
requests and checks, read alone); REVIEWER_APP_ID; and, with --dispatch only,
GH_TOKEN, this repository's own token, which may start a workflow here.

It lists the product's open pull requests and picks out each whose head is the
builder's ready mark, whose own `verify` passed on it, and which has never been
read. Those are the very three things review-product.yml checks again before it
pays for a read, and they are asked of the same rules in reads.py, so the asker
cannot ask for what the reviewer would refuse. Anything else is left: a draft, a
fork, work still moving, a check that has not passed, a commit already read or
being read, and a read that began and never finished, which nothing retries by
itself: a builder looks, and asks with `again`. Without --dispatch it only says
what it would ask, which is how it is tried before anything runs by itself.

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
            raise reads.Refused("GitHub answered %s to %s" % (status, path.split("?")[0]))
        return body

    try:
        commit = get("commits/%s" % sha)
        parents = commit.get("parents") or []
        parent = get("commits/%s" % parents[0]["sha"]) if len(parents) == 1 else {}
        reads.ready(commit, parent, sha)
        reads.verified(get("commits/%s/check-runs?check_name=%s&filter=all&per_page=100" % (sha, reads.VERIFY)), sha)
        reads.unread(get("commits/%s/check-runs?check_name=%s&app_id=%s&filter=all&per_page=100"
                         % (sha, reads.REVIEWER_CHECK, app_id)), app_id, sha, now)
    except (reads.Refused, KeyError, TypeError, IndexError) as why:
        return str(why) if isinstance(why, reads.Refused) else "an answer in a shape the asker does not read"
    return None


def candidates(call, repo, app_id, now):
    """([(pull request, head commit)] to ask for, how many were left and why in brief)."""
    chosen, left = [], {}
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
            why = ready_to_read(call, repo, sha, app_id, now)
        if why is None:
            chosen.append((number, sha))
        else:
            left[why.split(";")[0].split(",")[0]] = left.get(why.split(";")[0].split(",")[0], 0) + 1
    return chosen, left


def dispatch(call, repo, number, sha):
    """Start review-product.yml on main for one commit. 204 is the only yes."""
    status, _ = call("POST", "/repos/%s/actions/workflows/%s/dispatches" % (HERE_REPO, WORKFLOW),
                     {"ref": "main", "inputs": {"repo": repo, "pr": str(number), "sha": sha}})
    if status != 204:
        raise reads.Refused("GitHub answered %s to the dispatch for %s#%s" % (status, repo, number))


def run(call, send, repo, app_id, now, do_dispatch, say=print):
    reads.listed(open(os.path.join(HERE, "..", "README.md"), encoding="utf-8").read(), repo)
    chosen, left = candidates(call, repo, app_id, now)
    for number, sha in chosen:
        say("%s %s#%s at %s" % ("ask:" if do_dispatch else "would ask:", repo, number, sha))
        if do_dispatch:
            dispatch(send, repo, number, sha)
    say("%s: %d to ask, %d left%s" % (repo, len(chosen), sum(left.values()),
                                     "".join("; %d %s" % (n, why) for why, n in sorted(left.items()))))
    return len(chosen)


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

        def __init__(self, prs):
            self.prs, self.dispatched, self.check_queries = prs, [], []

        def __call__(self, method, path, body=None):
            if method == "POST":
                self.dispatched.append(body)
                return self.sent, None
            path, _, query = path.partition("?")
            # Whatever repository is asked of, the same answers: so only the README's list,
            # and not a 404 from this fake, can stop a product that is not on it.
            path = re.sub(r"^/repos/[^/]+/[^/]+", "", path)
            sha_of = {p["sha"]: p for p in self.prs}
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

    def go(prs, dispatch_=False, **env):
        api = Product(prs)
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

    if bad:
        for b in bad:
            print("  ask selftest: %s" % b)
        print("ask selftest failed: %d case(s)" % len(bad))
        return 1
    print("ok: the asker asks, once and exactly, only for a commit that is the ready mark with its own "
          "check passed and no read begun, leaves a draft, a fork, a read begun or lost, and never "
          "asks again by itself")
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
    if not token or not app.isdigit() or (do_dispatch and not here):
        print("PRODUCT_TOKEN, REVIEWER_APP_ID (a number) and, to dispatch, GH_TOKEN are read from the environment")
        return 2
    try:
        run(reads.github(token), reads.github(here or token), args[0], int(app), datetime.now(timezone.utc), do_dispatch)
    except reads.Refused as why:
        print("refused: %s" % why)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
