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
could see. `AGENTS.md` named that gap. So the gate gives one answer about the
head commit, and opens on `clean` alone:

    clean       read, and the reviewer left nothing on it
    findings    read, and the reviewer left something on it
    gate        the backup cleared it, but the change is one only the
                other vendor may clear
    no verdict  a review ran on it, but what it found is not on the page yet
    unread      no read of this commit at all

A finding outranks every other answer about the same commit. The answer to a
finding is a push, and a push makes a new commit for the reviewer to read; what
the CTO says about the old one never clears it.

From 17 September 2026 there are two reviewers, and the gate reads both. The
Chairman's ruling that evening: *"we better use GPT sol 5.6 as primary reviewer
because Fable will hit a wall. and if thats not available then default for Fable
5.1. this is because although it Claude, its still different to Opus 5 which is
the default builder for claude code mode."*

So Codex is the primary and reads first. The backup runs in
.github/workflows/review.yml, posts as github-actions[bot], and is counted ONLY
behind the primary's own refusal on that same pull request — the one half of
this the lead cannot write for itself. On the classes where the rulebook
requires the other vendor — here, the review gate itself — only Codex may
clear, refusal or no refusal.

Four things make the backup a gate rather than a way round, and the first two
are why its verdict can be counted at all:

  it posts as Actions     no personal token can post under that name; a Fable
                          read run inside a session posts as the Chairman, and
                          would be the lead clearing its own work
  issue_comment, never    that trigger runs the workflow file from the DEFAULT
  pull_request            BRANCH. On pull_request a branch could edit its own
                          reviewer and write itself a clean pass
  it may not clear the    a change to review-gate.py, check.sh or anything under
  gate                    .github/ waits for the other vendor, however long that
                          takes — see touches_the_gate()
  only behind a refusal   and only the primary's LATEST word on the pull
                          request. An allowance that reset since is a primary
                          that can answer, and it answers first

The third is what keeps the second true. To forge a verdict you must post as
Actions; to post as Actions you must add or change a workflow; and changing
anything under .github/ is exactly what makes this reviewer ineligible.

The fourth is why the backup never quietly becomes the habit.

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

# The backup reviewer, and the one identity no session can type as. GitHub gives
# this login to a workflow's own token; a personal access token cannot borrow
# it. That is the whole reason a Fable read counts here and the same read taken
# inside a builder session does not.
ACTIONS = "github-actions[bot]"

# The primary's own refusal, which is what makes the backup eligible at all.
# Matched from the start of its comment, and anchored: a body that merely
# mentions a limit is not the primary saying it cannot read.
QUOTA = re.compile(r"^You have reached your .{0,40}usage limits", re.IGNORECASE)


def primary_refused(bodies):
    """Is the primary's LATEST word on this pull request that it cannot read?

    Not "has it ever refused here". One allowance serves every repository, and
    it resets: on 17 September 2026 it refused at 11:46 and read again at 15:54
    on the same pull request, after a banked reset was spent. A gate that
    counted the older refusal would hand the afternoon's reviews to the backup
    while the primary sat available — the opposite of the ruling, which is that
    the other vendor reads first.

    So only the last thing the primary said counts. Anything else it has posted
    since — a summary, a clean pass, findings — is a primary that can answer,
    and the answer is to ask it.

    Failing to recognise a refusal shape leaves the backup ineligible and the
    slice waiting on the primary. That is the safe direction: the unsafe one is
    a backup that stands in while the primary is fine.
    """
    said = [b for b in bodies if b and b.strip()]
    if not said:
        return False
    return QUOTA.match(said[-1].strip()) is not None

# Its two shapes. The workflow writes one of these as the first line and nothing
# else, and matching is exact and whole-line — not a prefix. A prefix test is
# the hole the primary's matcher was hardened against on #24: "…Didn't find any
# major issues because the review did not complete" carries the whole verdict
# and takes it back. The same sentence works against a prefix here, so the whole
# line must be the verdict and nothing may follow it.
FABLE_CLEAN = "Review by Fable at max effort: nothing found."
FABLE_FINDINGS = "Review by Fable at max effort: findings below."

# What the backup may not clear. It is the same vendor as the lead, and
# the rulebook requires the other vendor on the review gate itself — so these
# wait for Codex however long it takes.
#
# The whole of .github/ is on the list, not merely the two workflow files that
# exist today, and that breadth is load-bearing rather than caution. A branch
# that wants to forge a clean pass has to post as github-actions[bot], and the
# only way to do that is to add a workflow of its own — which, on a same-repo
# pull request, GitHub would run from the branch. Putting every path under
# .github/ on this list means the one change that would make forgery possible is
# also the change this reviewer may not clear. The cost is that an unrelated
# change to a workflow waits for Codex, which in a repository holding two of
# them is a price worth paying for a door that shuts on itself.
GATE_PATHS = ("review-gate.py", "check.sh")


