#!/usr/bin/env bash
# The rulebook's own guard. CI runs it on every push and pull request.
# It refuses: an operating page over its word cap, a screen law over its own, a
# root, design or library file that is not on its list or missing from it, a
# library page over its size or unscoped, a link to a page that does not exist,
# an index row that opens its first page on words that page does not say,
# anything that looks like a secret (naming the place, never the value), a
# model named anywhere but the registry, a review gate that no longer matches the reviewer's answers or has drifted from
# the workflows that fetch them, and, in a pull request, a commit no reviewer
# has read clean — unread, or read and left a blocking finding on. Nothing else. A read by anybody the
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
# ceiling: from here a rule in means a rule out. See *Changing the rulebook*.
words=$(python3 -c 'import sys; print(len(open(sys.argv[1],encoding="utf-8").read().split()))' HOW-WE-BUILD.md)
if [ "$words" -gt 600 ]; then
  echo "FAIL: HOW-WE-BUILD.md is $words words; the cap is 600."
  fail=1
else
  echo "ok: HOW-WE-BUILD.md is $words words (cap 600)"
fi

# 2. Only these files exist at the root (plus .git and .github).
allowed=" AGENTS.md CHARTER.md HOW-WE-BUILD.md README.md RICH-DATA.md board check.sh consensuses design library model-registry review-gate.py "
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
    design) [ -d "$f" ] || { echo "FAIL: '$f' is missing, or is not a directory; the root list is a fixed set."; fail=1; } ;;
    # The build board's gate (decision 0007): its three files and nothing else. No roadmap data lives here.
    board) [ ! -e "$f" ] || { [ -d "$f" ] && [ "$(ls -A board | tr '\n' ' ')" = "middleware.js robots.txt vercel.json " ]; } || { echo "FAIL: 'board/' holds only middleware.js, robots.txt and vercel.json."; fail=1; } ;;
    # Git keeps no empty directory, so an absent library is the empty one, and
    # the README's index holds it to the list both ways instead (2c).
    library) [ ! -e "$f" ] || [ -d "$f" ] || { echo "FAIL: '$f' is not a directory."; fail=1; } ;;
    # The model registry (decision 0008): the one file that names models, its
    # resolver and its OpenAI-compatible caller, and nothing else.
    model-registry) [ -d "$f" ] && [ "$(ls -A model-registry | tr '\n' ' ')" = "ask.py registry.json resolve.py " ] || { echo "FAIL: 'model-registry/' holds ask.py, registry.json and resolve.py, and nothing else."; fail=1; } ;;
    # Consensuses committed verbatim for a build to read from GitHub (#103's
    # amendment): pages, one folder per project, nothing executable.
    consensuses) [ ! -e "$f" ] || { [ -d "$f" ] && [ -z "$(find consensuses -type f ! -name '*.md')" ] && [ -z "$(find consensuses -mindepth 1 -maxdepth 1 -type f)" ]; } || { echo "FAIL: 'consensuses/' holds only .md pages, each in a project's folder."; fail=1; } ;;
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

