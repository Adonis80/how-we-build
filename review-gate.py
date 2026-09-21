#!/usr/bin/env python3
"""Has a reviewer read THIS commit, did it leave anything on it, and was it the
reviewer this change requires?

A review clears only the commit it read, and a reviewer answers in shapes that
mean opposite things. Missing one fails in the good case: a clean pass leaves the
check red for ever, which is how a Juku Perfume pull request sat red overnight on
8 September with the reviewer having read the head and said it was fine. Matching
loosely fails in the worse direction: on 13 September the reviewer showed that a
substring test passes on "Task Completed for `abc1234`; no review was performed",
so the gate would certify a commit nobody read.

Counting read and clean as one answer — which this gate did until 14 September —
fails in a third direction, and #21 is the proof: it merged on a commit carrying
a P1 the reviewer had posted and nobody had answered, because a read was all the
gate could see. So the gate gives one of five answers about the head commit, and
opens on the first alone:

    clean         read clean by a reviewer this change may be cleared by
    findings      read, and the reviewer left something on it
    cross-vendor  read clean, but by the reviewer this change may NOT use
    no verdict    a review is running on it, and has not said what it found
    unread        no finished read of this commit at all

A finding outranks every other answer about the same commit. The answer to a
finding is a push, and a push makes a new commit for the reviewer to read; what
the CTO says about the old one never clears it.

WHAT A READ HAS TO BE, AND WHY THE SECOND REVIEWER IS A BADGE AND NOT A LOGIN.
#34 closed at round ten having established the bar this file is built to:
a read must arrive **under a login a branch cannot wear, as a signal a branch
cannot erase**. #38 was built against `github-actions[bot]` posting a comment and
met neither half — that login belongs to every workflow token here, so a workflow
on a throwaway branch can wear it, and an issue comment can be edited or deleted
by anyone with write access, which is the population this gate defends against.

So the default reviewer answers as a **check run created by the `juku-reviewer`
GitHub App** (id below). Both halves come from that one fact:

  * Only a GitHub App can create a check run. A repository writer cannot create
    one, cannot edit one, and cannot delete one. That is the signal half.
  * Creating it needs an installation token, which needs the App's private key,
    which lives in the `reviewer` environment restricted to `main`. A run whose
    ref is a branch cannot read it. That is the login half, and
    `.github/workflows/door.yml` is the standing proof of it rather than the
    claim — run it on a branch and the job is refused before it starts.

Nothing is parsed out of prose for that reviewer: the commit is the check run's
own `head_sha` and the verdict is its own `conclusion`. The comment its workflow
also posts is for people to read, and this gate does not count it, which is why
it does not matter who can edit it.

WHO REVIEWS IS ONE LINE. The Chairman has changed the named reviewer twice in two
days, so the choice is `DEFAULT_REVIEWER`, `GATE_REVIEWER`, and the model and
effort below — nothing else, and the pages are written by role.

WHICH REVIEWER A CHANGE REQUIRES is the second line, and it is not decoration.
The rulebook requires the other vendor on pricing, live database changes or
schema, authentication and authorisation, public trust boundaries, deploy and
release machinery, and this review gate itself. Of that list this repository only
ever holds the last, so here the rule has one door: a pull request that touches
the gate opens on `GATE_REVIEWER` alone. Until a second reviewer existed that was
true by accident — Codex was the only identity the gate could count — and an
accident is not a door.

Every shape is matched by its exact form, and --selftest holds the match against
the real ones and the fakes on every run of check.sh — no network, no GitHub, and
it fails the build before a loose rule can pass a commit.
"""

import json
import re
import sys
import urllib.error
import urllib.parse
import urllib.request

# ---------------------------------------------------------------------------
# Who reviews, and as what. The Chairman changes any of these in one line.
#
# DEFAULT_REVIEWER reads every pull request. GATE_REVIEWER is the other vendor,
# required on the classes the rulebook lists — here, the review machinery itself.
DEFAULT_REVIEWER = "claude"
GATE_REVIEWER = "codex"

# His ruling of 18 September 2026, replacing that day's earlier word for Fable
# 5.1: the reviewer must be at least as strong as the Opus that builds, or it is
# a rubber stamp. Named here and held against the workflow that runs it by
# _check_wiring(), so the two can never drift apart.
REVIEWER_MODEL = "claude-sonnet-5"
REVIEWER_EFFORT = "max"

CODEX = "chatgpt-codex-connector[bot]"
CODEX_ASK = "@codex review"

# The badge. `juku-reviewer`, created on the Chairman's account 19 September 2026
# and installed on this repository alone; installation 162987297. The id is the
# identity — a slug can be renamed by its owner, an id cannot — and the check
# run's name keeps a later, unrelated use of the same App from reading as a
# review.
REVIEWER_APP_ID = 5000405
REVIEWER_CHECK = "juku-reviewer"
REVIEWER_ASK = "/claude review"

# The environment that holds its private key, and the standing proof that a
# branch cannot reach in. Both named here because the wiring check below refuses
# a build where the workflow has stopped naming either.
KEY_ENVIRONMENT = "reviewer"

SUMMARY_MARKER = "codex-pull-request-review-summary"

