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
Chairman's ruling that evening put Codex first and a Fable 5.1 read behind it.
It is quoted whole in README.md, *The independent reviewer*, which is also where
the conditions a backup verdict must meet are written out for a reader. This
file enforces them; it does not keep a second copy of them.

Codex is the primary and reads first. The backup is counted ONLY behind the
primary's own refusal on that same pull request — the one half of this the lead
cannot write for itself — and never on the classes where the rulebook requires
the other vendor. Here that is the review gate itself: see touches_the_gate().

Eligibility is judged as at the moment the backup posted, never as at the moment
this check runs. Both directions of that matter. A verdict written while the
primary was able to answer is not made legitimate by a refusal that arrives
afterwards; and a real read's findings do not evaporate because the primary
answered later — the answer to a finding is a push, whoever found it.

BACKUP below is the login whose verdicts are counted, and it is empty. The
reviewer that would post them is not installed in any repository yet, so there
is no such login and this gate counts no backup at all. That is the correct
state and not a gap: with nothing posting, the gate stays red, and a gate that
opened when its reviewer was missing would not be a gate.

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

# The backup reviewer's login, and it is empty on purpose.
#
# It was github-actions[bot] until the backup's own first cold read said what
# that name actually is: the login GitHub gives EVERY workflow token in this
# repository, not an identity belonging to a reviewer. The argument for it was
# that forging a verdict means adding a workflow, and adding one is what makes a
# pull request ineligible. The last step is false. The workflow does not have to
# be in the pull request under review: push a throwaway branch — never opened as
# a pull request, so touches_the_gate() never sees it — carrying a workflow that
# runs on push, asks for pull-requests: write, and posts the verdict line on any
# pull request here. It needs only push access, which every lead session has.
#
# So the gate counts a login a pushed branch cannot wear: the reviewer's own, as
# the primary has its own. Until that identity exists this stays empty and NO
# backup is counted — the verdict shape, posted by Actions or by anyone else,
# reads as no read at all. The gate will not borrow a name to stand in for one.
BACKUP = ""

# The primary's own refusal, which is what makes the backup eligible at all.
# Matched from the start of its comment, and anchored: a body that merely
# mentions a limit is not the primary saying it cannot read.
QUOTA = re.compile(r"^You have reached your .{0,40}usage limits", re.IGNORECASE)


def primary_events(reviews, comments):
    """Everything the primary has said on this pull request, oldest first.

    Ordered by when each was last WRITTEN, and drawn from both halves of the
    page. Neither is fussiness — the primary's own habits defeat the obvious
    reading, and the primary found this on #34:

      it EDITS its summary comment   That comment is created when a review
                                     starts and edited when it finishes, so a
                                     summary created BEFORE a refusal is still
                                     the primary answering AFTER it. Ordering by
                                     creation puts the answer before the refusal
                                     and the refusal reads as the latest word.
                                     On #34 that comment was created at 16:07
                                     and edited at 16:13, 16:17 and 16:22.
      its findings are a REVIEW      Not a comment at all. A list of issue
                                     comments never sees them, so the primary
                                     could post findings after refusing and the
                                     refusal would still read as its last word.

    Either one hands the backup a pull request the primary is able to read,
    which is the single thing the ruling of 17 September forbids.

    Each entry is (when it was last written, its body, whether it was edited).
    The first two decide which word is the latest and whether it came after the
    head did; the third is read by primary_refused().

    Timestamps are ISO-8601 in Z, so they sort as text.
    """
    out = []
    for c in comments:
        if c.get("user", {}).get("login") == BOT:
            created = c.get("created_at") or ""
            updated = c.get("updated_at") or created
            out.append((updated or created, c.get("body") or "",
                        bool(created) and updated != created))
    for r in reviews:
        if r.get("user", {}).get("login") == BOT:
            # A submitted review is the primary answering. It is never a refusal.
            out.append((r.get("submitted_at") or "", r.get("body") or "", False))
    out.sort(key=lambda e: e[0])
    return out


