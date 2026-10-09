#!/usr/bin/env bash
# The rulebook's own guard. CI runs it on every push and pull request.
# It refuses: a front-end guide that is not HyperSolid alone, a root or library
# file that is not on its list or missing from it, a library page unscoped, a
# link to a page that does not exist,
# an index row that opens its first page on words that page does not say,
# anything that looks like a secret (naming the place, never the value), a
# model named anywhere but the registry, a review gate that no longer matches the reviewer's answers or has drifted from
# the workflows that fetch them, a build board that no longer renders as
# decision 0007 says, a product read's rules that no longer refuse what decision
# 0013 says they must, and, in a pull request, a commit no reviewer
# has read clean — unread, or read and left a blocking finding on — or a change to the review
# machinery while the newest canary on main is red. Nothing else. A read by anybody the
# gate does not count is unread, not a shape of its own.
# A third shape, "read clean by a reviewer the rulebook does not allow to
# clear this change", was real while two vendors were on the register and is
# gone with the second: see review-gate.py on CROSS_VENDOR. A header describing
# a state the file can no longer reach is the drift this guard exists to catch,
# so it is corrected here rather than left for the next reader to discover.
# Sizes it reports and never refuses: the operating page, the screen law and
# each library page are measured against a target and the number printed (his
# ruling, 8 October 2026, decision 0017). A change is never failed for length
# alone; it reconciles the rules it touches, which the cold review holds.
set -euo pipefail
cd "$(dirname "$0")"
fail=0
# TWO STEPS, ONE CHECK (his ask, 7 October 2026: the full self-test ran on
# every pull request and again when the verdict landed, about 22 minutes each).
# check.yml runs this file twice in the one `check` job: CHECK_PART=selftest for
# everything but the gate, then CHECK_PART=gate for the gate alone, so a re-run
# can see which half an earlier attempt passed. Unset, by hand, it runs whole.
part="${CHECK_PART:-whole}"
case "$part" in whole|selftest|gate) ;; *) echo "FAIL: CHECK_PART is '$part'; it is selftest, gate or unset."; exit 1 ;; esac
if [ "$part" != gate ]; then

# 1. Sizes, reported. Counted with python, not `wc -w`, which answers
# differently by locale, so a number means one thing wherever it is measured.
words_of() { python3 -c 'import sys; print(len(open(sys.argv[1],encoding="utf-8").read().split()))' "$1"; }
size_line() { # name, measured, target, unit
  if [ "$2" -gt "$3" ]; then echo "size: $1 is $2 $4, $(( $2 - $3 )) over its $3 target — a reading, never a failure"
  else echo "size: $1 is $2 $4 (target $3)"; fi
}
size_line HOW-WE-BUILD.md "$(words_of HOW-WE-BUILD.md)" 600 words

# 2. Only these files exist at the root (plus .git and .github).
allowed=" AGENTS.md CHARTER.md HOW-WE-BUILD.md README.md RICH-DATA.md board check.sh juku-library library model-registry product-reads review-gate.py "
while IFS= read -r f; do
  case "$f" in .git|.github) continue ;; esac
  case "$allowed" in
    *" $f "*) ;;
    *) echo "FAIL: '$f' is not on the file list ($allowed)."; fail=1 ;;
  esac
done < <(ls -A)
# Both ways: an unexpected file fails, and so
# does a missing one — otherwise deleting CHARTER.md or README.md passes.
# A directory of the same name is not the file: `-e` would pass a tracked
# `CHARTER.md/` that holds nothing this repository reads.
for f in $allowed; do
  case "$f" in
    # The build board (decision 0007): its gate's three files and the build that renders it, and nothing else. No roadmap data lives here.
    board) { [ -d "$f" ] && [ "$(ls -A board | tr '\n' ' ')" = "build.py middleware.js robots.txt vercel.json " ]; } || { echo "FAIL: 'board/' holds only build.py, middleware.js, robots.txt and vercel.json."; fail=1; } ;;
    # Git keeps no empty directory, so an absent library is the empty one, and
    # the README's index holds it to the list both ways instead (2c).
    library) [ ! -e "$f" ] || [ -d "$f" ] || { echo "FAIL: '$f' is not a directory."; fail=1; } ;;
    # The model registry (decision 0008): the one file that names models, its
    # resolver, its OpenAI-compatible caller, and the reviewer's context
    # selector with its partner map (decision 0014), and nothing else.
    model-registry) [ -d "$f" ] && [ "$(ls -A model-registry | tr '\n' ' ')" = "ask.py context.py registry.json resolve.py " ] || { echo "FAIL: 'model-registry/' holds ask.py, context.py, registry.json and resolve.py, and nothing else."; fail=1; } ;;
    # The product read's rules (decision 0013): the one module that says whether a
    # read is asked for and paid, and nothing else. It is part of the review gate.
    product-reads) [ -d "$f" ] && [ "$(LC_ALL=C ls -A product-reads | tr '\n' ' ')" = "ask.py kit reads.py setup.py " ] && [ "$(LC_ALL=C ls -A product-reads/kit | tr '\n' ' ')" = "AGENTS.starter.md gate.yml review-gate.py roadmap.starter.json verify.yml wake.yml " ] || { echo "FAIL: 'product-reads/' holds ask.py, reads.py, setup.py and kit/ (the starter kit's six files), and nothing else."; fail=1; } ;;
    # The rulebook's own library (the Chairman's ruling of 2 October 2026): the
    # papers and frozen records committed verbatim for a build to read from
    # GitHub (#103's amendment): .md pages directly inside, no subfolder,
    # nothing executable. A product keeps its own <product>-library/ in its
    # own private repo, never here.
    juku-library) [ ! -e "$f" ] || { [ -d "$f" ] && [ -z "$(find juku-library -type f ! -name '*.md')" ] && [ -z "$(find juku-library -mindepth 1 -type d)" ]; } || { echo "FAIL: 'juku-library/' holds only .md pages, directly inside it, with no subfolder."; fail=1; } ;;
    *) [ -f "$f" ] || { echo "FAIL: '$f' is missing, or is not a file; the root list is a fixed set."; fail=1; } ;;
  esac
