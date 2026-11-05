#!/usr/bin/env python3
"""The job ticket: what a successor reads, and nothing else (library/session-changeover.md,
*The ticket*; his ruling, 5 November 2026, 11:07, on #363: "Slim boot. A session loads one
start page plus only what its job names").

A ticket is a block in the standing task's words, which each handover replaces whole:

  Ticket:
  - how-we-build:library/session-changeover.md#After a wait
  - hemz:AGENTS.md
  - hemz:roadmap.json#P62
  - hemz:PRODUCT.md#5

Each line names a file, by `repo:path` or a path from the working directory, and after `#`
an address in it: in markdown, a heading (its text, or its start up to a word break; a
leading section sign is ignored) running to the next heading as high, else a paragraph
opening in bold with it, else a line whose first cell or item is it; in JSON, a top-level
key, else the object anywhere whose "id", "key" or "name" is it. No address is the whole
file. The block ends at the first line that is not an item.

  ticket.py read [--repo NAME=DIR ...] ADDRESS       print one piece
  ticket.py check [--repo NAME=DIR ...] [--product NAME] FILE
                                                      every piece resolves, the total fits
  ticket.py --selftest

`check` fails a piece that does not resolve, a path outside its repository, a total over
CAP tokens (bytes / 4, rounded up: an estimate a check can repeat, never a session's real
size, which the size hook reads), and, with --product, a ticket without that product's
`AGENTS.md` whole (decision 0015 keeps it read whole). Too big: the outgoing session splits
the job; the successor is never handed the excess. Exit 0 passes; 1 names each fault.
"""
import json
import os
import re
import sys
import tempfile

CAP = 40_000   # tokens a ticket may hand a successor: ~45k harness + this, under ~90k boot (#363)
ITEM = re.compile(r"^\s*[-*]\s+(\S.*?)\s*$")


def tokens(text):
    return (len(text.encode("utf-8")) + 3) // 4


def split(entry):
    path, _, address = entry.partition("#")
    repo, sep, rest = path.partition(":")
    if not sep or "/" in repo:
        repo, rest = "", path
    return repo, rest.strip(), address.strip()


def locate(repo, path, repos):
    if repo and repo not in repos:
        raise LookupError(f"no repository named '{repo}' (give --repo {repo}=DIR)")
    root = os.path.realpath(repos.get(repo, os.getcwd()))
    if not path or os.path.isabs(path):
        raise LookupError(f"'{path}' is not a path inside a repository")
    full = os.path.realpath(os.path.join(root, path))
    if os.path.commonpath([root, full]) != root:
        raise LookupError(f"'{path}' leaves its repository")
    if not os.path.isfile(full):
        raise LookupError(f"no file '{path}'" + (f" in '{repo}'" if repo else ""))
    return full


def norm(s):
    return re.sub(r"\s+", " ", s.replace("§", "").replace("*", "")).strip().lower()


def starts(text, address):
    a = norm(address)
    t = norm(text)
    return t == a or (t.startswith(a) and not t[len(a)].isalnum())


def md_piece(text, address):
    lines = text.split("\n")
    fence = False
    heads = []
    for i, line in enumerate(lines):
        if line.lstrip().startswith("```"):
            fence = not fence
        m = None if fence else re.match(r"^(#{1,6})\s+(.*)$", line)
        if m:
            heads.append((i, len(m.group(1)), m.group(2)))
    for n, (i, level, title) in enumerate(heads):
        if starts(title, address):
            end = next((j for j, lv, _ in heads[n + 1:] if lv <= level), len(lines))
            return "\n".join(lines[i:end]).rstrip() + "\n"
    paras = re.split(r"\n\s*\n", text)
    for p in paras:
        m = re.match(r"^\s*\*\*(.+?)\*\*", p)
        if m and starts(m.group(1), address):
            return p.strip() + "\n"
    for line in lines:
        cell = re.match(r"^\s*(?:\||[-*]|\d+\.)\s*([^|]*?)\s*(?:\||$|\s)", line)
        if cell and cell.group(1) and norm(cell.group(1)) == norm(address):
            return line.strip() + "\n"
    raise LookupError(f"no heading, bold paragraph or line '{address}'")


