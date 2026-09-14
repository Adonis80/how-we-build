#!/usr/bin/env python3
"""Has the reviewer read THIS commit? The gate's one question, asked in one place.

A review clears only the commit it read, and the reviewer answers in two shapes:
a submitted review, which carries the commit id, and — when it has nothing to say
— a plain comment. Counting only the first fails in the good case: a clean pass
leaves the check red for ever, which is how a Juku Perfume pull request sat red
overnight on 8 September with the reviewer having read the head and said it was
fine. Counting the second loosely fails in the worse direction: on 13 September
the reviewer showed that a substring test passes on "Task Completed for `abc1234`;
no review was performed", so the gate would certify a commit nobody read.

Both shapes are therefore matched by their exact form, and --selftest holds the
match against the real ones and those fakes on every run of check.sh — no network,
no GitHub, and it fails the build before a loose rule can pass a commit.
"""

import json
import re
import sys
import urllib.error
import urllib.request

BOT = "chatgpt-codex-connector[bot]"
SUMMARY_MARKER = "codex-pull-request-review-summary"


def _completed_row(head):
    # | 📝 **Code Review** | ✅ **Completed** <relative-time …>…</relative-time> | `090e429` | Manual request |
    return re.compile(
        r"^\|.*\*\*Code Review\*\*.*\|.*\*\*Completed\*\*.*\|\s*`"
        + r"(?P<sha>" + re.escape(head[:7]) + r"[0-9a-f]*)`\s*\|"
    )


def _reviewed_note(head):
    # **Reviewed commit:** `090e429a31`
    return re.compile(
        r"^\*\*Reviewed commit:\*\*\s*`(?P<sha>" + re.escape(head[:7]) + r"[0-9a-f]*)`\s*$"
    )


def comment_clears(body, head, resolve=None):
    """True only for the reviewer's own two clean shapes, naming this commit.

    The shapes carry an abbreviated sha, and a prefix is not a commit: two
    commits can share seven characters. When a resolver is given, the short form
    is resolved back through GitHub and must answer this very head.
    """
    if not body or not body.strip():
        return False
    lines = [ln.strip() for ln in body.splitlines()]
    def confirmed(line, pattern):
        m = pattern.match(line)
        if not m:
            return False
        if resolve is None:
            return True
        return resolve(m.group("sha")) == head

    if SUMMARY_MARKER in body:
        row = _completed_row(head)
        if any(confirmed(ln, row) for ln in lines):
            return True
    first = body.strip().splitlines()[0]
    if first.startswith("Codex Review:") and "major issues" in first:
        note = _reviewed_note(head)
        if any(confirmed(ln, note) for ln in lines):
            return True
    return False


SUBMITTED = {"APPROVED", "CHANGES_REQUESTED", "COMMENTED"}


def review_clears(review, head):
    """A review counts only if the reviewer submitted it, on this commit.

    PENDING is a draft nobody has sent; DISMISSED is one somebody took back.
    Neither is a read of this commit, and the old test — login and commit id —
    counted both.
    """
    return (review.get("user", {}).get("login") == BOT
            and review.get("commit_id") == head
            and review.get("state") in SUBMITTED)


