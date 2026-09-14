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
    findings    read, and whoever read it left something on it
    no verdict  a review ran on it, but what it found is not on the page yet
    unread      no read of this commit at all

A fifth answer arrives with the Chairman's ruling of 14 September 2026: when
Codex will not answer, a Fable 5.1 session reads in its place rather than the
slice parking, and `clean, by the stand-in` opens the gate on that read. It
counts only while Codex has said nothing about the head, and only from the
owner's own comments — see standin_verdict(), which also names what the machine
cannot check about it.

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

# What can be said about a commit. A commit is judged by the strongest of them,
# and only the two clean answers open the gate.
FINDINGS = "findings"
CLEAN = "clean"
STANDIN_CLEAN = "clean, by the stand-in"
NO_VERDICT = "no verdict"
NOT_ASKED = "not asked"
UNREAD = "unread"

STANDIN = "Fable 5.1"
# The whole heading and only the heading, matched as a line and not as a prefix.
# A prefix takes any qualification after it: the reviewer's own example on #26,
# "**Fable 5.1 review requested; no review was performed**", opened this gate —
# the same hole the clean verdict is anchored at both ends against, left open at
# the other end of the same file. A hyphen is allowed where the dash is, because
# a session types this line by hand and a gate jammed by a punctuation mark is a
# gate nobody can obey.
STANDIN_HEADING = "**%s review — in place of Codex.**" % STANDIN

# The ask that must come first: "@codex review", naming this head. The words are
# not this repository's to choose — they are what wakes the reviewer — so this
# cannot drift out of step with the thing it looks for.
ASK = re.compile(r"@codex\s+(security\s+)?review\b", re.IGNORECASE)


# **Verdict:** clean
STANDIN_VERDICT = re.compile(r"^\*\*Verdict:\*\*\s*(?P<verdict>clean|findings)\.?\s*$", re.IGNORECASE)


def _dashes(line):
    return line.replace("—", "-").replace("–", "-")


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


def _reviewed_head(head):
    # Head is `090e429`. — the ask names the commit in prose, not in a fixed
    # line, so this looks for the commit anywhere on it and lets the resolver
    # settle whether the short form is really this one.
    return re.compile(r".*`(?P<sha>" + re.escape(head[:7]) + r"[0-9a-f]*)`")


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


def standin_verdict(body, head, resolve=None):
    """What a stand-in review says about this commit, when Codex will not answer.

    The Chairman's ruling of 14 September 2026: a slice no longer parks when the
    reviewer is silent — a Fable 5.1 session reads it instead, in its own
    context, and its review is posted on the pull request whole. The gate has to
    be able to count that read or the ruling cannot be obeyed, and this is the
    shape it counts:

        **Fable 5.1 review — in place of Codex.**

        **Reviewed commit:** `090e429a31`
        **Verdict:** clean

    Three things are enforced: the heading, so a sentence about a stand-in
    review is not one; the commit, resolved like any other, because a short form
    is not a commit; and — in verdict() — that Codex has said nothing about this
    head, so a stand-in never speaks over the reviewer it stands in for.

    One thing is not, and is named here rather than discovered later: who wrote
    it. This review is posted by the account the CTO holds, not by an identity
    of its own, so the machine reads a shape and trusts a session. That is the
    weakest joint in this gate, and it closes the day a reviewer identity for
    this stack exists on GitHub — the same day `README.md` is already waiting
    for. Until then the pull request says which read it got, and a person can
    see which.
    """
    if not body or not body.strip():
        return None
    lines = [ln.strip() for ln in body.splitlines()]
    if _dashes(lines[0]) != _dashes(STANDIN_HEADING):
        return None
    note = _reviewed_note(head)
    if not any(_names_head(ln, note, head, resolve) for ln in lines):
        return None
    # Every verdict line in the comment, not the first one: a review that says
    # both — because it carries an example of the other shape, or kept an
    # earlier verdict — said findings, and findings are the stronger thing said,
    # here as everywhere else in this gate. The reviewer's P1 on #26: taking the
    # first line opened the gate on a clean line with a finding under it.
    said = [m.group("verdict").lower()
            for m in (STANDIN_VERDICT.match(ln) for ln in lines) if m]
    if "findings" in said:
        return FINDINGS
    return CLEAN if said else None


def asked_codex(mine, head, resolve=None):
    """Was Codex asked to read THIS commit, before anything stood in for it?

    The ask is `@codex review` — the reviewer's own trigger words, so this
    cannot fall out of step with what actually wakes it — and it must name this
    head, the way every other shape here names the commit it means. One ask per
    round is the rule, and a round is a commit, so an ask from the round before
    does not carry.
    """
    note = _reviewed_head(head)
    for c in mine:
        body = c.get("body") or ""
        if not ASK.search(body):
            continue
        if any(_names_head(ln.strip(), note, head, resolve) for ln in body.splitlines()):
            return True
    return False


