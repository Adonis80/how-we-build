#!/usr/bin/env python3
"""The rules' own guard: word budgets, the Replaces: line, the constitution's shape.

Run by check.sh here; a product is to run it from a pinned commit of this
repository, from its own check (library/changing-the-rulebook.md). Free: it reads files, and in
a pull request the pull request's own event and its list of changed files.

    product-reads/rules-check.py           this repository, from its root
    rules-check.py --product --path-budget N --active-budget M [--tokens FILE]
    rules-check.py --selftest

Budgets are hard: over either fails. A change that needs room cuts elsewhere in
the same pull request, and the count sees the cut. A product's requirements,
roadmap and locked figures are never counted (PRODUCT.md, roadmap.json, its
library and evidence are not rule pages).
"""
import fnmatch
import glob
import json
import os
import re
import sys
import urllib.request

# This repository's budgets. Changing one is a rule change like any other.
RULEBOOK_PATH = ("HOW-WE-BUILD.md", "README.md")
RULEBOOK_PATH_BUDGET = 1550
RULEBOOK_ACTIVE_BUDGET = 22300
# History, not rules: the archive and the upgrade log are never budgeted.
RULEBOOK_NOT_ACTIVE = ("library/upgrade-log.md",)
RULEBOOK_SCREEN = ("HOW-WE-BUILD.md", "README.md", "library/hypersolid.md", "library/voice-native.md")

PRODUCT_PATH = ("AGENTS.md", "design/CONSTITUTION.md")
PRODUCT_RULE_GLOBS = ("AGENTS.md", "CLAUDE.md", "NAMES.md", "design/*.md", "design-system.md")

CONSTITUTION_WORDS = 450
INTRO_WORDS = 80
HEADINGS = ("Tokens", "Units", "Money", "Domain law", "Approved by picture")
DATE = re.compile(r"\b(\d{1,2} (January|February|March|April|May|June|July|August|September|October|November|December) 20\d\d|20\d\d-\d\d-\d\d)\b")
PICTURE = re.compile(r"(https?://\S+|[\w./-]+\.(png|jpe?g|webp|gif|svg|pdf|mp4|mov|webm|m4a|mp3|wav))", re.I)
TEMPLATE_HOLES = ("<the text or page it supersedes>", "<product pages updated, or none>", "<pages updated|none>", "<why>")
REPLACES = re.compile(r"^\s*Replaces:\s*(.+)$", re.M | re.I)


def words(path):
    try:
        with open(path, encoding="utf-8") as f:
            return len(f.read().split())
    except OSError:
        return 0


def rulebook_active():
    files = [f for f in ("HOW-WE-BUILD.md", "README.md", "CHARTER.md", "RICH-DATA.md", "AGENTS.md")
             if os.path.isfile(f)]
    files += sorted(f for f in glob.glob("library/*.md") if f not in RULEBOOK_NOT_ACTIVE)
    return files


def product_active():
    seen = []
    for g in PRODUCT_RULE_GLOBS:
        for f in sorted(glob.glob(g)):
            if os.path.isfile(f) and f not in seen:
                seen.append(f)
    return seen


def budget(name, files, limit):
    n = sum(words(f) for f in files)
    if n > limit:
        return n, "FAIL: %s is %d words, over its %d budget by %d. Cut elsewhere in this pull request (library/changing-the-rulebook.md)." % (
            name, n, limit, n - limit)
    return n, "ok: %s is %d words (budget %d)" % (name, n, limit)


def constitution_faults(text):
    """What is wrong with a design/CONSTITUTION.md, as a list of reasons."""
    bad, section, before, approvals = [], None, [], []
    if len(text.split()) > CONSTITUTION_WORDS:
        bad.append("it is %d words; the cap is %d" % (len(text.split()), CONSTITUTION_WORDS))
    for line in text.splitlines():
        m = re.match(r"^##\s+(.+?)\s*$", line)
        if m:
            section = m.group(1)
            if section not in HEADINGS:
                bad.append("heading '%s' is not one of %s" % (section, ", ".join(HEADINGS)))
            continue
        if re.match(r"^#{3,}\s", line):
            bad.append("sub-heading '%s': the constitution has only its five headings" % line.lstrip("#").strip())
        if section is None and not line.startswith("# "):
            before.append(line)
        if section == "Approved by picture" and line.strip() and not line.strip().startswith("<!--"):
            if line[:1].isspace() and approvals:
                approvals[-1] += " " + line.strip()
            elif line.strip().rstrip(".") != "None yet":
                approvals.append(line.strip())
    for item in approvals:
        if not DATE.search(item):
            bad.append("an approval with no date: %s" % item[:80])
        if not PICTURE.search(item):
            bad.append("an approval naming no picture (a path or link): %s" % item[:80])
    if len(" ".join(before).split()) > INTRO_WORDS:
        bad.append("more than %d words before its first heading: rules go under the five headings" % INTRO_WORDS)
    return bad


