#!/usr/bin/env python3
"""Coherence: every ruling of his has one home, no rule is stated twice, nothing superseded stays.

His word, 9 November 2026 (Hemz-OS#285): "use machine checks to ensure that rules are followed
and not taken as suggestions"; and "a system that keeps it coherent". Free: it reads files.

    coherence.py inventory [--product] [ROOT]     every dated ruling of his found, as JSON lines
    coherence.py check     [--product] [ROOT]     the checks below; exit 1 names each fault
    coherence.py lost      [--product] [ROOT] SNAPSHOT
                                                 every ruling a snapshot (an earlier inventory)
                                                 found is still in the register, by its words
    coherence.py --selftest

ROOT defaults to the current directory. Without --product it reads this rulebook; with it, a
product (Hemz OS's layout). A product carries a byte-identical copy of this file.

The register (REGISTER below) is the one home of his words: one entry per ruling,

    ## R-2026-11-09a · what it rules, in a few words
    Source: <link or path>
    Home: <FILE>#<heading or id> | spent: <why> | kept until his word
    > his words, whole

A rule page states the rule once, in plain lines, and cites the entry's id; the entry's Home
names the one place the rule lives, and that place cites the id back.

The checks, on the rule pages (RULE_PAGES):
1. One home. Every entry has a Source and a Home; a Home naming a page resolves to a page that
   cites the id; every id cited anywhere is in the register; ids are unique.
2. No orphan ruling. A line naming a ruling of his with a date cites an id in its paragraph.
3. His words once. No eight-word run of an entry's words appears on a rule page.
4. No rule twice. No fourteen-word run appears twice across the rule pages.
5. No superseded lines. No rule page says what used to be (SUPERSEDED): git keeps history.
6. Size line. No paragraph over PARA bytes, no section over SECTION bytes.
"""
import fnmatch
import glob
import json
import os
import re
import sys
import tempfile

RULEBOOK = {
    "register": "library/rulings.md",
    "pages": ("HOW-WE-BUILD.md", "README.md", "CHARTER.md", "RICH-DATA.md", "AGENTS.md", "library/*.md"),
    "not_pages": ("library/upgrade-log.md", "library/rulings.md"),
    "records": (),
    "homes": ("roadmap.json",),
    "sources": ("juku-library/*.md",),
}
PRODUCT = {
    "register": "RULINGS.md",
    "pages": ("FOUNDATIONS.md", "AGENTS.md", "PRODUCT.md", "MAP.md", "NAMES.md", "README.md",
              "00-brief.md", "01-spine.md", "design/*.md", "design-system.md"),
    "not_pages": ("RULINGS.md",),
    "records": ("MAP.md",),
    "homes": ("roadmap.json",),
    "sources": ("evidence/*chairman*", "evidence/*.md"),
}

PARA = 1_600       # bytes: one rule, read without wading through its history
SECTION = 12_000   # bytes: one heading's drill-down
QUOTE_RUN = 8      # words of his that make a quote
REPEAT_RUN = 14    # words that make a rule stated twice

MONTHS = "January|February|March|April|May|June|July|August|September|October|November|December"
MON = MONTHS + "|Jan|Feb|Mar|Apr|Jun|Jul|Aug|Sep|Sept|Oct|Nov|Dec"
DATE = re.compile(r"\b(\d{1,2})(?:\s*[–-]\s*\d{1,2})?\s+(%s)\.?(?:\s+(20\d\d))?\b|\b(20\d\d)-(\d\d)-(\d\d)\b" % MON)
MARKER = re.compile(
    r"\b(?:his|the Chairman'?s?|Chairman'?s|Dhayan'?s?)\s+(?:own\s+)?"
    r"(?:ruling|rulings|word|words|answer|answers|approval|ask|rule|decision|decisions|go-ahead|weigh-in|root|"
    r"instruction|direction|challenge|brief|reply|correction|change of direction|limit)\b"
    r"|\bthe Chairman,|\bapproved by the Chairman\b|\bhe ruled\b", re.I)
NEAR = 90          # a date this close after a marker dates it
ID = re.compile(r"\bR-20\d\d-\d\d-\d\d[a-z]{1,2}\b")
ENTRY = re.compile(r"^##\s+(R-20\d\d-\d\d-\d\d[a-z]{1,2})\b.*$", re.M)
QUOTE = re.compile(r"[\"“]([^\"”]{12,}?)[\"”]")
SUPERSEDED = re.compile(
    r"\bsupersed\w*|\bstood here before\b|\bformerly\b|\bpreviously\b|\bno longer\b|\bused to be\b"
    r"|\buntil now\b|\bwas replaced\b|\bin part by\b|\bthe old rule\b|\bretired (?:rule|line|wording)\b", re.I)