# The five answers, worst first: a commit is judged by the strongest thing said
# about it, and only CLEAN opens the gate.
FINDINGS = "findings"
CLEAN = "clean"
CROSS_VENDOR = "cross-vendor"
NO_VERDICT = "no verdict"
UNREAD = "unread"
ORDER = (FINDINGS, CLEAN, CROSS_VENDOR, NO_VERDICT)


# ---------------------------------------------------------------------------
# Codex answers in prose, so its shapes are matched exactly. None of this
# changed when the badge arrived; it is the reviewer this repository has had
# since the beginning and the one the gate door requires.

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

    This line is the only thing that opens the gate for it, so a phrase test will
    not do — the reviewer made that case twice. As a P1 on #21: "Codex Review:
    Found major issues" contains the two words and means the opposite. As a P1 on
    #24, against the tighter phrase that answered it: "Codex Review: Didn't find
    any major issues because the review did not complete" carries the whole
    verdict and still takes it back. Verifying that one turned up its mirror
    image, "Codex Review: I almost didn't find any major issues", which passed
    too.

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

    This is the one place the gate leans on a reviewer keeping its habits: Codex's
    own blurb says it may signal no findings with a 👍 reaction alone, and a
    reaction names no commit, so the gate cannot read one. If the clean-pass
    comment ever stops arriving, a gate change here stops at "no verdict" until
    somebody teaches this function the new shape. Red is the right way to fail,
    but it is a jam, and the reason line says which shape is missing.
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


# ---------------------------------------------------------------------------
# The badge. The default reviewer answers as a check run, and a check run needs
# no parsing at all: it carries the commit it is about in a field GitHub fills,
# and the verdict in a field only the App that made it can set.
#
# WHICH CONCLUSIONS ARE A VERDICT, AND WHY THE REST ARE NOT. `success` and
# `failure` are the two the reviewer writes deliberately, and they are the only
# two counted. `neutral` is the shape its workflow writes when it ran and could
# not produce a verdict — reviewer unreachable, no JSON back, diff too big — so
# it is a read that failed, never a read that passed. GitHub writes the others
# itself when a run is cancelled, times out, is skipped or goes stale, and none
# of those is a reviewer saying anything. Listing the two rather than excluding
# the rest is deliberate: a conclusion GitHub adds in future defaults to "not a
# verdict" instead of quietly defaulting to clean.
CONCLUSIONS = {"success": CLEAN, "failure": FINDINGS}


def check_run_verdict(run, head):
    """What one check run says about this commit, or None if it says nothing.

    Every test here is against a field GitHub fills from the credential that
    created the run, not against anything the run itself claims. `app.id` is the
    whole of the identity: a repository writer holds no App credential, so no
    token available to a branch can produce a run carrying this id — and none can
    edit or delete one that exists, which is the half a comment could never give.
    """
    if (run.get("app") or {}).get("id") != REVIEWER_APP_ID:
        return None
    if run.get("name") != REVIEWER_CHECK:
        return None
    # The fetch asks for one commit's runs, so this is belt and braces — and it
    # is what lets verdict() be tested on a list somebody hands it.
    if run.get("head_sha") != head:
        return None
    if run.get("status") != "completed":
        # Queued or running: the reviewer is reading it now. Saying "unread"
        # here would send a session off to ask a second time for a review
        # already in flight, and spend the allowance twice.
        return NO_VERDICT
    return CONCLUSIONS.get(run.get("conclusion"))


# The register. Each reviewer, the route its answer arrives by, and how a session
# asks it. Exactly one route each: Codex is read out of the pull request's prose
# by the login that wrote it, the default reviewer out of a check run by the App
# that created it. A reviewer with no `login` is counted in no comment and no
# review, however the page reads — which is why `github-actions[bot]` is not on
# this register and cannot be talked onto it.
REVIEWERS = {
    "codex": {"name": CODEX, "ask": CODEX_ASK, "login": CODEX,
              "comment": _codex_comment_verdict, "app_id": None},
    "claude": {"name": REVIEWER_CHECK, "ask": REVIEWER_ASK, "login": None,
               "comment": None, "app_id": REVIEWER_APP_ID},
}


def _key_for(login):
    """The register key for a login, or None for everybody else."""
    if login is None:
        return None
    for key, who in REVIEWERS.items():
        if who["login"] == login:
            return key
    return None


def comment_verdict(body, head, login, resolve=None):
    """What a plain comment by `login` says about this commit, or None.

    Only a reviewer's own words count: anyone who can comment on a pull request
    can type a clean pass, so a comment by anybody else is not one.
    """
    if not body or not body.strip():
        return None
    key = _key_for(login)
    if key is None or REVIEWERS[key]["comment"] is None:
        return None
    return REVIEWERS[key]["comment"](body, head, resolve)


WITH_FINDINGS = {"COMMENTED", "CHANGES_REQUESTED"}


