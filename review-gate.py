#!/usr/bin/env python3
"""Has the reviewer read THIS commit, and did it leave anything on it?

A review clears only the commit it read, and the reviewer answers in two shapes
that mean opposite things. Findings arrive as a submitted review carrying the
commit id. A clean pass — nothing to say — arrives as a plain comment naming the
commit. Missing the second fails in the good case: a clean pass leaves the check
red for ever, which is how a Juku Perfume pull request sat red overnight on
8 September with the reviewer having read the head and said it was fine. Matching
it loosely fails in the worse direction: on 13 September the reviewer showed that
a substring test passes on "Task Completed for `abc1234`; no review was
performed", so the gate would certify a commit nobody read.

Counting both shapes as one answer — which this gate did until now — fails in a
third direction, and #21 is the proof: it merged on a commit carrying a P1 the
reviewer had posted and nobody had answered, because a read was all the gate
could see. `AGENTS.md` named that gap. So the gate now gives one of four answers
about the head commit, and opens on the first alone:

    clean       read, and the reviewer left nothing on it
    findings    read, and the reviewer left something on it
    no verdict  a review ran on it, but what it found is not on the page yet
    unread      no read of this commit at all

A finding outranks every other answer about the same commit. The answer to a
finding is a push, and a push makes a new commit for the reviewer to read; what
the CTO says about the old one never clears it.

Every shape is matched by its exact form, and --selftest holds the match against
the real ones and the fakes on every run of check.sh — no network, no GitHub, and
it fails the build before a loose rule can pass a commit.
"""

import json
import re
import sys
import urllib.error
import urllib.request

BOT = "chatgpt-codex-connector[bot]"
SUMMARY_MARKER = "codex-pull-request-review-summary"

# The four answers, worst first: a commit is judged by the strongest thing said
# about it, and only CLEAN opens the gate.
FINDINGS = "findings"
CLEAN = "clean"
NO_VERDICT = "no verdict"
UNREAD = "unread"
ORDER = (FINDINGS, CLEAN, NO_VERDICT)


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


def _names_head(line, pattern, head, resolve):
    """Does this line carry a commit id that is this head?

    The shapes carry an abbreviated sha, and a prefix is not a commit: two
    commits can share seven characters. When a resolver is given, the short form
    is resolved back through GitHub and must answer this very head.
    """
    m = pattern.match(line)
    if not m:
        return False
    if resolve is None:
        return True
    return resolve(m.group("sha")) == head


# Codex Review: Didn't find any major issues. Keep them coming!
CLEAN_VERDICT = re.compile(r"Codex Review:\s*Didn't find any major issues[.!]", re.IGNORECASE)


def _says_clean(first):
    """The reviewer's clean pass, as a finished sentence and not a phrase inside one.

    This line is the only thing that opens the gate, so a phrase test will not
    do — the reviewer made that case twice. As a P1 on #21: "Codex Review: Found
    major issues" contains the two words and means the opposite. As a P1 on #24,
    against the tighter phrase that answered it: "Codex Review: Didn't find any
    major issues because the review did not complete" carries the whole verdict
    and still takes it back. Verifying that one turned up its mirror image,
    "Codex Review: I almost didn't find any major issues", which passed too.

    So the verdict is anchored at both ends: nothing may stand before it, and it
    must close with its own full stop, which is where every qualification of the
    sentence has to attach. What is left undefended is a *following* sentence
    that reverses a finished verdict — "…issues. But the review did not
    complete." The alternative is enumerating the encouragements the reviewer
    appends ("Keep it up!", "Keep them coming!"), which jams this gate shut on
    the day it writes a new one. Named here rather than papered over.
    """
    return CLEAN_VERDICT.match(first.replace("\u2019", "'")) is not None


def comment_verdict(body, head, resolve=None):
    """What a plain comment by the reviewer says about this commit.

    Its clean pass names the commit and means nothing was found. Its summary
    table names the commit too, but a completed row says only that a review ran
    — the findings, if there were any, are a separate review — so it proves a
    read and never a clean one.

    This is the one place the gate leans on the reviewer keeping its habits: its
    own blurb says it may signal no findings with a 👍 reaction alone, and a
    reaction names no commit, so the gate cannot read one. If the clean-pass
    comment ever stops arriving, every pull request here stops at "no verdict"
    until somebody teaches this function the new shape. Red is the right way to
    fail — a gate that guessed clean from the absence of findings would be the
    gate this one replaces — but it is a jam, not a quiet one, and the reason
    line says which shape is missing.
    """
    if not body or not body.strip():
        return None
    lines = [ln.strip() for ln in body.splitlines()]
    if _says_clean(body.strip().splitlines()[0]):
        note = _reviewed_note(head)
        if any(_names_head(ln, note, head, resolve) for ln in lines):
            return CLEAN
    if SUMMARY_MARKER in body:
        row = _completed_row(head)
        if any(_names_head(ln, row, head, resolve) for ln in lines):
            return NO_VERDICT
    return None


