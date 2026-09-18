#!/usr/bin/env python3
"""Has a reviewer read THIS commit, did it leave anything on it, and was it the
reviewer this change requires?

A review clears only the commit it read, and a reviewer answers in two shapes
that mean opposite things. Findings arrive as a submitted review carrying the
commit id. A clean pass — nothing to say — arrives as a plain comment naming the
commit. Missing the second fails in the good case: a clean pass leaves the check
red for ever, which is how a Juku Perfume pull request sat red overnight on
8 September with the reviewer having read the head and said it was fine. Matching
it loosely fails in the worse direction: on 13 September the reviewer showed that
a substring test passes on "Task Completed for `abc1234`; no review was
performed", so the gate would certify a commit nobody read.

Counting both shapes as one answer — which this gate did until 14 September —
fails in a third direction, and #21 is the proof: it merged on a commit carrying
a P1 the reviewer had posted and nobody had answered, because a read was all the
gate could see. `AGENTS.md` named that gap. So the gate gives one of five answers
about the head commit, and opens on the first alone:

    clean         read clean by a reviewer this change may be cleared by
    findings      read, and the reviewer left something on it
    cross-vendor  read clean, but by the reviewer this change may NOT use
    no verdict    a review ran on it, but what it found is not on the page yet
    unread        no read of this commit at all

A finding outranks every other answer about the same commit. The answer to a
finding is a push, and a push makes a new commit for the reviewer to read; what
the CTO says about the old one never clears it.

WHO REVIEWS IS ONE LINE. The Chairman's ruling of 17 September 2026 made Sonnet 5
at maximum effort the default reviewer for every product, and he said plainly
that he may switch it again. So the choice is `DEFAULT_REVIEWER` and nothing
else: the pages are written by role, and the logins live in `REVIEWERS`.

WHICH REVIEWER A CHANGE REQUIRES is the second line, and it is not decoration.
The rulebook requires the other vendor on pricing, live database changes or
schema, authentication and authorisation, public trust boundaries, deploy and
release machinery, and this review gate itself. Of that list this repository only
ever holds the last, so here the rule has one door: a pull request that touches
the gate opens on `GATE_REVIEWER` alone. Until today that was true by accident —
Codex was the only identity the gate could count, so a gate change could not be
cleared by anyone else. Counting a second reviewer spends that accident, and the
door replaces it. Hemz OS found the same hole from the other side on 16 September
and put the same door in: the rulebook said it in a sentence, and a sentence is
not a door.

Every shape is matched by its exact form, and --selftest holds the match against
the real ones and the fakes on every run of check.sh — no network, no GitHub, and
it fails the build before a loose rule can pass a commit.
"""

import json
import re
import sys
import urllib.error
import urllib.request

# ---------------------------------------------------------------------------
# Who reviews. Two lines, and the Chairman changes either in one.
#
# DEFAULT_REVIEWER reads every pull request, and is who the reason lines tell a
# session to ask. GATE_REVIEWER is the other vendor, required on the classes the
# rulebook lists — here, the review machinery itself.
DEFAULT_REVIEWER = "sonnet"
GATE_REVIEWER = "codex"

CODEX = "chatgpt-codex-connector[bot]"
# The Sonnet reviewer answers as GitHub Actions, and that is the whole of its
# independence. A Sonnet read run from inside a builder session would post under
# the Chairman's own account, where it could not be told from the lead writing
# "looks fine" about its own work — the one thing this gate exists to prevent.
# No personal access token can post under this name; only a workflow can, and
# `issue_comment` runs that workflow from the default branch rather than from
# the pull request's head. See .github/workflows/review.yml.
ACTIONS = "github-actions[bot]"

SUMMARY_MARKER = "codex-pull-request-review-summary"