def review_verdict(review, head):
    """What a submitted GitHub review says about this commit.

    A reviewer submits a review only when it has something to say, so a submitted
    review is a finding on the commit it names; an approval is the one shape that
    is not. PENDING is a draft nobody has sent; DISMISSED is one somebody took
    back. Neither is a read of this commit, and the old test — login and commit
    id — counted both.
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
# The whole of .github/workflows/ stays on the list, and the reason has changed
# rather than gone. #38 had it there because a branch could add a workflow that
# posted the clean shape as `github-actions[bot]`; the badge closes that hole
# outright, since no workflow token can create a check run under an App's id. It
# stays because of what the workflows now are: one holds the environment
# reference that keeps the key out of a branch's reach, one is the reviewer
# itself, one wakes the check, and one is the standing proof of the door. A
# change to any of them is a change to the gate however it is dressed. Narrowing
# it to named files buys nothing and would have to be argued back the first time
# a fifth file mattered.
GATE_FILES = ("check.sh", "review-gate.py")
GATE_DIR = ".github/workflows/"


def touches_the_gate(paths):
    return sorted(set(p for p in paths if p in GATE_FILES or p.startswith(GATE_DIR)))


def verdict(reviews, comments, check_runs, head, resolve=None, gate_files=()):
    """The gate's one answer about the head commit, and who gave it.

    `gate_files` is what this pull request changes of the gate, empty for an
    ordinary change. When it is not empty only GATE_REVIEWER may clear the
    commit; a clean read by anyone else is CROSS_VENDOR, which is red, and says
    who has to read it instead.

    A finding binds only from a reviewer that may clear this change. Codex's P1
    on #38, accepted in part: with the findings test running first, a reviewer
    with no standing on a gate change could hold the gate shut against the clean
    read of the one required — a reviewer that cannot open a door should not be
    able to bolt it either. Its findings are still on the page for the CTO to
    answer; they are simply not what the gate is waiting on.
    """
    said = {}

    def note(answer, key):
        if answer is None or key is None:
            return
        # Worst wins for each reviewer, so a clean pass posted after findings on
        # the same commit does not take them back — and neither does asking again
        # until the answer comes out differently.
        if said.get(key) is None or ORDER.index(answer) < ORDER.index(said[key]):
            said[key] = answer

    for r in reviews:
        note(*review_verdict(r, head))
    for c in comments:
        login = c.get("user", {}).get("login")
        note(comment_verdict(c.get("body"), head, login, resolve), _key_for(login))
    for run in check_runs:
        note(check_run_verdict(run, head), DEFAULT_REVIEWER)

    may_clear = (GATE_REVIEWER,) if gate_files else tuple(REVIEWERS)
    for key in may_clear:
        if said.get(key) == FINDINGS:
            return FINDINGS, key
    for key in may_clear:
        if said.get(key) == CLEAN:
            return CLEAN, key
    if FINDINGS in said.values():
        return FINDINGS, _who(said, FINDINGS)
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
    """One line saying why the gate is shut, in the gate's own voice.

    It names the ask rather than the bot, because the next thing a session does
    with this line is act on it.
    """
    needed = REVIEWERS[GATE_REVIEWER] if gate_files else REVIEWERS[DEFAULT_REVIEWER]
    if answer == FINDINGS:
        return ("%s read commit %s and left findings on it — answer them, land the round's "
                "fixes as one push, and ask once; the gate opens on a commit a reviewer reads "
                "clean, never on an answer to a finding" % (REVIEWERS[who]["name"], head))
    if answer == CROSS_VENDOR:
        return ("%s read commit %s clean, but this pull request changes the review machinery "
                "(%s), where the rulebook requires the other vendor — write '%s' on this pull "
                "request, and it waits for that read however long it takes"
                % (REVIEWERS[who]["name"], head, ", ".join(gate_files), needed["ask"]))
    if answer == NO_VERDICT:
        return ("%s is reading commit %s and has not said what it found — re-run this check "
                "once it has" % (REVIEWERS[who]["name"], head))
    return ("no reviewer has read commit %s — write '%s' on the pull request, and when it has "
            "finished, re-run this check" % (head, needed["ask"]))


# ---------------------------------------------------------------------------
# The gate, the wake, the reviewer and the door have to agree, and a build is the
# only place anyone would notice that they do not.
#
# A read the gate counts but nothing wakes for is the failure of 8 September
# wearing a new coat: the answer sits on the page, correct, and the check stays
# red until a hand re-runs it. A wake for a login the gate does not count is the
# mirror — a re-run that can never change the answer. Hemz OS hit the first of
# these on 17 September and named the rule that catches both: check the set, not
# the count, and say which half is missing.
WAKE_LOGIN = re.compile(r"github\.event\.comment\.user\.login\s*==\s*'([^']+)'")
ACTIONS = "github-actions[bot]"


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
DOOR_WORKFLOW = ".github/workflows/door.yml"
CALLS_WAKE = "uses: ./" + WAKE_WORKFLOW
DOOR_BRANCHES = "proof/door-*"
USES_ENVIRONMENT = re.compile(r"^\s*environment:\s*" + re.escape(KEY_ENVIRONMENT) + r"\s*$", re.M)


def _read(path):
    with open(path, encoding="utf-8") as f:
        return f.read()


def _check_routes():
    """Every reviewer on the register is reachable exactly one way."""
    bad = 0
    for name in (DEFAULT_REVIEWER, GATE_REVIEWER):
        if name not in REVIEWERS:
            print("  wiring: '%s' is not on the register %s" % (name, sorted(REVIEWERS)))
            bad += 1
    for key in sorted(REVIEWERS):
        who = REVIEWERS[key]
        routes = [r for r in ("login", "app_id") if who[r] is not None]
        if len(routes) != 1:
            print("  wiring: reviewer '%s' answers by %s; it must be exactly one of login or "
                  "app_id, or the same answer counts twice" % (key, routes or "nothing"))
            bad += 1
        if (who["comment"] is not None) != (who["login"] is not None):
            print("  wiring: reviewer '%s' has a comment matcher and no login, or the other way "
                  "round — a matcher nothing reaches is a dead rule" % key)
            bad += 1
    # The login every workflow token in this repository can wear. It was #38's
    # reviewer identity and #34's closing argument is why it is not one here; a
    # register entry carrying it would hand that hole straight back.
    if ACTIONS in [w["login"] for w in REVIEWERS.values()]:
        print("  wiring: %s is on the register. Every workflow token here can post under it, "
              "including one on a branch that was never opened as a pull request — see #34" % ACTIONS)
        bad += 1
    return bad


def _check_wiring():
    """The four workflow files, held against the register and each other."""
    bad = _check_routes()
    if bad:
        return bad
    try:
        check = _read(CHECK_WORKFLOW)
        review = _read(REVIEW_WORKFLOW)
        door = _read(DOOR_WORKFLOW)
        wake = _read(WAKE_WORKFLOW)
        wake_on = triggers(wake)
    except OSError as e:
        print("  wiring: %s" % e)
        return 1
    listened = set(wake_logins(check))
    counted = dict((w["login"], key) for key, w in REVIEWERS.items() if w["login"])

    for login in sorted(counted):
        if login not in listened:
            print("  wiring: %s never wakes for %s, whose read the gate DOES count — that answer "
                  "would sit on the page unseen and the check stay red until a hand re-ran it"
                  % (CHECK_WORKFLOW, login))
            bad += 1
    for login in sorted(listened - set(counted)):
        print("  wiring: %s listens for %s, whom the gate does not count — a re-run that can "
              "never change the answer" % (CHECK_WORKFLOW, login))
        bad += 1

    # The gate reads check runs, and a workflow that may not read them gets a 403
    # where it expects an answer. Cheap to assert, and the failure it prevents
    # reads like "the reviewer has not read this commit".
    if "checks: read" not in check:
        print("  wiring: %s does not grant `checks: read`, so the gate cannot see the badge's "
              "check run at all and every pull request reads as unread" % CHECK_WORKFLOW)
        bad += 1

    # The reviewer runs on `issue_comment` and nothing else, which is half of its
    # independence: that trigger runs the workflow file from the DEFAULT branch,
    # and it is also the ref the environment's branch policy admits. On
    # `pull_request` a branch would run a reviewer of its own writing, and the
    # environment would refuse it the key — so the failure would be confusing
    # rather than dangerous, but it would still be a reviewer nobody wrote down.
    if triggers(review) != ["issue_comment"]:
        print("  wiring: %s triggers on %s; it must be issue_comment and nothing else, or a "
              "branch can run a reviewer of its own writing" % (REVIEW_WORKFLOW, triggers(review)))
        bad += 1
    if wake_on != ["workflow_call"]:
        print("  wiring: %s triggers on %s; it must be workflow_call and nothing else"
              % (WAKE_WORKFLOW, wake_on))
        bad += 1

    # THE WAKE MUST ASK AGAIN WHATEVER THE CHECK CURRENTLY SAYS. With one
    # reviewer a verdict could only move the gate from red to green, so the wake
    # re-ran the red runs and that was enough. Counting a second reviewer made
    # the other direction reachable — one reads a commit clean, the other leaves
    # findings on it, and the check must go from green to RED. On 21 September
    # that happened on #43 and the wake answered "no red check run — nothing to
    # re-run", leaving a stale green under a findings verdict, which is #24, #30
    # and #37's failure from the other side. A filter on the conclusion here is
    # that bug, so the build refuses one.
    if re.search(r'conclusion\s*!=\s*\\?"success\\?"', wake):
        print("  wiring: %s re-runs only a check that is already failing. Two reviewers can "
              "disagree about one commit, so a verdict can take the gate from green to red, "
              "and that re-run would never happen — the green would stand under the findings"
              % WAKE_WORKFLOW)
        bad += 1

    # The badge's check run is not something this repository has watched GitHub
    # deliver an event for, so nothing is built on the assumption that it does.
    # The reviewer asks the gate again itself, the way #38 proved works.
    if CALLS_WAKE not in review:
        print("  wiring: %s does not call %s. Its verdict is a check run, and no listener here "
              "has ever been shown to hear one — so it must ask the gate again itself, or its "
              "read sits unseen and the check stays red until a hand re-runs it"
              % (REVIEW_WORKFLOW, WAKE_WORKFLOW))
        bad += 1

    # NOTHING MAY CANCEL A REVIEW IN FLIGHT. GitHub puts a run in its concurrency
    # group before the job's `if:` is evaluated, so with cancel-in-progress set
    # every comment on the pull request — including the ones that carry no ask
    # and skip immediately — kills the read that is running. It destroyed one on
    # #43 on 21 September (run 35587070648, cancelled forty seconds in by a
    # stand-down note) and it fails silently: the ask is on the thread, the
    # reviewer never speaks, the gate says `unread`, and the allowance is spent
    # again on the retry. On a public repository it is also a griefing route,
    # because the cancellation happens before any author gate is read.
    if re.search(r'^\s*cancel-in-progress:\s*true\s*$', review, re.M):
        print("  wiring: %s sets cancel-in-progress. Every comment enters the concurrency group "
              "before the job's `if:` is read, so a passing remark cancels a review in flight "
              "and the gate just says unread" % REVIEW_WORKFLOW)
        bad += 1

    # THE DOOR. Without this line the App's private key is readable by any run on
    # any branch, and the badge is worth nothing: a branch mints an installation
    # token and writes itself a clean check run. It is one word deep in a YAML
    # file and would be the easiest thing here to tidy away by accident.
    if not USES_ENVIRONMENT.search(review):
        print("  wiring: %s does not run in the `%s` environment, so the App's private key is "
              "readable from any branch and the badge can be forged. This is the door"
              % (REVIEW_WORKFLOW, KEY_ENVIRONMENT))
        bad += 1
    if not USES_ENVIRONMENT.search(door):
        print("  wiring: %s no longer references the `%s` environment, so it proves nothing"
              % (DOOR_WORKFLOW, KEY_ENVIRONMENT))
        bad += 1
    # The proof has to be runnable on a branch, which is the whole point of it,
    # and must never fire on `pull_request` — there it would be red on every
    # ordinary pull request, presenting the correct result as a permanent
    # failure and teaching everyone to ignore it.
    if triggers(door) != ["push", "workflow_dispatch"]:
        print("  wiring: %s triggers on %s; it must be workflow_dispatch and a push to the "
              "proof branches, and nothing else" % (DOOR_WORKFLOW, triggers(door)))
        bad += 1
    if DOOR_BRANCHES not in door:
        print("  wiring: %s no longer restricts its push trigger to %s, so ordinary work would "
              "start it" % (DOOR_WORKFLOW, DOOR_BRANCHES))
        bad += 1

    # The check run's name and its conclusions live in two files — the workflow
    # writes them, this one reads them — and that is the one duplication this
    # design could not avoid. So they are held against each other rather than
    # trusted: every conclusion review.yml can write is fed to the matcher that
    # has to accept it. Change either file alone and the build says so, rather
    # than the gate quietly ceasing to recognise its own reviewer.
    if ('name=%s' % REVIEWER_CHECK) not in review and ('"%s"' % REVIEWER_CHECK) not in review:
        print("  wiring: %s does not name its check run `%s`, which is the only name this gate "
              "reads" % (REVIEW_WORKFLOW, REVIEWER_CHECK))
        bad += 1
    written = sorted(set(re.findall(r'^\s*conclusion=([a-z_]+)\s*$', review, re.M)))
    fake_head = "090e429a31cd5f0b2e4d7a1c9b8e6f4d2a1c3b5e"
    got = dict((c, check_run_verdict(
        {"app": {"id": REVIEWER_APP_ID}, "name": REVIEWER_CHECK, "head_sha": fake_head,
         "status": "completed", "conclusion": c}, fake_head)) for c in written)
    want = {"success": CLEAN, "failure": FINDINGS, "neutral": None}
    if got != want:
        print("  wiring: %s writes the conclusions %s, which this gate reads as %s — it must "
              "write exactly one clean (success), one findings (failure) and one that is no "
              "verdict at all (neutral)" % (REVIEW_WORKFLOW, written, got))
        bad += 1

    # "Read the code, write one check run and one comment, nothing else" is the
    # whole of what this reviewer promises, and a command-line binary with a tool
    # surface is a much larger thing to promise it of than a single HTTP call
    # would be. So the flags that make it true are checked rather than intended:
    # a later session tidying one of them away is the likeliest way this quietly
    # becomes a reviewer that can run commands on a hostile diff's say-so.
    for flag, why in (('--tools ""', "every built-in tool would be back on"),
                      ("--restricted", "it would read this repository's own settings files"),
                      ("--strict-mcp-config", "it could pick up MCP servers from elsewhere"),
                      ("--model " + REVIEWER_MODEL, "it would not be the reviewer he named"),
                      ("--effort " + REVIEWER_EFFORT, "it would not be at the effort he named")):
        if flag not in review:
            print("  wiring: %s no longer passes %s — %s" % (REVIEW_WORKFLOW, flag, why))
            bad += 1

    # Codex's P1 on #38, accepted in full: the brief was read from the pull
    # request's own head, so a proposer could edit AGENTS.md to instruct the
    # reviewer to answer clean. It is read from the protected branch instead, and
    # the pages under review reach the model as data in the user turn. That
    # distinction is the whole fix, and it is one `git show` away from being
    # undone.
    if "origin/${{ github.event.repository.default_branch }}:AGENTS.md" not in review:
        print("  wiring: %s no longer reads the brief from the protected branch. Read from the "
              "head, a pull request can write its own reviewer's instructions — Codex's P1 on "
              "#38" % REVIEW_WORKFLOW)
        bad += 1

    if not bad:
        print("ok: the gate counts %d reviewer(s) by %d route(s), each read reaches the check by "
              "a route that can actually fire, the reviewer runs only from the default branch, "
              "and its key sits behind the `%s` door"
              % (len(REVIEWERS), len(set(r["app_id"] is None for r in REVIEWERS.values())),
                 KEY_ENVIRONMENT))
    return bad


def _run(conclusion=None, status="completed", app=REVIEWER_APP_ID, name=REVIEWER_CHECK, sha=None):
    return {"app": None if app is None else {"id": app}, "name": name,
            "head_sha": sha, "status": status, "conclusion": conclusion}


def _url_cases():
    """The URLs the gate asks GitHub for, and the one that was wrong.

    Codex's P1 on `a706799`: every verdict case in the selftest passed while the
    live fetch asked a different question, because nothing here had ever built a
    URL. A rule proved only against hand-made dictionaries is proved against the
    wrong thing.
    """
    runs = "https://api.github.com/repos/o/r/commits/abc/check-runs"
    return [
        (runs, 1, {"filter": "all"},
         {"filter": ["all"], "per_page": ["100"], "page": ["1"]},
         "the check runs, with the filter passed as a parameter"),
        (runs + "?filter=all", 2, None,
         {"filter": ["all"], "per_page": ["100"], "page": ["2"]},
         "the same filter arriving in the URL — the shape that gave "
         "filter='all?per_page=100' and silently fell back to `latest`"),
        ("https://api.github.com/repos/o/r/pulls/7/reviews", 3, None,
         {"per_page": ["100"], "page": ["3"]},
         "a plain endpoint with no query of its own"),
    ]


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
    # The badge, and every way a looser test would be talked into one. Only the
    # first two are the reviewer speaking; the rest are what a branch, a tidy-up
    # or GitHub itself can put on the same commit.
    badge_cases = [
        (_run("success", sha=head), CLEAN, "the badge's clean verdict on this commit"),
        (_run("failure", sha=head), FINDINGS, "its findings on this commit"),
        (_run("success", sha=other), None, "its clean verdict on another commit"),
        (_run("success", status="queued", sha=head), NO_VERDICT, "a review queued on this commit"),
        (_run("success", status="in_progress", sha=head), NO_VERDICT, "one running on it"),
        (_run("neutral", sha=head), None, "the shape it writes when it ran and could not read"),
        (_run("cancelled", sha=head), None, "a run somebody cancelled"),
        (_run("timed_out", sha=head), None, "one GitHub timed out"),
        (_run("action_required", sha=head), None, "one asking for a hand"),
        (_run("skipped", sha=head), None, "one that never ran"),
        (_run("stale", sha=head), None, "one GitHub called stale"),
        (_run("success", app=15368, sha=head), None,
         "the same verdict from the GitHub Actions app — the token every workflow here holds"),
        (_run("success", app=None, sha=head), None, "a check run with no app at all"),
        (_run("success", app="5000405", sha=head), None, "the app id as a string, not the id"),
        (_run("success", name="Claude Review", sha=head), None,
         "the right app under a name this gate does not read"),
    ]
    review_cases = [
        ({"user": {"login": CODEX}, "commit_id": head, "state": "COMMENTED"}, (FINDINGS, "codex"), "a submitted review of this commit"),
        ({"user": {"login": CODEX}, "commit_id": head, "state": "CHANGES_REQUESTED"}, (FINDINGS, "codex"), "changes requested on this commit"),
        ({"user": {"login": CODEX}, "commit_id": head, "state": "APPROVED"}, (CLEAN, "codex"), "an approval of this commit"),
        ({"user": {"login": CODEX}, "commit_id": head, "state": "DISMISSED"}, (None, None), "a review somebody took back"),
        ({"user": {"login": CODEX}, "commit_id": head, "state": "PENDING"}, (None, None), "a draft nobody sent"),
        ({"user": {"login": "someone"}, "commit_id": head, "state": "APPROVED"}, (None, None), "an approval by anybody else"),
        ({"user": {"login": ACTIONS}, "commit_id": head, "state": "APPROVED"}, (None, None),
         "an approval by the login every workflow token here can wear"),
        ({"user": {"login": CODEX}, "commit_id": other, "state": "APPROVED"}, (None, None), "an approval of another commit"),
        ({"user": {"login": CODEX}, "commit_id": other, "state": "COMMENTED"}, (None, None), "findings on another commit"),
    ]
    codex = lambda body: {"user": {"login": CODEX}, "body": body}
    actions = lambda body: {"user": {"login": ACTIONS}, "body": body}
    findings = {"user": {"login": CODEX}, "commit_id": head, "state": "COMMENTED"}
    # What review.yml posts for people to read. The gate counts none of it, which
    # is exactly why it does not matter that a writer can edit or delete it.
    prose = ("Claude Review: no findings on this commit.\n\n**Reviewed commit:** `090e429a31`\n")
    gate_cases = [
        ([], [codex(clean)], [], (CLEAN, "codex"), "a clean pass and nothing else"),
        ([], [], [_run("success", sha=head)], (CLEAN, "claude"), "the badge clean and nothing else"),
        ([{"user": {"login": CODEX}, "commit_id": head, "state": "APPROVED"}], [], [], (CLEAN, "codex"),
         "an approval and nothing else"),
        ([findings], [], [], (FINDINGS, "codex"), "findings on the head"),
        ([], [], [_run("failure", sha=head)], (FINDINGS, "claude"), "the badge's findings on the head"),
        ([findings], [codex(clean)], [], (FINDINGS, "codex"),
         "a clean pass posted after findings on the same commit — the commit still carries them"),
        ([], [], [_run("failure", sha=head), _run("success", sha=head)], (FINDINGS, "claude"),
         "asked twice on one commit, the findings stand — the answer to a finding is a push"),
        ([], [codex(clean)], [_run("failure", sha=head)], (FINDINGS, "claude"),
         "one reviewer's findings outrank the other's clean pass"),
        ([findings], [codex(summary)], [], (FINDINGS, "codex"), "findings, with the summary calling the review completed"),
        ([{"user": {"login": CODEX}, "commit_id": other, "state": "COMMENTED"}], [codex(clean)], [], (CLEAN, "codex"),
         "findings on the commit before, a clean pass on this one"),
        ([], [codex(summary)], [], (NO_VERDICT, "codex"), "a completed review whose verdict is not posted yet"),
        ([], [], [_run(status="in_progress", sha=head)], (NO_VERDICT, "claude"), "the badge still reading"),
        ([], [{"user": {"login": "someone"}, "body": clean}], [], (UNREAD, None),
         "a clean pass typed by somebody who is not a reviewer"),
        ([], [actions(prose)], [], (UNREAD, None),
         "the reviewer's own prose comment — it is for people, and the gate reads none of it"),
        ([], [actions(clean)], [], (UNREAD, None), "Codex's shape posted by a workflow"),
        ([], [], [_run("success", app=15368, sha=head)], (UNREAD, None),
         "a clean check run from the app every workflow token here holds"),
        ([], [], [], (UNREAD, None), "an empty pull request"),
        ([{"user": {"login": CODEX}, "commit_id": head, "state": "DISMISSED"}], [], [], (UNREAD, None),
         "a review somebody took back, and nothing else"),
    ]
    # The door in the gate: a change to the review machinery opens on the other
    # vendor's read alone.
    gate_file_cases = [
        (["review-gate.py"], [], [_run("success", sha=head)], (CROSS_VENDOR, "claude"),
         "the default reviewer may not clear a change to the gate"),
        (["check.sh"], [], [_run("success", sha=head)], (CROSS_VENDOR, "claude"), "nor to the check that runs it"),
        ([".github/workflows/review.yml"], [], [_run("success", sha=head)], (CROSS_VENDOR, "claude"),
         "nor to the reviewer it is"),
        ([".github/workflows/check.yml"], [], [_run("success", sha=head)], (CROSS_VENDOR, "claude"),
         "nor to the wake that fetches it"),
        ([".github/workflows/door.yml"], [], [_run("success", sha=head)], (CROSS_VENDOR, "claude"),
         "nor to the proof that the key is out of reach"),
        ([".github/workflows/anything-new.yml"], [], [_run("success", sha=head)], (CROSS_VENDOR, "claude"),
         "nor to a workflow a branch adds"),
        (["review-gate.py"], [codex(clean)], [], (CLEAN, "codex"), "the other vendor clears it"),
        (["review-gate.py"], [codex(clean)], [_run("success", sha=head)], (CLEAN, "codex"),
         "both read it clean — the required one is what counts"),
        (["review-gate.py"], [codex(clean)], [_run("failure", sha=head)], (CLEAN, "codex"),
         "findings by a reviewer with no standing here do not bolt a door it cannot open "
         "(Codex's P1 on #38, accepted in part)"),
        (["review-gate.py"], [], [_run("failure", sha=head)], (FINDINGS, "claude"),
         "but with no read by the required one they are still the most useful thing to say — "
         "real work first, then the scarce ask"),
        (["README.md"], [], [_run("success", sha=head)], (CLEAN, "claude"), "an ordinary change still clears"),
        (["design/SCREEN-LAW.md", "README.md"], [], [_run("success", sha=head)], (CLEAN, "claude"),
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
        # No reviewer's shape may be read as another's, and no bystander's as one.
        bad += hold(comment_verdict(body, h, ACTIONS), None, what + ", posted by a workflow")
    for run, want, what in badge_cases:
        bad += hold(check_run_verdict(run, head), want, what)
    for reviews, comments, runs, want, what in gate_cases:
        bad += hold(verdict(reviews, comments, runs, head), want, what)
    for paths, comments, runs, want, what in gate_file_cases:
        bad += hold(verdict([], comments, runs, head, gate_files=touches_the_gate(paths)), want, what)
    bad += hold(comment_verdict(summary, head, CODEX, resolve=resolver), None,
                "a short form that resolves to another commit")
    bad += hold(comment_verdict(clean, head, CODEX, resolve=resolver), CLEAN,
                "a clean pass whose short form resolves to this head")
    # touches_the_gate decides which door a pull request goes through, so it is
    # held on its own rather than only through the cases above.
    bad += hold(touches_the_gate(["README.md", "check.sh", ".github/workflows/x.yml"]),
                [".github/workflows/x.yml", "check.sh"], "which files are the gate")
    bad += hold(touches_the_gate(["design/ARCHITECT.md", "AGENTS.md"]), [], "and which are not")
    for url, page, params, want, what in _url_cases():
        built = _page_url(url, page, params)
        bad += hold(urllib.parse.parse_qs(urllib.parse.urlsplit(built).query), want, what)
        # One query string, and the path untouched: a second `?` is how the
        # parameters got swallowed in the first place.
        bad += hold(built.count("?"), 1, what + " — exactly one query string")
        bad += hold(urllib.parse.urlsplit(built).path, urllib.parse.urlsplit(url).path,
                    what + " — the path unchanged")
    if bad:
        print("review-gate selftest failed: %d case(s)" % bad)
        return 1
    fakes = (sum(1 for c in codex_cases if c[2] is None)
             + sum(1 for b in badge_cases if b[1] is None)
             + sum(1 for r in review_cases if r[1] == (None, None))
             + sum(1 for g in gate_cases if g[3] == (UNREAD, None))
             + sum(1 for g in gate_file_cases if g[3][0] == CROSS_VENDOR) + 1)
    print("ok: review gate tells a clean read from a commented one, for each reviewer on the "
          "register, in every shape and state they arrive in; it refuses a gate change cleared "
          "by anyone but %s; it asks GitHub for %d URL(s) that carry the parameters they say "
          "they do; and it is fooled by none of the %d fakes"
          % (REVIEWERS[GATE_REVIEWER]["name"], len(_url_cases()), fakes))
    return 1 if _check_wiring() else 0


# Which fetch is in flight. There are four — reviews, comments, the changed files
# and the check runs — and an error that names the wrong one sends the next
# session looking behind the wrong door.
_asking = [""]


def _page_url(url, page, params=None):
    """`url`, keeping any query it already carries, plus `params` and this page.

    Codex's P1 on `a706799`, and it was live rather than theoretical. The old
    form pasted `?per_page=…` onto a URL that already carried `?filter=all`,
    giving `?filter=all?per_page=100&page=1`. That parses as
    `filter="all?per_page=100"` with no `per_page` at all — and GitHub does not
    refuse it, it ignores the unrecognised filter and falls back to the default,
    `latest`. So the live fetch quietly asked for only the newest check run per
    name while this file documented, and its selftest proved, a worst-wins rule
    over every run on the commit. A findings verdict could have been retired by
    asking again until the answer came out differently: the exact hole the
    caller's comment says it closes. Nothing in the selftest could see it,
    because the selftest never built a URL.

    So the query is assembled rather than concatenated, and a URL that arrives
    with a query of its own keeps it. Both are held by _url_cases() below.
    """
    parts = urllib.parse.urlsplit(url)
    query = urllib.parse.parse_qsl(parts.query, keep_blank_values=True)
    query += sorted((params or {}).items())
    query += [("per_page", "100"), ("page", str(page))]
    return urllib.parse.urlunsplit(parts._replace(query=urllib.parse.urlencode(query)))


def _pages(url, token, key=None, params=None):
    """Every page of a GitHub list, whether it answers bare or in a wrapper."""
    _asking[0] = urllib.parse.urlsplit(url).path.rsplit("/", 1)[-1]
    page = 1
    while True:
        req = urllib.request.Request(
            _page_url(url, page, params),
            headers={"Authorization": "Bearer " + token, "Accept": "application/vnd.github+json"},
        )
        with urllib.request.urlopen(req) as r:
            body = json.load(r)
        batch = body if key is None else body.get(key, [])
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
        # `filter=all`, not the default `latest`: every run the badge has made on
        # this commit counts, worst first. On `latest` a findings verdict could be
        # retired by asking again until the answer came out differently, and the
        # gate's own rule is that the answer to a finding is a push.
        runs = list(_pages("%s/commits/%s/check-runs" % (api, head), token,
                           key="check_runs", params={"filter": "all"}))
        gate_files = touches_the_gate(files)
        answer, who = verdict(reviews, comments, runs, head, resolve=resolve, gate_files=gate_files)
    except urllib.error.HTTPError as e:
        if e.code in (401, 403):
            why = ("the workflow's token may not read this (it needs pull-requests: read and "
                   "checks: read), or GitHub is rate-limiting")
        elif e.code == 404:
            why = "GitHub found no such repository, pull request or commit — check GITHUB_REPOSITORY, PR_NUMBER and HEAD_SHA"
        elif e.code >= 500:
            why = "GitHub itself answered with an error — re-run the check"
        else:
            why = "GitHub refused the request"
        print("reason: HTTP %s when asked for the %s — %s" % (e.code, _asking[0] or "reviews", why))
        return 2
    if answer == CLEAN:
        print("ok: %s has read %s and left nothing on it" % (REVIEWERS[who]["name"], head))
        return 0
    print("reason: " + reason(answer, who, head, gate_files))
    return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
