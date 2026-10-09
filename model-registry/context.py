#!/usr/bin/env python3
"""What the rulebook's reviewer is shown beside the diff, on every class of change (decisions 0014 and 0018).

    context.py CLASS CHANGED_NUL DIFF_FILE PAGES_OUT     run in the head's checkout
    context.py unit PATH#NAME < FILE                     print one unit of a file, or exit 1
    context.py part PATH DIFF_FILE < FILE                print a touched file's touched parts, or exit 1

Every read, risky or not, is given a selection, never the repository whole
(his ruling, 9 October 2026, decision 0018: "Yes, I want the full read
narrowing switched on now."). A risky change is still a class: it picks
reviewer-risky at max and carries the registry. Each read is given
HOW-WE-BUILD.md; the README's *Where each topic lives* table; each file the
change touches, whole, or past WHOLE bytes the sections its hunks fall in; the
partners PARTNERS names, both ways, a large one as the sections that name a
touched file; every page that names a touched file by its path; and, on a
`code` or `risky` read, the registry. Everything else is named with its size
and left out, so a reader that needed it says so (`needs-context`), naming a
file or one unit of one (`path#heading`, `path#function`, `path#step name`),
and is read once more with every unit it asked for whole (#170), or not at all.

It prints numbers alone: what it read is the change's, and this log is public.
Standard library only.
"""
import fnmatch
import os
import re
import subprocess
import sys

sys.dont_write_bytecode = True

# A touched file past this many bytes is given as the sections its hunks touch.
WHOLE = 40000
KINDS = re.compile(r"\.(md|sh|py|ya?ml)$")
REGISTRY = "model-registry/registry.json"
INDEX = ("README.md", "Where each topic lives")
# Pages that name everything and are no rule: the papers are read like the
# decision issues, and AGENTS.md is the reviewer's own brief, given from main.
NOT_NAMING = ("juku-library/*", "AGENTS.md")
# THE PARTNER MAP: files whose correctness depends on each other, read together
# whichever one a change touches. `path#Heading` gives that section only. A
# starting bundle, never a boundary: what it misses, the reader names. A partner
# past WHOLE bytes is given as its sections that name a touched file, or, when
# those are past WHOLE too, as their names, each one a reader may ask for.
GATE = ("check.sh", "review-gate.py", ".github/workflows/check.yml", ".github/workflows/review.yml",
        ".github/workflows/wake.yml", ".github/workflows/review-product.yml")
# THE GATE (decision 0018): the check, the gate it runs, the workflows that run
# them or that it holds line for line, and the product reader's own.
GATE_PARTNERS = (
    ("check.sh", [".github/workflows/check.yml", "review-gate.py"]),
    ("review-gate.py", [f for f in GATE if f != "review-gate.py"] + ["product-reads/kit/review-gate.py"]),
    (".github/workflows/check.yml", ["check.sh", "review-gate.py"]),
    (".github/workflows/review.yml", ["review-gate.py", ".github/workflows/wake.yml", "model-registry/ask.py",
                                      "model-registry/context.py", "model-registry/resolve.py", REGISTRY]),
    (".github/workflows/wake.yml", ["review-gate.py", ".github/workflows/review.yml", "product-reads/kit/wake.yml"]),
    (".github/workflows/review-product.yml", ["review-gate.py", ".github/workflows/review.yml",
                                              ".github/workflows/ask-product-reads.yml", "product-reads/reads.py",
                                              "model-registry/ask.py", "model-registry/context.py"]),
    ("product-reads/*", [".github/workflows/review-product.yml", ".github/workflows/ask-product-reads.yml",
                         "review-gate.py"]),
    ("model-registry/*.py", [REGISTRY, ".github/workflows/review.yml", "review-gate.py"]),
)
PARTNERS = (
    ("check.sh", ["library/rulebook-files.md"]),
    ("HOW-WE-BUILD.md", ["check.sh"]),
    ("library/changing-the-rulebook.md", ["check.sh"]),
    ("library/model-registry.md", [REGISTRY]),
    ("library/*.md", ["README.md#Where each topic lives"]),
) + GATE_PARTNERS
LEFT_OUT = "%s: %d bytes, left out: not selected for this read"


def _read(path):
    try:
        with open(path, encoding="utf-8") as f:
            return f.read()
    except (OSError, UnicodeDecodeError):
        return None