FENCE = re.compile(r"^```.*?^```\s*$", re.M | re.S)


def words(text):
    return re.findall(r"[a-z0-9£%']+", text.lower().replace("’", "'"))


def runs(ws, n):
    return {" ".join(ws[i:i + n]) for i in range(len(ws) - n + 1)}


def expand(root, patterns, exclude=()):
    out = []
    for p in patterns:
        for f in sorted(glob.glob(os.path.join(root, p))):
            rel = os.path.relpath(f, root)
            if os.path.isfile(f) and rel not in out and not any(fnmatch.fnmatch(rel, x) for x in exclude):
                out.append(rel)
    return out


def read(root, rel):
    with open(os.path.join(root, rel), encoding="utf-8", errors="replace") as fh:
        return fh.read()


def paragraphs(text):
    """(first line number, paragraph) for each blank-line paragraph outside code fences."""
    text = FENCE.sub(lambda m: "\n" * m.group(0).count("\n"), text)
    out, start, buf = [], None, []
    for n, line in enumerate(text.split("\n"), 1):
        if line.strip():
            if start is None:
                start = n
            buf.append(line)
        elif buf:
            out.append((start, "\n".join(buf)))
            start, buf = None, []
    if buf:
        out.append((start, "\n".join(buf)))
    return out


def sections(text):
    """(heading, body) per heading, at any level: each is an address a ticket can drill to."""
    out, head, buf = [], "(top)", []
    for line in text.split("\n"):
        if re.match(r"^#{1,6}\s", line):
            out.append((head, "\n".join(buf)))
            head, buf = line.strip("# ").strip(), []
        else:
            buf.append(line)
    out.append((head, "\n".join(buf)))
    return out


DECISION = re.compile(r"\bdecision\s+(\d{4})\b", re.I)


def dated_markers(para):
    """Each (marker, date, offset) in a paragraph: a marker of his with a date close after it,
    a date just before it, a decision number after it, or his words quoted straight after it."""
    found = []
    for m in MARKER.finditer(para):
        d = DATE.search(para, m.end(), m.end() + NEAR)
        before = [b for b in DATE.finditer(para, max(0, m.start() - 40), m.start())]
        dec = DECISION.search(para, m.end(), m.end() + 30)
        q = re.match(r"[^\"“\n]{0,25}[:,]?\s*\*?[\"“]", para[m.end():])
        if d:
            found.append((m.group(0), d.group(0), m.start()))
        elif before:
            found.append((m.group(0), before[-1].group(0), m.start()))
        elif dec:
            found.append((m.group(0), "decision " + dec.group(1), m.start()))
        elif q:
            found.append((m.group(0), "undated", m.start()))
    return found


def inventory(root, cfg):
    """Every dated ruling of his on a rule page, in the register, or in a source file."""
    items = []
    reg = cfg["register"]
    files = expand(root, cfg["pages"], cfg["not_pages"]) + expand(root, cfg["sources"])
    if os.path.isfile(os.path.join(root, reg)):
        files.append(reg)
    seen = set()
    for rel in files:
        if rel in seen:
            continue
        seen.add(rel)
        for line, para in paragraphs(read(root, rel)):
            for marker, date, at in dated_markers(para):
                q = QUOTE.search(para, at)
                items.append({"file": rel, "line": line, "marker": marker, "date": date,
                              "quote": q.group(1).strip() if q else None,
                              "ids": sorted(set(ID.findall(para)))})
    return items


def register_entries(text):
    """{id: {"source", "home", "words"}} and a list of faults, from the register's text."""
    entries, faults = {}, []
    heads = list(ENTRY.finditer(text))
    for i, m in enumerate(heads):
        body = text[m.end(): heads[i + 1].start() if i + 1 < len(heads) else len(text)]
        rid = m.group(1)
        if rid in entries:
            faults.append("register: %s appears twice; an id is one ruling" % rid)
        src = re.search(r"^Source:\s*(\S.*)$", body, re.M)
        home = re.search(r"^Home:\s*(\S.*)$", body, re.M)
        said = "\n".join(l[1:].strip() for l in body.split("\n") if l.startswith(">"))
        if not src:
            faults.append("register: %s has no 'Source:' line" % rid)
        if not home:
            faults.append("register: %s has no 'Home:' line" % rid)
        if not said.strip():
            faults.append("register: %s holds none of his words (a '> ' line)" % rid)
        entries[rid] = {"source": src and src.group(1).strip(), "home": home and home.group(1).strip(), "words": said}
    return entries, faults