# The five answers, worst first: a commit is judged by the strongest thing said
# about it, and only CLEAN opens the gate.
FINDINGS = "findings"
CLEAN = "clean"
CROSS_VENDOR = "cross-vendor"
NO_VERDICT = "no verdict"
UNREAD = "unread"
ORDER = (FINDINGS, CLEAN, CROSS_VENDOR, NO_VERDICT)


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
    """Codex's clean pass, as a finished sentence and not a phrase inside one.

    This line is one of the two things that open the gate, so a phrase test will
    not do — the reviewer made that case twice. As a P1 on #21: "Codex Review:
    Found major issues" contains the two words and means the opposite. As a P1 on
    #24, against the tighter phrase that answered it: "Codex Review: Didn't find
    any major issues because the review did not complete" carries the whole
    verdict and still takes it back. Verifying that one turned up its mirror
    image, "Codex Review: I almost didn't find any major issues", which passed too.

    So the verdict is anchored at both ends: nothing may stand before it, and it
    must close with its own full stop, which is where every qualification of the
    sentence has to attach. What is left undefended is a *following* sentence
    that reverses a finished verdict — "…issues. But the review did not
    complete." The alternative is enumerating the encouragements the reviewer
    appends ("Keep it up!", "Keep them coming!"), which jams this gate shut on
    the day it writes a new one. Named here rather than papered over.
    """
    return CLEAN_VERDICT.match(first.replace("’", "'")) is not None


def _codex_comment_verdict(body, head, resolve=None):
    """What a plain comment by Codex says about this commit.

    Its clean pass names the commit and means nothing was found. Its summary
    table names the commit too, but a completed row says only that a review ran
    — the findings, if there were any, are a separate review — so it proves a
    read and never a clean one.

    This is the one place the gate leans on Codex keeping its habits: its own
    blurb says it may signal no findings with a 👍 reaction alone, and a reaction
    names no commit, so the gate cannot read one. If the clean-pass comment ever
    stops arriving, a pull request waiting on Codex stops at "no verdict" until
    somebody teaches this function the new shape. Red is the right way to fail —
    a gate that guessed clean from the absence of findings would be the gate this
    one replaces — but it is a jam, not a quiet one, and the reason line says
    which shape is missing.
    """
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


# The Sonnet reviewer's two first lines, written by .github/workflows/review.yml
# and matched here. Anchored at both ends for the reason _says_clean gives: a
# phrase test passed "I almost didn't find any major issues" on #24, and the
# same trick works on any wording that is only matched at the front. These two
# shapes are ours rather than a vendor's, so unlike Codex's they cannot change
# under us — but the workflow and this file have to be edited together, and the
# gate files rule below is what keeps a change to either read cold.
SONNET_CLEAN = re.compile(r"Claude Review:\s*no findings on this commit\.\s*$")
SONNET_FINDINGS = re.compile(r"Claude Review:\s*findings on this commit, below\.\s*$")


def _sonnet_comment_verdict(body, head, resolve=None):
    """What a comment by the Sonnet reviewer says about this commit.

    It answers only in comments — it submits no GitHub review — so both of its
    verdicts arrive here, and the commit is named the same way Codex names it.
    Anything else the workflow posts, its own did-not-read notice included, is
    deliberately not one of these two shapes and counts as nothing.
    """
    first = body.strip().splitlines()[0]
    said = None
    if SONNET_CLEAN.match(first):
        said = CLEAN
    elif SONNET_FINDINGS.match(first):
        said = FINDINGS
    if said is None:
        return None
    note = _reviewed_note(head)
    lines = [ln.strip() for ln in body.splitlines()]
    if any(_names_head(ln, note, head, resolve) for ln in lines):
        return said
    return None


# The register. A login, and how that reviewer's plain comments read. Adding a
# reviewer is an entry here and the same login in the wake job of
# .github/workflows/check.yml — _wake_matches_register() below refuses the build
# if the two ever disagree.
REVIEWERS = {
    "codex": (CODEX, _codex_comment_verdict),
    "sonnet": (ACTIONS, _sonnet_comment_verdict),
}


def comment_verdict(body, head, login, resolve=None):
    """What a plain comment by `login` says about this commit, or None.

    Only a reviewer's own words count: anyone who can comment on a pull request
    can type a clean pass, so a comment by anybody else is not one.
    """
    if not body or not body.strip():
        return None
    entry = REVIEWERS.get(_key_for(login))
    if entry is None:
        return None
    return entry[1](body, head, resolve)


def _key_for(login):
    for key, (who, _) in REVIEWERS.items():
        if who == login:
            return key
    return None


WITH_FINDINGS = {"COMMENTED", "CHANGES_REQUESTED"}