def section(text, heading):
    """The `## heading` section of a page, through to the next heading of its level or above."""
    lines = text.splitlines(keepends=True)
    for i, line in enumerate(lines):
        m = re.match(r"(#+)\s+(.*?)\s*$", line)
        if m and m.group(2) == heading:
            level = len(m.group(1))
            for j in range(i + 1, len(lines)):
                n = re.match(r"(#+)\s", lines[j])
                if n and len(n.group(1)) <= level:
                    return "".join(lines[i:j])
            return "".join(lines[i:])
    return None


def hunks(diff, path):
    """The head's line numbers each hunk of `path` covers, from a unified diff."""
    spans, on = [], False
    for line in diff.splitlines():
        if line.startswith("diff --git "):
            on = line.endswith(" b/" + path)
        elif on:
            m = re.match(r"@@ -\d+(?:,\d+)? \+(\d+)(?:,(\d+))? @@", line)
            if m:
                start, n = int(m.group(1)), int(m.group(2) or 1)
                spans.append((start, start + max(n, 1) - 1))
    return spans


def starts(lines, path):
    """The lines a file's units begin on: headings, steps, top-level definitions, or paragraphs."""
    if path.endswith(".md"):
        return [i for i, l in enumerate(lines) if re.match(r"#+\s", l)]
    if path.endswith((".yml", ".yaml")):
        return [i for i, l in enumerate(lines) if re.match(r"\s*- name:", l)]
    if path.endswith(".py"):
        return [i for i, l in enumerate(lines) if re.match(r"(def|class)\s|[A-Za-z_][A-Za-z0-9_]*\s*=", l)]
    return [i for i, l in enumerate(lines) if not l.strip()]


def name_of(line, path):
    """The name a reader asks for a unit by (`path#name`): a heading, a step's name, a definition's."""
    if path.endswith(".md"):
        m = re.match(r"#+\s+(.*?)\s*$", line)
    elif path.endswith((".yml", ".yaml")):
        m = re.match(r"\s*- name:\s*[\"']?(.*?)[\"']?\s*$", line)
    elif path.endswith(".py"):
        m = re.match(r"(?:def|class)\s+([A-Za-z_][A-Za-z0-9_]*)|([A-Za-z_][A-Za-z0-9_]*)\s*=", line)
        return next((g for g in m.groups() if g), None) if m else None
    else:
        return None
    return m.group(1) if m else None


def spans_of(text, path):
    """[(name, first line, last line + 1)]: each unit of a file, in order, the opening before the first unnamed."""
    lines = text.splitlines(keepends=True)
    at = starts(lines, path)
    out = [(None, 0, at[0])] if at and at[0] > 0 else []
    if path.endswith(".md"):
        return out + [(name_of(lines[i], path), i, _md_end(lines, i)) for i in at]
    return out + [(name_of(lines[i], path), i, j) for i, j in zip(at, at[1:] + [len(lines)])]


def _md_end(lines, i):
    level = len(re.match(r"(#+)", lines[i]).group(1))
    for j in range(i + 1, len(lines)):
        n = re.match(r"(#+)\s", lines[j])
        if n and len(n.group(1)) <= level:
            return j
    return len(lines)


# What a file's lines before its first unit are asked for by: `path#opening`.
OPENING = "opening"


def unit(text, path, name):
    """The unit of a file a reader asked for by name (`path#name`), whole, or None when it has none.

    A heading, a step's name or a definition's; a numbered section of a page by
    its number too (`PRODUCT.md#6` or `#§6`); and a roadmap's item by its id
    (`roadmap.json#P48`), that item alone.
    """
    if os.path.basename(path) == "roadmap.json":
        try:
            import json
            items = json.loads(text).get("items")
        except (ValueError, AttributeError):
            return None
        item = next((i for i in items or [] if isinstance(i, dict) and i.get("id") == name), None)
        return json.dumps(item, ensure_ascii=False, indent=1) + "\n" if item is not None else None
    lines = text.splitlines(keepends=True)
    number = re.fullmatch(r"§?\s?(\d+(?:\.\d+)*)\.?", name) if path.endswith(".md") else None
    for n, i, j in spans_of(text, path):
        if n is None and name == OPENING:
            return "".join(lines[i:j])
        if n is not None and (n == name or (number and re.match(r"§?\s?%s[.\s]" % re.escape(number.group(1)), n + " "))):
            return "".join(lines[i:j])
    return None


def widened(text, path, spans):
    """The parts of a large file a change touches, each widened to its whole section, step or function."""
    lines = text.splitlines(keepends=True)
    at = starts(lines, path)
    keep = set()
    for a, b in spans:
        lo = max([s for s in at if s <= a - 1] or [0])
        hi = min([s for s in at if s > b - 1] or [len(lines)])
        keep.update(range(lo, hi))
    return _joined(lines, keep)


