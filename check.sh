#!/usr/bin/env bash
# The rulebook's own guard. CI runs it on every push and pull request.
# It refuses: an operating page over its word cap, a screen law over its own, a
# README, library page or boot over its size, a root, design or library file
# that is not on its list or missing from it, anything that
# looks like a secret (naming the place, never the value), a review gate that no
# longer matches the reviewer's answers or has drifted from the workflows that
# fetch them, and, in a pull request, a commit no reviewer has read clean —
# unread, or read and left findings on. Nothing else. A read by anybody the
# gate does not count is unread, not a shape of its own.
# A third shape, "read clean by a reviewer the rulebook does not allow to
# clear this change", was real while two vendors were on the register and is
# gone with the second: see review-gate.py on CROSS_VENDOR. A header describing
# a state the file can no longer reach is the drift this guard exists to catch,
# so it is corrected here rather than left for the next reader to discover.
set -euo pipefail
cd "$(dirname "$0")"
fail=0

# 1. The operating page stays short.
# Counted with python, not `wc -w`: wc answers differently by locale — it
# splits on the em dash in C.UTF-8 and not in C — so the same bytes passed on
# a session's machine and failed in CI. On 7 September 2026 that cost a build
# in the Alma repo, whose identical guard was fixed the same way. A cap must
# mean one thing wherever it is measured.
# The cap was 500 from 28 August to 12 September 2026, when the two-lead rules
# could not fit under it without spending a rule the page requires. It moved to
# 600 in the pull request that needed it, for that stated reason, and 600 is the
# ceiling: from here a rule in means a rule out. See library/changing-the-rulebook.md.
words=$(python3 -c 'import sys; print(len(open(sys.argv[1],encoding="utf-8").read().split()))' HOW-WE-BUILD.md)
if [ "$words" -gt 600 ]; then
  echo "FAIL: HOW-WE-BUILD.md is $words words; the cap is 600."
  fail=1
else
  echo "ok: HOW-WE-BUILD.md is $words words (cap 600)"
fi

# 2. Only these files exist at the root (plus .git and .github).
allowed=" AGENTS.md CHARTER.md HOW-WE-BUILD.md README.md RICH-DATA.md check.sh design library review-gate.py "
while IFS= read -r f; do
  case "$f" in .git|.github) continue ;; esac
  case "$allowed" in
    *" $f "*) ;;
    *) echo "FAIL: '$f' is not on the file list ($allowed)."; fail=1 ;;
  esac
done < <(ls -A)
# Both ways, as the design list already is: an unexpected file fails, and so
# does a missing one — otherwise deleting CHARTER.md or README.md passes.
# A directory of the same name is not the file: `-e` would pass a tracked
# `CHARTER.md/` that holds nothing this repository reads.
for f in $allowed; do
  case "$f" in
    design|library) [ -d "$f" ] || { echo "FAIL: '$f' is missing, or is not a directory; the root list is a fixed set."; fail=1; } ;;
    *) [ -f "$f" ] || { echo "FAIL: '$f' is missing, or is not a file; the root list is a fixed set."; fail=1; } ;;
  esac
done
[ "$fail" -eq 0 ] && echo "ok: file list unchanged"

# 2b. The design pages: a fixed list, and a law that stays law-sized.
# The screen law is carried here once so every product reads the same one; a
# product's own constitution holds only what is true there and points at this.
lawwords=$(python3 -c 'import sys; print(len(open(sys.argv[1],encoding="utf-8").read().split()))' design/SCREEN-LAW.md)
if [ "$lawwords" -gt 450 ]; then
  echo "FAIL: design/SCREEN-LAW.md is $lawwords words; the cap is 450 - a rule in means a rule out."
  fail=1
else
  echo "ok: design/SCREEN-LAW.md is $lawwords words (cap 450)"
fi
design_allowed=" ARCHITECT.md BRIEF_TEMPLATE.md REVIEW_RUBRIC.md SCREEN-LAW.md SCREEN_SPEC_TEMPLATE.md "
while IFS= read -r f; do
  case "$design_allowed" in
    *" $f "*) ;;
    *) echo "FAIL: 'design/$f' is not on the design file list ($design_allowed)."; fail=1 ;;
  esac
done < <(ls -A design)
# The list is both ways: an unexpected page fails, and a missing one fails too,
# or a later change could quietly delete a role, a form or the rubric and stay green.
for f in $design_allowed; do
  [ -f "design/$f" ] || { echo "FAIL: 'design/$f' is missing; the design pages are a fixed set."; fail=1; }
done

# 2c. The boot stays small, and the library is the map's to name: his ruling of
# 23 September 2026 and decision 0005 (issue #75), built in #70's slices.
# A session reads HOW-WE-BUILD.md and this README at its start and opens a
# library page only when its task touches the topic, so what every session pays
# for is capped in bytes, a stand-in for tokens at about four to one. The
# README's index is the library's list, both ways: a page it does not name is
# never opened, and a name with no page sends a session nowhere. Each page is
# one topic, current truth only, under a cap; each says whom it binds.
readme_bytes=$(wc -c < README.md)
boot_bytes=$(( $(wc -c < HOW-WE-BUILD.md) + readme_bytes ))
if [ "$readme_bytes" -gt 12000 ]; then
  echo "FAIL: README.md is $readme_bytes bytes; the map's cap is 12000 - move a topic to a library page."; fail=1
elif [ "$boot_bytes" -gt 16000 ]; then
  echo "FAIL: the boot list is $boot_bytes bytes; the rulebook's share is 16000."; fail=1
else
  echo "ok: README.md is $readme_bytes bytes (cap 12000); the boot is $boot_bytes (cap 16000)"
