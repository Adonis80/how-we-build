#!/usr/bin/env python3
"""This repository's review gate: green only on a commit the independent reviewer has read clean.

    review-gate.py OWNER/REPO HEAD_SHA TOKEN     the gate, for one commit
    review-gate.py --selftest

Copied into a product by the rulebook's setup script from one reviewed commit of
Adonis80/how-we-build (product-reads/kit/), and changed only there: the
rulebook's own review-gate.py holds this file's verdict to its own on every case
it has, so the two cannot drift. Standard library only.

It asks GitHub for every check run on the commit and counts one thing: the
`juku-reviewer` check run signed by the reviewer's App. The App's id is the whole
of the identity — a repository writer holds no App credential, so nothing a
branch can run produces a check run carrying it, and nothing can edit or delete
one that exists. Nothing is read out of a comment or a submitted review. `success`
and `failure` are the two conclusions the reviewer writes on purpose; any other,
and a run still going, says nothing. A commit is judged by the worst thing said
about it, so asking again never retires a finding: the answer to one is a push.
"""
import json
import sys
import urllib.error
import urllib.parse
import urllib.request

REVIEWER_APP_ID = 5000405
REVIEWER_CHECK = "juku-reviewer"
FINDINGS, CLEAN, UNREAD = "findings", "clean", "unread"
CONCLUSIONS = {"success": CLEAN, "failure": FINDINGS}


def check_run_verdict(run, head):
    """What one check run says about this commit, or None if it says nothing."""
    if (run.get("app") or {}).get("id") != REVIEWER_APP_ID:
        return None
    if run.get("name") != REVIEWER_CHECK:
        return None
    if run.get("head_sha") != head:
        return None
    if run.get("status") != "completed":
        return None
    return CONCLUSIONS.get(run.get("conclusion"))


def verdict(check_runs, head):
    """FINDINGS if the reviewer left any, else CLEAN if it read clean, else UNREAD."""
    said = [check_run_verdict(run, head) for run in check_runs]
    if FINDINGS in said:
        return FINDINGS
    if CLEAN in said:
        return CLEAN
    return UNREAD


def reason(answer, head):
    """One line saying why the gate is shut, in the gate's own voice."""
    if answer == FINDINGS:
        return ("the reviewer read commit %s and left a blocking finding on it — answer it, land "
                "the round's fixes as one push, and mark that push ready; the gate opens on a "
                "commit the reviewer reads with nothing blocking, never on an answer to a finding"
                % head)
    return ("no reviewer has read commit %s — when the round is finished, add one commit that "
            "changes no file, whose message carries `Review-Ready: yes` and `Review-Parent: <the "
            "full id of the commit beneath it>`, each alone on a line; the read follows, and this "
            "check re-runs itself when the verdict lands" % head)


def _pages(url, token):
    """Every page of the commit's check runs. `filter=all`, not the default `latest`:
    on `latest` a findings verdict could be retired by asking again until it came out
    differently."""
    page = 1
    while True:
        query = urllib.parse.urlencode({"filter": "all", "per_page": "100", "page": str(page)})
        req = urllib.request.Request(
            "%s?%s" % (url, query),
            headers={"Authorization": "Bearer " + token, "Accept": "application/vnd.github+json"})
        with urllib.request.urlopen(req) as r:
            batch = json.load(r).get("check_runs", [])
        if not batch:
            return
        for run in batch:
            yield run
        page += 1


def main(argv):
    if argv[1:] == ["--selftest"]:
        return _selftest()
    if len(argv) != 4:
        print("usage: review-gate.py OWNER/REPO HEAD_SHA TOKEN | --selftest")
        return 2
    repo, head, token = argv[1:4]
    try:
        runs = list(_pages("https://api.github.com/repos/%s/commits/%s/check-runs" % (repo, head), token))
    except urllib.error.HTTPError as e:
        print("reason: HTTP %s when asked for the commit's check runs — %s" % (
            e.code, "the workflow's token may not read checks, or GitHub is rate-limiting"
            if e.code in (401, 403) else "no such repository or commit" if e.code == 404
            else "GitHub itself answered with an error; re-run the check"))
        return 2
    answer = verdict(runs, head)
    if answer == CLEAN:
        print("ok: %s has read %s and left nothing on it" % (REVIEWER_CHECK, head))
        return 0
    print("reason: " + reason(answer, head))
    return 1


def _selftest():
    head = "a" * 40

    def run(**kw):
        base = {"app": {"id": REVIEWER_APP_ID}, "name": REVIEWER_CHECK, "head_sha": head,
                "status": "completed", "conclusion": "success"}
        base.update(kw)
        return base

    cases = (
        ("a clean read", [run()], CLEAN),
        ("findings", [run(conclusion="failure")], FINDINGS),
        ("nothing at all", [], UNREAD),
        ("findings beat a clean read", [run(), run(conclusion="failure")], FINDINGS),
        ("findings beat a clean read, either order", [run(conclusion="failure"), run()], FINDINGS),
        ("a read that did not happen", [run(conclusion="neutral")], UNREAD),
        ("a run still going", [run(status="in_progress", conclusion=None)], UNREAD),
        ("a run still going with a verdict-looking conclusion", [run(status="in_progress")], UNREAD),
        ("cancelled", [run(conclusion="cancelled")], UNREAD),
        ("timed out", [run(conclusion="timed_out")], UNREAD),
        ("skipped", [run(conclusion="skipped")], UNREAD),
        ("another App", [run(app={"id": 15368})], UNREAD),
        ("no App", [run(app=None)], UNREAD),
        ("an App id as text", [run(app={"id": str(REVIEWER_APP_ID)})], UNREAD),
        ("another name", [run(name="check")], UNREAD),
        ("another commit", [run(head_sha="b" * 40)], UNREAD),
        ("a clean read of another commit beside findings of this one",
         [run(head_sha="b" * 40), run(conclusion="failure")], FINDINGS),
        ("a clean read beside someone else's findings",
         [run(), run(app={"id": 15368}, conclusion="failure")], CLEAN),
    )
    bad = [what for what, runs, want in cases if verdict(runs, head) != want]
    for what in bad:
        print("  selftest: %s" % what)
    if "`Review-Ready: yes`" not in reason(UNREAD, head) or "blocking finding" not in reason(FINDINGS, head):
        bad.append("the reasons no longer say what to do")
    if bad:
        print("review-gate selftest failed: %d case(s)" % len(bad))
        return 1
    print("ok: the gate counts only the reviewer's own check run on this commit, worst first")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