def replaces_fault(body, rule_pages_changed):
    """None when the Replaces: line is in order, else the reason."""
    if not rule_pages_changed:
        return None
    m = REPLACES.search(body or "")
    if not m:
        return ("this pull request changes %s and carries no 'Replaces:' line: 'Replaces: <the text or page it "
                "supersedes>; products: <pages updated, or none>', or 'Replaces: nothing — not a check because: "
                "<why>'" % ", ".join(repr(p) for p in rule_pages_changed[:5]))
    said = m.group(1).strip()
    if any(t in said for t in TEMPLATE_HOLES):
        return "the 'Replaces:' line still holds the template's <placeholders>"
    if re.match(r"(?i)^nothing\b", said) and not re.search(r"(?i)not a check because:\s*\S", said):
        return "'Replaces: nothing' must say 'not a check because: <why>'"
    if not re.match(r"(?i)^nothing\b", said) and not re.search(r"(?i)\bproducts:\s*\S", said):
        return "'Replaces:' must also say 'products: <pages updated, or none>'"
    return None


class _Stay(urllib.request.HTTPRedirectHandler):
    """No redirect is followed, so the token never travels to another host."""
    def redirect_request(self, *args, **kwargs):
        return None


_OPEN = urllib.request.build_opener(_Stay)


def _get(url, token):
    req = urllib.request.Request(url, headers={"Authorization": "Bearer " + token,
                                               "Accept": "application/vnd.github+json",
                                               "User-Agent": "juku-rules-check"})
    with _OPEN.open(req, timeout=30) as r:
        return json.loads(r.read().decode("utf-8"))


def pull_request():
    """(body, changed files) of the pull request this run is for, or None outside one.

    A pull_request run reads its own event; a push run on a branch (a product
    whose checks run on push alone) asks GitHub for that branch's open pull
    request. No token, no pull request, or main: nothing to check, and it says so.
    """
    path = os.environ.get("GITHUB_EVENT_PATH")
    if not path or not os.path.isfile(path):
        return None
    with open(path, encoding="utf-8") as f:
        event = json.load(f)
    token = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")
    repo = os.environ.get("GITHUB_REPOSITORY")
    pr = event.get("pull_request")
    if not token or not repo:
        print("note: no token, so the Replaces: line is not checked on this run")
        return None
    if not pr:
        ref = os.environ.get("GITHUB_REF", "")
        if not ref.startswith("refs/heads/") or ref == "refs/heads/main":
            return None
        owner = repo.split("/")[0]
        found = _get("https://api.github.com/repos/%s/pulls?state=open&head=%s:%s" % (
            repo, owner, urllib.request.quote(ref[len("refs/heads/"):], safe="")), token)
        if not found:
            print("note: this branch has no open pull request yet, so the Replaces: line waits for its next run")
            return None
        pr = found[0]
    # The body as it stands now, not as the event that started this run saw it:
    # a re-run keeps its first event, and the line may have been fixed since.
    pr = _get("https://api.github.com/repos/%s/pulls/%d" % (repo, pr["number"]), token)
    files, page = [], 1
    while True:
        got = _get("https://api.github.com/repos/%s/pulls/%d/files?per_page=100&page=%d" % (
            repo, pr["number"], page), token)
        files += [g["filename"] for g in got]
        if len(got) < 100:
            break
        page += 1
    return pr.get("body") or "", files


