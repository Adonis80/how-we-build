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
    findings      read, and the reviewer left something on it
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

import io
import json
import os
import re
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.parse
import urllib.request

# ---------------------------------------------------------------------------
# Who reviews, and as what. The Chairman changes any of these in one line.
#
# DEFAULT_REVIEWER reads every pull request. There is no second name beside it:
# his ruling of 22 September 2026 retired Codex as a reviewer, and the door that
# named it is gone rather than pointed somewhere else — see the docstring.
DEFAULT_REVIEWER = "claude"

# His ruling of 18 September 2026, replacing that day's earlier word for Fable
# 5.1: the reviewer must be at least as strong as the Opus that builds, or it is
# a rubber stamp. Named here and held against the workflow that runs it by
# _check_wiring(), so the two can never drift apart.
REVIEWER_MODEL = "claude-sonnet-5"
# And the effort a read is at is its change's class's. Decision 0005 (issue
# #75, 23 September 2026), in its own words: "Effort. Build at medium, high
# after one failed attempt, max only for reviews of the risky classes." A
# change to pages alone is read at WORDS_EFFORT; anything else, this machinery
# included, at REVIEWER_EFFORT. The class is worked out in each workflow and
# held below, at CLASS_FIRST.
REVIEWER_EFFORT = "max"
# Why high and not medium, since the decision names only what risky reads get
# (#79's seventh read): his ruling of 18 September holds the reviewer at least
# as strong as the lead that builds, and the lead builds at medium and steps to
# high after one failed attempt. At high, a read of pages stays at or above the
# lead's own effort; at medium it could fall below it. The CTO's reading.
WORDS_EFFORT = "high"

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
# strongest thing said about it, and only CLEAN opens the gate.
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
GATE_FILES = ("check.sh", "review-gate.py")
GATE_DIR = ".github/workflows/"


def touches_the_gate(paths):
    return sorted(set(p for p in paths if p in GATE_FILES or p.startswith(GATE_DIR)))


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
        return ("%s read commit %s and left findings on it — answer them, land the round's "
                "fixes as one push, and ask once; the gate opens on a commit a reviewer reads "
                "clean, never on an answer to a finding" % (REVIEWERS[who]["name"], head))
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
                      ("--model " + REVIEWER_MODEL, "it would not be the reviewer he named"),
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
READ_CALL = 'timeout --kill-after=60s "${left}s" claude -p \\'
READ_LIMIT = re.compile(r"^\s*limit=(\d+)\s*$", re.M)
READ_MARGIN = 5
READ_START = 'echo "started=$(date +%s)" >> "$GITHUB_OUTPUT"'
READ_LEFT = 'left=$(( STARTED + limit * 60 - $(date +%s) ))'
# (what the steps before the read did, how long ago the job started or what was
# recorded, whether the read may begin). `limit` is 25 in both files.
DEADLINE_CASES = (
    ("the job has just started", 0, True),
    ("the steps before ran to minute 20", 20 * 60, True),
    ("they ran to within a minute of the deadline", 25 * 60 - 30, False),
    ("they ran past it", 60 * 60, False),
    ("no start was recorded", "", False),
    ("the start is not a number", "1+1", False),
    # Unchecked, a word is an unset variable to the arithmetic, and the step
    # dies on it before it can say why.
    ("the start is a word", "soon", False),
)
READ_FAIL = """printf 'why=%s\\n' "$(printf '%s' "$1" | tr -d '\\r\\n')" >> "$GITHUB_OUTPUT\""""
READ_WHY = ("WHY: ${{ steps.read.outputs.why }}", 'title="Did not read: $WHY"')
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
            '"modelUsage":{"claude-sonnet-5":{"contextWindow":200000}}}', "allowance is spent"),
    (1, "", '{"is_error":true,"result":"boom","modelUsage":{"m":{"contextWindow":200000}}}',
     "unrecognised; 0 bytes on stderr"),
    (1, "", "not json: Prompt is too long", "too long for one read"),
    (1, "OAuth token has expired", "", "credential was refused"),
    (0, "", '{"subtype":"error_max_turns"}', "the tool answered 'error_max_turns'"),
    # A subtype is the tool's to write, and the reason is written to
    # $GITHUB_OUTPUT: a line break in it would be a second output of its own.
    (0, "", '{"subtype":"x\\nverdict=clean"}', "the tool answered 'xverdictclean'"),
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
    ("a read the job cuts off first", lambda t: t.replace("          limit=25\n", "          limit=28\n", 1)),
    ("no limit set", lambda t: t.replace("          limit=25\n", "", 1)),
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
# (#70's slice 2), and decision 0005 keeps max for the risky classes alone. So
# each reviewer works out a class from the diff it reads: `words` when every
# file the change touches is a page, `code` otherwise. The brief, AGENTS.md at
# any depth, is never a page: it instructs the reviewer or an agent, so a change
# to it changes a reader. Nor are the pages whose words are law here:
# HOW-WE-BUILD.md and CHARTER.md at the root (twice on 9 September a trim
# weakened what the operating page required, and a reader caught it where no
# machine could: #79's first read), RICH-DATA.md's data rules and the capped
# design/SCREEN-LAW.md (#79's third read), and a product's PRODUCT.md and
# design/CONSTITUTION.md (#79's fourth and sixth reads): every page
# review-product.yml carries but NAMES.md, a glossary. Nor is anything in a dot-directory, where .github
# and .claude keep settings and agents' instructions whatever their extension.
# The README is read as code while it still holds the rulebook's prose (#79's
# eighth read); once the library move leaves it an index, one line returns it
# to pages. The list splits renames, so a script renamed to a page is still a script, and is
# NUL-separated, so no name is read as two. It is written to a file first, so a
# list that cannot be made stops the step: read through `< <(...)` it failed
# unseen and read as no change at all, which is pages. The block is run, not read, against
# the changes below, from its first line to the one output that hands the
# effort to the read, so any line added inside it is run too.
CLASS_FIRST = "class=words"
CLASS_CODE = ("AGENTS.md|*/AGENTS.md|HOW-WE-BUILD.md|CHARTER.md|RICH-DATA.md|design/SCREEN-LAW.md|"
              "design/CONSTITUTION.md|PRODUCT.md|README.md|.*|*/.*) class=code ;;")