WITH_FINDINGS = {"COMMENTED", "CHANGES_REQUESTED"}


def review_verdict(review, head):
    """What a review by the reviewer says about this commit.

    It submits a review only when it has something to say, so a submitted review
    is a finding on the commit it names; an approval is the one shape that is
    not. PENDING is a draft nobody has sent; DISMISSED is one somebody took
    back. Neither is a read of this commit, and the old test — login and commit
    id — counted both.
    """
    if review.get("user", {}).get("login") != BOT:
        return None
    if review.get("commit_id") != head:
        return None
    state = review.get("state")
    if state == "APPROVED":
        return CLEAN
    if state in WITH_FINDINGS:
        return FINDINGS
    return None


def verdict(reviews, comments, head, resolve=None):
    """The gate's one answer about the head commit, from the whole page.

    Only the reviewer's own words count: anyone who can comment on a pull
    request can type a clean pass, so a comment by anybody else is not one.
    """
    said = [review_verdict(r, head) for r in reviews]
    said += [comment_verdict(c.get("body"), head, resolve)
             for c in comments if c.get("user", {}).get("login") == BOT]
    for answer in ORDER:
        if answer in said:
            return answer
    return UNREAD


REASONS = {
    FINDINGS: ("the reviewer read commit %s and left findings on it — answer them, land the "
               "round's fixes as one push, and ask once; the gate opens on a commit the reviewer "
               "reads clean, never on an answer to a finding"),
    NO_VERDICT: ("the reviewer has run a review on commit %s but has not posted what it found — "
                 "re-run this check once it has"),
    UNREAD: ("the reviewer has not read commit %s — ask it on the pull request, and when it "
             "has finished, re-run this check"),
}