def is_rule_page(path, product):
    if product:
        return any(fnmatch.fnmatch(path, g) for g in PRODUCT_RULE_GLOBS)
    if path in RULEBOOK_NOT_ACTIVE:
        return False
    return path in ("HOW-WE-BUILD.md", "README.md", "CHARTER.md", "RICH-DATA.md", "AGENTS.md",
                    "product-reads/rules-check.py") or (
        path.startswith("library/") and path.endswith(".md"))


def main(argv):
    product = "--product" in argv
    fail = 0

    def arg(name, default=None):
        return int(argv[argv.index(name) + 1]) if name in argv else default

    if product:
        pb, ab = arg("--path-budget"), arg("--active-budget")
        if pb is None or ab is None:
            print("FAIL: a product passes --path-budget and --active-budget")
            return 1
        path = [f for f in PRODUCT_PATH if os.path.isfile(f)]
        active = product_active()
        screen = path + ([argv[argv.index("--tokens") + 1]] if "--tokens" in argv else [])
    else:
        pb, ab = RULEBOOK_PATH_BUDGET, RULEBOOK_ACTIVE_BUDGET
        path, active, screen = list(RULEBOOK_PATH), rulebook_active(), list(RULEBOOK_SCREEN)
    for name, files, limit in (("the reading path", path, pb), ("the active rules", active, ab)):
        _, line = budget(name, files, limit)
        print(line)
        fail |= line.startswith("FAIL")
    print("size: the screen path here is %d words (%s)" % (sum(words(f) for f in screen), ", ".join(screen)))
    if active:
        big = max(active, key=words)
        print("size: the largest active page is %s, %d words" % (big, words(big)))
    if product and os.path.isfile("design/CONSTITUTION.md"):
        with open("design/CONSTITUTION.md", encoding="utf-8") as f:
            faults = constitution_faults(f.read())
        for b in faults:
            print("FAIL: design/CONSTITUTION.md: " + b)
        fail |= bool(faults)
        if not faults:
            print("ok: design/CONSTITUTION.md has only its five headings, each approval dated with its picture")
    try:
        pr = pull_request()
    except (OSError, ValueError, KeyError) as e:
        print("FAIL: GitHub did not answer about this pull request (%s), so the Replaces: line is unread" % type(e).__name__)
        return 1
    if pr is not None:
        body, files = pr
        why = replaces_fault(body, [f for f in files if is_rule_page(f, product)])
        if why:
            print("FAIL: " + "".join(c for c in why if c.isprintable()))
            fail = 1
        else:
            print("ok: the Replaces: line is in order, or no rule page changed")
    return 1 if fail else 0