CLASS_ARMS = (CLASS_CODE, "*.md) ;;", "*) class=code ;;")
CLASS_EFFORT = ('case "$class" in words) effort=%s ;; *) effort=%s ;; esac'
                % (WORDS_EFFORT, REVIEWER_EFFORT))
CLASS_OUT = 'echo "effort=$effort" >> "$GITHUB_OUTPUT"'
CLASS_LIST = {
    REVIEW_WORKFLOW: ('git diff -z --name-only --no-renames "origin/${{ github.event.repository'
                      '.default_branch }}...${{ steps.head.outputs.sha }}" > "$RUNNER_TEMP/changed.txt"',
                      'done < "$RUNNER_TEMP/changed.txt"'),
    PRODUCT_WORKFLOW: ('g diff -z --name-only --no-renames "origin/$MAIN...$SHA" > "$t/changed.txt"',
                       'done < "$t/changed.txt"'),
}
EFFORT_IN = "EFFORT: ${{ steps.gather.outputs.effort }}"
EFFORT_GUARD = ('case "$EFFORT" in high|max) ;; *) fail "the change\'s class set no effort to '
                'read at" ;; esac')
READ_EFFORT = '--effort "$EFFORT"'
# review.yml's pages: a change to pages alone is given the pages and check.sh;
# any other is given every file, as every read was before. What is left out is
# named with its size, and the reviewer is told so and asked to say if a
# finding needed it: without those, a read short of a file is silent about it.
REVIEW_PAGES = "words:*.md|words:check.sh|code:*) ;;"
# And the verdict says how thoroughly it was read (#79's eighth read): a clean
# read at high with pages alone must not look like one at max with everything.
VERDICT_SAYS = ('title="No findings on this commit (read as $CLASS at effort $EFFORT)"',
                'title="Findings on this commit (read as $CLASS at effort $EFFORT)"',
                "CLASS: ${{ steps.gather.outputs.class }}", "EFFORT: ${{ steps.gather.outputs.effort }}")
