#!/usr/bin/env bash
# The rulebook's own guard. CI runs it on every push and pull request.
# It refuses: an operating page over its word cap, a screen law over its own, a
# root or design file that is not on its list or missing from it, anything that
# looks like a secret (naming the place, never the value), a review gate that no
# longer matches the reviewer's answers, and, in a pull request, a commit the
# reviewer has not read. Nothing else.
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
# ceiling: from here a rule in means a rule out. See README, Changing the rulebook.
words=$(python3 -c 'import sys; print(len(open(sys.argv[1],encoding="utf-8").read().split()))' HOW-WE-BUILD.md)
if [ "$words" -gt 600 ]; then
  echo "FAIL: HOW-WE-BUILD.md is $words words; the cap is 600."
  fail=1
else
  echo "ok: HOW-WE-BUILD.md is $words words (cap 600)"
fi

# 2. Only these files exist at the root (plus .git and .github).
allowed=" AGENTS.md CHARTER.md HOW-WE-BUILD.md README.md check.sh design review-gate.py "
while IFS= read -r f; do
  case "$f" in .git|.github) continue ;; esac
  case "$allowed" in
    *" $f "*) ;;
    *) echo "FAIL: '$f' is not on the file list ($allowed)."; fail=1 ;;
  esac
done < <(ls -A)
# Both ways, as the design list already is: an unexpected file fails, and so
# does a missing one — otherwise deleting CHARTER.md or README.md passes.
for f in $allowed; do
  [ -e "$f" ] || { echo "FAIL: '$f' is missing; the root list is a fixed set."; fail=1; }
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

# 4. In a pull request, a review clears only the commit it read: green only when the
# reviewer has read this very commit. A later push turns it red until it has.
# The gate's own rule is machine-checked before anything asks GitHub: one
# implementation, held against the reviewer's real answers, the states a review
# can arrive in, and the fakes that once passed a looser test.
python3 review-gate.py --selftest || fail_gate=1
[ "${fail_gate:-0}" -eq 0 ] || { echo "FAIL: the review gate no longer matches the reviewer's answers — see the cases above."; fail=1; }
case "${GITHUB_EVENT_NAME:-}" in pull_request|pull_request_review)
  if [ -z "${GH_TOKEN:-}" ] || [ -z "${PR_NUMBER:-}" ] || [ -z "${HEAD_SHA:-}" ]; then
    echo "FAIL: the check cannot ask GitHub which commit the reviewer read — the workflow must set PR_NUMBER, HEAD_SHA and GH_TOKEN."; fail=1
  elif python3 review-gate.py "${GITHUB_REPOSITORY:-Adonis80/how-we-build}" "$PR_NUMBER" "$HEAD_SHA" "$GH_TOKEN"; then
    echo "ok: the reviewer has read $HEAD_SHA"
  else
    echo "FAIL: see the reason above."; fail=1
  fi
;; esac

if [ "$fail" -eq 0 ]; then
  echo "check.sh: all clear"
fi
exit "$fail"