done
[ "$fail" -eq 0 ] && echo "ok: file list unchanged"

# 2b. One front-end guide (his ruling, 8 October 2026: "we should be left with
# only library/hypersolid.md"). It holds the screen law, carried once so every
# product reads the same one; a product's own constitution holds only what is
# true there and points at it. The law's size is reported, like every size. The guide's old pages
# stay gone: none exists outside juku-library/, whose records are history, and
# nothing else names one. The names are spelled without ".md" so this file is
# not a hit of its own.
guide=library/hypersolid.md
old_pages="library/screen-design design/ARCHITECT design/BRIEF_TEMPLATE design/SCREEN_SPEC_TEMPLATE design/REVIEW_RUBRIC design/SCREEN-LAW"
for o in $old_pages; do
  [ ! -e "$o.md" ] || { echo "FAIL: '$o.md' exists; $guide is the only front-end guide."; fail=1; }
  if grep -R -n -F --exclude-dir=.git --exclude-dir=juku-library "$o.md" . | cut -d: -f1,2 | sed 's/^/  /' | grep . ; then
    echo "FAIL: the place(s) above name '$o.md'; point at $guide instead."; fail=1
  fi
done
if [ ! -f "$guide" ]; then
  echo "FAIL: '$guide' is missing; it is the only front-end guide."; fail=1
else
  for h in "Distillation rule" "Spatial layer" "Screen law"; do
    grep -q -E "^## $h( |$)" "$guide" || { echo "FAIL: '$guide' has no '## $h' heading."; fail=1; }
  done
  lawwords=$(python3 -c 'import re,sys; m=re.search(r"^## Screen law\n(.*?)(?=^## |\Z)", open(sys.argv[1],encoding="utf-8").read(), re.S|re.M); print(len(m.group(1).split()) if m else 0)' "$guide")
  echo "ok: $guide is the only front-end guide"
  size_line "the screen law in $guide" "$lawwords" 450 words
fi

# 2c. The library: one page per topic, opened only when a task touches it (his
# ruling of 23 September 2026, decision 0005, issue #75). The README is its
# index, both ways: a page the README does not name is never opened, and a
# name with no page sends a session nowhere. Each page is one topic, says whom
# it binds and when to open it, and has its size reported against 4000 bytes,
# the machine's proxy for the decision's 1,000 tokens. A link to a page from
# anywhere in this repository must resolve too, not only the README's: a list
# of the files to search would be one more list to drift. With no page named there is no
# library, and that passes: the check exists before the pages it holds.
lib_fail=0
lib_max=0
# A page name starts at a name boundary: a folder that merely ends in
# "library" (juku-library/, <product>-library/) holds papers, not library
# pages, and its files are not links to library/.
page_re='library/[A-Za-z0-9._-]+\.md'
named=$( { grep -o -P "(?<![A-Za-z0-9._-])$page_re" README.md || true; } | sort -u)
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
  [ "$b" -le "$lib_max" ] || lib_max=$b
  # HyperSolid is one page by his ruling of 8 October 2026, so its target is its own.
  target=4000; [ "$f" != "$guide" ] || target=6500
  [ "$b" -le "$target" ] || size_line "$f" "$b" "$target" bytes
  grep -q -E '^Scope: .+ Open when: .+' "$f" || { echo "FAIL: '$f' has no 'Scope: … Open when: …' line."; lib_fail=1; }
done
for f in $named; do
  [ -f "$f" ] || { echo "FAIL: the README names '$f', which does not exist."; lib_fail=1; }