def _selftest():
    head = "090e429a31cd5f0b2e4d7a1c9b8e6f4d2a1c3b5e"
    other = "29d7b5435bf968d75ac7451c5457d440fcba5a0c"
    summary = (
        "<!-- codex-pull-request-review-summary -->\n\n## Codex Review Summary\n\n"
        "| Review | Status | Commit | Review trigger |\n| --- | --- | --- | --- |\n"
        "| \U0001f4dd **Code Review** | ✅ **Completed** <relative-time datetime=\"x\">x</relative-time> | `090e429` | Manual request |\n"
    )
    running = summary.replace("✅ **Completed**", "\U0001f504 **Running** since")
    clean = "Codex Review: Didn't find any major issues. Keep them coming!\n\n**Reviewed commit:** `090e429a31`\n"
    comment_cases = [
        (clean, head, CLEAN, "the clean pass naming the commit"),
        (clean.replace("Didn't", "Didn’t"), head, CLEAN, "the same, with a curly apostrophe"),
        (summary, head, NO_VERDICT, "the summary's completed row — a read, not a verdict"),
        (summary, other, None, "the summary row for another commit"),
        (running, head, None, "a review still running"),
        (clean.replace("090e429a31", "29d7b543"), head, None, "a clean pass on another commit"),
        ("Codex Review: Found major issues; review did not complete.\n\n**Reviewed commit:** `090e429a31`\n",
         head, None, "a comment that has the words 'major issues' and means the opposite"),
        ("Codex Review: Didn't find any major issues because the review did not complete.\n\n"
         "**Reviewed commit:** `090e429a31`\n", head, None,
         "the whole verdict, taken back by what follows it (the reviewer's P1 on #24)"),
        ("Codex Review: I almost didn't find any major issues.\n\n**Reviewed commit:** `090e429a31`\n",
         head, None, "the same verdict with a qualifier in front of it"),
        (clean.replace("Keep them coming!", "Keep it up!"), head, CLEAN,
         "the clean pass with the reviewer's other encouragement"),
        ("Task Completed for `090e429`; no review was performed", head, None, "a status line that says Completed"),
        ("I have not Reviewed commit `090e429a31`", head, None, "a sentence containing the words"),
        ("Codex Review: Something went wrong. Try again later.\n\n**Reviewed commit:** `090e429a31`\n",
         head, None, "a failed run that names the commit"),
        ("You have reached your Codex usage limits for code reviews.", head, None, "the quota message"),
        ("", head, None, "an empty comment"),
    ]
    review_cases = [
        ({"user": {"login": BOT}, "commit_id": head, "state": "COMMENTED"}, FINDINGS, "a submitted review of this commit"),
        ({"user": {"login": BOT}, "commit_id": head, "state": "CHANGES_REQUESTED"}, FINDINGS, "changes requested on this commit"),
        ({"user": {"login": BOT}, "commit_id": head, "state": "APPROVED"}, CLEAN, "an approval of this commit"),
        ({"user": {"login": BOT}, "commit_id": head, "state": "DISMISSED"}, None, "a review somebody took back"),
        ({"user": {"login": BOT}, "commit_id": head, "state": "PENDING"}, None, "a draft nobody sent"),
        ({"user": {"login": "someone"}, "commit_id": head, "state": "APPROVED"}, None, "an approval by anybody else"),
        ({"user": {"login": BOT}, "commit_id": other, "state": "APPROVED"}, None, "an approval of another commit"),
        ({"user": {"login": BOT}, "commit_id": other, "state": "COMMENTED"}, None, "findings on another commit"),
    ]
    bot = lambda body: {"user": {"login": BOT}, "body": body}
    findings = {"user": {"login": BOT}, "commit_id": head, "state": "COMMENTED"}
    gate_cases = [
        ([], [bot(clean)], CLEAN, "a clean pass and nothing else"),
        ([{"user": {"login": BOT}, "commit_id": head, "state": "APPROVED"}], [], CLEAN,
         "an approval and nothing else"),
        ([findings], [], FINDINGS, "findings on the head"),
        ([findings], [bot(clean)], FINDINGS,
         "a clean pass posted after findings on the same commit — the commit still carries them"),
        ([findings], [bot(summary)], FINDINGS, "findings, with the summary calling the review completed"),
        ([{"user": {"login": BOT}, "commit_id": other, "state": "COMMENTED"}], [bot(clean)], CLEAN,
         "findings on the commit before, a clean pass on this one"),
        ([], [bot(summary)], NO_VERDICT, "a completed review whose verdict is not posted yet"),
        ([], [{"user": {"login": "someone"}, "body": clean}], UNREAD,
         "a clean pass typed by somebody who is not the reviewer"),
        ([], [], UNREAD, "an empty pull request"),
        ([{"user": {"login": BOT}, "commit_id": head, "state": "DISMISSED"}], [], UNREAD,
         "a review somebody took back, and nothing else"),
    ]
    twin = "090e429" + "f" * 33  # another commit sharing the short form
    resolved = {"090e429": twin, "090e429a31": head}
    resolver = lambda sha: resolved.get(sha)
    bad = 0

    def hold(got, want, what):
        if got == want:
            return 0
        print("  selftest: %s — expected %s, got %s" % (what, want, got))
        return 1

    for review, want, what in review_cases:
        bad += hold(review_verdict(review, head), want, what)
    for body, h, want, what in comment_cases:
        bad += hold(comment_verdict(body, h), want, what)
    for reviews, comments, want, what in gate_cases:
        bad += hold(verdict(reviews, comments, head), want, what)
    bad += hold(comment_verdict(summary, head, resolve=resolver), None,
                "a short form that resolves to another commit")
    bad += hold(comment_verdict(clean, head, resolve=resolver), CLEAN,
                "a clean pass whose short form resolves to this head")
    if bad:
        print("review-gate selftest failed: %d case(s)" % bad)
        return 1
    fakes = (sum(1 for c in comment_cases if c[2] is None)
             + sum(1 for r in review_cases if r[1] is None) + 1)
    print("ok: review gate tells a clean read from a commented one, in both shapes and every "
          "state they arrive in, and is fooled by none of the %d fakes" % fakes)
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
    seen = {}

    def resolve(short):
        """The short form, asked of GitHub, must answer this very commit."""
        if short not in seen:
            req = urllib.request.Request(
                "%s/commits/%s" % (api, short),
                headers={"Authorization": "Bearer " + token, "Accept": "application/vnd.github+json"},
            )
            # A refusal from GitHub is not an answer: let it reach the handler
            # below, which says HTTP and why, rather than becoming "the reviewer
            # has not read this commit".
            with urllib.request.urlopen(req) as r:
                seen[short] = json.load(r).get("sha")
        return seen[short]

    try:
        # Both sides of the page, every time: the reviewer's verdict is in one
        # and its findings in the other, and a gate that stopped at the first
        # answer it liked would be the gate this one replaces.
        reviews = list(_pages("%s/pulls/%s/reviews" % (api, num), token))
        comments = list(_pages("%s/issues/%s/comments" % (api, num), token))
        answer = verdict(reviews, comments, head, resolve=resolve)
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
    if answer == CLEAN:
        print("ok: the reviewer has read %s and left nothing on it" % head)
        return 0
    print("reason: " + REASONS[answer] % head)
    return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