fi
named=$(grep -o -E 'library/[A-Za-z0-9._-]+\.md' README.md | sort -u)
present=$( { ls -A library 2>/dev/null || true; } | sed 's|^|library/|' | sort)
lib_fail=0
for f in $present; do
  case " $(echo $named) " in *" $f "*) ;; *) echo "FAIL: '$f' is not in the README's index, so no session is sent to it."; lib_fail=1 ;; esac
  [ -f "$f" ] || { echo "FAIL: '$f' is not a file."; lib_fail=1; continue; }
  b=$(wc -c < "$f")
  [ "$b" -le 4000 ] || { echo "FAIL: '$f' is $b bytes; a library page's cap is 4000 - split the topic or cut history."; lib_fail=1; }
  grep -q -E '^Scope: .+ Open when: .+' "$f" || { echo "FAIL: '$f' has no 'Scope: … Open when: …' line."; lib_fail=1; }
done
for f in $named; do
  [ -f "$f" ] || { echo "FAIL: the README's index names '$f', which does not exist."; lib_fail=1; }
done
# The Project templates carry the date the README's boot line names, so a
# session compares one date instead of reading both templates at every start.
current=$(grep -o -E 'template is dated \*\*[0-9]{4}-[0-9]{2}-[0-9]{2}\*\*' README.md | grep -o -E '[0-9]{4}-[0-9]{2}-[0-9]{2}')
for f in library/project-template.md library/juku-os-project.md; do
  d=$(grep -o -E '\(template [0-9]{4}-[0-9]{2}-[0-9]{2}\)' "$f" | grep -o -E '[0-9]{4}-[0-9]{2}-[0-9]{2}')
  [ -n "$current" ] && [ "$d" = "$current" ] || { echo "FAIL: '$f' is dated '${d:-none}' and the README names '${current:-none}'."; lib_fail=1; }
done
[ "$lib_fail" -eq 0 ] && echo "ok: $(echo $present | wc -w) library pages, each named by the README, each under 4000 bytes, each scoped; the templates carry the current date"
[ "$lib_fail" -eq 0 ] || fail=1

# 3. Nothing that looks like a secret, anywhere.
pattern='(ghp_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,}|sk-[A-Za-z0-9]{20,}|xox[baprs]-[A-Za-z0-9-]{10,}|-----BEGIN [A-Z ]*PRIVATE KEY-----|eyJ[A-Za-z0-9_-]{20,}\.[A-Za-z0-9_-]{20,})'
# Never print the match: this repository's logs are public, so a guard that
# echoes what it catches leaks the secret on the one day it fires. The file and
# line are enough to find it.
if grep -R -n -E --exclude-dir=.git "$pattern" . | cut -d: -f1,2 | sed 's/^/  /' | grep . ; then
  echo "FAIL: the place(s) above look like a secret — the value is not printed."
  fail=1
else
  echo "ok: nothing that looks like a secret"
fi

# 4. In a pull request, a review clears only the commit it read, and only if it
# left nothing on it: green when a reviewer has read this very commit clean.
# A later push turns it red until it has; so does a finding, until the push that
# answers it makes a commit the reviewer reads afresh. The CTO's answer to a
# finding is not clearance — the proposer does not clear its own change.
# A change to the review machinery used to need the other vendor's read alone,
# and since his ruling of 22 September 2026 retiring Codex there is no other
# vendor: it clears on the one reviewer's read, like everything else. The gate
# says so on the run rather than letting a green imply otherwise.
# The gate's own rule is machine-checked before anything asks GitHub: one
# implementation, held against the reviewer's real answers, the states a read
# can arrive in, the fakes that once passed a looser test, the routes the gate
# has stopped reading, and the five workflow files — the check, the reviewer,
# the wake it calls, the door's standing proof and the product reviewer — which
# must still agree with the register and with each other.
python3 review-gate.py --selftest || fail_gate=1
[ "${fail_gate:-0}" -eq 0 ] || { echo "FAIL: the review gate no longer matches the reviewer's answers, or has drifted from the workflows — see the cases above."; fail=1; }
# WHICH EVENTS THE GATE RUNS ON, WRITTEN AS WHAT IT SKIPS RATHER THAN WHAT IT
# CATCHES. This read `pull_request|pull_request_review`, and this change removed
# the second of those triggers from check.yml, leaving that arm unreachable.
# Deleting the dead arm is the obvious tidy and it is the wrong fix: a list of
# events the gate RUNS on means any trigger added later and not added here is a
# check that goes green having asked no reviewer anything — fail-open, silently,
# in the file whose whole job is to fail closed. Inverted, an unknown event runs
# the gate and fails loudly for want of a pull request number instead. `push` is
# main's own, which carries no pull request to judge; an empty name is a run by
# hand on somebody's machine.
case "${GITHUB_EVENT_NAME:-}" in push|"") : ;; *)
  if [ -z "${GH_TOKEN:-}" ] || [ -z "${PR_NUMBER:-}" ] || [ -z "${HEAD_SHA:-}" ]; then
    echo "FAIL: the check cannot ask GitHub which commit the reviewer read — the workflow must set PR_NUMBER, HEAD_SHA and GH_TOKEN."; fail=1
  elif python3 review-gate.py "${GITHUB_REPOSITORY:-Adonis80/how-we-build}" "$PR_NUMBER" "$HEAD_SHA" "$GH_TOKEN"; then
    : # the gate says which read it found; one voice, not two
  else
    echo "FAIL: see the reason above."; fail=1
  fi
;; esac

if [ "$fail" -eq 0 ]; then
  echo "check.sh: all clear"
fi
exit "$fail"