def _joined(lines, keep):
    out, last = [], None
    for i in sorted(keep):
        if last is not None and i != last + 1:
            out.append("\n[...]\n")
        out.append(lines[i])
        last = i
    return "".join(out)


def naming(text, path, touched):
    """(the units of a large partner that name a touched file, as one text, their names); text None if none do."""
    lines = text.splitlines(keepends=True)
    keep, names = set(), []
    for n, i, j in spans_of(text, path):
        body = "".join(lines[i:j])
        if any(t in body for t in touched):
            keep.update(range(i, j))
            names.append(n or OPENING)
    return (_joined(lines, keep) if keep else None), names


def changed_lines(diff, path):
    """The lines a diff adds or removes in `path`, as one text."""
    out, on = [], False
    for line in diff.splitlines():
        if line.startswith("diff --git "):
            on = line.endswith(" b/" + path)
        elif on and line[:1] in "+-" and not line.startswith(("+++", "---")):
            out.append(line[1:])
    return "\n".join(out)


def partners(touched, tree, diff):
    """The partner entries the touched files bring in, both ways, in order.

    Forward, a touched file matching a pattern brings its partners. Back, a
    touched partner brings the files its pattern matches: all of them for one
    file, and for a pattern of many, those the change's own lines name (a row
    of the README's index brings its page, not the whole library).
    """
    out = []
    for pattern, theirs in PARTNERS:
        if any(fnmatch.fnmatchcase(t, pattern) for t in touched):
            out.extend(theirs)
        for t in touched:
            if t not in [p.split("#")[0] for p in theirs]:
                continue
            matched = [f for f in tree if fnmatch.fnmatchcase(f, pattern)]
            if any(c in pattern for c in "*?["):
                lines = changed_lines(diff, t)
                matched = [f for f in matched if f in lines]
            out.extend(matched)
    seen = []
    for p in out:
        if p not in seen and p not in touched:
            seen.append(p)
    return seen


def select(cls, tree, changed, diff, read=_read):
    """[(marker, text or None, bytes)]: what the read is given, in order, and every other file named with its size.

    The same selection for every class (decision 0018); a `code` or `risky` read
    carries the registry, and a `words` read names it as left out.
    """
    pool = sorted(f for f in tree if KINDS.search(f) or f == REGISTRY)
    whole, parts, out = set(), set(), []

    def give(name, text):
        if text is None or name in whole:
            return
        whole.add(name)
        out.append((name, text))

    def give_part(name, key, marker, text):
        if name in whole or (name, key) in parts or not text:
            return
        parts.add((name, key))
        out.append((marker, text))

    touched = [f for f in changed if f in tree]
    # What a large partner is searched for: each touched file's path, and its
    # bare name, which is how a script or a workflow is usually spoken of.
    names = sorted(set(touched) | {os.path.basename(t) for t in touched if "/" in t})
    give("HOW-WE-BUILD.md", read("HOW-WE-BUILD.md"))
    if INDEX[0] not in touched:
        give_part(INDEX[0], "#" + INDEX[1], '%s, its section "%s" only' % INDEX, section(read(INDEX[0]) or "", INDEX[1]))
    for f in touched:
        text = read(f)
        if text is None:
            continue
        if len(text.encode("utf-8")) <= WHOLE:
            give(f, text)
        else:
            give_part(f, "hunks", "%s, the sections the change touches only (of %d bytes)"
                      % (f, len(text.encode("utf-8"))), widened(text, f, hunks(diff, f)))
    for p in partners(touched, tree, diff):
        name, _, heading = p.partition("#")
        if name not in tree:
            continue
        text = read(name)
        if heading:
            give_part(name, "#" + heading, '%s, its section "%s" only' % (name, heading),
                      section(text or "", heading))
        elif text is None or len(text.encode("utf-8")) <= WHOLE:
            give(name, text)
        else:
            size = len(text.encode("utf-8"))
            found, units = naming(text, name, names)
            if found and len(found.encode("utf-8")) <= WHOLE:
                give_part(name, "naming", "%s, its sections naming the change's files only (of %d bytes)"
                          % (name, size), found)
            elif units:
                give_part(name, "index", "%s: %d bytes; its sections naming the change's files, by name, each "
                          "one a reader may ask for as %s#name" % (name, size, name), "\n".join(units) + "\n")
    for f in pool:
        if f in whole or not f.endswith(".md") or any(fnmatch.fnmatchcase(f, n) for n in NOT_NAMING):
            continue
        text = read(f)
        if not text or not any(t in text for t in touched):
            continue
        if f == INDEX[0]:
            # The README is the map and names every page: its sections that
            # name a touched file, not the whole of it.
            for h in re.findall(r"^## (.+?)\s*$", text, re.M):
                sec = section(text, h) or ""
                if any(t in sec for t in touched):
                    give_part(f, "#" + h, '%s, its section "%s" only' % (f, h), sec)
        else:
            give(f, text)
    if cls != "words":
        give(REGISTRY, read(REGISTRY))
    given = whole | {n for n, _ in parts}
    for f in pool:
        if f not in given:
            text = read(f)
            size = os.path.getsize(f) if read is _read and os.path.exists(f) else len((text or "").encode("utf-8"))
            out.append((LEFT_OUT % (f, size), None))
    return [(m, t, len(t.encode("utf-8")) if t is not None else 0) for m, t in out]