def verdict(reviews, comments, head, resolve=None, owner=None):
    """The gate's one answer about the head commit, from the whole page.

    Only the reviewer's own words count: anyone who can comment on a pull
    request can type a clean pass, so a comment by anybody else is not one. The
    stand-in is read from the owner's comments alone, and only when `owner` is
    given, so a page read without one answers exactly as it did before there was
    a stand-in at all.

    The order is the rule. A finding — from either of them — outranks
    everything, because the answer to a finding is a push. Codex decides
    whenever it has spoken about this head, including when it has only finished
    and not yet said what it found: a stand-in stands in for silence, never for
    a verdict that is on its way.

    And it stands in only for a silence somebody asked for. A stand-in clean
    counts only where `@codex review` naming this head is on the page, because
    the rule is *ask Codex, then fall through* and a gate that skipped the first
    half would have written down a rule it did not hold. The reviewer's P1 on
    #26, against my own argument that a session willing to skip the ask would
    equally type it: the shape of the ask is not ours to drift, since those are
    the words that wake the reviewer, and the failure this catches is a session
    that forgot rather than one that lied. A stand-in *finding* needs no ask —
    it keeps the head red either way, and nothing is opened by it.
    """
    codex = [review_verdict(r, head) for r in reviews]
    codex += [comment_verdict(c.get("body"), head, resolve)
              for c in comments if c.get("user", {}).get("login") == BOT]
    mine = [c for c in comments
            if owner is not None and c.get("user", {}).get("login") == owner]
    standin = [standin_verdict(c.get("body"), head, resolve) for c in mine]
    if FINDINGS in codex or FINDINGS in standin:
        return FINDINGS
    if CLEAN in codex:
        return CLEAN
    if NO_VERDICT in codex:
        return NO_VERDICT
    if CLEAN in standin:
        return STANDIN_CLEAN if asked_codex(mine, head, resolve) else NOT_ASKED
    return UNREAD