def review_verdict(review, head):
    """What a submitted GitHub review says about this commit.

    A reviewer submits a review only when it has something to say, so a submitted
    review is a finding on the commit it names; an approval is the one shape that
    is not. PENDING is a draft nobody has sent; DISMISSED is one somebody took
    back. Neither is a read of this commit, and the old test — login and commit
    id — counted both.

    Read for every login on the register, not just Codex's. Today only Codex
    submits reviews, but a reviewer that answered by approving would otherwise be
    silently uncountable, and the asymmetry would be a trap rather than a rule.
    """
    key = _key_for(review.get("user", {}).get("login"))
    if key is None:
        return None, None
    if review.get("commit_id") != head:
        return None, None
    state = review.get("state")
    if state == "APPROVED":
        return CLEAN, key
    if state in WITH_FINDINGS:
        return FINDINGS, key
    return None, None


# The gate's own files. A pull request touching any of them is the class the
# rulebook calls "this review gate itself", where the other vendor is required.
#
# The whole of .github/workflows/ is on the list, not just the two files that
# exist there today, and that is the sharp edge rather than tidiness. A comment
# by GitHub Actions is what the Sonnet reviewer's read looks like, and any
# workflow holding the repository's token can post one. A branch may add a
# workflow of its own that runs on `pull_request` — from a branch of this
# repository that token can write — and post the clean shape about its own head.
# With the whole directory on this list such a branch is a gate change, so its
# own comment cannot clear it and GATE_REVIEWER must read it cold. Narrow this to
# named files and that route opens.
GATE_FILES = ("check.sh", "review-gate.py")
GATE_DIR = ".github/workflows/"


def touches_the_gate(paths):
    return sorted(set(p for p in paths if p in GATE_FILES or p.startswith(GATE_DIR)))


def verdict(reviews, comments, head, resolve=None, gate_files=()):
    """The gate's one answer about the head commit, and who gave it.

    `gate_files` is what this pull request changes of the gate, empty for an
    ordinary change. When it is not empty only GATE_REVIEWER may clear the
    commit; a clean read by anyone else is CROSS_VENDOR, which is red, and says
    who has to read it instead.
    """
    said = {}

    def note(answer, key):
        if answer is None:
            return
        # Worst wins for each reviewer, so a clean pass posted after findings on
        # the same commit does not take them back.
        if said.get(key) is None or ORDER.index(answer) < ORDER.index(said[key]):
            said[key] = answer

    for r in reviews:
        note(*review_verdict(r, head))
    for c in comments:
        login = c.get("user", {}).get("login")
        note(comment_verdict(c.get("body"), head, login, resolve), _key_for(login))

    if FINDINGS in said.values():
        return FINDINGS, _who(said, FINDINGS)
    may_clear = (GATE_REVIEWER,) if gate_files else tuple(REVIEWERS)
    for key in may_clear:
        if said.get(key) == CLEAN:
            return CLEAN, key
    if CLEAN in said.values():
        return CROSS_VENDOR, _who(said, CLEAN)
    if NO_VERDICT in said.values():
        return NO_VERDICT, _who(said, NO_VERDICT)
    return UNREAD, None


def _who(said, answer):
    for key in sorted(said):
        if said[key] == answer:
            return key
    return None


def reason(answer, who, head, gate_files=()):
    """One line saying why the gate is shut, in the gate's own voice."""
    asked = REVIEWERS[DEFAULT_REVIEWER][0]
    if gate_files:
        asked = REVIEWERS[GATE_REVIEWER][0]
    if answer == FINDINGS:
        return ("the reviewer (%s) read commit %s and left findings on it — answer them, land "
                "the round's fixes as one push, and ask once; the gate opens on a commit a "
                "reviewer reads clean, never on an answer to a finding"
                % (REVIEWERS[who][0], head))
    if answer == CROSS_VENDOR:
        return ("%s read commit %s clean, but this pull request changes the review machinery "
                "(%s), where the rulebook requires the other vendor — ask %s on this pull "
                "request, and it waits for that read however long it takes"
                % (REVIEWERS[who][0], head, ", ".join(gate_files), asked))
    if answer == NO_VERDICT:
        return ("%s has run a review on commit %s but has not posted what it found — re-run "
                "this check once it has" % (REVIEWERS[who][0], head))
    return ("no reviewer has read commit %s — ask %s on the pull request, and when it has "
            "finished, re-run this check" % (head, asked))


