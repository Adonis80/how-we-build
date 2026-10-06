#!/usr/bin/env python3
"""What the rulebook's reviewer is shown beside the diff, by the change's class (decision 0014).

    context.py CLASS CHANGED_NUL DIFF_FILE PAGES_OUT     run in the head's checkout

A `risky` read is given every page whole, as before: every .md, .sh, .py and
.yml file and `model-registry/registry.json` (0014 G and H: cold review and
max effort stay). A `words` or `code` read is the context pilot (0014's order,
item 4, now that a read short of context can say so and be read again):
HOW-WE-BUILD.md; the README's *Where each topic lives* table; each file the
change touches, whole, or past WHOLE bytes the sections its hunks fall in; the
partners PARTNERS names, both ways; every page that names a touched file by its
path; and, on a `code` read, the registry. Everything else is named with its
size and left out, so a reader that needed it says so (`needs-context`).

The pilot is bounded: the month review on or after 2 November 2026 keeps it or
reverts it, on the attempt records. It prints numbers alone: what it read is
the change's, and this log is public. Standard library only.
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
# starting bundle, never a boundary: what it misses, the reader names. An entry
# only risky files can bring is none: a risky read is given every file whole.
PARTNERS = (
    ("check.sh", ["library/rulebook-files.md"]),
    ("HOW-WE-BUILD.md", ["check.sh"]),
    ("library/changing-the-rulebook.md", ["check.sh"]),
    ("library/model-registry.md", [REGISTRY]),
    ("library/*.md", ["README.md#Where each topic lives"]),
)
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


def widened(text, path, spans):
    """The parts of a large file a change touches, each widened to its whole section, step or function."""
    lines = text.splitlines(keepends=True)
    if path.endswith(".md"):
        starts = [i for i, l in enumerate(lines) if re.match(r"#+\s", l)]
    elif path.endswith((".yml", ".yaml")):
        starts = [i for i, l in enumerate(lines) if re.match(r"\s*- name:", l)]
    elif path.endswith(".py"):
        starts = [i for i, l in enumerate(lines) if re.match(r"(def|class)\s", l)]
    else:
        starts = [i for i, l in enumerate(lines) if not l.strip()]
    keep = set()
    for a, b in spans:
        lo = max([s for s in starts if s <= a - 1] or [0])
        hi = min([s for s in starts if s > b - 1] or [len(lines)])
        keep.update(range(lo, hi))
    out, last = [], None
    for i in sorted(keep):
        if last is not None and i != last + 1:
            out.append("\n[...]\n")
        out.append(lines[i])
        last = i
    return "".join(out)


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
    """[(marker, text or None, bytes)]: what the read is given, in order, and every other file named with its size."""
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

    if cls not in ("words", "code"):
        for f in pool:
            give(f, read(f))
    else:
        touched = [f for f in changed if f in tree]
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
            else:
                give(name, text)
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
        if cls == "code":
            give(REGISTRY, read(REGISTRY))
    given = whole | {n for n, _ in parts}
    for f in pool:
        if f not in given:
            text = read(f)
            size = os.path.getsize(f) if read is _read and os.path.exists(f) else len((text or "").encode("utf-8"))
            out.append((LEFT_OUT % (f, size), None))
    return [(m, t, len(t.encode("utf-8")) if t is not None else 0) for m, t in out]


def main(argv):
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