# 2c. The library: one page per topic, opened only when a task touches it (his
# ruling of 23 September 2026, decision 0005, issue #75). The README is its
# index, both ways: a page the README does not name is never opened, and a
# name with no page sends a session nowhere. Each page is one topic in at most
# 4000 bytes, the machine's proxy for the decision's 1,000 tokens, and says
# whom it binds and when to open it. A link to a page from anywhere in this
# repository must resolve too, not only the README's: a list of the files to
# search would be one more list to drift. With no page named there is no
# library, and that passes: the check exists before the pages it holds.
lib_fail=0
page_re='library/[A-Za-z0-9._-]+\.md'
named=$( { grep -o -E "$page_re" README.md || true; } | sort -u)
shopt -s dotglob nullglob
pages=(library/*)
shopt -u dotglob nullglob
for f in "${pages[@]}"; do
  # A name the index cannot spell can never be named, so it is refused before
  # anything is read from it, and printed escaped, not raw.
  [[ "$f" =~ ^${page_re}$ ]] || { printf "FAIL: %q is not a page name the README can hold (letters, digits, '.', '_', '-', ending .md).\n" "$f"; lib_fail=1; continue; }
  grep -qxF "$f" <<< "$named" || { echo "FAIL: '$f' is not named in the README, so no session is sent to it."; lib_fail=1; }
  [ -f "$f" ] || { echo "FAIL: '$f' is not a file."; lib_fail=1; continue; }
  b=$(wc -c < "$f" | tr -d ' ')
  [ "$b" -le 4000 ] || { echo "FAIL: '$f' is $b bytes; a library page's cap is 4000 - split the topic or cut history."; lib_fail=1; }
  grep -q -E '^Scope: .+ Open when: .+' "$f" || { echo "FAIL: '$f' has no 'Scope: … Open when: …' line."; lib_fail=1; }
done
for f in $named; do
  [ -f "$f" ] || { echo "FAIL: the README names '$f', which does not exist."; lib_fail=1; }
done
while IFS= read -r hit; do
  f=${hit##*:}
  # The page is held to the name pattern; the file linking it is any path in
  # the repository, so it is printed escaped, as a page name the pattern
  # refuses is above: a control character in a path reaches a public log.
  [ -f "$f" ] || { printf "FAIL: %q links '%s', which does not exist.\n" "${hit%:*}" "$f"; lib_fail=1; }
done < <(grep -r -o -I -E --exclude-dir=.git "$page_re" . | sed 's|^\./||' | sort -u || true)
# The index holds its pages in words as well as in names. Decision 0005
# (issue #75: his ruling of 23 September 2026, and his challenge "machine
# first, reading last") made the map "one line per topic saying when to open
# it", and ruled that what a machine can check "becomes a shared check the
# same day". So this holds a settled rule rather than adding one. A page's
# trigger lives twice: in the index row a session scans to decide what to
# open, and on the page it opens. Nothing held the two equal (#83's read),
# so a row edited alone would send a session to a page on words the page
# does not say. Each row's "Open when" must be the first page it names',
# less the final full stop. The other pages of a several-page row carry
# lines of their own and are held only to being named. The text is
# repository text, but it reaches a public log, so control characters are
# dropped before it is printed.
while IFS='|' read -r _ cell when _; do
  first=$( { grep -o -E "$page_re" <<< "$cell" || true; } | head -n 1)
  [ -f "$first" ] || continue
  want=$(sed -n -E 's/^Scope: .+ Open when: (.+)\.$/\1/p' "$first" | head -n 1 | tr -d '[:cntrl:]')
  when=$(sed -E 's/^ +//; s/ +$//' <<< "$when" | tr -d '[:cntrl:]')
  [ "$when" = "$want" ] || { printf 'FAIL: the README opens %s when "%s"; the page says it opens when "%s".\n' "$first" "$when" "$want"; lib_fail=1; }
done < <(grep -E "^\| \`$page_re\`" README.md || true)
if [ "$lib_fail" -ne 0 ]; then
  fail=1
elif [ "${#pages[@]}" -eq 0 ]; then
  echo "ok: no library pages yet, and nothing names or links one"
else
  echo "ok: ${#pages[@]} library pages, each named by the README, each at most 4000 bytes and scoped, every link to one resolves, and each index row opens the first page it names on that page's own words"
fi

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

# 3b. A model is named in the registry and nowhere else (decision 0008). Every
# other file asks for a role, so a switch is one edit to one file. Refused: any
# id the registry lists, and anything shaped like a model id from a vendor we
# use, anywhere but model-registry/ and consensuses/, whose records are kept
# verbatim. The ids are read from the registry, so a new model is held the day
# it is added, and case hides none of them.
ids=$(python3 -c 'import json,sys; print("|".join(m.replace(".", "[.]") for m in json.load(open(sys.argv[1]))["models"]))' model-registry/registry.json)
shape='claude-(opus|sonnet|haiku|fable)-[0-9][0-9a-z.-]*|(z-ai|moonshotai|qwen|deepseek|anthropic|openai|google|meta-llama|mistralai|x-ai)/[a-z0-9][a-z0-9._-]*|gpt-[0-9][0-9a-z.-]*|glm-[0-9][0-9a-z.-]*|kimi-k[0-9][0-9a-z.-]*'
if [ -z "$ids" ]; then
  echo "FAIL: model-registry/registry.json lists no models, so nothing could be held to it."; fail=1
elif grep -R -n -i -E --exclude-dir=.git --exclude-dir=model-registry --exclude-dir=consensuses "($ids|$shape)" . | cut -d: -f1,2 | sed 's/^/  /' | grep . ; then
  echo "FAIL: the place(s) above name a model; name the role instead, and the model in model-registry/registry.json."
  fail=1
else
  echo "ok: no model is named outside model-registry/registry.json"
fi

# 4. In a pull request, a review clears only the commit it read, and only if it
# left nothing blocking on it: green when a reviewer has read this very commit
# clean, or with advisory findings alone, which stay standing on the pull
# request. A later push turns it red until it has; so does a blocking finding,
# until the push that
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