def check(root, cfg):
    faults = []
    pages = expand(root, cfg["pages"], cfg["not_pages"])
    reg = cfg["register"]
    if not os.path.isfile(os.path.join(root, reg)):
        return ["the register '%s' is missing: it is the one home of his words" % reg]
    entries, f = register_entries(read(root, reg))
    faults += f
    texts = {p: read(root, p) for p in pages}
    homes = {h: read(root, h) for h in expand(root, cfg["homes"])}

    # 1. One home.
    for rid, e in entries.items():
        home = e["home"] or ""
        if re.match(r"(?i)^(spent:\s*\S|kept until his word)", home):
            continue
        target = home.split("#", 1)[0].strip().strip("`")
        if target not in texts and target not in homes:
            faults.append("%s: its Home '%s' is not a rule page, a roadmap, 'spent: <why>' or 'kept until his word'" % (rid, home))
        elif rid not in (texts.get(target) or homes.get(target)):
            faults.append("%s: its Home is %s, which does not cite it" % (rid, target))
    for p, t in list(texts.items()) + list(homes.items()):
        for rid in sorted(set(ID.findall(t))):
            if rid not in entries:
                faults.append("%s cites %s, which is not in %s" % (p, rid, reg))

    # 2. No orphan ruling.
    for p, t in texts.items():
        for line, para in paragraphs(t):
            for marker, date, _ in dated_markers(para):
                if not ID.search(para):
                    faults.append("%s:%d: '%s, %s' is a ruling of his with no register id; his words go to %s, "
                                  "the page cites the id" % (p, line, marker, date, reg))
                    break

    # 3. His words once.
    quoted = {}
    for rid, e in entries.items():
        for r in runs(words(e["words"]), QUOTE_RUN):
            quoted.setdefault(r, rid)
    for p, t in texts.items():
        for line, para in paragraphs(t):
            hit = next((quoted[r] for r in runs(words(para), QUOTE_RUN) if r in quoted), None)
            if hit:
                faults.append("%s:%d repeats words of %s; they live in %s alone, cite the id" % (p, line, hit, reg))

    # 4. No rule twice. A records page (a map of jobs, each in the same fields) is held by its own
    # check, and its fields repeat by design: it is read for his words and orphans, not for this.
    prose = {p: t for p, t in texts.items() if p not in cfg["records"]}
    where = {}
    for p, t in prose.items():
        for line, para in paragraphs(t):
            if para.lstrip().startswith("|"):
                continue
            for r in runs(words(para), REPEAT_RUN):
                if r in where and where[r] != (p, line):
                    faults.append("%s:%d states again what %s:%d says (\"%s …\"); one home, the other points" %
                                  (p, line, where[r][0], where[r][1], " ".join(r.split()[:8])))
                    break
                where.setdefault(r, (p, line))

    # 5. No superseded lines. 6. Size line, on prose pages.
    for p, t in texts.items():
        for line, para in paragraphs(t):
            m = SUPERSEDED.search(para)
            if m:
                faults.append("%s:%d says '%s': delete what was replaced, git keeps it" % (p, line, m.group(0)))
            if p in prose and len(para.encode()) > PARA and not para.lstrip().startswith("|"):
                faults.append("%s:%d: a paragraph of %d bytes, over %d; split it or cut its history" %
                              (p, line, len(para.encode()), PARA))
        for head, body in (sections(t) if p in prose else ()):
            if len(body.encode()) > SECTION:
                faults.append("%s, section '%s': %d bytes, over %d; split it into headings a task can drill into" %
                              (p, head[:60], len(body.encode()), SECTION))
    return faults


def lost(root, cfg, snapshot):
    """Rulings an earlier inventory found whose words are no longer in the register."""
    reg_path = os.path.join(root, cfg["register"])
    if not os.path.isfile(reg_path):
        return ["the register '%s' is missing" % cfg["register"]]
    with open(reg_path, encoding="utf-8") as fh:
        held = " ".join(words(fh.read()))
    out = []
    with open(snapshot, encoding="utf-8") as fh:
        for raw in fh:
            item = json.loads(raw)
            q = item.get("quote")
            if not q:
                continue
            pieces = [p for p in re.split(r"…|\.\.\.|\[[^\]]*\]", q) if len(words(p)) >= 4]
            if any(" ".join(words(p)) not in held for p in pieces):
                out.append("%s:%s (%s, %s): \"%s\" is not in %s" %
                           (item["file"], item["line"], item["marker"], item["date"], q[:90], cfg["register"]))
    return out