# ---------------------------------------------------------------------------
# The gate and the wake that feeds it have to agree, and a build is the only
# place anyone would notice that they do not.
#
# A read the gate counts but nothing wakes for is the failure of 8 September
# wearing a new coat: the answer sits on the page, correct, and the check stays
# red until a hand re-runs it. A wake for a login the gate does not count is the
# mirror — a re-run that can never change the answer. Hemz OS hit the first of
# these on 17 September with this exact reviewer, and named the rule that catches
# both: check the set, not the count, and say which half is missing.
#
# There is a third, which only appears once a reviewer answers through the
# repository's own token. GitHub starts no workflow run for an event that token
# caused, so a listener for github-actions[bot] can never fire — it reads like a
# guarantee and is a dead line. That reviewer's own workflow must call the wake
# instead, and this refuses both the dead line and its absence.
WAKE_LOGIN = re.compile(r"github\.event\.comment\.user\.login\s*==\s*'([^']+)'")


def wake_logins(text):
    return sorted(set(WAKE_LOGIN.findall(text)))


def triggers(text):
    """The top-level trigger names in a workflow file's `on:` block."""
    found, inside = [], False
    for line in text.splitlines():
        if re.match(r"^on:\s*$", line):
            inside = True
            continue
        if inside:
            if line.strip() and not line.startswith((" ", "\t", "#")):
                break
            m = re.match(r"^  ([A-Za-z_]+):", line)
            if m:
                found.append(m.group(1))
    return sorted(set(found))


CHECK_WORKFLOW = ".github/workflows/check.yml"
REVIEW_WORKFLOW = ".github/workflows/review.yml"
WAKE_WORKFLOW = ".github/workflows/wake.yml"
CALLS_WAKE = "uses: ./" + WAKE_WORKFLOW


def _read(path):
    with open(path, encoding="utf-8") as f:
        return f.read()