def json_piece(text, address):
    data = json.loads(text)
    if isinstance(data, dict) and address in data:
        return json.dumps({address: data[address]}, indent=1, ensure_ascii=False) + "\n"
    stack = [data]
    while stack:
        node = stack.pop()
        if isinstance(node, dict):
            if any(node.get(k) == address for k in ("id", "key", "name")):
                return json.dumps(node, indent=1, ensure_ascii=False) + "\n"
            stack.extend(reversed(list(node.values())))
        elif isinstance(node, list):
            stack.extend(reversed(node))
    raise LookupError(f"no key or item '{address}'")


def piece(entry, repos):
    repo, path, address = split(entry)
    full = locate(repo, path, repos)
    with open(full, encoding="utf-8") as f:
        text = f.read()
    if not address:
        return text
    if full.endswith(".json"):
        return json_piece(text, address)
    return md_piece(text, address)


def ticket_lines(words):
    lines = words.split("\n")
    for i, line in enumerate(lines):
        if line.strip() == "Ticket:":
            out = []
            for item in lines[i + 1:]:
                m = ITEM.match(item)
                if not m:
                    break
                out.append(m.group(1).strip("`"))
            return out
    return None


def check(words, repos, product=None):
    faults, total, report = [], 0, []
    entries = ticket_lines(words)
    if entries is None:
        return ["no 'Ticket:' line"], ""
    if not entries:
        faults.append("the ticket lists nothing")
    for e in entries:
        try:
            n = tokens(piece(e, repos))
            total += n
            report.append(f"  {n:>7,}  {e}")
        except (LookupError, ValueError, UnicodeDecodeError) as err:
            faults.append(f"'{e}': {err}")
    if product and f"{product}:AGENTS.md" not in entries:
        faults.append(f"no '{product}:AGENTS.md' (whole): a product's AGENTS.md is read whole (decision 0015)")
    report.append(f"  {total:>7,}  total (cap {CAP:,})")
    if total > CAP:
        faults.append(f"{total:,} tokens is over the {CAP:,} cap: split the job")
    return faults, "\n".join(report)


def args(argv):
    repos, product, rest = {}, None, []
    it = iter(argv)
    for a in it:
        if a == "--repo":
            name, _, d = next(it, "").partition("=")
            if not name or not d:
                raise SystemExit("--repo NAME=DIR")
            repos[name] = d
        elif a == "--product":
            product = next(it, None)
        else:
            rest.append(a)
    return repos, product, rest