REVIEW_LEFT_OUT = "%s bytes, left out: this change touches pages only ====="
REVIEW_COUNT = ('echo "left_out=$(grep -cE \'^===== .+: [0-9]+ bytes, left out: this change touches pages only =====$\' /tmp/pages.txt || true)" >> "$GITHUB_OUTPUT"')
REVIEW_COUNT_IN = "LEFT_OUT: ${{ steps.gather.outputs.left_out }}"
REVIEW_TOLD = ('if [ "$CLASS" = words ]; then', 'echo "a finding needed one, say which."',
               "CLASS: ${{ steps.gather.outputs.class }}")
# (the files a change touches, the class it must be read as). None is a list
# git could not make, which must stop the block rather than read as anything.
CLASS_CASES = (
    (None, None),
    ([], "words"),
    (["README.md"], "code"),
    (["docs/README.md"], "words"),
    (["docs/reviewer.md", "design/ARCHITECT.md", "design/REVIEW_RUBRIC.md"], "words"),
    (["docs/HOW-WE-BUILD.md", "docs/CHARTER.md"], "words"),
    (["a page with spaces.md"], "words"),
    (["AGENTS.md"], "code"),
    (["HOW-WE-BUILD.md"], "code"),
    (["README.md", "CHARTER.md"], "code"),
    (["RICH-DATA.md"], "code"),
    (["design/SCREEN-LAW.md"], "code"),
    (["design/CONSTITUTION.md", "README.md"], "code"),
    (["PRODUCT.md"], "code"),
    (["NAMES.md", "docs/guide.md"], "words"),
    (["docs/AGENTS.md"], "code"),
    (["README.md", "check.sh"], "code"),
    (["review-gate.py"], "code"),
    ([".github/workflows/review.yml"], "code"),
    ([".github/copilot-instructions.md"], "code"),
    ([".claude/skills/steward/SKILL.md"], "code"),
    (["docs/.hidden/page.md"], "code"),
    (["README.MD"], "code"),
    (["page.md.sh"], "code"),
    (["page.md\nx.sh"], "code"),
    (["supabase/migrations/0001_init.sql", "README.md"], "code"),
)


def _class_block(text):
    """The class block, as the stripped lines from `class=words` to the effort's output."""
    return _block(text, lambda l: l == CLASS_FIRST, lambda l: l == CLASS_OUT)