def _check_wiring():
    """The gate, the wake and the reviewer workflow, held against each other."""
    bad = 0
    registered = dict((login, key) for key, (login, _) in REVIEWERS.items())
    for name in (DEFAULT_REVIEWER, GATE_REVIEWER):
        if name not in REVIEWERS:
            print("  wiring: '%s' is not on the register %s" % (name, sorted(REVIEWERS)))
            bad += 1
    if bad:
        return bad
    try:
        listened = set(wake_logins(_read(CHECK_WORKFLOW)))
        review = _read(REVIEW_WORKFLOW)
        review_on = triggers(review)
        wake_on = triggers(_read(WAKE_WORKFLOW))
    except OSError as e:
        print("  wiring: %s" % e)
        return 1

    for login in sorted(registered):
        if login == ACTIONS:
            # It answers through the repository's own token, so no listener can
            # hear it. Its own workflow has to ask the gate again.
            if CALLS_WAKE not in review:
                print("  wiring: %s answers as %s, whose comment starts no workflow run — %s "
                      "must call %s itself, or its read sits on the page unseen and the check "
                      "stays red until a hand re-runs it"
                      % (registered[login], login, REVIEW_WORKFLOW, WAKE_WORKFLOW))
                bad += 1
            if login in listened:
                print("  wiring: %s listens for %s, which can never fire — GitHub starts no "
                      "workflow run for an event the repository's own token caused. A dead line "
                      "that looks like a wake is worse than none" % (CHECK_WORKFLOW, login))
                bad += 1
        elif login not in listened:
            print("  wiring: %s never wakes for %s, whose read the gate DOES count — that answer "
                  "would sit on the page unseen and the check stay red until a hand re-ran it"
                  % (CHECK_WORKFLOW, login))
            bad += 1
    for login in sorted(listened - set(registered)):
        print("  wiring: %s listens for %s, whom the gate does not count — a re-run that can "
              "never change the answer" % (CHECK_WORKFLOW, login))
        bad += 1

    # The reviewer runs on `issue_comment` and nothing else, which is the whole
    # of its independence: that trigger runs the workflow file from the DEFAULT
    # branch. On `pull_request` a branch could edit its own reviewer and write
    # itself a clean pass, and the gate would count it. The wake it calls is
    # reached the same way, so it may only ever be called.
    if review_on != ["issue_comment"]:
        print("  wiring: %s triggers on %s; it must be issue_comment and nothing else, or a "
              "branch can run a reviewer of its own writing" % (REVIEW_WORKFLOW, review_on))
        bad += 1
    if wake_on != ["workflow_call"]:
        print("  wiring: %s triggers on %s; it must be workflow_call and nothing else"
              % (WAKE_WORKFLOW, wake_on))
        bad += 1

    # The verdict lines live in two files — the workflow writes them, this one
    # matches them — and that is the one duplication this design could not avoid.
    # So they are held against each other here rather than trusted: the exact
    # strings review.yml would post are fed to the matcher that has to accept
    # them. Change the wording in either file alone and the build says so, rather
    # than the gate quietly ceasing to recognise its own reviewer.
    posted = re.findall(r'first="([^"]+)"', review)
    fake_head = "090e429a31cd5f0b2e4d7a1c9b8e6f4d2a1c3b5e"
    got = set()
    for line in posted:
        got.add(_sonnet_comment_verdict(
            "%s\n\n**Reviewed commit:** `%s`\n" % (line, fake_head), fake_head))
    if got != {CLEAN, FINDINGS}:
        print("  wiring: the verdict lines %s posts are %s; this gate reads them as %s, and it "
              "must read exactly one clean and one findings" % (REVIEW_WORKFLOW, posted, sorted(
                  str(g) for g in got)))
        bad += 1
    if "**Reviewed commit:**" not in review:
        print("  wiring: %s no longer names the commit in the form this gate matches"
              % REVIEW_WORKFLOW)
        bad += 1

    # "Read the code, write one comment, nothing else" is the whole of what this
    # reviewer promises, and a command-line binary with a tool surface is a much
    # larger thing to promise it of than a single HTTP call would be. So the
    # flags that make it true are checked rather than intended: a later session
    # tidying one of them away is the likeliest way this quietly becomes a
    # reviewer that can run commands on a hostile diff's say-so.
    for flag, why in (('--tools ""', "every built-in tool would be back on"),
                      ("--restricted", "it would read this repository's own settings files"),
                      ("--strict-mcp-config", "it could pick up MCP servers from elsewhere"),
                      ("--model claude-sonnet-5", "it would not be the reviewer he named"),
                      ("--effort max", "it would not be at the effort he named")):
        if flag not in review:
            print("  wiring: %s no longer passes %s — %s" % (REVIEW_WORKFLOW, flag, why))
            bad += 1
    if not bad:
        print("ok: the gate counts %d reviewer(s), each read reaches the check by a route that "
              "can actually fire, and the reviewer runs only from the default branch"
              % len(registered))
    return bad


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
    codex_cases = [
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
    # The Sonnet reviewer's own shapes, and the ways a looser match would be
    # talked into one. The workflow writes these two lines and nothing else
    # carries them; its did-not-read notice deliberately does not.
    sclean = "Claude Review: no findings on this commit.\n\n**Reviewed commit:** `090e429a31`\n"
    sfound = ("Claude Review: findings on this commit, below.\n\n**Reviewed commit:** `090e429a31`\n"
              "\n---\n\n1. The cap is spent and this adds a rule.\n")
    sonnet_cases = [
        (sclean, head, CLEAN, "the Sonnet reviewer's clean pass naming the commit"),
        (sfound, head, FINDINGS, "its findings on this commit"),
        (sclean.replace("090e429a31", "29d7b543"), head, None, "its clean pass on another commit"),
        ("Claude Review: no findings on this commit.\n", head, None, "a clean pass naming no commit"),
        ("Claude Review: no findings on this commit. The review did not complete.\n\n"
         "**Reviewed commit:** `090e429a31`\n", head, None,
         "the whole verdict, taken back by what follows it on the same line"),
        ("I almost wrote Claude Review: no findings on this commit.\n\n"
         "**Reviewed commit:** `090e429a31`\n", head, None, "a sentence containing the verdict"),
        ("**The Sonnet reviewer did not read this commit** — the diff is over 600 KB.\n\n"
         "**Reviewed commit:** `090e429a31`\n", head, None, "the workflow's own did-not-read notice"),
        ("Claude Review: findings on this commit, below.\n", head, None, "findings naming no commit"),
        ("", head, None, "an empty comment"),
    ]
    review_cases = [
        ({"user": {"login": CODEX}, "commit_id": head, "state": "COMMENTED"}, (FINDINGS, "codex"), "a submitted review of this commit"),
        ({"user": {"login": CODEX}, "commit_id": head, "state": "CHANGES_REQUESTED"}, (FINDINGS, "codex"), "changes requested on this commit"),
        ({"user": {"login": CODEX}, "commit_id": head, "state": "APPROVED"}, (CLEAN, "codex"), "an approval of this commit"),
        ({"user": {"login": ACTIONS}, "commit_id": head, "state": "APPROVED"}, (CLEAN, "sonnet"), "an approval by the other reviewer on the register"),
        ({"user": {"login": CODEX}, "commit_id": head, "state": "DISMISSED"}, (None, None), "a review somebody took back"),
        ({"user": {"login": CODEX}, "commit_id": head, "state": "PENDING"}, (None, None), "a draft nobody sent"),
        ({"user": {"login": "someone"}, "commit_id": head, "state": "APPROVED"}, (None, None), "an approval by anybody else"),
        ({"user": {"login": CODEX}, "commit_id": other, "state": "APPROVED"}, (None, None), "an approval of another commit"),
        ({"user": {"login": CODEX}, "commit_id": other, "state": "COMMENTED"}, (None, None), "findings on another commit"),
    ]
    codex = lambda body: {"user": {"login": CODEX}, "body": body}
    sonnet = lambda body: {"user": {"login": ACTIONS}, "body": body}
    findings = {"user": {"login": CODEX}, "commit_id": head, "state": "COMMENTED"}
    gate_cases = [
        ([], [codex(clean)], (CLEAN, "codex"), "a clean pass and nothing else"),
        ([], [sonnet(sclean)], (CLEAN, "sonnet"), "the Sonnet reviewer's clean pass and nothing else"),
        ([{"user": {"login": CODEX}, "commit_id": head, "state": "APPROVED"}], [], (CLEAN, "codex"),
         "an approval and nothing else"),
        ([findings], [], (FINDINGS, "codex"), "findings on the head"),
        ([], [sonnet(sfound)], (FINDINGS, "sonnet"), "the Sonnet reviewer's findings on the head"),
        ([findings], [codex(clean)], (FINDINGS, "codex"),
         "a clean pass posted after findings on the same commit — the commit still carries them"),
        ([], [sonnet(sfound), sonnet(sclean)], (FINDINGS, "sonnet"),
         "the same reviewer clean after its own findings — still carried"),
        ([], [sonnet(sfound), codex(clean)], (FINDINGS, "sonnet"),
         "one reviewer's findings outrank the other's clean pass"),
        ([findings], [codex(summary)], (FINDINGS, "codex"), "findings, with the summary calling the review completed"),
        ([{"user": {"login": CODEX}, "commit_id": other, "state": "COMMENTED"}], [codex(clean)], (CLEAN, "codex"),
         "findings on the commit before, a clean pass on this one"),
        ([], [codex(summary)], (NO_VERDICT, "codex"), "a completed review whose verdict is not posted yet"),
        ([], [{"user": {"login": "someone"}, "body": clean}], (UNREAD, None),
         "a clean pass typed by somebody who is not a reviewer"),
        ([], [{"user": {"login": "someone"}, "body": sclean}], (UNREAD, None),
         "the Sonnet shape typed by a person — a builder session posts under his own account"),
        ([], [codex(sclean)], (UNREAD, None), "the Sonnet shape posted under Codex's identity"),
        ([], [sonnet(clean)], (UNREAD, None), "Codex's shape posted by Actions"),
        ([], [], (UNREAD, None), "an empty pull request"),
        ([{"user": {"login": CODEX}, "commit_id": head, "state": "DISMISSED"}], [], (UNREAD, None),
         "a review somebody took back, and nothing else"),
    ]
    # The door the second reviewer needed. Until today a gate change could only
    # be cleared by Codex because Codex was the only identity the gate could
    # count; counting Sonnet spends that accident, so the rule is written down.
    gate_file_cases = [
        (["review-gate.py"], [sonnet(sclean)], (CROSS_VENDOR, "sonnet"),
         "the default reviewer may not clear a change to the gate"),
        (["check.sh"], [sonnet(sclean)], (CROSS_VENDOR, "sonnet"), "nor to the check that runs it"),
        ([".github/workflows/review.yml"], [sonnet(sclean)], (CROSS_VENDOR, "sonnet"),
         "nor to the reviewer it is"),
        ([".github/workflows/check.yml"], [sonnet(sclean)], (CROSS_VENDOR, "sonnet"),
         "nor to the wake that fetches it"),
        ([".github/workflows/anything-new.yml"], [sonnet(sclean)], (CROSS_VENDOR, "sonnet"),
         "nor to a workflow a branch adds — which could post this very comment"),
        (["review-gate.py"], [codex(clean)], (CLEAN, "codex"), "the other vendor clears it"),
        (["review-gate.py"], [codex(clean), sonnet(sclean)], (CLEAN, "codex"),
         "both read it clean — the required one is what counts"),
        (["review-gate.py"], [sonnet(sfound)], (FINDINGS, "sonnet"),
         "findings on a gate change are still findings, whoever left them"),
        (["README.md"], [sonnet(sclean)], (CLEAN, "sonnet"), "an ordinary change still clears"),
        (["design/SCREEN-LAW.md", "README.md"], [sonnet(sclean)], (CLEAN, "sonnet"),
         "and so does one touching several ordinary files"),
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
    for body, h, want, what in codex_cases:
        bad += hold(comment_verdict(body, h, CODEX), want, what)
        # And no reviewer's shape may ever be mistaken for another's.
        if want is not None:
            bad += hold(comment_verdict(body, h, ACTIONS), None, what + ", read as the other reviewer's")
    for body, h, want, what in sonnet_cases:
        bad += hold(comment_verdict(body, h, ACTIONS), want, what)
        if want is not None:
            bad += hold(comment_verdict(body, h, CODEX), None, what + ", read as the other reviewer's")
    for reviews, comments, want, what in gate_cases:
        bad += hold(verdict(reviews, comments, head), want, what)
    for paths, comments, want, what in gate_file_cases:
        bad += hold(verdict([], comments, head, gate_files=touches_the_gate(paths)), want, what)
    bad += hold(comment_verdict(summary, head, CODEX, resolve=resolver), None,
                "a short form that resolves to another commit")
    bad += hold(comment_verdict(clean, head, CODEX, resolve=resolver), CLEAN,
                "a clean pass whose short form resolves to this head")
    bad += hold(comment_verdict(sclean, head, ACTIONS, resolve=resolver), CLEAN,
                "the Sonnet reviewer's clean pass, short form resolved")
    # touches_the_gate decides which door a pull request goes through, so it is
    # held on its own rather than only through the cases above.
    bad += hold(touches_the_gate(["README.md", "check.sh", ".github/workflows/x.yml"]),
                [".github/workflows/x.yml", "check.sh"], "which files are the gate")
    bad += hold(touches_the_gate(["design/ARCHITECT.md", "AGENTS.md"]), [],
                "and which are not")
    if bad:
        print("review-gate selftest failed: %d case(s)" % bad)
        return 1
    fakes = (sum(1 for c in codex_cases if c[2] is None)
             + sum(1 for c in sonnet_cases if c[2] is None)
             + sum(1 for r in review_cases if r[1] == (None, None))
             + sum(1 for g in gate_file_cases if g[2][0] == CROSS_VENDOR) + 1)
    print("ok: review gate tells a clean read from a commented one, for each reviewer on the "
          "register, in both shapes and every state they arrive in; it refuses a gate change "
          "cleared by anyone but %s; and it is fooled by none of the %d fakes"
          % (REVIEWERS[GATE_REVIEWER][0], fakes))
    return 1 if _check_wiring() else 0


# Which fetch is in flight. There are three — reviews, comments, and the pull
# request's changed files — and an error that names the wrong one sends the next
# session looking behind the wrong door.
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
            _asking[0] = "commit " + short
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
        # Every side of the page, every time: a reviewer's verdict is in one and
        # its findings in the other, and a gate that stopped at the first answer
        # it liked would be the gate this one replaces. The changed files decide
        # which reviewer is allowed to clear it.
        reviews = list(_pages("%s/pulls/%s/reviews" % (api, num), token))
        comments = list(_pages("%s/issues/%s/comments" % (api, num), token))
        files = [f.get("filename") for f in _pages("%s/pulls/%s/files" % (api, num), token)]
        gate_files = touches_the_gate(files)
        answer, who = verdict(reviews, comments, head, resolve=resolve, gate_files=gate_files)
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
        print("ok: %s has read %s and left nothing on it" % (REVIEWERS[who][0], head))
        return 0
    print("reason: " + reason(answer, who, head, gate_files))
    return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