def touches_the_gate(paths):
    """The paths in this pull request that only the other vendor may clear."""
    return sorted(set(p for p in paths
                      if p in GATE_PATHS or p.startswith(".github/")))

# The answers, worst first: a commit is judged by the strongest thing said about
# it, and only CLEAN opens the gate.
#
# GATE_CHANGE sits below CLEAN on purpose. It is what the backup's clean
# pass becomes on a change to the gate, and Codex's own clean pass outranks it —
# which is exactly right, because Codex is the vendor that may clear one.
FINDINGS = "findings"
CLEAN = "clean"
GATE_CHANGE = "gate"
PRIMARY_FIRST = "primary first"
NO_VERDICT = "no verdict"
UNREAD = "unread"
ORDER = (FINDINGS, CLEAN, GATE_CHANGE, PRIMARY_FIRST, NO_VERDICT)


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


def fable_verdict(body, head, resolve=None):
    """What a review posted by the workflow says about this commit.

    The first line is the whole verdict and must be one of the two shapes
    exactly — no prefix, no trailing clause. Everything below it is the review
    itself and is never parsed. The commit must be named, in the same
    `**Reviewed commit:**` note the primary uses, so one push voids it the same
    way.

    The workflow's own did-not-read notice deliberately carries neither shape,
    so a run that failed to reach the model can never read as a read.
    """
    if not body or not body.strip():
        return None
    stripped = body.strip().splitlines()
    first = stripped[0].strip()
    if first == FABLE_CLEAN:
        answer = CLEAN
    elif first == FABLE_FINDINGS:
        answer = FINDINGS
    else:
        return None
    note = _reviewed_note(head)
    if any(_names_head(ln.strip(), note, head, resolve) for ln in stripped):
        return answer
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


def verdict(reviews, comments, head, resolve=None, gate_files=()):
    """The gate's one answer about the head commit, from the whole page.

    Only a reviewer's own words count: anyone who can comment on a pull request
    can type a clean pass, so a comment by anybody else is not one. There are
    two reviewers and each has its own login — the primary's shapes are never
    read from the backup's comments, nor the other way round, so neither
    can be spoken for by the other.

    The backup is counted only behind the primary's latest-word refusal. With
    no refusal its verdict says nothing either way — not even its findings —
    because the answer then is to ask the primary, and a backup finding that
    could hold a pull request red would let an unasked-for run do it.

    `gate_files` is what this pull request changes that only the other vendor
    may clear. It downgrades the backup's clean pass and nothing else: its
    findings still count as findings, and the primary's clean pass still opens
    the gate — which is right, because the primary is the vendor that may
    clear one.
    """
    said = [review_verdict(r, head) for r in reviews]
    spoke, backup = [], []
    for c in comments:
        who = c.get("user", {}).get("login")
        if who == BOT:
            said.append(comment_verdict(c.get("body"), head, resolve))
            spoke.append(c.get("body"))
        elif who == ACTIONS:
            answer = fable_verdict(c.get("body"), head, resolve)
            if answer is not None:
                backup.append(answer)
    if backup:
        if not primary_refused(spoke):
            said.append(PRIMARY_FIRST)
        else:
            said += [GATE_CHANGE if a == CLEAN and gate_files else a for a in backup]
    for answer in ORDER:
        if answer in said:
            return answer
    return UNREAD