def selftest():
    bad = []
    with tempfile.TemporaryDirectory() as d:
        def put(rel, text):
            os.makedirs(os.path.dirname(os.path.join(d, rel)) or d, exist_ok=True)
            with open(os.path.join(d, rel), "w", encoding="utf-8") as fh:
                fh.write(text)
        cfg = dict(PRODUCT)
        reg = ("# Rulings\n\n## R-2026-11-09a · voice\nSource: x\nHome: FOUNDATIONS.md#F3\n"
               "> every staff action reachable by words typed or spoken in any language\n")
        put("RULINGS.md", reg)
        put("FOUNDATIONS.md", "# Foundations\n\n**F3 Voice Native.** Every action has a spoken path (R-2026-11-09a).\n")
        if check(d, cfg):
            bad.append("a clean product fails: %s" % check(d, cfg))
        cases = [
            ("FOUNDATIONS.md", "# F\n\nVoice (his ruling, 9 November 2026).\n", "no register id"),
            ("FOUNDATIONS.md", "# F\n\nF3 (R-2026-11-09a): every staff action reachable by words typed or spoken.\n",
             "repeats words of R-2026-11-09a"),
            ("FOUNDATIONS.md", "# F\n\nF3 (R-2026-11-09a). This superseded the old till.\n", "says 'superseded'"),
            ("FOUNDATIONS.md", "# F\n\nF3 (R-2026-11-09b).\n", "not in RULINGS.md"),
            ("FOUNDATIONS.md", "# F\n\nNothing cites it.\n", "does not cite it"),
            ("FOUNDATIONS.md", "# F\n\nF3 (R-2026-11-09a). " + "word " * 400 + "\n", "a paragraph of"),
        ]
        for rel, text, want in cases:
            put(rel, text)
            got = check(d, cfg)
            if not any(want in g for g in got):
                bad.append("expected '%s', got %s" % (want, got))
        put("FOUNDATIONS.md", "# F\n\nF3 (R-2026-11-09a).\n")
        twice = "a shop sets its own hourly rate minimum charges and extras through the product with no code at all"
        put("AGENTS.md", "# A\n\n" + twice + ".\n")
        put("NAMES.md", "# N\n\n" + twice + ".\n")
        if not any("states again" in g for g in check(d, cfg)):
            bad.append("a rule stated twice passes")
        os.remove(os.path.join(d, "NAMES.md"))
        put("RULINGS.md", reg + "\n## R-2026-11-09a · again\nSource: y\nHome: spent: done\n> twice\n")
        if not any("appears twice" in g for g in check(d, cfg)):
            bad.append("a duplicate id passes")
        put("RULINGS.md", reg)
        put("PRODUCT.md", "# P\n\nThe first sale (his word, 28 October 2026: \"the smallest version another shop would pay for\").\n")
        inv = inventory(d, cfg)
        snap = os.path.join(d, "snap.jsonl")
        with open(snap, "w") as fh:
            fh.write("\n".join(json.dumps(i) for i in inv))
        if not any(i["quote"] and "smallest version" in i["quote"] for i in inv):
            bad.append("the inventory misses a dated, quoted ruling: %s" % inv)
        if not lost(d, cfg, snap):
            bad.append("a ruling whose words left the pages and never reached the register is not reported lost")
        put("RULINGS.md", reg + "\n## R-2026-10-28a · first sale\nSource: z\nHome: spent: moved\n"
            "> the smallest version another shop would pay for\n")
        if lost(d, cfg, snap):
            bad.append("a ruling moved to the register is reported lost: %s" % lost(d, cfg, snap))
    for b in bad:
        print("selftest FAIL:", b)
    print("coherence.py selftest: %s" % ("ok" if not bad else "%d failing" % len(bad)))
    return 1 if bad else 0


def main(argv):
    if argv[:1] == ["--selftest"]:
        return selftest()
    if not argv or argv[0] not in ("inventory", "check", "lost"):
        print(__doc__)
        return 2
    cmd, rest = argv[0], argv[1:]
    cfg = PRODUCT if "--product" in rest else RULEBOOK
    rest = [a for a in rest if a != "--product"]
    root = rest[0] if rest and cmd != "lost" or len(rest) > 1 else "."
    if cmd == "inventory":
        for item in inventory(root, cfg):
            print(json.dumps(item, ensure_ascii=False))
        return 0
    faults = check(root, cfg) if cmd == "check" else lost(root, cfg, rest[-1])
    for f in faults:
        print("FAIL:", f)
    print("coherence.py %s: %s" % (cmd, "ok" if not faults else "%d fault(s)" % len(faults)))
    return 1 if faults else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