done
while IFS= read -r hit; do
  f=${hit##*:}
  # A frozen record in juku-library/ may still link a retired guide page (2b):
  # it is history, and 2b already holds that the page stays gone.
  case "${hit%:*} $old_pages " in juku-library/*" ${f%.md} "*) continue ;; esac
  # The page is held to the name pattern; the file linking it is any path in
  # the repository, so it is printed escaped, as a page name the pattern
  # refuses is above: a control character in a path reaches a public log.
  [ -f "$f" ] || { printf "FAIL: %q links '%s', which does not exist.\n" "${hit%:*}" "$f"; lib_fail=1; }
done < <(grep -r -o -I -P --exclude-dir=.git "(?<![A-Za-z0-9._-])$page_re" . | sed 's|^\./||' | sort -u || true)
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
  echo "size: the largest library page is $lib_max bytes (target 4000; $guide 6500)"
  echo "ok: ${#pages[@]} library pages, each named by the README and scoped, every link to one resolves, and each index row opens the first page it names on that page's own words"
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
# use, anywhere but model-registry/ and juku-library/, whose records are kept
# verbatim. The ids are read from the registry, so a new model is held the day
# it is added, and case hides none of them.
ids=$(python3 -c 'import json,sys; print("|".join(m.replace(".", "[.]") for m in json.load(open(sys.argv[1]))["models"]))' model-registry/registry.json)
shape='claude-(opus|sonnet|haiku|fable)-[0-9][0-9a-z.-]*|(z-ai|moonshotai|qwen|deepseek|anthropic|openai|google|meta-llama|mistralai|x-ai)/[a-z0-9][a-z0-9._-]*|gpt-[0-9][0-9a-z.-]*|glm-[0-9][0-9a-z.-]*|kimi-k[0-9][0-9a-z.-]*'
if [ -z "$ids" ]; then
  echo "FAIL: model-registry/registry.json lists no models, so nothing could be held to it."; fail=1
elif grep -R -n -i -E --exclude-dir=.git --exclude-dir=model-registry --exclude-dir=juku-library "($ids|$shape)" . | cut -d: -f1,2 | sed 's/^/  /' | grep . ; then
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
# has stopped reading, and the workflow files — the check, the reviewer, the wake
# it calls, the door's standing proof, the product reviewer, the asker and the
# board's build — which must still agree with the register and with each other.
# It runs unless review-gate.py's plan says it can say nothing new: an earlier
# attempt of this same run passed it, or no file the pull request changes is
# one it reads. Anything else, an error included, runs it (see SELFTEST_NOT_READ).
plan=$(python3 review-gate.py --selftest-plan 2>/dev/null | tail -n 1) || plan="run: the plan could not be made"
case "$plan" in
  "skip: "*) echo "selftest: not run, ${plan#skip: }" ;;
  *) echo "selftest: run, ${plan#run: }"; python3 review-gate.py --selftest || fail_gate=1 ;;
esac
[ "${fail_gate:-0}" -eq 0 ] || { echo "FAIL: the review gate no longer matches the reviewer's answers, or has drifted from the workflows — see the cases above."; fail=1; }
# The build board's build (decision 0007): what the page may say, run on
# made-up roadmaps, since the real ones are private and never reach this log.
python3 -I board/build.py --selftest || { echo "FAIL: board/build.py no longer renders the board as decision 0007 says — see the case above."; fail=1; }
# The product read's rules (decision 0013): the README's list, the ready mark, the
# product's own check and the three kinds of not read, run on made-up cases and on
# the real README, since a README edit that breaks the list would stop every read.
python3 -I product-reads/reads.py --selftest || { echo "FAIL: product-reads/reads.py no longer refuses what decision 0013 says it must — see the case above."; fail=1; }
# The asker and the setup script, each run against a GitHub kept in memory, and the
# starter kit's own gate, which a new product runs as `verify`.
python3 -I product-reads/ask.py --selftest || { echo "FAIL: product-reads/ask.py asks for what it should not, or leaves what it should ask for — see the case above."; fail=1; }
python3 -I product-reads/setup.py --selftest || { echo "FAIL: product-reads/setup.py no longer sets a product up as decision 0013 says — see the case above."; fail=1; }
python3 -I product-reads/kit/review-gate.py --selftest || { echo "FAIL: the starter kit's gate no longer counts what it must — see the case above."; fail=1; }
fi
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
[ "$part" = selftest ] || case "${GITHUB_EVENT_NAME:-}" in push|"") : ;; *)
  if [ -z "${GH_TOKEN:-}" ] || [ -z "${PR_NUMBER:-}" ] || [ -z "${HEAD_SHA:-}" ]; then
    echo "FAIL: the check cannot ask GitHub which commit the reviewer read — the workflow must set PR_NUMBER, HEAD_SHA and GH_TOKEN."; fail=1
  elif python3 review-gate.py "${GITHUB_REPOSITORY:-Adonis80/how-we-build}" "$PR_NUMBER" "$HEAD_SHA" "$GH_TOKEN"; then
    : # the gate says which read it found; one voice, not two
  else
    echo "FAIL: see the reason above."; fail=1
  fi
;; esac

if [ "$fail" -eq 0 ]; then
  case "$part" in whole) echo "check.sh: all clear" ;; *) echo "check.sh: all clear ($part)" ;; esac
fi
exit "$fail"