def primary_refused(events, since, at=None):
    """Is the primary's latest word, as at `at`, that it cannot read THIS head?

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
    a backup that stands in while the primary is fine. An empty last word is
    read the same way — it is not the primary saying it cannot read, so it is
    not a refusal, and the answer is to ask.

    Two things narrow "latest word", and the backup's own cold read found both.

    `since` is when this head reached the pull request, on GitHub's clock. A
    refusal names no commit, so without this one refusal on Monday's head hands
    the backup every push after it and the primary is never asked about any of
    them — the ruling reversed. A refusal written before this head existed is
    not the primary saying it cannot read this head. An unknown arrival counts
    no refusal at all, which stands the backup down and asks the primary.

    `at` is when the backup spoke, and eligibility is judged there rather than
    here. A verdict written while the primary could still answer is not made
    legitimate by a refusal that lands afterwards, and a read that was
    legitimate when it was taken does not stop being one because the primary
    answered since.

    An edited comment is not counted at all. Anyone with write access can edit
    anyone's comment and the login stays the author's, so the three shapes the
    reviewers never edit — this refusal, the primary's clean pass, the backup's
    verdict — are refused the moment they differ from what was posted. The
    primary's summary, which it edits by design, is untouched by this.
    """
    if at is not None:
        events = [e for e in events if e[0] <= at]
    if not events or not since:
        return False
    when, body, was_edited = events[-1]
    if was_edited:
        return False
    if QUOTA.match((body or "").strip()) is None:
        return False
    return when >= since


def edited(comment):
    """Has this comment been rewritten since it was posted?"""
    created = comment.get("created_at") or ""
    updated = comment.get("updated_at") or ""
    return bool(created) and bool(updated) and updated != created

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
# The whole of .github/ is on the list, not merely the one workflow file that
# exists today. This breadth was argued as the thing that made forgery
# impossible: to post as Actions you must add a workflow, and adding one is what
# makes you ineligible. The backup's own read showed that argument false — the
# workflow need not be in the pull request under review at all. The breadth
# stays for the reason that does hold: the machinery that decides is machinery
# only the other vendor may clear. What shuts the forgery is BACKUP naming a
# login a pushed branch cannot wear.
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


def verdict(reviews, comments, head, resolve=None, gate_files=(),
            backup=BACKUP, head_arrived=""):
    """The gate's one answer about the head commit, from the whole page.

    Only a reviewer's own words count: anyone who can comment on a pull request
    can type a clean pass, so a comment by anybody else is not one. There are
    two reviewers and each has its own login — the primary's shapes are never
    read from the backup's comments, nor the other way round, so neither can be
    spoken for by the other. `backup` is that second login, and it is empty
    until the reviewer exists: with no login to match, no backup is counted, and
    the name shared by every workflow in the repository buys nothing.

    Each backup verdict is judged as at the moment it was written. With no
    refusal standing behind it then, it says nothing either way — not even its
    findings — because the answer is to ask the primary, and an unasked-for run
    should not be able to hold a pull request red. With one, it counts, and goes
    on counting: a read that was legitimate when it was taken is not undone by
    the primary answering afterwards, which is why a real read's findings stay
    red under a later clean pass rather than evaporating beneath it.

    `gate_files` is what this pull request changes that only the other vendor
    may clear. It downgrades the backup's clean pass and nothing else: its
    findings still count as findings, and the primary's clean pass still opens
    the gate — which is right, because the primary is the vendor that may
    clear one.
    """
    said = [review_verdict(r, head) for r in reviews]
    spoke, backup_said = primary_events(reviews, comments), []
    for c in comments:
        who = c.get("user", {}).get("login")
        if who == BOT:
            answer = comment_verdict(c.get("body"), head, resolve)
            # Its clean pass is a shape it never edits; its summary is one it
            # edits by design. Only the verdict is void for being rewritten.
            said.append(None if answer == CLEAN and edited(c) else answer)
        elif backup and who == backup:
            answer = fable_verdict(c.get("body"), head, resolve)
            if answer is not None and not edited(c):
                backup_said.append(
                    (c.get("updated_at") or c.get("created_at") or "", answer))
    for when, answer in backup_said:
        if not primary_refused(spoke, head_arrived, at=when):
            said.append(PRIMARY_FIRST)
        else:
            said.append(GATE_CHANGE if answer == CLEAN and gate_files else answer)
    for answer in ORDER:
        if answer in said:
            return answer
    return UNREAD


