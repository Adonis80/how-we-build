#!/usr/bin/env python3
"""What the rulebook's reviewer is shown beside the diff, on every class of change (decisions 0014 and 0018).

    context.py CLASS CHANGED_NUL DIFF_FILE PAGES_OUT     run in the head's checkout
    context.py unit PATH#NAME < FILE                     print one unit of a file, or exit 1
    context.py part PATH DIFF_FILE < FILE                print a touched file's touched parts, or exit 1

Every read, risky or not, is given a selection, never the repository whole
(his ruling, 9 October 2026, decision 0018: "Yes, I want the full read
narrowing switched on now."). A risky change is still a class: it picks
reviewer-risky, at the effort the registry holds for it (decision 0019), and
carries the registry. Each read is given
HOW-WE-BUILD.md; the README's *Where each topic lives* table; each file the
change touches, whole, or past WHOLE bytes the sections its hunks fall in; the
partners PARTNERS names, both ways, a large one as the sections that name a
touched file; every page that names a touched file by its path, as its
passages that name one (#235, fix 3); and, on a
`code` or `risky` read, the registry. Everything else is named with its size
and left out, so a reader that needed it says so (`needs-context`), naming a
file or one unit of one (`path#heading`, `path#function`, `path#step name`),
and is read once more with what can be found of what it asked for, the rest
marked (#187), or not at all when nothing can be; a second shortfall is signed.

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
    # JSON has no blank lines, so it was one unit and a one-line change to a
    # generated file of records, one a line, carried all of it (Hemz-OS#153's
    # read of 7db24d1: 131 KB of hosting/hemzy-knows.json for two lines). A line
    # opening at the margin starts a unit; an indented document keeps one.
    if path.endswith(".json"):
        return [i for i, l in enumerate(lines) if l[:1] not in ("", " ", "\t", "\r", "\n", "]", "}")]
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


# ONE DEFINITION OF A SCRIPT (#217, agreed 17 October 2026): `page.html#itemEdit`
# is that function whole, or nothing. Hemz-OS#159's read asked for a function of
# a 998 KB page, the selector knew no names in it, and the read was signed
# incomplete. A script is walked once, lexically: strings, templates and their
# `${}`, comments, regexes and every bracket, so a definition is found in code
# only, at any depth, with its true extent. On anything it is unsure of, a name
# defined twice, or a form it does not know (a method, a property), it gives no
# unit and says why in one line, and the file stands whole as before (#187).
# A `/` after `)` is a regex only when that `)` closed an `if`, `while`, `for`,
# `for await` or `with` head, division only when it closed anything else known,
# and unsure otherwise; after `}` it is always unsure.
SCRIPTS = (".js", ".mjs", ".html", ".htm")
_WORD = re.compile(r"(?:[^\W\d]|\$)(?:\w|\$)*")
_RESERVED = frozenset(
    "break case catch class const continue debugger default delete do else enum export extends finally for "
    "function if import in instanceof let new return static super switch this throw try typeof var void while "
    "with yield await async of get set null true false".split())
_VALUES = frozenset(("this", "super", "null", "true", "false", "import"))
# A `/` after one of these words starts a regex; a `(` after one opens an expression.
_BEFORE_REGEX = frozenset(("return", "typeof", "instanceof", "in", "new", "delete", "void", "throw", "case", "do",
                           "else"))
_HEADS = frozenset(("if", "while", "for", "with"))
# A line break inside an initializer: after one of these words the line goes on.
_GOES_ON = frozenset(("in", "instanceof", "typeof", "new", "void", "delete", "await"))
_PUNCT = ("...", "?.", "=>", "++", "--")
_CONTINUES = frozenset(". ?. , = + - * / % < > & | ^ ? : ;".split())


class Unsure(Exception):
    """The walk could not settle something; carries its one-line reason."""


def _after_dot(toks, k):
    return k > 0 and toks[k - 1][0] == "p" and toks[k - 1][1] in (".", "?.")


def _paren_kind(toks):
    """What a `(` opens, by the token before it: a control head, an expression, or unknown."""
    if not toks:
        return "expr"
    kind, val = toks[-1][0], toks[-1][1]
    if kind != "id" or _after_dot(toks, len(toks) - 1):
        return "expr"
    if val in _HEADS:
        return "head"
    if val == "await" and len(toks) > 1 and toks[-2][:2] == ("id", "for"):
        return "head"
    if val not in _RESERVED or val in _VALUES or val in _BEFORE_REGEX or val in ("await", "async", "yield", "of"):
        return "expr"
    return "unknown"


def _slash_is_regex(toks, at):
    """Does a `/` start a regex, given the tokens before it? Raises Unsure when that is not known."""
    if not toks:
        return True
    kind, val = toks[-1][0], toks[-1][1]
    if kind in ("lit", "num"):
        return False
    if kind == "id":
        if _after_dot(toks, len(toks) - 1) or val not in _RESERVED or val in _VALUES:
            return False
        if val in _BEFORE_REGEX:
            return True
        raise Unsure("a / after the word %s at line %d" % (val, at))
    if kind == "close":
        if val == ")":
            if toks[-1][5] == "head":
                return True
            if toks[-1][5] == "expr":
                return False
            raise Unsure("a / after a ) that closed neither a condition nor an expression, line %d" % at)
        if val == "}":
            raise Unsure("a / after } at line %d: a regex or a division" % at)
        return False
    if val in ("++", "--"):
        raise Unsure("a / after %s at line %d" % (val, at))
    return True


def tokens(src, base=0, line_of=None):
    """[(kind, value, start, end, newline before, paren kind)]: one script, walked once.

    kind is id, num, lit (a string, a regex, or a template with no `${}`), p
    (punctuation), open or close (`(`, `[`, `{`, a template's backtick, `${`).
    Raises Unsure on anything it cannot settle, and when the brackets do not
    return to none.
    """
    where = line_of
    line_of = (lambda i: where(base + i)) if where else (lambda i: src.count("\n", 0, i) + 1)
    toks, stack, i, n, nl = [], [], 0, len(src), False
    if src.startswith("#!"):
        i = src.find("\n") if "\n" in src else n

    def emit(kind, val, a, b, pk=None):
        nonlocal nl
        toks.append((kind, val, base + a, base + b, nl, pk))
        nl = False

    def template(j):
        """Walk a template's text from j: to its closing backtick, or into a `${`. Returns where code resumes."""
        while j < n:
            c = src[j]
            if c == "\\":
                j += 2
                continue
            if c == "`":
                stack.pop()
                emit("close", "`", j, j + 1)
                return j + 1
            if src.startswith("${", j):
                stack.append(("${", None))
                emit("open", "${", j, j + 2)
                return j + 2
            j += 1
        raise Unsure("a template literal never closes, from line %d" % line_of(i))

    while i < n:
        c = src[i]
        if c in " \t\r\n\f\v ﻿  ":
            nl = nl or c in "\n\r  "
            i += 1
            continue
        if src.startswith("//", i):
            j = src.find("\n", i)
            i = n if j < 0 else j
            continue
        if src.startswith("/*", i):
            j = src.find("*/", i + 2)
            if j < 0:
                raise Unsure("a block comment never closes, from line %d" % line_of(i))
            nl = nl or "\n" in src[i:j]
            i = j + 2
            continue
        if src.startswith("<!--", i) or (src.startswith("-->", i) and (nl or not toks)):
            raise Unsure("an HTML-style comment in a script at line %d" % line_of(i))
        if c in "'\"":
            j = i + 1
            while j < n and src[j] != c:
                if src[j] == "\\":
                    j += 1
                elif src[j] in "\n\r":
                    raise Unsure("a string breaks its line at line %d" % line_of(i))
                j += 1
            if j >= n:
                raise Unsure("a string never closes, from line %d" % line_of(i))
            emit("lit", c, i, j + 1)
            i = j + 1
            continue
        if c == "`":
            stack.append(("`", None))
            emit("open", "`", i, i + 1)
            i = template(i + 1)
            continue
        if c in "([{":
            pk = _paren_kind(toks) if c == "(" else None
            stack.append((c, pk))
            emit("open", c, i, i + 1, pk)
            i += 1
            continue
        if c in ")]}":
            want = {")": ("(",), "]": ("[",), "}": ("{", "${")}[c]
            if not stack or stack[-1][0] not in want:
                raise Unsure("a %s that closes nothing open at line %d" % (c, line_of(i)))
            opener, pk = stack.pop()
            emit("close", c, i, i + 1, pk)
            i = template(i + 1) if opener == "${" else i + 1
            continue
        if c == "/":
            if _slash_is_regex(toks, line_of(i)):
                j, cls = i + 1, False
                while j < n:
                    d = src[j]
                    if d == "\\":
                        j += 2
                        continue
                    if d in "\n\r":
                        raise Unsure("a regex breaks its line at line %d" % line_of(i))
                    if cls:
                        cls = d != "]"
                    elif d == "[":
                        cls = True
                    elif d == "/":
                        break
                    j += 1
                if j >= n:
                    raise Unsure("a regex never closes, from line %d" % line_of(i))
                j += 1
                while j < n and (src[j].isalnum() or src[j] in "_$"):
                    j += 1
                emit("lit", "/", i, j)
                i = j
                continue
            emit("p", "/", i, i + 1)
            i += 1
            continue
        if c.isdigit() or (c == "." and i + 1 < n and src[i + 1].isdigit()):
            j = i + 1
            while j < n and (src[j].isalnum() or src[j] in "._"):
                j += 1
            emit("num", src[i:j], i, j)
            i = j
            continue
        if c == "#" and i + 1 < n and _WORD.match(src, i + 1):
            m = _WORD.match(src, i + 1)
            emit("id", "#" + m.group(0), i, m.end())
            i = m.end()
            continue
        m = _WORD.match(src, i)
        if m:
            emit("id", m.group(0), i, m.end())
            i = m.end()
            continue
        if c == "\\":
            raise Unsure("an escaped name at line %d" % line_of(i))
        p = next((q for q in _PUNCT if src.startswith(q, i) and not (q == "?." and src[i + 2:i + 3].isdigit())), c)
        emit("p", p, i, i + len(p))
        i += len(p)
    if stack:
        raise Unsure("brackets never return to none: a %s stays open" % stack[-1][0])
    return toks


def _matches(toks):
    """{index of an opening bracket: index of the one that closes it}."""
    out, stack = {}, []
    for k, t in enumerate(toks):
        if t[0] == "open":
            stack.append(k)
        elif t[0] == "close":
            out[stack.pop()] = k
    return out


def definitions(toks, match, line_of):
    """[(name, first token, last token, or None and why when unsure)]: every definition, at any depth.

    `function NAME(`, `async function NAME(`, `function* NAME(`; `class NAME`;
    and each `NAME = ` a `const`, `let` or `var` declares, the declaration
    whole being its unit. A method, a property or a destructuring is none.
    """
    out = []
    for k, t in enumerate(toks):
        if t[0] != "id" or _after_dot(toks, k):
            continue
        try:
            if t[1] == "function":
                j = k + 1
                if j < len(toks) and toks[j][:2] == ("p", "*"):
                    j += 1
                if j + 1 < len(toks) and toks[j][0] == "id" and toks[j + 1][:2] == ("open", "("):
                    name = toks[j][1]
                    start = k - 1 if k and toks[k - 1][:2] == ("id", "async") and not t[4] else k
                    body = match[j + 1] + 1
                    if body >= len(toks) or toks[body][:2] != ("open", "{"):
                        raise Unsure("function %s has no body where one belongs, line %d" % (name, line_of(t[2])))
                    out.append((name, start, match[body], None))
            elif t[1] == "class" and k + 1 < len(toks) and toks[k + 1][0] == "id" and toks[k + 1][1] != "extends":
                name = toks[k + 1][1]
                out.append((name, k, _class_end(toks, match, k + 2, name, line_of), None))
            elif t[1] in ("const", "let", "var") and k + 1 < len(toks) and toks[k + 1][0] in ("id", "open"):
                out.extend(_declared(toks, match, k, line_of))
        except Unsure as why:
            out.append((toks[k + 1][1] if t[1] == "class" else name, None, None, str(why)))
    return out


def _class_end(toks, match, k, name, line_of):
    """The `}` closing a class's body, its heading being only names, dots and bracketed groups."""
    start = k
    while k < len(toks):
        t = toks[k]
        if t[:2] == ("open", "{"):
            return match[k]
        if t[0] == "open":
            k = match[k] + 1
        elif t[0] == "id" or t[:2] in (("p", "."), ("p", "?.")):
            k += 1
        else:
            break
    raise Unsure("class %s has a heading the selector does not read, line %d" % (name, line_of(toks[start - 1][2])))


def _ender(toks, k):
    """Is token k one an expression can end on? None when that is not known (`++`, `yield`, ...)."""
    kind, val = toks[k][0], toks[k][1]
    if kind in ("lit", "num", "close"):
        return True
    if kind == "id":
        if _after_dot(toks, k) or val not in _RESERVED or val in _VALUES:
            return True
        return False if val in _GOES_ON else None
    return None if val in ("++", "--") else False


def _declared(toks, match, k, line_of, seen=None):
    """[(name, k, last token, None)] for each `NAME =` the declaration at token k makes.

    Its names are every `NAME =` at its own level that opens it or follows one
    of its commas. It ends at its `;` (before it, in a `for` heading), before a
    `}` closing what holds it, or at a line break the language ends it on:
    after a token an expression can end on, before one that cannot go on from
    it. A line break neither settles makes it unsure, and every name it was
    seen to make is given as unsure, never as a unit. Each name's token is
    added to `seen`.
    """
    seen = set() if seen is None else seen
    names, last, j, head = [], k, k + 1, k and toks[k - 1][:2] == ("open", "(") and toks[k - 1][5] == "head"
    try:
        while j < len(toks):
            t = toks[j]
            if (j == k + 1 or toks[j - 1][:2] == ("p", ",")) and t[0] == "id" and toks[j + 1:j + 2] \
                    and toks[j + 1][:2] == ("p", "="):
                names.append(t[1])
                seen.add(j)
            if t[4] and last != k:
                ends = _ender(toks, last)
                if ends is None:
                    raise Unsure("a line break after %s in a declaration, line %d" % (toks[last][1], line_of(t[2])))
                if ends and _ends_before(toks, j, line_of):
                    break
            if t[:2] == ("p", ";"):
                last = last if head else j
                break
            if t[0] == "close":
                if t[1] != "}":
                    raise Unsure("a declaration ends at a %s, line %d" % (t[1], line_of(t[2])))
                break
            if t[0] == "open":
                last = match[j]
                j = last + 1
                continue
            last = j
            j += 1
    except Unsure as why:
        # The names past where it was unsure are still its names: each `, NAME =`
        # at its level, up to a `;` or what closes it, more than it makes if anything.
        while j < len(toks) and toks[j][:2] != ("p", ";") and toks[j][0] != "close":
            if toks[j - 1][:2] == ("p", ",") and toks[j][0] == "id" and toks[j + 1:j + 2] \
                    and toks[j + 1][:2] == ("p", "="):
                names.append(toks[j][1])
                seen.add(j)
            j = match[j] + 1 if toks[j][0] == "open" else j + 1
        return [(n, None, None, str(why)) for n in names]
    return [(n, k, last, None) for n in names]


_NOT_METHODS = frozenset(("if", "for", "while", "switch", "catch", "with", "function"))


def other_forms(toks, match, line_of):
    """The names a script also gives in a form the selector does not give as a unit.

    A method or shorthand `NAME(…) {`; a property `NAME:` or `.NAME =` given
    a function, or `window.NAME =` given anything; or an
    assignment `NAME =` no declaration makes (#236's first read: a recognised
    definition beside one of these is not the only one). Counted loosely: a
    name in here that is none of them only costs a fallback.
    """
    declared, out = set(), set()
    for k, t in enumerate(toks):
        if t[0] == "id" and t[1] in ("const", "let", "var") and not _after_dot(toks, k) and k + 1 < len(toks) \
                and toks[k + 1][0] in ("id", "open"):
            _declared(toks, match, k, line_of, declared)
    for k, t in enumerate(toks[:-1]):
        if t[0] != "id":
            continue
        nxt, prev = toks[k + 1], toks[k - 1] if k else None
        # `exports.NAME = NAME;` and `{ NAME: NAME }` hand the definition on and make no other: the
        # value is the name alone, ended by `;`, `,`, a closing bracket, a line break or the script's
        # end. `NAME = NAME || …` or `NAME = NAME + 1` goes on, and is counted (#237's read).
        after = toks[k + 3] if k + 3 < len(toks) else None
        if nxt[:2] in (("p", "="), ("p", ":")) and toks[k + 2:k + 3] and toks[k + 2][:2] == ("id", t[1]) \
                and (after is None or after[4] or after[0] == "close" or after[:2] in (("p", ";"), ("p", ","))):
            continue
        given = toks[k + 2:k + 3] and (toks[k + 2][:2] in (("id", "function"), ("id", "async"), ("open", "("))
                                       or toks[k + 3:k + 4] and toks[k + 3][:2] == ("p", "=>"))
        if nxt[:2] == ("p", "=") and toks[k + 2:k + 3] and toks[k + 2][:2] != ("p", "=") and k not in declared:
            # A bare `NAME =` rebinds the name; `obj.NAME =` defines one when
            # given a function, or on the page's global (`window.NAME =`).
            if not _after_dot(toks, k) or given or (k > 1 and toks[k - 2][1] in ("window", "globalThis", "self")):
                out.add(t[1])
        elif nxt[:2] == ("p", ":") and prev is not None and prev[:2] in (("open", "{"), ("p", ",")) and given:
            out.add(t[1])
        elif nxt[:2] == ("open", "(") and t[1] not in _NOT_METHODS and not _after_dot(toks, k) \
                and toks[match[k + 1] + 1:match[k + 1] + 2] and toks[match[k + 1] + 1][:2] == ("open", "{") \
                and not (prev is not None and (prev[:2] == ("id", "function")
                                               or (prev[:2] == ("p", "*") and toks[k - 2][:2] == ("id", "function")))):
            out.add(t[1])
    return out


def _ends_before(toks, j, line_of):
    """After a line break that follows a token an expression can end on, does token j begin a new statement?"""
    kind, val = toks[j][0], toks[j][1]
    if kind == "id" and not _after_dot(toks, j):
        if val == "of":
            raise Unsure("a line break before of in a declaration, line %d" % line_of(toks[j][2]))
        return val not in ("in", "instanceof")
    if kind in ("lit", "num") or (kind == "open" and val == "{"):
        return True
    if kind == "p":
        if val in ("++", "--", "~") or (val == "!" and toks[j + 1:j + 2] and toks[j + 1][1] != "="):
            return True
        if val not in _CONTINUES and val != "!":
            raise Unsure("a line break before %s in a declaration, line %d" % (val, line_of(toks[j][2])))
    return False


def scripts_of(text, path):
    """[(offset, source)]: a file's JavaScript; for a page, the bodies of its inline scripts, never its markup."""
    if not path.endswith((".html", ".htm")):
        return [(0, text)]
    out, pos = [], 0
    opens = re.compile(r"<!--|<script\b([^>]*)>", re.I)
    while True:
        m = opens.search(text, pos)
        if not m:
            return out
        if m.group(0) == "<!--":
            j = text.find("-->", m.end())
            if j < 0:
                return out
            pos = j + 3
            continue
        close = re.compile(r"</script\s*>", re.I).search(text, m.end())
        if not close:
            raise Unsure("a <script> never closes, from line %d" % (text.count("\n", 0, m.start()) + 1))
        attrs = m.group(1)
        kind = re.search(r"""\btype\s*=\s*["']?([^"'\s>]*)""", attrs, re.I)
        if not re.search(r"\bsrc\s*=", attrs, re.I) and (not kind or kind.group(1).lower() in (
                "", "module", "text/javascript", "application/javascript")):
            out.append((m.end(), text[m.end():close.start()]))
        pos = close.end()


def script_unit(text, path, name):
    """(one definition of a script, whole, and None) or (None, why in one line)."""
    starts_at = [0] + [m.end() for m in re.finditer("\n", text)]

    def line_of(i):
        import bisect
        return bisect.bisect_right(starts_at, i)
    found, other = [], False
    try:
        for off, src in scripts_of(text, path):
            toks = tokens(src, off, line_of)
            match = _matches(toks)
            found += [(toks, d) for d in definitions(toks, match, line_of) if d[0] == name]
            other = other or name in other_forms(toks, match, line_of)
    except Unsure as why:
        return None, "unsure, so no unit: %s" % why
    if found and other:
        return None, ("that name is also given as a method, a property or an assignment: which one is meant is "
                      "not known")
    if len(found) != 1:
        return None, ("%d definitions of that name: which one is meant is not known" % len(found) if found else
                      "no definition of that name the selector knows (a function, a class, or a const, let or "
                      "var given a value)")
    toks, (_, a, b, why) = found[0]
    if why:
        return None, "unsure, so no unit: %s" % why
    # Its own lines when it has them to itself; else its exact span.
    s, e = toks[a][2], toks[b][3]
    head, tail = text.rfind("\n", 0, s) + 1, text.find("\n", e)
    tail = len(text) if tail < 0 else tail
    if text[head:s].strip() in ("", "export", "export default") and text[e:tail].strip() in ("", ";"):
        s, e = head, tail
    return text[s:e] + "\n", None


def unit(text, path, name):
    """The unit of a file a reader asked for by name (`path#name`), whole, or None when it has none."""
    return unit_and_why(text, path, name)[0]


def unit_and_why(text, path, name):
    """(the unit asked for, whole, and None), or (None, why it has none, in one line).

    A heading, a step's name or a definition's; a numbered section of a page by
    its number too (`PRODUCT.md#6` or `#§6`); a roadmap's item by its id
    (`roadmap.json#P48`), that item alone; and a script's function, class or
    declaration, in a `.js`, `.mjs` or a page's inline scripts (#217).
    """
    if path.endswith(SCRIPTS) and name != OPENING:
        return script_unit(text, path, name)
    got = _unit(text, path, name)
    return got, None if got is not None else "no unit by that name"


def _unit(text, path, name):
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
    spans = spans_of(text, path)
    # A unit named `opening` is that unit; only a file with none gives its opening.
    if name == OPENING and not any(n == OPENING for n, _, _ in spans):
        return next(("".join(lines[i:j]) for n, i, j in spans if n is None), None)
    for n, i, j in spans:
        if n is not None and (n == name or (number and re.match(r"§?\s?%s[.\s]" % re.escape(number.group(1)), n + " "))):
            return "".join(lines[i:j])
    # A record's lettered or numbered item, `- **H. Title.** …`, by its mark
    # (`DECISION-0016-….md#H`): that item and its own indented lines, up to the
    # first line not indented past it. A reader of a decision asks by the mark
    # the page cites it by, and a mark no heading carries left the re-read
    # unmet and the read incomplete (#181, rounds 4 to 6).
    if path.endswith(".md"):
        mark = re.compile(r"([ \t]*)[-*]\s+\*\*%s[.):]" % re.escape(name))
        for i, line in enumerate(lines):
            m = mark.match(line)
            if m:
                depth = len(m.group(1))
                j = next((k for k in range(i + 1, len(lines))
                          if lines[k].strip() and len(lines[k]) - len(lines[k].lstrip()) <= depth), len(lines))
                return "".join(lines[i:j]).rstrip("\n") + "\n"
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


# A PAGE THAT NAMES A TOUCHED FILE (#235, fix 3, agreed 18 October 2026) is
# given its passages that name one, never the page whole: #230's read carried
# seven library pages whole, 33 KB, for a sentence or two each. A passage is a
# paragraph with the list, table or indented lines that follow it, and a fenced
# block whole; it is given whole or not at all, never cut to fit a size. Its
# page's opening (the title and the scope line under it) and every heading a
# passage sits under, one a level, come with it. The rest of the page is the reader's to ask
# for, the page whole, by its path.
PASSAGES = "%s, its passages naming the change's files only (of %d bytes; the page whole may be asked for as %s)"
_FOLLOWS = re.compile(r"\s+\S|\s*(?:[-*+]|\d+[.)])\s|\s*\|")


def passages(text, touched):
    """A page's passages that name a touched file, with its opening and every heading above them, as one text.

    None when the page names no touched file, or when those passages are the
    whole page, which is then given whole as before.
    """
    lines = text.splitlines(keepends=True)
    blocks, cur, fence = [], [], None
    for i, line in enumerate(lines):
        mark = re.match(r"\s*(```|~~~)", line)
        if fence:
            cur.append(i)
            fence = None if mark and mark.group(1) == fence else fence
            continue
        if not line.strip():
            if cur:
                blocks.append(cur)
            cur = []
            continue
        if re.match(r"#+\s", line):
            if cur:
                blocks.append(cur)
            blocks.append([i])
            cur = []
            continue
        if not cur and blocks and not re.match(r"#+\s", lines[blocks[-1][-1]]) and _FOLLOWS.match(line):
            # A list, table or indented line after a blank belongs to the paragraph above it.
            cur = blocks.pop()
        cur.append(i)
        if mark:
            fence = mark.group(1)
    if cur:
        blocks.append(cur)
    heads = [k for k, b in enumerate(blocks) if re.match(r"#+\s", lines[b[0]])]
    body = [k for k in range(len(blocks)) if k not in heads]
    named = [k for k in body if any(t in "".join(lines[i] for i in blocks[k]) for t in touched)]
    if not named:
        return None
    keep = set(range(body[0] + 1))
    for k in named:
        keep.add(k)
        # Every heading it sits under, one a level (#291's first read): a
        # passage under a `###` keeps its `##` too, which can change what it governs.
        level = None
        for h in reversed([h for h in heads if h < k]):
            depth = len(re.match(r"#+", lines[blocks[h][0]]).group(0))
            if level is None or depth < level:
                keep.add(h)
                level = depth
    if len(keep) == len(blocks):
        return None
    # Two kept blocks with only blank lines between them are next to each other, never a gap.
    kept = sorted(i for k in keep for i in blocks[k])
    blank = [i for a, b in zip(kept, kept[1:]) if not "".join(lines[a + 1:b]).strip() for i in range(a + 1, b)]
    return _joined(lines, set(kept + blank))


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
            found = passages(text, touched)
            if found is None:
                give(f, text)
            else:
                give_part(f, "passages", PASSAGES % (f, len(text.encode("utf-8")), f), found)
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
    """`context.py unit PATH#NAME < FILE`: the one unit asked for, whole, on stdout; exit 1 when the file has none.

    Why it has none goes to stderr in one line, for the reader's marker: fixed
    words and line numbers, at most one name or token of the file beside them,
    never a line of it. The marker goes into the reader's prompt alone; a
    change that printed it to a public log would print that name too.
    """
    path, _, name = want.partition("#")
    text = sys.stdin.read()
    got, why = unit_and_why(text, path, name) if name else (None, "no unit named")
    if got is None:
        print(why, file=sys.stderr)
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