def _selftest():
    head = "090e429a31cd5f0b2e4d7a1c9b8e6f4d2a1c3b5e"
    other = "29d7b5435bf968d75ac7451c5457d440fcba5a0c"
    summary = (
        "<!-- codex-pull-request-review-summary -->\n\n## Codex Review Summary\n\n"
        "| Review | Status | Commit | Review trigger |\n| --- | --- | --- | --- |\n"
        "| \U0001f4dd **Code Review** | ✅ **Completed** <relative-time datetime=\"x\">x</relative-time> | `090e429` | Manual request |\n"
    )
    running = summary.replace("✅ **Completed**", "\U0001f504 **Running** since")
    clean = "Codex Review: Didn't find any major issues. Keep it up!\n\n**Reviewed commit:** `090e429a31`\n"
    cases = [
        (summary, head, True, "the summary table's completed row"),
        (clean, head, True, "the clean pass naming the commit"),
        (summary, other, False, "the summary row for another commit"),
        (running, head, False, "a review still running"),
        (clean.replace("090e429a31", "29d7b543"), head, False, "a clean pass on another commit"),
        ("Task Completed for `090e429`; no review was performed", head, False, "a status line that says Completed"),
        ("I have not Reviewed commit `090e429a31`", head, False, "a sentence containing the words"),
        ("Codex Review: Something went wrong. Try again later.\n\n**Reviewed commit:** `090e429a31`\n", head, False, "a failed run that names the commit"),
        ("You have reached your Codex usage limits for code reviews.", head, False, "the quota message"),
        ("", head, False, "an empty comment"),
    ]
    review_cases = [
        ({"user": {"login": BOT}, "commit_id": head, "state": "COMMENTED"}, True, "a submitted review of this commit"),
        ({"user": {"login": BOT}, "commit_id": head, "state": "APPROVED"}, True, "an approval of this commit"),
        ({"user": {"login": BOT}, "commit_id": head, "state": "DISMISSED"}, False, "a review somebody took back"),
        ({"user": {"login": BOT}, "commit_id": head, "state": "PENDING"}, False, "a draft nobody sent"),
        ({"user": {"login": "someone"}, "commit_id": head, "state": "APPROVED"}, False, "an approval by anybody else"),
        ({"user": {"login": BOT}, "commit_id": other, "state": "APPROVED"}, False, "an approval of another commit"),
    ]
    twin = "090e429" + "f" * 33  # another commit sharing the short form
    resolved = {"090e429": twin, "090e429a31": head}
    bad = 0
    for review, want, what in review_cases:
        got = review_clears(review, head)
        if got != want:
            bad += 1
            print("  selftest: %s — expected %s, got %s" % (what, want, got))
    got = comment_clears(summary, head, resolve=lambda sha: resolved.get(sha))
    if got:
        bad += 1
        print("  selftest: a short form that resolves to another commit — expected False, got True")
    got = comment_clears(clean, head, resolve=lambda sha: resolved.get(sha))
    if not got:
        bad += 1
        print("  selftest: a clean pass whose short form resolves to this head — expected True, got False")
    for body, h, want, what in cases:
        got = comment_clears(body, h)
        if got != want:
            bad += 1
            print("  selftest: %s — expected %s, got %s" % (what, want, got))
    if bad:
        print("review-gate selftest failed: %d of %d cases" % (bad, len(cases)))
        return 1
    print("ok: review gate matches the reviewer's two shapes, the states it may arrive in, "
          "and none of the %d fakes" % (sum(1 for c in cases if not c[2]) + sum(1 for r in review_cases if not r[1]) + 1))
    return 0


def _pages(url, token):
    page = 1
    while True:
        req = urllib.request.Request(
            "%s?per_page=100&page=%d" % (url, page),
            headers={"Authorization": "Bearer " + token, "Accept": "application/vnd.github+json"},
        )
        with urllib.request.urlopen(req) as r:
            batch = json.load(r)
        if not batch:
            return
        for item in batch:
            yield item
        page += 1


def main(argv):
    if len(argv) == 2 and argv[1] == "--selftest":
        return _selftest()
    if len(argv) != 5:
        print("usage: review-gate.py <owner/repo> <pr-number> <head-sha> <token> | --selftest")
        return 2
    repo, num, head, token = argv[1:5]
    api = "https://api.github.com/repos/%s" % repo
    try:
        for r in _pages("%s/pulls/%s/reviews" % (api, num), token):
            if review_clears(r, head):
                return 0
        seen = {}

        def resolve(short):
            """The short form, asked of GitHub, must answer this very commit."""
            if short not in seen:
                req = urllib.request.Request(
                    "%s/commits/%s" % (api, short),
                    headers={"Authorization": "Bearer " + token, "Accept": "application/vnd.github+json"},
                )
                try:
                    with urllib.request.urlopen(req) as r:
                        seen[short] = json.load(r).get("sha")
                except urllib.error.HTTPError:
                    seen[short] = None
            return seen[short]

        for c in _pages("%s/issues/%s/comments" % (api, num), token):
            if c.get("user", {}).get("login") != BOT:
                continue
            if comment_clears(c.get("body"), head, resolve=resolve):
                return 0
    except urllib.error.HTTPError as e:
        if e.code in (401, 403):
            why = "the workflow's token may not read pull requests (it needs pull-requests: read), or GitHub is rate-limiting"
        elif e.code == 404:
            why = "GitHub found no such repository or pull request — check GITHUB_REPOSITORY and PR_NUMBER"
        elif e.code >= 500:
            why = "GitHub itself answered with an error — re-run the check"
        else:
            why = "GitHub refused the request"
        print("reason: HTTP %s when asked for the reviews — %s" % (e.code, why))
        return 2
    print("reason: the reviewer has not read commit %s — ask it on the pull request, and when it "
          "has finished, re-run this check" % head)
    return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