def touched_items(text, diff, path):
    """A roadmap's items whose lines the change's hunks fall in, each alone, as one text; None for none.

    An item's lines run from its `"id"` line to the next item's; a hunk before the
    first is in the roadmap's own fields, which the diff shows, and gives no item.
    """
    import json
    try:
        items = [i for i in json.loads(text).get("items") or [] if isinstance(i, dict) and isinstance(i.get("id"), str)]
    except (ValueError, AttributeError):
        return None
    lines = text.splitlines()
    at = []
    for item in items:
        mark = re.compile(r'^\s*"id":\s*%s,?\s*$' % re.escape(json.dumps(item["id"], ensure_ascii=False)))
        n = next((k for k, l in enumerate(lines) if mark.match(l)), None)
        if n is not None:
            at.append((n + 1, item))
    at.sort(key=lambda x: x[0])
    picked = []
    for a, b in hunks(diff, path):
        for k, (line, item) in enumerate(at):
            end = at[k + 1][0] - 1 if k + 1 < len(at) else len(lines)
            if line <= b and a <= end and item not in picked:
                picked.append(item)
    return "".join(json.dumps(i, ensure_ascii=False, indent=1) + "\n" for i in picked) or None


def part_main(path, diff_file):
    """`context.py part PATH DIFF_FILE < FILE`: what a product read carries of a touched file past its size.

    A roadmap's touched items, each alone; any other file, the sections its hunks
    fall in. Exit 1 when the change touches none of it.
    """
    text, diff = sys.stdin.read(), _read(diff_file) or ""
    if os.path.basename(path) == "roadmap.json":
        got = touched_items(text, diff, path)
    else:
        spans = hunks(diff, path)
        got = widened(text, path, spans) if spans else None
    if not got:
        return 1
    sys.stdout.write(got)
    return 0


def unit_main(want):
    """`context.py unit PATH#NAME < FILE`: the one unit asked for, whole, on stdout; exit 1 when the file has none."""
    path, _, name = want.partition("#")
    text = sys.stdin.read()
    got = unit(text, path, name) if name else None
    if got is None:
        return 1
    sys.stdout.write(got)
    return 0


def main(argv):
    if len(argv) == 3 and argv[1] == "unit":
        return unit_main(argv[2])
    if len(argv) == 4 and argv[1] == "part":
        return part_main(argv[2], argv[3])
    if len(argv) != 5:
        print(__doc__.strip().split("\n\n")[1], file=sys.stderr)
        return 2
    cls, changed_file, diff_file, pages_out = argv[1:5]
    tree = subprocess.run(["git", "ls-tree", "-r", "-z", "--name-only", "HEAD"], capture_output=True,
                          check=True).stdout.decode("utf-8").split("\0")
    tree = [f for f in tree if f]
    with open(changed_file, "rb") as f:
        changed = [p.decode("utf-8") for p in f.read().split(b"\0") if p]
    diff = _read(diff_file) or ""
    picked = select(cls, tree, changed, diff)
    with open(pages_out, "w", encoding="utf-8") as f:
        for marker, text, _ in picked:
            if text is None:
                f.write("\n===== %s =====\n" % marker)
            else:
                f.write("\n===== %s =====\n" % marker)
                f.write(text)
    given = [p for p in picked if p[1] is not None]
    print("selected: %d part(s) given, %d file(s) named as left out" % (len(given), len(picked) - len(given)))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
