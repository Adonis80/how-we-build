#!/usr/bin/env python3
"""The rules' own guard: the ledger and the constitution's shape. No word count.

Run by check.sh here; a product is to run it from a pinned commit of this
repository, from its own check (library/changing-the-rulebook.md). Free: it reads files only.
The ledger (LEDGER.md) lists every live rule, old against new, kept, moved or retired; a
rule dropped or reworded without its row is red. It replaced the pull request's Replaces:
line, which a session declared and which no run showed catching a dropped rule (Hemz-OS#441).

    product-reads/rules-check.py           this repository, from its root
    rules-check.py --product
    rules-check.py --selftest

No page is held to a word count (his ruling, 4 November 2026, decision 0026:
"There should not be a word limit. Instead, we will have a hierarchy of
information"). The hierarchy is held by check.sh's index checks: every page
named by the README with when to open it.
"""
import fnmatch
import hashlib
import os
import re
import sys

# History, not rules: the upgrade log is never a rule page.
RULEBOOK_NOT_ACTIVE = ("library/upgrade-log.md",)

PRODUCT_RULE_GLOBS = ("AGENTS.md", "CLAUDE.md", "NAMES.md", "design/*.md", "design-system.md")

HEADINGS = ("Tokens", "Units", "Money", "Domain law", "Approved by picture")
DATE = re.compile(r"\b(\d{1,2} (January|February|March|April|May|June|July|August|September|October|November|December) 20\d\d|20\d\d-\d\d-\d\d)\b")
PICTURE = re.compile(r"(https?://\S+|[\w./-]+\.(png|jpe?g|webp|gif|svg|pdf|mp4|mov|webm|m4a|mp3|wav))", re.I)
LEDGER = "LEDGER.md"


def constitution_faults(text):
    """What is wrong with a design/CONSTITUTION.md, as a list of reasons."""
    bad, section, approvals = [], None, []
    for line in text.splitlines():
        m = re.match(r"^##\s+(.+?)\s*$", line)
        if m:
            section = m.group(1)
            if section not in HEADINGS:
                bad.append("heading '%s' is not one of %s" % (section, ", ".join(HEADINGS)))
            continue
        if re.match(r"^#{3,}\s", line):
            bad.append("sub-heading '%s': the constitution has only its five headings" % line.lstrip("#").strip())
        # Every line under the last heading is an approval, or the indented
        # continuation of one. An indented list item is an approval of its own
        # and never borrows its parent's date or picture.
        if section == "Approved by picture" and line.strip() and not line.strip().startswith("<!--"):
            if line[:1].isspace() and approvals and not re.match(r"^\s*([-*+]|\d+[.)])\s", line):
                approvals[-1] += " " + line.strip()
            elif line.strip().rstrip(".") != "None yet":
                approvals.append(line.strip())
    for item in approvals:
        if not DATE.search(item):
            bad.append("an approval with no date: %s" % item[:80])
        if not PICTURE.search(item):
            bad.append("an approval naming no picture (a path or link): %s" % item[:80])
    return bad


def flat(text):
    return " ".join(re.sub(r"[*`]", "", text).split())


def rule_units(text):
    """A page's rule units, flat: each paragraph, list item and table row, as LEDGER.md counts them."""
    out, cur, code, prev = [], None, False, None
    for line in text.splitlines():
        if line.startswith("```"):
            code, cur = not code, None
            continue
        if code or not line.strip() or line.startswith("#") or line.startswith("!["):
            cur = None
            continue
        if re.match(r"^\|[-: |]+\|$", line.strip()):
            if out and out[-1] is prev:
                out.pop()   # a table's header row is no rule
            continue
        if re.match(r"^\s*([-*]|\d+\.)\s", line) or line.startswith("|"):
            cur = [line]
            out.append(cur)
            prev = cur if line.startswith("|") else None
            if line.startswith("|"):
                cur = None
            continue
        if cur is None:
            cur = [line]
            out.append(cur)
        else:
            cur.append(line)
    return [flat(" ".join(u)) for u in out]


def words_of(unit):
    """A rule unit's fingerprint: any word added, cut or changed changes it."""
    return hashlib.sha256(unit.encode("utf-8")).hexdigest()[:10]