def class_says(block, paths):
    """Run the class block as a change touching `paths` would. (class, effort) or None."""
    with tempfile.TemporaryDirectory() as d:
        changed, out = os.path.join(d, "changed"), os.path.join(d, "out")
        if paths is not None:
            with open(changed, "wb") as f:
                f.write(b"".join(p.encode("utf-8") + b"\0" for p in paths))
        # A workflow expression is not shell; the listing it names is stubbed,
        # and fails as git would when there is no list to give.
        body = "\n".join(re.sub(r"\$\{\{[^}]*\}\}", "x", l) for l in block)
        script = 'git() { cat "$CHANGED"; }\ng() { cat "$CHANGED"; }\n%s\n' % body
        try:
            p = subprocess.run(["bash", "-c", "set -euo pipefail\n" + script],
                               env=dict(os.environ, CHANGED=changed, GITHUB_OUTPUT=out,
                                        RUNNER_TEMP=d, t=d, MAIN="main", SHA="0" * 40),
                               capture_output=True, text=True, timeout=30)
            said = open(out, encoding="utf-8").read() if p.returncode == 0 else ""
        except (OSError, subprocess.SubprocessError):
            return None
    got = dict(l.split("=", 1) for l in said.splitlines() if "=" in l)
    return (got["class"], got["effort"]) if "class" in got and "effort" in got else None


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
        for line in (CLASS_CODE, CLASS_EFFORT):
            if line not in block:
                lost.append("`%s`" % line)
        # The shape, not only the strings (#79's ninth read): an arm added for
        # an extension no case lists would pass every case and every loosening
        # above, so the `case` holds exactly its three arms and nothing else.
        try:
            arms = block[block.index('case "$f" in') + 1:block.index("esac")]
        except ValueError:
            arms = None
        if arms != list(CLASS_ARMS):
            lost.append("a `case` of exactly three arms, %s (it has %s)"
                        % (" / ".join("`%s`" % a for a in CLASS_ARMS), arms))
        for paths, want in CLASS_CASES:
            got = class_says(block, paths)
            need = want and (want, WORDS_EFFORT if want == "words" else REVIEWER_EFFORT)
            if got != need:
                lost.append("%s (it was %s)"
                            % ("a change to %r read as %s at %s" % ((paths,) + need) if need
                               else "a list that could not be made stopping the step",
                               "%s at %s" % got if got else "not run to an answer"))
    if len([l for l in g.splitlines() if "effort=" in l and "GITHUB_OUTPUT" in l]) != 1:
        lost.append("one line, and only one, handing the effort on (`%s`)" % CLASS_OUT)
    if len(re.findall(r"^\s*EFFORT:", r, re.M)) != 1 or EFFORT_IN not in r:
        lost.append("`%s` as the read's one effort" % EFFORT_IN)
    if EFFORT_GUARD not in r or READ_CALL not in r or r.index(EFFORT_GUARD) > r.index(READ_CALL):
        lost.append("`%s` before the call" % EFFORT_GUARD)
    if [f for f in (_call(text) or []) if f.startswith("--effort")] != [READ_EFFORT + " \\"]:
        lost.append("`%s` as the call's one effort" % READ_EFFORT)
    sign = _step_span(text, "Sign the verdict")
    sg = text[sign[0]:sign[1]] if sign else ""
    for line in VERDICT_SAYS:
        if line not in sg:
            lost.append("the verdict naming the class and effort it was read at (`%s`)" % line)
    if path == REVIEW_WORKFLOW and REVIEW_PAGES not in g:
        lost.append("every file given to a change that is not pages alone (`%s`)" % REVIEW_PAGES)
    if path == REVIEW_WORKFLOW and REVIEW_LEFT_OUT not in g:
        lost.append("each file left out of a read named with its size (`%s`)" % REVIEW_LEFT_OUT)
    say = _step_span(text, "Say it where people read")
    sy = text[say[0]:say[1]] if say else ""
    if path == REVIEW_WORKFLOW and (REVIEW_COUNT not in g or REVIEW_COUNT_IN not in sy):
        lost.append("the files left out counted where they are named and handed to the comment "
                    "(`%s`, `%s`)" % (REVIEW_COUNT, REVIEW_COUNT_IN))
    if path == REVIEW_WORKFLOW and not all(line in r for line in REVIEW_TOLD):
        lost.append("the reviewer told what was left out and asked to say if it needed it (`%s`)"
                    % "`, `".join(REVIEW_TOLD))
    return lost