REASONS = {
    GATE_CHANGE: ("the backup reviewer read commit %s and left nothing on it, but this pull "
                  "request changes the gate itself (%s). The rulebook requires the other "
                  "vendor there, and a gate the reviewer it admits can open is not a gate — "
                  "so this one waits for " + BOT + " however long it takes"),
    PRIMARY_FIRST: ("the backup reviewer read commit %s, but " + BOT + " has not refused here "
                    "— or has answered since it did. The primary reads first: ask it, and the "
                    "backup stands in only where it says it cannot"),
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
    # The backup's two shapes, and the notice it posts when it did not
    # read. That notice names a commit on purpose — it is the fake most likely
    # to be written by accident, and it must never read as a read.
    fable_clean = ("Review by Fable at max effort: nothing found.\n\n"
                   "**Reviewed commit:** `090e429a31`\n\n---\n\nI read the diff against the "
                   "rulebook and the existing pages.\n")
    fable_found = ("Review by Fable at max effort: findings below.\n\n"
                   "**Reviewed commit:** `090e429a31`\n\n---\n\n1. The cap is spent twice.\n")
    did_not_read = ("**The reviewer did not read this commit** — the reviewer could not be "
                    "reached.\n\n**Reviewed commit:** `090e429a31`\n")
    fable_cases = [
        (fable_clean, head, CLEAN, "the backup's clean pass naming the commit"),
        (fable_found, head, FINDINGS, "its findings naming the commit"),
        (fable_clean.replace("090e429a31", "29d7b543"), head, None, "its clean pass on another commit"),
        (fable_found.replace("090e429a31", "29d7b543"), head, None, "its findings on another commit"),
        (did_not_read, head, None, "the workflow's own did-not-read notice, which names a commit"),
        (fable_clean.replace("nothing found.", "nothing found. But the review did not complete."),
         head, None, "the whole verdict, taken back by what follows it on the same line"),
        (fable_clean.replace("Review by Fable", "I asked for a Review by Fable"),
         head, None, "a sentence containing the words"),
        ("Review by Fable at max effort: nothing found.\n\nnothing else\n", head, None,
         "the shape naming no commit"),
        (fable_clean.replace("nothing found.", "nothing found"), head, None,
         "the verdict without its full stop"),
        ("", head, None, "an empty comment"),
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
    for body, h, want, what in fable_cases:
        bad += hold(fable_verdict(body, h), want, what)
        # Neither reviewer's matcher may ever read the other's shape: that is
        # what keeps two logins two reviewers rather than one.
        bad += hold(comment_verdict(body, h), None,
                    "the PRIMARY's matcher on: " + what)
    for body, what in ((clean, "the primary's clean pass"),
                       (summary, "the primary's summary table")):
        bad += hold(fable_verdict(body, head), None,
                    "the BACKUP's matcher on: " + what)

    # The primary's refusal, which is the only thing that makes the backup
    # eligible — and only while it is the primary's latest word here.
    quota = "You have reached your Codex usage limits for code reviews."
    for bodies, want, what in [
        ([quota], True, "the quota message"),
        ([quota, summary], False, "a refusal the primary has answered since (the 17 Sep reset)"),
        ([summary, quota], True, "a refusal after an earlier answer"),
        ([clean], False, "a clean pass"),
        ([], False, "nothing from the primary at all"),
        (["", "  "], False, "empty comments"),
        ([quota, ""], True, "a refusal followed by an empty comment"),
        (["We could not review; you may be near your usage limits."], False,
         "a sentence mentioning a limit, which is not the primary refusing"),
        (["You have reached your GPT usage limits for code reviews."], True,
         "the same refusal under another product name"),
    ]:
        bad += hold(primary_refused(bodies), want, "the primary's refusal: " + what)

    # The whole decision. The three that matter most: the person, the gate
    # change, and a backup read with no live refusal behind it. A Fable read
    # taken inside a builder session posts under the Chairman's own account —
    # it is a real review, and it is the lead clearing its own work, which is
    # the one thing this gate exists to refuse.
    actions = lambda body: {"user": {"login": ACTIONS}, "body": body}
    person = lambda body: {"user": {"login": "Adonis80"}, "body": body}
    gate = touches_the_gate(["review-gate.py"])
    for reviews, comments, files, want, what in [
        ([], [bot(quota), actions(fable_clean)], (), CLEAN, "the backup, behind a real refusal"),
        ([], [bot(quota), actions(fable_found)], (), FINDINGS, "its findings, behind one"),
        ([], [actions(fable_clean)], (), PRIMARY_FIRST,
         "the backup with the primary never refusing — ask the primary"),
        ([], [actions(fable_found)], (), PRIMARY_FIRST,
         "even its FINDINGS say nothing with no refusal behind them"),
        ([], [bot(quota), bot(summary), actions(fable_clean)], (), PRIMARY_FIRST,
         "a refusal the primary has answered since — the reset case, and the whole point"),
        ([], [bot(quota), person(fable_clean)], (), UNREAD,
         "the backup's exact shape posted by a person"),
        ([], [bot(quota), bot(fable_clean)], (), UNREAD,
         "the backup's exact shape posted by the primary"),
        ([], [bot(quota), actions(clean)], (), UNREAD, "the primary's shape posted by Actions"),
        ([], [bot(quota), actions(fable_clean)], gate, GATE_CHANGE,
         "the backup clearing a change to the gate itself"),
        ([], [bot(quota), actions(fable_found)], gate, FINDINGS,
         "its findings on a gate change — still findings, still red"),
        ([], [actions(fable_clean), bot(clean)], gate, CLEAN,
         "the other vendor clearing a gate change, which it alone may"),
        ([findings], [bot(quota), actions(fable_clean)], (), FINDINGS,
         "the primary's findings outrank the backup's clean pass"),
        ([], [bot(quota), actions(fable_clean.replace("090e429a31", "29d7b543"))], (), UNREAD,
         "its clean pass on the commit before this one"),
        ([], [bot(quota), actions(did_not_read)], (), UNREAD,
         "a run that did not reach the reviewer"),
    ]:
        bad += hold(verdict(reviews, comments, head, gate_files=files), want, what)

    # What counts as the gate. The whole of .github/ is on the list because
    # adding a workflow is the only way to post as Actions at all.
    for paths, want, what in [
        (["review-gate.py"], ["review-gate.py"], "the gate's own decision"),
        (["check.sh"], ["check.sh"], "the check that runs it"),
        ([".github/workflows/review.yml"], [".github/workflows/review.yml"], "the reviewer itself"),
        ([".github/workflows/check.yml"], [".github/workflows/check.yml"], "the workflow that gates"),
        ([".github/anything-at-all"], [".github/anything-at-all"], "anything else under .github/"),
        (["README.md", "HOW-WE-BUILD.md", "design/SCREEN-LAW.md", "AGENTS.md"], [],
         "the pages, which the backup may clear"),
        (["design/.github-notes.md"], [], "a path that only looks like it"),
    ]:
        bad += hold(touches_the_gate(paths), want, "what counts as the gate: " + what)
    bad += hold(comment_verdict(summary, head, resolve=resolver), None,
                "a short form that resolves to another commit")
    bad += hold(comment_verdict(clean, head, resolve=resolver), CLEAN,
                "a clean pass whose short form resolves to this head")
    if bad:
        print("review-gate selftest failed: %d case(s)" % bad)
        return 1
    fakes = (sum(1 for c in comment_cases if c[2] is None)
             + sum(1 for r in review_cases if r[1] is None)
             + sum(1 for c in fable_cases if c[2] is None) + 1)
    print("ok: review gate tells a clean read from a commented one, tells its two reviewers "
          "apart, stands the backup down unless the primary has just refused, refuses to let "
          "it clear the gate itself, and is fooled by none of the %d fakes" % fakes)
    return 0


# Which fetch is in flight. There are three now — the reviews, the comments and
# the pull request's changed files — and the HTTP error below used to say "the
# reviews" whichever one had failed. A check that misreports which door was shut
# sends the next session looking in the wrong place.
_asking = [""]


def _pages(url, token):
    _asking[0] = url.rsplit("/", 1)[-1]
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


def _eligible(repo, num, token):
    """Exit 0 if the backup may stand in on this pull request.

    The workflow asks this before it spends a review, so the rule lives in one
    place: this file, read from the default branch by both callers. A second
    copy in YAML would be the same truth written twice, and the two would drift
    the first time one of them was corrected.
    """
    api = "https://api.github.com/repos/%s" % repo
    spoke = [c.get("body") for c in _pages("%s/issues/%s/comments" % (api, num), token)
             if c.get("user", {}).get("login") == BOT]
    if primary_refused(spoke):
        print("the primary has refused here and not answered since — the backup may stand in")
        return 0
    print("the primary has not refused on this pull request, or has answered since it did.")
    print("Ask it first. The backup stands in only where the primary says it cannot — the")
    print("Chairman's ruling of 17 September 2026, and not a preference.")
    return 1


def main(argv):
    if len(argv) == 2 and argv[1] == "--selftest":
        return _selftest()
    if len(argv) == 5 and argv[1] == "--eligible":
        return _eligible(argv[2], argv[3], argv[4])
    if len(argv) != 5:
        print("usage: review-gate.py <owner/repo> <pr-number> <head-sha> <token>")
        print("       review-gate.py --eligible <owner/repo> <pr-number> <token>")
        print("       review-gate.py --selftest")
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
        # Asked of GitHub, not of the checkout: the check runs on the proposed
        # tree, so a branch that edited its own diff could otherwise hide the
        # very file that makes it ineligible.
        changed = [f.get("filename") for f in _pages("%s/pulls/%s/files" % (api, num), token)]
        gate_files = touches_the_gate(changed)
        answer = verdict(reviews, comments, head, resolve=resolve, gate_files=gate_files)
    except urllib.error.HTTPError as e:
        if e.code in (401, 403):
            why = "the workflow's token may not read pull requests (it needs pull-requests: read), or GitHub is rate-limiting"
        elif e.code == 404:
            why = "GitHub found no such repository or pull request — check GITHUB_REPOSITORY and PR_NUMBER"
        elif e.code >= 500:
            why = "GitHub itself answered with an error — re-run the check"
        else:
            why = "GitHub refused the request"
        print("reason: HTTP %s when asked for the %s — %s" % (e.code, _asking[0] or "reviews", why))
        return 2
    if answer == CLEAN:
        print("ok: the reviewer has read %s and left nothing on it" % head)
        return 0
    if answer == GATE_CHANGE:
        print("reason: " + REASONS[answer] % (head, ", ".join(gate_files)))
        return 1
    print("reason: " + REASONS[answer] % head)
    return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