def ledger_faults(root="."):
    """Every kept or moved rule's anchor is still in its home; a retired one says why.

    The same rule as Hemz OS's coherence.py rule 8, so one ledger shape serves both halves.
    A home in another repository (`Hemz-OS/AGENTS.md`) is held only where that clone sits
    beside this one; that repository's own check holds it otherwise.
    """
    path = os.path.join(root, LEDGER)
    if not os.path.isfile(path):
        return ["%s is missing: every live rule is listed there, old against new" % LEDGER]
    faults, seen, cache = [], set(), {}
    with open(path, encoding="utf-8") as f:
        lines = f.read().splitlines()
    for n, line in enumerate(lines, 1):
        cells = [c.strip() for c in line.strip().strip("|").split("|")] if line.startswith("|") else []
        if len(cells) < 5 or cells[0].lower() == "id" or set(cells[0]) <= set("-: "):
            continue
        rid, now, anchor = cells[0], cells[3], cells[4].strip('`"\u201c\u201d ')
        if rid in seen:
            faults.append("%s:%d: %s appears twice" % (LEDGER, n, rid))
        seen.add(rid)
        state = now.split(":", 1)[0].strip().lower()
        if state == "retired":
            if len(anchor.split()) < 2:
                faults.append("%s:%d: %s is retired with no reason" % (LEDGER, n, rid))
            continue
        m = re.search(r"([\w./-]+\.(?:md|json|py|sh|yml))", now)
        if state not in ("kept", "moved") or not m or len(anchor.split()) < 2:
            faults.append("%s:%d: %s: 'now' is kept or moved with its home file, or retired; the anchor is two words or more"
                          % (LEDGER, n, rid))
            continue
        home = m.group(1)
        full = os.path.join(root, home)
        other = home.split("/")[0] if "/" in home and not os.path.exists(os.path.join(root, home.split("/")[0])) else None
        if other:
            if not os.path.isdir(os.path.join(root, "..", other)):
                continue   # another repository, not beside this clone: its own check holds that row
            full = os.path.join(root, "..", home)
        if full not in cache:
            text = open(full, encoding="utf-8").read() if os.path.isfile(full) else None
            cache[full] = (flat(text), rule_units(text)) if text is not None else None
        if cache[full] is None:
            faults.append("%s:%d: %s: its home %s does not exist" % (LEDGER, n, rid, home))
        elif flat(anchor) not in cache[full][0]:
            faults.append('%s:%d: %s: "%s" is no longer in %s: a rule was dropped or reworded without its row' %
                          (LEDGER, n, rid, flat(anchor)[:60], home))
        elif len(cells) > 5 and cells[5].strip("` "):
            now_words = [words_of(u) for u in cache[full][1] if flat(anchor) in u]
            if cells[5].strip("` ") not in now_words:
                faults.append("%s:%d: %s: the rule holding \"%s\" in %s has changed its words since its row (%s, now %s): "
                              "a clause was cut, added or reworded without its row; say so in the row and give it its new words"
                              % (LEDGER, n, rid, flat(anchor)[:40], home, cells[5].strip("` "), "/".join(now_words) or "none"))
    return faults


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
    if product and os.path.isfile("design/CONSTITUTION.md"):
        with open("design/CONSTITUTION.md", encoding="utf-8") as f:
            faults = constitution_faults(f.read())
        for b in faults:
            print("FAIL: design/CONSTITUTION.md: " + b)
        fail |= bool(faults)
        if not faults:
            print("ok: design/CONSTITUTION.md has only its five headings, each approval dated with its picture")
    if not product:
        faults = ledger_faults()
        for b in faults:
            print("FAIL: " + "".join(c for c in b if c.isprintable()))
        fail |= bool(faults)
        if not faults:
            print("ok: every kept or moved rule in %s is still in its home" % LEDGER)
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
    want("a long constitution is no fault (no word limits)",
         constitution_faults("# C\n\n" + "word " * 90 + "\n\n## Domain law\n\n" + "word " * 2000), [])
    want("a paragraph of undated exceptions",
         len(constitution_faults("## Approved by picture\n\nThe old look stays, as agreed.\n")) > 0, True)
    want("none yet", constitution_faults("## Approved by picture\n\nNone yet.\n"), [])
    want("none yet, no stop", constitution_faults("## Approved by picture\n\nNone yet\n"), [])
    want("an item wrapped onto a second line", constitution_faults(
        "## Approved by picture\n\n- The plaque, 12 August 2026,\n  hemz-library/design/plaque/sheet.png\n"), [])
    want("an indented sub-item borrows nothing from its parent", len(constitution_faults(
        "## Approved by picture\n\n- The plaque, 12 August 2026, design/p.png\n  - and the tiles too\n")), 2)
    want("a plus or a 1) sub-item borrows nothing either", len(constitution_faults(
        "## Approved by picture\n\n- The plaque, 12 August 2026, design/p.png\n  + the tiles\n  1) the header\n")), 4)
    want("a rehearsal recording", constitution_faults("## Approved by picture\n\n- Sound, 12 October 2026, design/r.m4a\n"), [])
    want("the upgrade log is not a rule page", is_rule_page("library/upgrade-log.md", False), False)
    want("a library page is", is_rule_page("library/reviewer.md", False), True)
    want("a product's design page is", is_rule_page("design/HEMZ-VOICE.md", True), True)
    want("a product's PRODUCT.md is not", is_rule_page("PRODUCT.md", True), False)
    want("this check's own file is", is_rule_page("product-reads/rules-check.py", False), True)
    # The wiring: main() on a made-up rulebook of any size passes; a dropped rule fails;
    # a product's constitution is held to its headings.
    import contextlib, io, tempfile
    keep = os.getcwd()
    with tempfile.TemporaryDirectory() as d:
        os.makedirs(os.path.join(d, "rule"))
        os.chdir(os.path.join(d, "rule"))   # the rulebook; ../Hemz-OS beside it stays inside d
        try:
            os.makedirs("library")
            for f, n in (("HOW-WE-BUILD.md", 50000), ("README.md", 10), ("library/" + "a.md", 50000)):
                with open(f, "w") as h:
                    h.write("word " * n)
            with open("HOW-WE-BUILD.md", "a") as h:
                h.write("\n\n**Never answer a failure with a new rule.** Repair the cause.\n")
            with open(LEDGER, "w") as h:
                h.write("| id | rule | was | now | anchor | words |\n|---|---|---|---|---|---|\n"
                        "| R1 | No new rule for a failure. | HOW-WE-BUILD.md | kept: HOW-WE-BUILD.md | `Never answer a failure with a new rule` | `"
                        + words_of(flat("**Never answer a failure with a new rule.** Repair the cause.")) + "` |\n"
                        "| R2 | An old line. | README.md | retired: superseded by R1 | `superseded by R1, the same rule` |\n"
                        "| R3 | A product's rule. | x | moved: Hemz-OS/AGENTS.md | `held there, not here` |\n")
            with contextlib.redirect_stdout(io.StringIO()):
                want("a rulebook of any size, its ledger whole, passes", main([]), 0)
            want("a ledger whose rows all hold", ledger_faults(), [])
            text = open("HOW-WE-BUILD.md").read()
            with open("HOW-WE-BUILD.md", "w") as h:
                h.write(text.replace("**Never answer a failure with a new rule.** ", ""))
            got = ledger_faults()
            want("a planted drop names its row", len(got) == 1 and "R1" in got[0] and "dropped" in got[0], True)
            with open("HOW-WE-BUILD.md", "w") as h:
                h.write(text.replace("**Never answer a failure with a new rule.**", "**Never answer a failure with a new  rule.**"))
            want("bold and spacing are not a rewording", ledger_faults(), [])
            with open("HOW-WE-BUILD.md", "w") as h:
                h.write(text.replace(" Repair the cause.", ""))
            got = ledger_faults()
            want("a clause cut from the middle of a kept rule names its row", len(got) == 1 and "changed its words" in got[0], True)
            with open("HOW-WE-BUILD.md", "w") as h:
                h.write(text)
            os.makedirs("../Hemz-OS", exist_ok=True)
            with open("../Hemz-OS/AGENTS.md", "w") as h:
                h.write("nothing\n")
            want("a moved row is held where its repository is beside", len(ledger_faults()), 1)
            os.remove("../Hemz-OS/AGENTS.md")
            os.rmdir("../Hemz-OS")
            with open(LEDGER, "a") as h:
                h.write("| R4 | A retired line. | x | retired: | `` |\n| R1 | twice. | x | kept: README.md | `two words` |\n")
            want("a retirement with no reason, and a row twice, both fail", len(ledger_faults()), 3)
            os.remove(LEDGER)
            want("no ledger fails", len(ledger_faults()), 1)
            with open("AGENTS.md", "w") as h:
                h.write("word " * 50000)
            os.makedirs("design")
            with open("design/CONSTITUTION.md", "w") as h:
                h.write("## Domain law\n\n" + "word " * 5000 + "\n")
            with contextlib.redirect_stdout(io.StringIO()):
                want("a product of any size passes", main(["--product"]), 0)
            with open("design/CONSTITUTION.md", "w") as h:
                h.write("## Style\n\nA bank statement.\n")
            with contextlib.redirect_stdout(io.StringIO()):
                want("a product's constitution off its headings still fails", main(["--product"]), 1)
        finally:
            os.chdir(keep)
    print("ok: rules-check selftest, every case as it should be" if not bad else "FAIL: rules-check selftest")
    return 1 if bad else 0


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        sys.exit(selftest())
    sys.exit(main(sys.argv[1:]))