# Each must turn the hold red on both reviewers' files (or on the one it names).
CLASS_LOOSENINGS = (
    ("a script read as a page", None, lambda t: t.replace("              *.md) ;;\n", "              *.md|*.sh) ;;\n", 1)),
    ("the brief read as a page", None, lambda t: t.replace(CLASS_CODE, CLASS_CODE.replace("AGENTS.md|*/AGENTS.md|", "", 1), 1)),
    ("the operating page read as a page", None, lambda t: t.replace(CLASS_CODE, CLASS_CODE.replace("HOW-WE-BUILD.md|", "", 1), 1)),
    ("the charter read as a page", None, lambda t: t.replace(CLASS_CODE, CLASS_CODE.replace("CHARTER.md|", "", 1), 1)),
    ("the data rules read as a page", None, lambda t: t.replace(CLASS_CODE, CLASS_CODE.replace("RICH-DATA.md|", "", 1), 1)),
    ("the screen law read as a page", None, lambda t: t.replace(CLASS_CODE, CLASS_CODE.replace("design/SCREEN-LAW.md|", "", 1), 1)),
    ("a product's constitution read as a page", None, lambda t: t.replace(CLASS_CODE, CLASS_CODE.replace("design/CONSTITUTION.md|", "", 1), 1)),
    ("the README read as a page", None, lambda t: t.replace(CLASS_CODE, CLASS_CODE.replace("README.md|", "", 1), 1)),
    ("an arm for an unlisted extension", None, lambda t: t.replace("              *.md) ;;\n", "              *.sql) ;;\n              *.md) ;;\n", 1)),
    ("the left-out count dropped", REVIEW_WORKFLOW, lambda t: t.replace("          " + REVIEW_COUNT_IN + "\n", "", 1)),
    ("a verdict that hides its effort", None, lambda t: t.replace(' (read as $CLASS at effort $EFFORT)"', '"', 1)),
    ("a product's decisions read as a page", None, lambda t: t.replace(CLASS_CODE, CLASS_CODE.replace("PRODUCT.md|", "", 1), 1)),
    ("a dot-directory read as pages", None, lambda t: t.replace(CLASS_CODE, CLASS_CODE.replace("|.*|*/.*", "", 1), 1)),
    ("anything unrecognised read as pages", None, lambda t: t.replace("              *) class=code ;;\n", "              *) ;;\n", 1)),
    ("the class reset after the list", None, lambda t: t.replace("          " + CLASS_EFFORT + "\n", "          class=words\n          " + CLASS_EFFORT + "\n", 1)),
    ("code read at the lower effort", None, lambda t: t.replace("*) effort=%s ;;" % REVIEWER_EFFORT, "*) effort=%s ;;" % WORDS_EFFORT, 1)),
    ("the effort lowered before it is handed on", None, lambda t: t.replace("          " + CLASS_OUT + "\n", "          effort=%s\n          %s\n" % (WORDS_EFFORT, CLASS_OUT), 1)),
    ("a list that fails read as no change", None, lambda t: t.replace("--name-only --no-renames", "--name-only --no-renames 2>/dev/null || true; : ", 1)),
    ("a rename read as its new name", None, lambda t: t.replace("--name-only --no-renames", "--name-only", 1)),
    ("names split on a line break", None, lambda t: t.replace("diff -z --name-only --no-renames", "diff --name-only --no-renames", 1)),
    ("the effort never handed on", None, lambda t: t.replace("          " + CLASS_OUT + "\n", "", 1)),
    ("the effort handed on twice", None, lambda t: _in_step(t, "Gather what the reviewer reads", CLASS_OUT, CLASS_OUT + '\n          echo "effort=%s" >> "$GITHUB_OUTPUT"' % WORDS_EFFORT)),
    ("the effort not the class's", None, lambda t: t.replace(EFFORT_IN, "EFFORT: " + WORDS_EFFORT, 1)),
    ("a second effort in the read", None, lambda t: t.replace("          " + EFFORT_IN + "\n", "          %s\n          EFFORT: %s\n" % (EFFORT_IN, WORDS_EFFORT), 1)),
    ("an effort unchecked", None, lambda t: t.replace(EFFORT_GUARD, "true", 1)),
    ("an effort written into the call", None, lambda t: t.replace(READ_EFFORT + " \\", "--effort " + WORDS_EFFORT + " \\", 1)),
    ("code given pages alone", REVIEW_WORKFLOW, lambda t: t.replace("code:*) ;;", "code:*.md) ;;", 1)),
    ("a file left out unnamed", REVIEW_WORKFLOW, lambda t: re.sub(r"\*\) printf '[^\n]*" + re.escape(REVIEW_LEFT_OUT) + r"[^\n]*; continue ;;", "*) continue ;;", t, 1)),
    ("the reviewer not told", REVIEW_WORKFLOW, lambda t: t.replace(REVIEW_TOLD[1], 'echo "."', 1)),
    ("the class kept from the read", REVIEW_WORKFLOW, lambda t: t.replace("          " + REVIEW_TOLD[2] + "\n", "", 1)),
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
        print("ok: each reviewer reads a change at its class's effort, %s for pages alone and %s "
              "for anything else, worked out from the diff it reads; the class was run on %d "
              "change(s), review.yml gives any change but pages every file, and each of %d "
              "loosenings was refused" % (WORDS_EFFORT, REVIEWER_EFFORT, len(CLASS_CASES),
                                          len(CLASS_LOOSENINGS)))
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
                      ("--model " + REVIEWER_MODEL, "it would not be the reviewer he named"),
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
    ("a lower effort", lambda t: t.replace("*) effort=%s ;;" % REVIEWER_EFFORT, "*) effort=%s ;;" % WORDS_EFFORT, 1)),
    ("the tools back on", lambda t: t.replace('--tools "" \\\n', "", 1)),
    ("settings files read", lambda t: t.replace("--restricted \\\n", "", 1)),
    ("MCP servers from elsewhere", lambda t: t.replace("--strict-mcp-config \\\n", "", 1)),
    ("another model", lambda t: t.replace("--model " + REVIEWER_MODEL, "--model claude-haiku-4-5", 1)),
    ("the tool unpinned", lambda t: t.replace("claude-code@2.1.280", "claude-code", 1)),
    ("a different version", lambda t: re.sub(r"claude-code@(\d+)\.(\d+)\.(\d+)", "claude-code@9.9.9", t, 1)),
    ("the brief from the head", lambda t: t.replace('g show "origin/$MAIN:AGENTS.md"', 'g show "$SHA:AGENTS.md"', 1)),
    ("the diff against the base", lambda t: t.replace(PRODUCT_DIFF, 'g diff "$BASE...$SHA" > "$t/diff.txt"  # .base.sha', 1)),
    ("the head never checked", lambda t: t.replace(PRODUCT_HEAD[0], "true", 1)),
    ("the fetched head never checked", lambda t: t.replace(PRODUCT_HEAD[1], "true", 1)),
    ("the token's reach never asked", lambda t: t.replace(PRODUCT_REACH[0], '"https://api.github.com/user/repos"', 1)),
    ("the install beside a secret", lambda t: t.replace("        run: npm install -g @anthropic-ai/claude-code@", "        env:\n          CLAUDE_CODE_OAUTH_TOKEN: ${{ secrets.CLAUDE_CODE_OAUTH_TOKEN }}\n        run: npm install -g @anthropic-ai/claude-code@", 1)),
    ("a secret above the steps", lambda t: t.replace("    environment: reviewer\n", "    environment: reviewer\n    env:\n      KEY: ${{ secrets.REVIEWER_APP_KEY }}\n", 1)),
    ("a second, unpinned install", lambda t: t.replace("run: npm install -g @anthropic-ai/claude-code@2.1.280", "run: npm install -g @anthropic-ai/claude-code@2.1.280 && npm install -g @anthropic-ai/claude-code", 1)),
    ("a cancel-in-progress setting alone", lambda t: t.replace("    timeout-minutes: 30\n", "    timeout-minutes: 30\n    cancel-in-progress: true\n", 1)),
    ("the base fetched beside the right diff", lambda t: t.replace(PRODUCT_DIFF, PRODUCT_DIFF + "  # .base.sha", 1)),
    ("a different size ceiling", lambda t: t.replace('"$bytes" -gt 600000', '"$bytes" -gt 900000', 1)),
    ("no product at all", lambda t: t.replace("          - Adonis80/Hemz-OS\n", "", 1).replace("            Adonis80/Hemz-OS) ;;\n", "", 1)),
    ("the token unscoped", lambda t: t.replace(PRODUCT_SCOPE, "{}", 1)),
    ("an input pasted", lambda t: t.replace('echo "asked: $REPO', 'echo "asked: ${{ inputs.repo }}', 1)),
    ("the shell traced", lambda t: t.replace("set -euo pipefail\n", "set -euxo pipefail\n", 1)),
    ("the instruction altered", lambda t: t.replace("Read COLD:", "Read kindly:", 1)),
    ("the JWT's lifetime altered", lambda t: t.replace("$((now + 540))", "$((now + 3600))", 1)),
    ("the verdict's shape altered", lambda t: t.replace('"enum":["clean","findings"]', '"enum":["clean"]', 1)),
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
    ("a different time limit", lambda t: t.replace("    timeout-minutes: 30\n", "    timeout-minutes: 90\n", 1)),
    ("a different read limit", lambda t: t.replace("          limit=25\n", "          limit=20\n", 1)),
    ("a reason worded otherwise", lambda t: _in_step(t, "Read it", "the reviewer was rate-limited or overloaded", "the reviewer was busy")),
    # What the token was granted (#68's twelfth read).
    ("the grant printed, not checked", lambda t: t.replace(PRODUCT_GRANT[2], "if false; then", 1)),
    ("a wider grant wanted", lambda t: t.replace(PRODUCT_GRANT[0], PRODUCT_GRANT[0].replace('"contents":"read"', '"contents":"read","issues":"write"'), 1)),
    ("the grant taken on trust", lambda t: t.replace(PRODUCT_GRANT[1], "granted=$want", 1)),
    ("another secret written as the key", lambda t: t.replace('"$APP_KEY" > "$key"', '"$APP_ID" > "$key"', 1)),
)


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
    failed += _check_review_loosenings()
    failed += _check_read_loosenings()
    failed += _check_class_loosenings()
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