def selftest():
    bad = 0

    def want(what, got, expect):
        nonlocal bad
        if got != expect:
            print("  rules-check selftest: %s: got %r, want %r" % (what, got, expect))
            bad += 1

    good = ("# C\n\n## Tokens\n\nsee design-system.md\n\n## Money\n\n1. prices derived.\n\n"
            "## Approved by picture\n\n- The plaque, 12 August 2026, hemz-library/design/plaque/sheet.png\n")
    want("a good constitution", constitution_faults(good), [])
    want("a style heading", len(constitution_faults(good + "\n## Style\n\nA bank statement.\n")), 1)
    want("an approval without a date",
         len(constitution_faults("## Approved by picture\n\n- The plaque, hemz-library/design/p.png\n")), 1)
    want("an approval without a picture",
         len(constitution_faults("## Approved by picture\n\n- The plaque, 12 August 2026\n")), 1)
    want("a sub-heading", len(constitution_faults("## Money\n\n### Style\n")), 1)
    want("a deeper sub-heading", len(constitution_faults("## Money\n\n#### Style\n")), 1)
    want("a long preamble", len(constitution_faults("# C\n\n" + "word " * 90 + "\n\n## Tokens\n")), 1)
    want("an over-long constitution", len(constitution_faults("## Domain law\n\n" + "word " * 460)), 1)
    want("a paragraph of undated exceptions",
         len(constitution_faults("## Approved by picture\n\nThe old look stays, as agreed.\n")) > 0, True)
    want("none yet", constitution_faults("## Approved by picture\n\nNone yet.\n"), [])
    want("none yet, no stop", constitution_faults("## Approved by picture\n\nNone yet\n"), [])
    want("an item wrapped onto a second line", constitution_faults(
        "## Approved by picture\n\n- The plaque, 12 August 2026,\n  hemz-library/design/plaque/sheet.png\n"), [])
    want("a rehearsal recording", constitution_faults("## Approved by picture\n\n- Sound, 12 October 2026, design/r.m4a\n"), [])
    want("no rule page changed", replaces_fault("", []), None)
    want("a rule page and no line", replaces_fault("Fixes things", ["HOW-WE-BUILD.md"]) is not None, True)
    want("a full line", replaces_fault("Replaces: the old loop; products: none", ["CHARTER.md"]), None)
    want("a line without products",
         replaces_fault("Replaces: the old loop", ["CHARTER.md"]) is not None, True)
    want("nothing, with a reason",
         replaces_fault("Replaces: nothing — not a check because: it is a judgement", ["AGENTS.md"]), None)
    want("nothing, without a reason", replaces_fault("Replaces: nothing", ["AGENTS.md"]) is not None, True)
    want("the template pasted as it is", replaces_fault(
        "Replaces: <the text or page it supersedes>; products: <product pages updated, or none>", ["AGENTS.md"]) is not None, True)
    want("the upgrade log is not a rule page", is_rule_page("library/upgrade-log.md", False), False)
    want("a library page is", is_rule_page("library/reviewer.md", False), True)
    want("a product's design page is", is_rule_page("design/HEMZ-VOICE.md", True), True)
    want("a product's PRODUCT.md is not", is_rule_page("PRODUCT.md", True), False)
    want("the budgets' own file is", is_rule_page("product-reads/rules-check.py", False), True)
    want("a filled line naming <product>-library", replaces_fault(
        "Replaces: the old `<product>-library` rule; products: none", ["AGENTS.md"]), None)
    want("over budget", budget("x", [__file__], 1)[1].startswith("FAIL"), True)
    # The wiring: main() on a made-up rulebook, over budget and under; the upgrade log
    # and the archive never counted; a GitHub that does not answer fails the run.
    import contextlib, io, tempfile
    global RULEBOOK_PATH_BUDGET, RULEBOOK_ACTIVE_BUDGET, pull_request
    keep = (os.getcwd(), RULEBOOK_PATH_BUDGET, RULEBOOK_ACTIVE_BUDGET, pull_request)
    with tempfile.TemporaryDirectory() as d:
        os.chdir(d)
        try:
            os.makedirs("library"); os.makedirs("juku-library")
            for f, n in (("HOW-WE-BUILD.md", 10), ("README.md", 10), ("library/" + "a.md", 10),
                         ("library/upgrade-log.md", 500), ("juku-library/X.md", 500)):
                with open(f, "w") as h:
                    h.write("word " * n)
            want("the upgrade log and the archive are not active rules", rulebook_active(),
                 ["HOW-WE-BUILD.md", "README.md", "library/" + "a.md"])
            pull_request = lambda: None
            RULEBOOK_PATH_BUDGET, RULEBOOK_ACTIVE_BUDGET = 20, 30
            with contextlib.redirect_stdout(io.StringIO()):
                want("under both budgets passes", main([]), 0)
            RULEBOOK_PATH_BUDGET = 19
            with contextlib.redirect_stdout(io.StringIO()):
                want("over the reading path's budget fails", main([]), 1)
            RULEBOOK_PATH_BUDGET, RULEBOOK_ACTIVE_BUDGET = 20, 29
            with contextlib.redirect_stdout(io.StringIO()):
                want("over the active rules' budget fails", main([]), 1)
            RULEBOOK_ACTIVE_BUDGET = 30

            def down():
                raise OSError("no answer")
            pull_request = down
            with contextlib.redirect_stdout(io.StringIO()):
                want("a GitHub that does not answer fails the run", main([]), 1)
        finally:
            os.chdir(keep[0])
            RULEBOOK_PATH_BUDGET, RULEBOOK_ACTIVE_BUDGET, pull_request = keep[1], keep[2], keep[3]
    print("ok: rules-check selftest, every case as it should be" if not bad else "FAIL: rules-check selftest")
    return 1 if bad else 0


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        sys.exit(selftest())
    sys.exit(main(sys.argv[1:]))