def selftest():
    bad = 0
    with tempfile.TemporaryDirectory() as root:
        rule = os.path.join(root, "rule")
        prod = os.path.join(root, "prod")
        os.makedirs(os.path.join(rule, "notes"))
        os.makedirs(prod)
        open(os.path.join(rule, "notes", "page.md"), "w").write(
            "# Page\n\nIntro.\n\n**After a wait** (his ruling). Stays subscribed.\n\n"
            "**Afterwards** another.\n\n## Part two\n\nBody two.\n\n### Deeper\n\nStill two.\n\n## Part three\n\nThree.\n")
        open(os.path.join(prod, "AGENTS.md"), "w").write("# Agents\n\nRules.\n")
        open(os.path.join(prod, "PRODUCT.md"), "w").write(
            "# Product\n\n## §5 Prices\n\nFive.\n\n## §50 Other\n\nFifty.\n\n```\n## 6 not a heading\n```\n")
        open(os.path.join(prod, "MAP.md"), "w").write("# Map\n\n| K10 | Take an order | first |\n| K1 | Other | second |\n")
        json.dump({"_what_this_is": "order", "items": [{"id": "P62", "next": "build"}, {"id": "P6", "next": "no"}]},
                  open(os.path.join(prod, "roadmap.json"), "w"))
        open(os.path.join(prod, "big.md"), "w").write("x" * (4 * CAP + 8))
        repos = {"how-we-build": rule, "hemz": prod}

        def read(entry):
            try:
                return piece(entry, repos)
            except (LookupError, ValueError) as err:
                return f"ERR {err}"

        cases = [
            ("bold paragraph", read("how-we-build:notes/page.md#After a wait"), lambda r: r.startswith("**After a wait**") and "Afterwards" not in r),
            ("heading runs to the next as high", read("how-we-build:notes/page.md#Part two"), lambda r: "Still two" in r and "Three" not in r),
            ("section sign, word break", read("hemz:PRODUCT.md#5"), lambda r: "Five" in r and "Fifty" not in r),
            ("fenced text is no heading", read("hemz:PRODUCT.md#6"), lambda r: r.startswith("ERR")),
            ("map row by its id", read("hemz:MAP.md#K10"), lambda r: "Take an order" in r and "Other" not in r),
            ("roadmap item by id", read("hemz:roadmap.json#P62"), lambda r: '"build"' in r and '"no"' not in r),
            ("roadmap top-level key", read("hemz:roadmap.json#_what_this_is"), lambda r: '"order"' in r),
            ("whole file", read("hemz:AGENTS.md"), lambda r: r.startswith("# Agents")),
            ("missing address refused", read("hemz:PRODUCT.md#9"), lambda r: r.startswith("ERR")),
            ("missing file refused", read("hemz:NOPE.md"), lambda r: r.startswith("ERR")),
            ("unknown repository refused", read("myst:AGENTS.md"), lambda r: r.startswith("ERR")),
            ("leaving the repository refused", read("hemz:../rule/notes/page.md"), lambda r: r.startswith("ERR")),
            ("absolute path refused", read("hemz:" + os.path.join(prod, "AGENTS.md")), lambda r: r.startswith("ERR")),
        ]
        good = "Ticket:\n- hemz:AGENTS.md\n- hemz:roadmap.json#P62\n- how-we-build:notes/page.md#After a wait\n\nRest of the words.\n- not an item of the ticket: nope.md\n"
        tickets = [
            ("a good ticket passes", check(good, repos, "hemz")[0], lambda f: f == []),
            ("no Ticket line fails", check("Words only.", repos)[0], lambda f: f != []),
            ("an empty ticket fails", check("Ticket:\n\nNothing.", repos)[0], lambda f: f != []),
            ("an unresolved piece fails", check("Ticket:\n- hemz:PRODUCT.md#9\n", repos)[0], lambda f: f != []),
            ("over the cap fails", check("Ticket:\n- hemz:big.md\n", repos)[0], lambda f: any("cap" in x for x in f)),
            ("a product ticket without its AGENTS.md fails", check("Ticket:\n- hemz:roadmap.json#P62\n", repos, "hemz")[0], lambda f: any("AGENTS.md" in x for x in f)),
            ("a product AGENTS.md by address is not whole", check("Ticket:\n- hemz:AGENTS.md#Agents\n", repos, "hemz")[0], lambda f: any("AGENTS.md" in x for x in f)),
        ]
        for name, result, ok in cases + tickets:
            if ok(result):
                print(f"ok   {name}")
            else:
                print(f"FAIL {name}: {result!r}")
                bad = 1
    return bad


def main(argv):
    if argv[:1] == ["--selftest"]:
        return selftest()
    repos, product, rest = args(argv)
    if len(rest) == 2 and rest[0] == "read":
        try:
            sys.stdout.write(piece(rest[1], repos))
            return 0
        except (LookupError, ValueError) as err:
            print(f"FAIL: {err}", file=sys.stderr)
            return 1
    if len(rest) == 2 and rest[0] == "check":
        with open(rest[1], encoding="utf-8") as f:
            faults, report = check(f.read(), repos, product)
        print(report)
        for x in faults:
            print(f"FAIL: {x}")
        return 1 if faults else 0
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
