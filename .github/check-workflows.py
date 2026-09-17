#!/usr/bin/env python3
"""The reviewer's own workflow, held by the check that runs it.

The facts below are the reviewer. Written in prose they would be comments; here
they are the build, so the day one of them is loosened is the day CI says so
rather than the day somebody notices.
"""
import io, re, subprocess, sys

WF = ".github/workflows/review.yml"
bad = 0
src = io.open(WF, encoding="utf-8").read()
lines = src.splitlines()

# The trigger, read without a YAML library so this runs anywhere check.sh does.
# issue_comment is what makes the reviewer safe: GitHub runs this file from the
# DEFAULT BRANCH on that event, so a branch cannot rewrite its own reviewer. On
# pull_request it would run the branch's own copy.
triggers, seen_on = [], False
for ln in lines:
    if not seen_on:
        if ln.rstrip() == "on:":
            seen_on = True
        continue
    if not ln.strip() or ln.lstrip().startswith("#"):
        continue
    if not ln[:1].isspace():
        break
    indent = len(ln) - len(ln.lstrip())
    if indent == 2 and ln.rstrip().endswith(":"):
        triggers.append(ln.strip()[:-1])
if triggers != ["issue_comment"]:
    print("FAIL: %s must trigger on issue_comment and nothing else; it has %s."
          % (WF, triggers or "none"))
    print("      On pull_request a branch would run its own copy of the reviewer.")
    bad = 1

# Every shell block in both workflows is valid bash. `run: |` only — nothing
# here uses a folded or single-line run, and a new one would show up as a
# block this loop does not find rather than as one it silently skips.
for wf in (WF, ".github/workflows/check.yml"):
    text = io.open(wf, encoding="utf-8").read().splitlines()
    found = 0
    i = 0
    while i < len(text):
        m = re.match(r"^(\s*)run: \|\s*$", text[i])
        if not m:
            i += 1
            continue
        pad = len(m.group(1))
        body, i = [], i + 1
        while i < len(text) and (not text[i].strip() or len(text[i]) - len(text[i].lstrip()) > pad):
            body.append(text[i][pad + 2:])
            i += 1
        found += 1
        r = subprocess.run(["bash", "-n"], input="\n".join(body), text=True, capture_output=True)
        if r.returncode:
            print("FAIL: a shell block in %s is not valid bash:\n%s" % (wf, r.stderr.strip()))
            bad = 1
    if not found:
        print("FAIL: found no shell blocks in %s — this check has stopped checking." % wf)
        bad = 1
    if wf == WF:
        n_review = found

# The model and the effort are the Chairman's ruling written as a flag, not a
# preference: if either goes, the reviewer is no longer the one he named.
#
# The reviewer reads the default-branch checkout so it can judge the diff
# against the pages the brief names — the primary's second P1 on #34 — so what
# bounds it is no longer "no tools" but "only tools that read". --restricted
# takes away the ones that run commands or code and confines the file tools to
# the working directory; --permission-prompts none denies anything that would
# ask; and persist-credentials: false keeps the job's token out of .git/config,
# where a Read would otherwise reach it.
for want in ("--model claude-fable-5-1", "--effort max", "--restricted",
             "--permission-prompts none", "--strict-mcp-config",
             "persist-credentials: false"):
    if want not in src:
        print("FAIL: %s no longer passes %s to the reviewer." % (WF, want))
        bad = 1

named = re.search(r'--tools "([^"]*)"', src)
if not named:
    print("FAIL: %s no longer names the reviewer's tools. It must name only tools that read."
          % WF)
    bad = 1
else:
    tools = [t.strip() for t in named.group(1).split(",") if t.strip()]
    allowed = {"Read", "Glob", "Grep"}
    over = sorted(set(tools) - allowed)
    if over:
        print("FAIL: %s gives the reviewer %s. It may have only %s — a reviewer that can run"
              % (WF, ", ".join(over), ", ".join(sorted(allowed))))
        print("      code or reach the network is no longer only reading the change.")
        bad = 1

# The head is fetched as data. Resolving it through FETCH_HEAD is the bug the
# primary found on #34 and this reproduced: FETCH_HEAD holds a line per ref and
# rev-parse answers the FIRST, which in a base-first two-ref fetch is the base.
# The reviewer then diffed the base against itself and refused to run.
#
# Read from the code alone. A comment is where that bug is explained, and a
# check that cannot tell the explanation from the mistake forbids writing the
# explanation down — which is how the reason for a guard gets deleted.
code = "\n".join(ln for ln in lines if not ln.lstrip().startswith("#"))
if "rev-parse FETCH_HEAD" in code:
    print("FAIL: %s resolves the commit under review through FETCH_HEAD." % WF)
    print("      In a multi-ref fetch that answers the first ref — the base, not the head.")
    bad = 1

# The backup is a backup. It asks review-gate.py whether the primary has refused
# here, rather than deciding for itself — one implementation, so the reviewer and
# the gate that counts it can never disagree about who reads first. Dropping this
# step would spend a review every time somebody asked, while the primary sat
# available, which is the opposite of the ruling of 17 September 2026.
if "review-gate.py --eligible" not in src:
    print("FAIL: %s no longer asks whether the primary is unavailable before reviewing." % WF)
    print("      The backup stands in only behind the primary's own refusal.")
    bad = 1
for step in ("The pull request", "Gather what the reviewer reads"):
    if ("id: eligible" in src) and (src.index("id: eligible") > src.index(step)):
        print("FAIL: %s runs '%s' before it checks the primary is unavailable." % (WF, step))
        bad = 1

if not bad:
    print("ok: the backup runs from the default branch on issue_comment alone, only behind "
          "the primary's refusal, as Fable at max effort with only tools that read, on the "
          "head it actually fetched, and its %d shell blocks parse" % n_review)
sys.exit(bad)
