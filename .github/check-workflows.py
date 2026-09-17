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
for want in ("--model claude-fable-5-1", "--effort max", "--tools \"\""):
    if want not in src:
        print("FAIL: %s no longer passes %s to the reviewer." % (WF, want))
        bad = 1

if not bad:
    print("ok: the reviewer runs from the default branch on issue_comment alone, "
          "as Fable at max effort with every tool off, and its %d shell blocks parse" % n_review)
sys.exit(bad)
