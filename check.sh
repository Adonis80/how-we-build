#!/usr/bin/env bash
# The rulebook's own guard. CI runs it on every push and pull request.
# It refuses: an operating page over 500 words, a file that is not on the
# list, anything that looks like a secret, and — in a pull request — a commit
# the reviewer has not read. Nothing else.
set -euo pipefail
cd "$(dirname "$0")"
fail=0

# 1. The operating page stays short.
# Counted with python, not `wc -w`: wc answers differently by locale — it
# splits on the em dash in C.UTF-8 and not in C — so the same bytes passed on
# a session's machine and failed in CI. On 7 September 2026 that cost a build
# in the Alma repo, whose identical guard was fixed the same way. A cap must
# mean one thing wherever it is measured.
words=$(python3 -c 'import sys; print(len(open(sys.argv[1],encoding="utf-8").read().split()))' HOW-WE-BUILD.md)
if [ "$words" -gt 500 ]; then
  echo "FAIL: HOW-WE-BUILD.md is $words words; the cap is 500."
  fail=1
else
  echo "ok: HOW-WE-BUILD.md is $words words (cap 500)"
fi

# 2. Only these files exist at the root (plus .git and .github).
allowed=" AGENTS.md CHARTER.md HOW-WE-BUILD.md README.md check.sh design "
for f in $(ls -A); do
  case "$f" in .git|.github) continue ;; esac
  case "$allowed" in
    *" $f "*) ;;
    *) echo "FAIL: '$f' is not on the file list ($allowed)."; fail=1 ;;
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
for f in $(ls -A design); do
  case "$design_allowed" in
    *" $f "*) ;;
    *) echo "FAIL: 'design/$f' is not on the design file list ($design_allowed)."; fail=1 ;;
  esac
done
# The list is both ways: an unexpected page fails, and a missing one fails too,
# or a later change could quietly delete a role, a form or the rubric and stay green.
for f in $design_allowed; do
  [ -f "design/$f" ] || { echo "FAIL: 'design/$f' is missing; the design pages are a fixed set."; fail=1; }
done

# 3. Nothing that looks like a secret, anywhere.
pattern='(ghp_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,}|sk-[A-Za-z0-9]{20,}|xox[baprs]-[A-Za-z0-9-]{10,}|-----BEGIN [A-Z ]*PRIVATE KEY-----|eyJ[A-Za-z0-9_-]{20,}\.[A-Za-z0-9_-]{20,})'
if grep -R -n -E --exclude-dir=.git "$pattern" . ; then
  echo "FAIL: the line(s) above look like a secret."
  fail=1
else
  echo "ok: nothing that looks like a secret"
fi

# 4. In a pull request, a review clears only the commit it read: green only when the
# reviewer has read this very commit. A later push turns it red until it has.
case "${GITHUB_EVENT_NAME:-}" in pull_request|pull_request_review)
  if [ -z "${GH_TOKEN:-}" ] || [ -z "${PR_NUMBER:-}" ] || [ -z "${HEAD_SHA:-}" ]; then
    echo "FAIL: the check cannot ask GitHub which commit the reviewer read — the workflow must set PR_NUMBER, HEAD_SHA and GH_TOKEN."; fail=1
  elif python3 - "${GITHUB_REPOSITORY:-Adonis80/how-we-build}" "$PR_NUMBER" "$HEAD_SHA" "$GH_TOKEN" <<'PY'
import json, sys, urllib.request, urllib.error
repo, num, head, token = sys.argv[1:5]
def get(url):
    req = urllib.request.Request(url, headers={"Authorization": "Bearer " + token, "Accept": "application/vnd.github+json"})
    with urllib.request.urlopen(req) as r:
        return json.load(r)
def pages(url):
    page = 1
    while True:
        batch = get("%s?per_page=100&page=%d" % (url, page))
        if not batch:
            return
        for item in batch:
            yield item
        page += 1
bot = "chatgpt-codex-connector[bot]"
try:
    for r in pages("https://api.github.com/repos/%s/pulls/%s/reviews" % (repo, num)):
        if r["user"]["login"] == bot and r["commit_id"] == head:
            sys.exit(0)
    for c in pages("https://api.github.com/repos/%s/issues/%s/comments" % (repo, num)):
        if c["user"]["login"] == bot and "codex-pull-request-review-summary" in c["body"]:
            for line in c["body"].splitlines():
                if "Completed" in line and "`" + head[:7] in line:
                    sys.exit(0)
except urllib.error.HTTPError as e:
    if e.code in (401, 403):
        why = "the workflow's token may not read pull requests (it needs pull-requests: read), or GitHub is rate-limiting"
    elif e.code == 404:
        why = "GitHub found no such repository or pull request — check GITHUB_REPOSITORY and PR_NUMBER"
    elif e.code >= 500:
        why = "GitHub itself answered with an error — re-run the check"
    else:
        why = "GitHub refused the request"
    print("reason: HTTP %s when asked for the reviews — %s" % (e.code, why))
    sys.exit(2)
print("reason: the reviewer has not read commit %s — write '@codex review' on the pull request, and when it has finished, re-run this check" % head)
sys.exit(1)
PY
  then echo "ok: the reviewer has read $HEAD_SHA"
  else echo "FAIL: see the reason above."; fail=1
  fi
;; esac

if [ "$fail" -eq 0 ]; then
  echo "check.sh: all clear"
fi
exit "$fail"