REASONS = {
    GATE_CHANGE: ("the backup reviewer read commit %s and left nothing on it, but this pull "
                  "request changes the gate itself (%s). The rulebook requires the other "
                  "vendor there, and a gate the reviewer it admits can open is not a gate — "
                  "so this one waits for " + BOT + " however long it takes"),
    PRIMARY_FIRST: ("the backup reviewer read commit %s, but no refusal by " + BOT + " stands "
                    "behind that read: it has not refused here, or it answered before the read "
                    "was taken, or it refused before this commit arrived and has not been asked "
                    "about this one. The primary reads first: ask it, and the backup stands in "
                    "only where it says it cannot"),
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
    # When this head reached the pull request, and three moments around it. A
    # refusal is only the primary refusing THIS head if it was written after it.
    ARRIVED = "2026-09-17T16:00:00Z"
    STALE = "2026-09-17T15:00:00Z"   # said about the commit before this one
    LATER = "2026-09-17T17:00:00Z"   # said since this head arrived
    LAST = "2026-09-17T18:00:00Z"
    ENDED = "2026-09-17T19:00:00Z"

    def bot(body, at=LATER, edited_at=None):
        return {"user": {"login": BOT}, "body": body,
                "created_at": at, "updated_at": edited_at or at}
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
    # (when it was written, its body, whether somebody edited it)
    ev = lambda body, at=LATER, was_edited=False: (at, body, was_edited)
    for events, want, what in [
        ([ev(quota)], True, "the quota message"),
        ([ev(quota), ev(summary)], False, "a refusal the primary has answered since (the 17 Sep reset)"),
        ([ev(summary), ev(quota)], True, "a refusal after an earlier answer"),
        ([ev(clean)], False, "a clean pass"),
        ([], False, "nothing from the primary at all"),
        ([ev(""), ev("  ")], False, "empty comments"),
        ([ev(quota), ev("")], False, "a refusal followed by an empty comment — an empty last word "
                                     "is not the primary saying it cannot read, so the answer is to ask"),
        ([ev("We could not review; you may be near your usage limits.")], False,
         "a sentence mentioning a limit, which is not the primary refusing"),
        ([ev("You have reached your GPT usage limits for code reviews.")], True,
         "the same refusal under another product name"),
        # Bound to the head it was written about, which is the whole of finding 4.
        ([ev(quota, STALE)], False,
         "a refusal written before this head arrived — it refused the commit before, "
         "and nobody has asked the primary about this one"),
        ([ev(quota, ARRIVED)], True, "a refusal written as this head arrived"),
        # And void if somebody rewrote it: the login stays the bot's after an edit.
        ([ev(quota, LATER, True)], False, "a refusal somebody has edited since it was posted"),
    ]:
        bad += hold(primary_refused(events, ARRIVED), want, "the primary's refusal: " + what)
    bad += hold(primary_refused([ev(quota)], ""), False,
                "the primary's refusal: one with no arrival known for the head — "
                "unknown means the backup stands down, never that it stands in")

    # And the ORDER those bodies arrive in, which is where the primary found
    # this gate wrong on #34. Its summary comment is created when a review
    # starts and edited when it finishes, and its findings are a submitted
    # review rather than a comment at all — so a list of comments in creation
    # order can show a refusal as the last word long after it has answered.
    def _c(created, updated, body):
        return {"user": {"login": BOT}, "created_at": created,
                "updated_at": updated, "body": body}

    def _r(at, body):
        return {"user": {"login": BOT}, "submitted_at": at, "body": body}

    for reviews_, comments_, want, what in [
        ([], [_c("16:07", "16:22", summary), _c("16:10", "16:10", quota)], False,
         "a summary CREATED before a refusal and EDITED after it — the edit is the last word"),
        ([_r("16:15", "### Codex Review")], [_c("16:10", "16:10", quota)], False,
         "findings submitted as a REVIEW after a refusal, which a comment list never sees"),
        ([], [_c("16:07", "16:10", summary), _c("16:20", "16:20", quota)], True,
         "a refusal that really is the latest thing the primary wrote"),
        ([], [_c("16:10", "16:10", quota)], True, "a refusal and nothing else"),
        ([_r("16:05", "### Codex Review")], [_c("16:10", "16:10", quota)], True,
         "findings BEFORE the refusal, which do not answer it"),
        ([], [], False, "silence"),
    ]:
        bad += hold(primary_refused(primary_events(reviews_, comments_), "16:00"), want,
                    "the primary's latest word: " + what)

    # The whole decision. A Fable read taken inside a builder session posts
    # under the Chairman's own account — it is a real review, and it is the lead
    # clearing its own work, which is the one thing this gate exists to refuse.
    #
    # REVIEWER stands in for the login the backup will hold. The shipped BACKUP
    # is empty, so these cases pass it explicitly; the two holds after the loop
    # are the gate exactly as it ships.
    REVIEWER = "juku-reviewer[bot]"

    def reviewer(body, at=LAST, edited_at=None):
        return {"user": {"login": REVIEWER}, "body": body,
                "created_at": at, "updated_at": edited_at or at}

    def other(login, body, at=LAST):
        return {"user": {"login": login}, "body": body,
                "created_at": at, "updated_at": at}

    actions = lambda body: other("github-actions[bot]", body)
    person = lambda body: other("Adonis80", body)
    gate = touches_the_gate(["review-gate.py"])
    for reviews, comments, files, want, what in [
        ([], [bot(quota), reviewer(fable_clean)], (), CLEAN, "the backup, behind a real refusal"),
        ([], [bot(quota), reviewer(fable_found)], (), FINDINGS, "its findings, behind one"),
        ([], [reviewer(fable_clean)], (), PRIMARY_FIRST,
         "the backup with the primary never refusing — ask the primary"),
        ([], [reviewer(fable_found)], (), PRIMARY_FIRST,
         "even its FINDINGS say nothing with no refusal behind them"),
        ([], [bot(quota, LATER), bot(summary, LAST), reviewer(fable_clean, ENDED)], (), PRIMARY_FIRST,
         "a refusal the primary has answered since — the reset case, and the whole point"),
        ([], [bot(quota), person(fable_clean)], (), UNREAD,
         "the backup's exact shape posted by a person"),
        ([], [bot(quota), bot(fable_clean)], (), UNREAD,
         "the backup's exact shape posted by the primary"),
        ([], [bot(quota), reviewer(clean)], (), UNREAD, "the primary's shape posted by the backup"),
        # The login the gate used to count, and what the backup's own read said
        # it is: every workflow in the repository, reachable from any pushed
        # branch. It is not the reviewer, so it is not a reviewer.
        ([], [bot(quota), actions(fable_clean)], (), UNREAD,
         "the verdict shape posted as github-actions[bot] — the name every workflow "
         "here wears, and no reviewer's own"),
        ([], [bot(quota), reviewer(fable_clean)], gate, GATE_CHANGE,
         "the backup clearing a change to the gate itself"),
        ([], [bot(quota), reviewer(fable_found)], gate, FINDINGS,
         "its findings on a gate change — still findings, still red"),
        ([], [reviewer(fable_clean), bot(clean)], gate, CLEAN,
         "the other vendor clearing a gate change, which it alone may"),
        ([], [bot(clean, LATER), bot(quota, LAST), reviewer(fable_clean, ENDED)], gate, CLEAN,
         "the primary's own clean pass outranks the backup's on a gate change — CLEAN "
         "sits above GATE_CHANGE in ORDER, and this is the page that shows both"),
        ([findings], [bot(quota), reviewer(fable_clean)], (), FINDINGS,
         "the primary's findings outrank the backup's clean pass"),
        # A refusal names no commit. Both directions of binding it: to the head
        # it was written about, and to the moment the backup spoke.
        ([], [bot(quota, STALE), reviewer(fable_clean)], (), PRIMARY_FIRST,
         "a refusal written before this head arrived — it refused the commit before, "
         "and nobody has asked the primary about this one"),
        ([], [reviewer(fable_clean, LATER), bot(quota, LAST)], (), PRIMARY_FIRST,
         "a verdict written while the primary could still answer, with a refusal landing "
         "after it — a later refusal does not reach back and legitimise a read"),
        ([], [bot(quota, LATER), reviewer(fable_found, LAST), bot(clean, ENDED)], (), FINDINGS,
         "a real read's findings, and the primary reading the same commit clean after "
         "them — findings do not evaporate; the answer to one is a push"),
        # Anyone with write access can edit anyone's comment, and the login
        # stays the author's. The shapes the reviewers never edit are void once
        # they differ from what was posted; the summary they do edit is not.
        ([], [bot(quota), reviewer(fable_clean, LAST, edited_at=ENDED)], (), UNREAD,
         "a backup verdict somebody rewrote after it was posted"),
        ([], [bot(clean, LATER, edited_at=LAST)], (), UNREAD,
         "the primary's clean pass, rewritten after it was posted"),
        ([], [bot(summary, LATER, edited_at=LAST)], (), NO_VERDICT,
         "its summary, which it edits by design, which that must not touch"),
        ([], [bot(quota), reviewer(fable_clean.replace("090e429a31", "29d7b543"))], (), UNREAD,
         "its clean pass on the commit before this one"),
        ([], [bot(quota), reviewer(did_not_read)], (), UNREAD,
         "a run that did not reach the reviewer"),
    ]:
        bad += hold(verdict(reviews, comments, head, gate_files=files,
                            backup=REVIEWER, head_arrived=ARRIVED), want, what)

    # And the gate exactly as it ships: BACKUP is empty, so there is no login a
    # backup verdict could be posted under, and none is counted.
    for comments_, what in [
        ([bot(quota), reviewer(fable_clean)], "the reviewer's own login, which does not exist yet"),
        ([bot(quota), actions(fable_clean)], "the shared Actions name it used to count"),
    ]:
        bad += hold(verdict([], comments_, head, head_arrived=ARRIVED), UNREAD,
                    "as the gate SHIPS it, no backup is counted: " + what)

    # What a comparison hands the guard, which is the half the selftest used to
    # take on trust. A rename names its destination in `filename` and its source
    # only in `previous_filename`, so reading one of them loses the other.
    for files_, want, what in [
        ([{"filename": "README.md", "status": "modified"}], ["README.md"], "an ordinary edit"),
        ([{"filename": "docs/check.yml", "previous_filename": ".github/workflows/check.yml",
           "status": "renamed"}],
         ["docs/check.yml", ".github/workflows/check.yml"],
         "the gate's own workflow renamed onto an ordinary path"),
        ([{"filename": "review-gate.py", "status": "modified"}], ["review-gate.py"],
         "the gate edited in place"),
        ([{"filename": "notes.md", "previous_filename": "review-gate.py", "status": "renamed"}],
         ["notes.md", "review-gate.py"], "the gate renamed away"),
        ([{"filename": ""}, {}], [], "entries naming nothing"),
        ([], [], "an empty comparison"),
    ]:
        bad += hold(paths_in(files_), want, "what a comparison hands the guard: " + what)

    # And the two together: a renamed gate file must still be a gate change.
    for files_, want, what in [
        ([{"filename": "docs/check.yml", "previous_filename": ".github/workflows/check.yml"}],
         [".github/workflows/check.yml"],
         "renaming the gate workflow away is still touching the gate"),
        ([{"filename": "notes.md", "previous_filename": "review-gate.py"}],
         ["review-gate.py"], "so is renaming the gate itself"),
        ([{"filename": "NAMES.md", "previous_filename": "README.md"}], [],
         "renaming an ordinary page is not"),
    ]:
        bad += hold(touches_the_gate(paths_in(files_)), want,
                    "a renamed path reaches the guard: " + what)

    # What counts as the gate. The whole of .github/ is on the list because the
    # machinery that decides is only the other vendor's to clear — NOT because
    # adding a workflow is the only way to post a verdict, which it is not: see
    # BACKUP. That argument was the one the backup's read disproved, and it is
    # not restated here in the one place a reader would take it for settled.
    for paths, want, what in [
        (["review-gate.py"], ["review-gate.py"], "the gate's own decision"),
        (["check.sh"], ["check.sh"], "the check that runs it"),
        ([".github/workflows/review.yml"], [".github/workflows/review.yml"],
         "the reviewer's own workflow, for when it lands — the path, not a file that is here"),
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
    bad += hold(fable_verdict(fable_clean.replace("090e429a31", "090e429"), head,
                              resolve=resolver), None,
                "the BACKUP's clean pass on a short form that resolves to another commit")
    bad += hold(fable_verdict(fable_clean, head, resolve=resolver), CLEAN,
                "the BACKUP's clean pass whose short form resolves to this head")
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


def _get(url, token, asking=None):
    # `asking` names the thing in plain words where the URL's last segment does
    # not: /repos/owner/name ends in the repository's name, and "asked for the
    # how-we-build" sends the next session looking in the wrong place.
    _asking[0] = asking or url.rsplit("/", 1)[-1]
    req = urllib.request.Request(
        url,
        headers={"Authorization": "Bearer " + token, "Accept": "application/vnd.github+json"},
    )
    with urllib.request.urlopen(req) as r:
        return json.load(r)


# GitHub caps a comparison at 300 files and does not page them, so a larger one
# comes back quietly short. A short list could omit the very file that makes a
# pull request ineligible, so it is refused rather than trusted.
COMPARE_CAP = 300


def changed_paths(api, base, head, token):
    """What changed between two commits, asked of the COMMITS.

    Never of the pull request. `/pulls/N/files` answers about whatever the
    branch points at now, and the branch is the contributor's to move — so a
    decision taken from it is a decision about a moving target, whatever is
    done afterwards to bind the result.

    That is the cause behind every race found on #34: eligibility asked the
    mutable pull request for a fact and acted on it later. Round three bound the
    head; the primary then showed the same hole reached by A → B → A, because
    the paths were still read from the pull request while the sha was captured
    from a different moment. Two immutable shas have no such moment: the answer
    is the same whenever it is asked, and whoever asks it.

    Raises ValueError when the comparison is too large to be sure of.
    """
    data = _get("%s/compare/%s...%s" % (api, base, head), token)
    files = data.get("files") or []
    if len(files) >= COMPARE_CAP:
        raise ValueError(
            "the comparison between %s and %s names %d files, which is GitHub's cap — "
            "the list may be short, and a short list could hide the file that makes this "
            "pull request ineligible. Refusing rather than guessing." % (base, head, len(files)))
    return paths_in(files)


def protected_tip(api, token):
    """The tip of the branch this repository merges to, asked of GitHub.

    Never pulls/N.base.sha. The base is whoever opened the pull request's to
    change, and retargeting fires `pull_request: edited`, which check.yml does
    not subscribe to — so no fresh check runs and the green already attached to
    the head survives the move. Open a head against a branch that already
    carries the gate edit, let the comparison look innocent, have it cleared,
    then retarget to the protected branch and merge.

    It is also the right question rather than merely the safe one: this
    repository merges only to its default branch, so what a pull request
    changes is what it changes against that branch's tip now.

    Raises ValueError when GitHub names no tip, which is red rather than an
    empty comparison that would hide every gate file in it.
    """
    default = _get(api, token, "repository").get("default_branch") or "main"
    sha = (_get("%s/branches/%s" % (api, default), token,
                "protected branch").get("commit") or {}).get("sha")
    if not sha:
        raise ValueError(
            "GitHub named no tip for the protected branch (%s), so what this pull "
            "request changes cannot be established. Refusing rather than guessing."
            % default)
    return sha


def head_arrived(api, head, token):
    """When this head reached the pull request, on GitHub's clock.

    A refusal names no commit, so "the primary refused here" says nothing about
    which commit it could not read. This is what binds one to the other, and it
    is taken from the earliest check run GitHub recorded against this sha —
    never from the commit's own author or committer date, which whoever pushes
    sets to whatever they like.

    An unknown arrival is returned as "", and primary_refused() counts no
    refusal without one: the backup stands down and the answer is to ask.
    """
    runs = _get("%s/commits/%s/check-runs" % (api, head), token,
                "head's check runs").get("check_runs") or []
    starts = sorted(r.get("started_at") or "" for r in runs if r.get("started_at"))
    return starts[0] if starts else ""


def paths_in(files):
    """Every path a comparison touches — where each file went AND where it was.

    GitHub names a renamed file by its DESTINATION in `filename`, and its source
    only in `previous_filename`. Reading the destination alone loses the fact
    that something was taken away from where it used to be. So a pull request
    could rename `.github/workflows/check.yml` onto an ordinary path and
    touches_the_gate() would see an ordinary path — missing that the gate's own
    workflow had just been carried off, and letting a backup verdict clear it.

    The primary found that on #34, and named why the selftest did not: it held
    touches_the_gate() against the paths it was handed, and nothing held what
    was handed to it. This function is the seam that was missing, and it is
    pure so the selftest can hold it.
    """
    out = []
    for f in files:
        for key in ("filename", "previous_filename"):
            name = f.get(key)
            if name:
                out.append(name)
    return out


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
        # Asked of GitHub, not of the checkout: the check runs on the proposed
        # tree, so a branch that edited its own diff could otherwise hide the
        # very file that makes it ineligible.
        # Of the commit under review and the protected branch's tip, not of the
        # pull request: the same reason as changed_paths()'s docstring, and
        # protected_tip()'s. This check is handed a HEAD_SHA, and asking the
        # pull request for either end would answer about whatever the branch
        # and the base point at now — both of which move without starting a
        # check, and neither of which is what is being judged.
        base = protected_tip(api, token)
        changed = changed_paths(api, base, head, token)
        gate_files = touches_the_gate(changed)
        # Only asked when there is a backup login to judge: with none, no
        # refusal is ever consulted and the fetch would buy nothing.
        arrived = head_arrived(api, head, token) if BACKUP else ""
        answer = verdict(reviews, comments, head, resolve=resolve,
                         gate_files=gate_files, head_arrived=arrived)
    except ValueError as e:
        # A comparison too large to be sure of. Red, and says which.
        print("reason: " + str(e))
        return 2
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