REASONS = {
    # Findings are not attributed to Codex by name: since the stand-in, the read
    # that left them may not have been its own, and a gate that names the wrong
    # reader sends the next session to the wrong place.
    FINDINGS: ("commit %s was read, and findings were left on it — answer them, land the "
               "round's fixes as one push, and ask once; the gate opens on a commit that is "
               "read clean, never on an answer to a finding"),
    NO_VERDICT: ("the reviewer has run a review on commit %s but has not posted what it found — "
                 "re-run this check once it has"),
    NOT_ASKED: ("a stand-in read of commit %s is on the page, but Codex was never asked to read "
                "it — the rule is ask Codex, once, and stand in only for the silence that "
                "follows; post `@codex review` naming this commit, and the stand-in counts if "
                "nothing comes back"),
    # One placeholder, and only one: main() fills these with the head and
    # nothing else, so the stand-in's name is spliced in here rather than there.
    UNREAD: ("the reviewer has not read commit %s — ask it on the pull request, and when it "
             "has finished, re-run this check; if it will not answer at all, a " + STANDIN +
             " read posted in the stand-in shape counts instead"),
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
    standin = (STANDIN_HEADING + "\n\n"
               "**Reviewed commit:** `090e429a31`\n"
               "**Verdict:** clean\n\n"
               "What I checked: the diff and the pages before the pull request's own account.\n")
    standin_findings = standin.replace("**Verdict:** clean", "**Verdict:** findings")
    standin_cases = [
        (standin, head, CLEAN, "a stand-in read that left nothing"),
        (standin_findings, head, FINDINGS, "a stand-in read that left something"),
        (standin.replace("**Fable 5.1 review — in place of Codex.**",
                         "**Fable 5.1 review requested; no review was performed**"), head, None,
         "a heading that carries the name and says the opposite (the reviewer's P1 on #26)"),
        (standin.replace("Codex.**", "Codex.** Or it would have been."), head, None,
         "the whole heading, taken back by what follows it on the line"),
        (_dashes(standin), head, CLEAN, "the heading typed with a hyphen for the dash"),
        (standin + "\nAn example of the other shape:\n**Verdict:** findings\n", head, FINDINGS,
         "a clean line with a findings line under it (the reviewer's second P1 on #26)"),
        (standin_findings + "\n**Verdict:** clean\n", head, FINDINGS,
         "the same the other way round — the stronger thing said still wins"),
        (standin.replace("090e429a31", "29d7b543"), head, None, "a stand-in read of another commit"),
        (standin.replace("**Verdict:** clean", "**Verdict:** looks fine"), head, None,
         "a verdict that is neither word"),
        (standin.split("\n\n", 1)[1], head, None, "a verdict with nothing saying who read it"),
        (standin.replace("**Verdict:** clean\n", ""), head, None,
         "a stand-in read that never says what it found"),
        ("I asked for a **%s review** of this.\n\n**Reviewed commit:** `090e429a31`\n"
         "**Verdict:** clean\n" % STANDIN, head, None,
         "a sentence about a stand-in review, carrying the shape below it"),
        ("", head, None, "an empty comment"),
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
    owner = "the-account-the-cto-holds"
    mine = lambda body: {"user": {"login": owner}, "body": body}
    ask = mine("@codex review\n\nHead is `090e429a31`. Three places I think it could be wrong.")
    standin_gate_cases = [
        ([], [ask, mine(standin)], STANDIN_CLEAN,
         "Codex asked on this head and silent; the stand-in read it clean"),
        ([], [mine(standin)], NOT_ASKED,
         "a stand-in clean where Codex was never asked (the reviewer's first P1 on #26)"),
        ([], [mine("@codex review\n\nHead is `29d7b543`."), mine(standin)], NOT_ASKED,
         "an ask naming the round before, and a stand-in read of this one"),
        ([], [{"user": {"login": "someone"}, "body": "@codex review\n\nHead is `090e429a31`."},
              mine(standin)], NOT_ASKED,
         "the ask typed by somebody who is not the account the CTO holds"),
        ([], [mine(standin_findings)], FINDINGS,
         "a stand-in finding with no ask — it opens nothing, so it needs none"),
        ([findings], [ask, mine(standin)], FINDINGS,
         "a stand-in clean over findings Codex left — the findings stand"),
        ([], [bot(summary), ask, mine(standin)], NO_VERDICT,
         "Codex has finished on this head; a stand-in may not answer for it"),
        ([], [bot(clean), ask, mine(standin_findings)], FINDINGS,
         "the stand-in found what Codex did not"),
        ([], [bot(clean), ask, mine(standin)], CLEAN, "both of them clean — Codex is the one named"),
        ([], [ask, {"user": {"login": "someone"}, "body": standin}], UNREAD,
         "a stand-in verdict typed by somebody who is not the account the CTO holds"),
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
    for body, h, want, what in standin_cases:
        bad += hold(standin_verdict(body, h), want, what)
    for reviews, comments, want, what in standin_gate_cases:
        bad += hold(verdict(reviews, comments, head, owner=owner), want, what)
    bad += hold(verdict([], [ask, mine(standin)], head), UNREAD,
                "a stand-in read with no owner given — closed unless it is asked for")
    bad += hold(verdict([], [mine("@codex review\n\nHead is `090e429`."), mine(standin)], head,
                        resolve=resolver, owner=owner), NOT_ASKED,
                "an ask whose short form resolves to another commit")
    bad += hold(comment_verdict(summary, head, resolve=resolver), None,
                "a short form that resolves to another commit")
    bad += hold(comment_verdict(clean, head, resolve=resolver), CLEAN,
                "a clean pass whose short form resolves to this head")
    bad += hold(standin_verdict(standin.replace("090e429a31", "090e429"), head, resolve=resolver),
                None, "a stand-in read whose short form resolves to another commit")
    bad += hold(standin_verdict(standin, head, resolve=resolver), CLEAN,
                "a stand-in read whose short form resolves to this head")
    if bad:
        print("review-gate selftest failed: %d case(s)" % bad)
        return 1
    # A fake is anything that must not open the gate — counted, not asserted, so
    # the number cannot drift away from the cases that hold it.
    opens = (CLEAN, STANDIN_CLEAN)
    fakes = (sum(1 for c in comment_cases if c[2] is None)
             + sum(1 for r in review_cases if r[1] is None)
             + sum(1 for c in standin_cases if c[2] is None)
             + sum(1 for g in gate_cases if g[2] not in opens)
             + sum(1 for g in standin_gate_cases if g[2] not in opens) + 4)
    print("ok: review gate tells a clean read from a commented one, in both shapes and every "
          "state they arrive in, keeps the stand-in behind Codex wherever Codex has spoken and "
          "behind the ask that fell silent, and is fooled by none of the %d fakes" % fakes)
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
    # The stand-in is read from this account's comments and no other: a shape
    # anyone who can comment could type would be no gate at all.
    owner = repo.split("/")[0]
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
        answer = verdict(reviews, comments, head, resolve=resolve, owner=owner)
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
    if answer == STANDIN_CLEAN:
        print("ok: Codex has said nothing about %s, and a %s read in its place left nothing on "
              "it — the same vendor as the lead, and the pull request says so" % (head, STANDIN))
        return 0
    print("reason: " + REASONS[answer] % head)
    return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
