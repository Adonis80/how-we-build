#!/usr/bin/env python3
"""The style lock (his ruling, 5 November 2026, 11:07, on how-we-build#363:
"A machine check on every build flags boxes, cards or borders round content
(a highlighted control excepted, one hairline above a total); the reviewer
compares the rest against the agreed reference build").

Its rule's one home is library/juku-style.md, *Always / Never*: content on the
ground, never in boxes, cards, panels, borders or row dividers; the only filled
thing is the (i) sheet, and controls carry none (his picks of 12 November 2026,
#408: a selected choice is gold text and a gold edge, no fill).

  style-lock.py build PATH...   a product's screens: its own stylesheets and markup
  style-lock.py kit [ROOT]      the kit itself: library/juku-style.css loads nothing
                                from outside, and every value table (b) of
                                library/juku-style.md names is in it
  style-lock.py --selftest

`build` reads each file under PATH (.css .scss .html .htm .jsx .tsx .vue .svelte
.astro, and a script: .js .mjs .cjs .ts), skipping node_modules, .git, build output, a `*-library/` folder (papers
and pictures, never the build) and the kit's own stylesheet, which a product reads
from this repository and never copies. It flags, naming file, line and rule:
  - a border, outline or box-shadow declared in a stylesheet or an inline style on
    anything that is not a control, or the hairline: a top border on a total (a
    rule whose styled element names .j-sum or "total");
  - a background fill on anything but the page's ground (html, body, :root,
    .j-page, .j-screen) and the (i) sheet (.j-info): a control's fill included,
    save a press's flash (:active) and a line it draws (::before, ::after);
  - a utility class drawing the same (border, ring, shadow, outline, divide on
    anything but a control; bg- on anything);
  - an element dressed as a control it is not: the kit's choice classes (.j-btn,
    .j-pick, .j-icon-btn, .j-tab) or its typed line (.j-field) on an element that
    is no control, and a choice class on a typed field (a text input or a
    textarea), which is drawn as .j-field.
A control is button, input, select, textarea, option, an element whose role is a
control's, the kit's .j-btn, .j-pick, .j-icon-btn, .j-field, .j-tab and .j-tabs
(the tabs' hairline is the control's own), and a :focus or :focus-visible,
aria-pressed, aria-selected or aria-checked state. A selector is judged by the
element it styles, its last compound, never by a control it sits in, beside, or
names in :not() or :has(). Zero, none and transparent draw
nothing and pass. A script is read for the markup it writes: the tags in its
strings and template strings (JSX in a .js file too), judged as markup, and the
classes and styles it puts on an element it makes with createElement (className,
classList.add, setAttribute("class"), .style.border), judged as that tag; on an
element it did not make, which the lock cannot name, only a fill is flagged. What
the lock cannot see (a box drawn by an image or a canvas, a class name a script
computes, a border a script puts on an element it did not make) is the
reviewer's, against the agreed reference build. Exit 0 passes; 1 names each fault.
"""
import os
import re
import sys

SCRIPT_EXTS = (".js", ".mjs", ".cjs", ".ts")
EXTS = (".css", ".scss", ".html", ".htm", ".jsx", ".tsx", ".vue", ".svelte", ".astro") + SCRIPT_EXTS
SKIP_DIRS = {"node_modules", ".git", "dist", "build", "out", ".next", ".svelte-kit", "coverage"}
KIT_FILE = "juku-style.css"

DRAWS = re.compile(r"^(border(-[a-z-]+)?|outline(-[a-z-]+)?|box-shadow|background(-color|-image)?)$")
NOT_DRAWN = re.compile(r"radius|collapse|spacing|^background-(position|size|repeat|attachment|origin|clip|blend-mode)")
FILL = re.compile(r"^background(-color|-image)?$")
NOTHING = re.compile(r"^\s*(0|0px|none|transparent|inherit|initial|unset|revert|0\s+none|none\s+0)\s*(!important)?\s*$", re.I)
CONTROL = re.compile(
    r"(^|[\s>+~(,])(button|input|select|textarea|option)\b"
    r"|\[role=['\"]?(button|tab|switch|radio|checkbox|option|slider|menuitem\w*|combobox|spinbutton)\b"
    r"|\.j-(btn|pick|icon-btn|field|tabs?)\b"
    r"|:focus(-visible|-within)?\b"
    r"|\[aria-(pressed|selected|checked)")
GROUND = re.compile(r"^\s*(html|body|:root|\.j-page|\.j-screen|\.j-info|\[data-theme[^\]]*\]|:root\[data-theme[^\]]*\])\s*$")
PASSING = re.compile(r":active\b|::?(before|after)\b")  # a press's flash, a control's drawn line
TOTAL = re.compile(r"\.j-sum\b|total", re.I)
HAIRLINE = re.compile(r"^border-(top|block-start)(-(width|style|color))?$")
CONTROL_TAGS = {"button", "input", "select", "textarea", "option"}
CHOICE_CLASSES = {"j-btn", "j-pick", "j-icon-btn", "j-tab"}
DRESS_CLASSES = CHOICE_CLASSES | {"j-field"}
TYPED_INPUTS = {"", "text", "number", "email", "tel", "search", "url", "password", "date", "time", "datetime-local", "month", "week"}
CONTROL_ROLE = re.compile(r"^(button|tab|switch|radio|checkbox|option|slider|menuitem\w*|combobox|spinbutton)$")
UTILITY = re.compile(r"^(border(-[trblxyse])?(-\d+|-\[[^\]]+\])?|border-(solid|dashed|dotted|double)"
                     r"|border(-[trblxyse])?-(?!(collapse|separate|spacing\S*)$)[a-z]+(-\d+)?(/\d+)?|ring(?!-offset)(-\d+|-\[[^\]]+\]|-[a-z]+(-\d+)?)?"
                     r"|shadow(-[a-z0-9]+|-\[[^\]]+\])?|outline(?!-offset)(-\d+|-[a-z]+(-\d+)?)?|divide-[xy](-\d+)?"
                     r"|bg-(?!(cover|contain|auto|center|top|bottom|left|right|no-repeat|repeat\S*|fixed|local|scroll|clip-\S+|origin-\S+|blend-\S+)$).+)$")
UTILITY_NOTHING = re.compile(r"^(border(-[trblxyse])?-(0|none|transparent)|ring-0|shadow-none|outline-none|outline-0"
                             r"|divide-none|bg-(transparent|none|inherit))$")


def _lineno(text, pos):
    return text.count("\n", 0, pos) + 1


def _blank_comments(text, kind):
    """Comments become spaces of the same length, so line numbers hold."""
    pats = [r"/\*.*?\*/"]
    if kind == "markup":
        pats.append(r"<!--.*?-->")
    for p in pats:
        text = re.sub(p, lambda m: re.sub(r"[^\n]", " ", m.group(0)), text, flags=re.S)
    return text


def _split_top(text, seps):
    """Split on any of seps outside brackets and parentheses."""
    out, depth, cur = [], 0, ""
    for c in text:
        depth += c in "([" and 1 or (c in ")]" and -1 or 0)
        if depth == 0 and c in seps:
            out.append(cur)
            cur = ""
        else:
            cur += c
    out.append(cur)
    return [x.strip() for x in out]


def _subject(sel):
    """The compound a rule styles: the selector's last, past every combinator, with
    :not(), :has() and :focus-within dropped, since none of them names what is styled."""
    last = [x for x in _split_top(sel, " >+~") if x][-1:] or [""]
    out, i, s = "", 0, last[0]
    while i < len(s):
        m = re.match(r":(not|has)\(", s[i:])
        if m:
            depth, j = 0, i
            while j < len(s):
                depth += s[j] == "(" and 1 or (s[j] == ")" and -1 or 0)
                j += 1
                if depth == 0 and s[j - 1] == ")":
                    break
            i = j
            continue
        out += s[i]
        i += 1
    return out.replace(":focus-within", "")


def _decl_faults(prop, value, selector):
    """The fault a declaration makes on that selector, or None. Each selector in a list
    is judged by its subject alone, the element the rule draws on."""
    prop = prop.strip().lower()
    if not DRAWS.match(prop) or NOT_DRAWN.search(prop) or NOTHING.match(value):
        return None
    parts = [_subject(s) for s in _split_top(selector, ",") if s]
    if FILL.match(prop):
        if parts and all(GROUND.match(s) for s in parts):
            return None
        if parts and any(CONTROL.search(s) and not PASSING.search(s) for s in parts):
            return f"a fill on a control ({prop}: {value.strip()} on '{selector.strip()}'); controls carry none"
        if parts and all(CONTROL.search(s) for s in parts):
            return None
    elif parts and all(CONTROL.search(s) for s in parts):
        return None
    if HAIRLINE.match(prop) and parts and all(TOTAL.search(s) for s in parts):
        return None
    what = "a fill" if FILL.match(prop) else ("a shadow" if prop == "box-shadow" else "a border")
    return f"{what} on content ({prop}: {value.strip()} on '{selector.strip()}')"


def lock_css(text, name):
    """Walk a stylesheet's rules, nested @media and the like included."""
    faults = []
    text = _blank_comments(text, "css")
    stack = []  # selectors of open blocks
    i, start = 0, 0
    while i < len(text):
        c = text[i]
        if c == "{":
            stack.append(text[start:i].strip())
            start = i + 1
        elif c == "}" or c == ";":
            chunk = text[start:i]
            sel = next((s for s in reversed(stack) if s and not s.startswith("@")), "")
            if ":" in chunk and sel and not chunk.strip().startswith("@"):
                prop, _, value = chunk.partition(":")
                if not prop.strip().startswith("--"):
                    why = _decl_faults(prop, value, sel)
                    if why:
                        faults.append(f"{name}:{_lineno(text, start + len(chunk) - len(chunk.lstrip()))}: {why}")
            if c == "}" and stack:
                stack.pop()
            start = i + 1
        i += 1
    return faults


TAG = re.compile(r"<([a-zA-Z][\w.-]*)((?:[^>\"'{]|\"[^\"]*\"|'[^']*'|\{(?:[^{}]|\{[^{}]*\})*\})*)>", re.S)
ATTR = lambda n: re.compile(r"(?:^|\s)" + n + r"\s*=\s*(\"[^\"]*\"|'[^']*'|\{(?:[^{}]|\{[^{}]*\})*\})", re.S)
CLASS_ATTR = ATTR(r"(?:class|className)")
STYLE_ATTR = ATTR("style")
ROLE_ATTR = ATTR("role")
TYPE_ATTR = ATTR("type")
JS_KEY = re.compile(r"\b(border\w*|outline\w*|boxShadow|background(?:Color|Image)?)\s*:\s*(\"[^\"]*\"|'[^']*'|`[^`]*`|[\w.]+)")


def _camel(k):
    return re.sub(r"[A-Z]", lambda m: "-" + m.group(0).lower(), k)


def _tokens(classes):
    return re.findall(r"[\w:\[\]/.#%()-]+", classes)


def _class_faults(name, line, tag, control, typed, toks):
    """The faults a class list makes on one element. tag None is an element a script dresses without
    making it: what it is cannot be read, so only a fill, a fault on anything, is flagged."""
    faults = []
    known = tag is not None
    dressed = sorted(DRESS_CLASSES & set(toks))
    if known and dressed and not control:
        faults.append(f"{name}:{line}: <{tag}> dressed as a control it is not ('{' '.join(dressed)}'); a choice is a button, a typed line an input")
    chose = sorted(CHOICE_CLASSES & set(toks))
    if control and chose and typed:
        faults.append(f"{name}:{line}: a typed field drawn as a choice ('{' '.join(chose)}' on <{tag}>); a typed line is .j-field")
    on = f"<{tag}>" if known else "an element a script dresses"
    for tok in toks:
        base = tok.split(":")[-1]
        if UTILITY.match(base) and not UTILITY_NOTHING.match(base) and ((known and not control) or base.startswith("bg-")):
            what = "a fill on a control" if control else "a box drawn" if known else "a fill"
            faults.append(f"{name}:{line}: {what} by a utility class ('{tok}' on {on})")
    return faults


JS_STR = r"(\"[^\"\n]*\"|'[^'\n]*'|`[^`]*`)"
JS_VAR = r"\b([A-Za-z_$][\w$]*)"
MADE = re.compile(JS_VAR + r"\s*=\s*document\.createElement\(\s*['\"`]([\w-]+)['\"`]")
CLASS_SETS = (re.compile(JS_VAR + r"\.className\s*\+?=\s*" + JS_STR),
              re.compile(JS_VAR + r"\.setAttribute\(\s*['\"`]class['\"`]\s*,\s*" + JS_STR),
              re.compile(JS_VAR + r"\.classList\.(?:add|toggle)\(([^)]*)\)"))
STYLE_SET = re.compile(JS_VAR + r"\.style\.(border\w*|outline\w*|boxShadow|background(?:Color|Image)?)\s*=\s*" + JS_STR)


def lock_script(text, name):
    """A script: the markup it writes in its strings (and JSX in a .js file), read as markup, then the
    classes and styles it puts on an element by name (className, classList.add, setAttribute("class"),
    .style.border). An element the same file makes with createElement is judged as that tag; any other
    is unknown, and only a fill is flagged on it."""
    faults = lock_markup(text.replace('\\"', ' "').replace("\\'", " '"), name)   # an escaped quote, same length
    text = _blank_comments(text, "css")
    made = {m.group(1): m.group(2).lower() for m in MADE.finditer(text)}
    for pat in CLASS_SETS:
        for m in pat.finditer(text):
            tag = made.get(m.group(1))
            toks = [t for lit in re.findall(JS_STR, m.group(2)) for t in _tokens(lit[1:-1])]
            faults += _class_faults(name, _lineno(text, m.start()), tag, tag in CONTROL_TAGS, tag == "textarea", toks)
    for m in STYLE_SET.finditer(text):
        tag, prop = made.get(m.group(1)), _camel(m.group(2))
        if (tag is None or tag in CONTROL_TAGS) and not FILL.match(prop):
            continue   # a control's border passes; an unknown element's is the reviewer's
        why = _decl_faults(prop, m.group(3)[1:-1], tag or "an element a script styles")
        if why:
            faults.append(f"{name}:{_lineno(text, m.start())}: a script's style, {why}")
    return faults


def lock_markup(text, name):
    faults = []
    text = _blank_comments(text, "markup")
    for m in TAG.finditer(text):
        tag, attrs = m.group(1).lower(), m.group(2)
        role = ROLE_ATTR.search(attrs)
        role = role.group(1).strip("\"'{}` ") if role else ""
        control = tag in CONTROL_TAGS or bool(CONTROL_ROLE.match(role))
        if tag == "style":
            end = text.find("</style>", m.end())
            if end > 0:
                body = text[m.end():end]
                pad = "\n" * (_lineno(text, m.end()) - 1)
                faults += lock_css(pad + body, name)
            continue
        line = _lineno(text, m.start())
        cl = CLASS_ATTR.search(attrs)
        ty = TYPE_ATTR.search(attrs)
        ty = ty.group(1).strip("\"'{}` ").lower() if ty else ""
        typed = tag == "textarea" or (tag == "input" and ty in TYPED_INPUTS)
        faults += _class_faults(name, line, tag, control, typed, _tokens(cl.group(1)) if cl else [])
        if control:
            continue
        st = STYLE_ATTR.search(attrs)
        if st:
            raw = st.group(1)
            if raw.startswith("{"):
                for k, v in JS_KEY.findall(raw):
                    why = _decl_faults(_camel(k), v.strip("\"'`"), tag)
                    if why:
                        faults.append(f"{name}:{line}: inline style, {why}")
            else:
                for decl in raw.strip("\"'").split(";"):
                    if ":" in decl:
                        p, _, v = decl.partition(":")
                        why = _decl_faults(p, v, tag)
                        if why:
                            faults.append(f"{name}:{line}: inline style, {why}")
    return faults


def lock_file(path, text):
    if path.endswith((".css", ".scss")):
        return lock_css(text, path)
    if path.endswith(SCRIPT_EXTS):
        return lock_script(text, path)
    return lock_markup(text, path)


def build(paths):
    faults, seen = [], 0
    for root in paths:
        walk = [(os.path.dirname(root), [], [os.path.basename(root)])] if os.path.isfile(root) else os.walk(root)
        for d, dirs, files in walk:
            dirs[:] = sorted(x for x in dirs if x not in SKIP_DIRS and not x.endswith("-library"))
            for f in sorted(files):
                if not f.endswith(EXTS) or f == KIT_FILE:
                    continue
                p = os.path.join(d, f)
                try:
                    with open(p, encoding="utf-8") as fh:
                        text = fh.read()
                except (OSError, UnicodeDecodeError) as e:
                    faults.append(f"{p}: unreadable ({e.__class__.__name__}); the lock passes nothing it cannot read")
                    continue
                seen += 1
                faults += lock_file(p, text)
    return faults, seen


VALUE = re.compile(r"#[0-9a-fA-F]{3,8}\b|rgba\([^)]*\)|cubic-bezier\([^)]*\)|-?\d*\.?\d+(?:px|ms|em|s)\b")


def kit(page_text, css_text):
    """The kit loads nothing from outside, and its page's table (b) repeats only its values."""
    faults = []
    bare = _blank_comments(css_text, "css")
    if re.search(r"@import\b", bare, re.I):
        faults.append("library/juku-style.css: an @import; the kit loads nothing from outside (products load it live)")
    for u in re.findall(r"url\(\s*['\"]?([^)'\"]*)", bare, re.I):
        if not u.startswith("data:") and not u.startswith("#"):
            faults.append(f"library/juku-style.css: url({u}); the kit loads nothing from outside (products load it live)")
    if "## (b) The parts" not in page_text or "## (c)" not in page_text:
        return faults + ["library/juku-style.md: no '## (b) The parts' table before '## (c)'"]
    table = page_text.split("## (b) The parts", 1)[1].split("## (c)", 1)[0]
    squashed = re.sub(r"\s", "", bare.lower())
    rows = 0
    for line in table.splitlines():
        cells = line.split("|")
        if len(cells) < 4 or not line.startswith("| ") or cells[1].strip() in ("Element", "") or set(cells[1].strip()) <= set("-"):
            continue
        rows += 1
        for v in VALUE.findall(cells[2].replace("\u2212", "-")):
            if re.sub(r"\s", "", v.lower()) not in squashed:
                faults.append(f"library/juku-style.md: table (b), '{cells[1].strip()}' names {v}, which library/juku-style.css does not hold")
    if rows == 0:
        faults.append("library/juku-style.md: table (b) has no rows")
    return faults


def selftest():
    bad = 0

    def expect(label, faults, n):
        nonlocal bad
        ok = (len(faults) == n) if n is not None else bool(faults)
        if not ok:
            bad += 1
            print(f"FAIL selftest: {label}: expected {n if n is not None else 'some'} fault(s), got {faults}")

    css = lambda t: lock_css(t, "t.css")
    mk = lambda t: lock_markup(t, "t.tsx")
    # Passes: tokens only, controls, the hairline, the ground, nothing drawn.
    expect("tokens only", css(":root{--j-gold:#ffb01f;--j-ground:#08090a}"), 0)
    expect("a control's border", css("button{border:1px solid var(--j-line)}"), 0)
    expect("the kit's selected choice", css(".j-btn.is-on{color:var(--j-gold);border-color:var(--j-gold-edge)}"), 0)
    expect("the typed line", css(".j-field{border-bottom:1px solid var(--j-line)}.j-field:focus{border-bottom-color:var(--j-gold-edge)}"), 0)
    expect("the tabs' hairline", css(".j-tabs{border-bottom:1px solid var(--j-line)}"), 0)
    expect("the (i) sheet's fill", css(".j-info{background:var(--j-surface)}"), 0)
    expect("a focus ring", css(".j-screen button:focus-visible{outline:1px solid var(--j-gold)}"), 0)
    expect("a role=tab", css("[role=tab][aria-selected=true]{border-bottom:1px solid}"), 0)
    expect("the hairline on .j-sum", css(".j-sum{border-top:1px solid var(--j-line-soft)}"), 0)
    expect("the hairline on a total", css(".grand-total{border-top:var(--j-hair) solid var(--j-line-soft)}"), 0)
    expect("the ground", css("body{background:#08090a}.j-page{background-color:var(--j-ground)}"), 0)
    expect("nothing drawn", css(".x{border:0;box-shadow:none;outline:none;background:transparent}"), 0)
    expect("a comment", css("/* .card{border:1px solid} */ .a{color:red}"), 0)
    # Flags: boxes, cards, borders, dividers, fills and shadows round content.
    expect("a card", css(".card{border:1px solid #333;border-radius:12px}"), 1)
    expect("a panel's fill", css(".panel{background:#111}"), 1)
    expect("a row divider", css(".row + .row{border-bottom:1px solid var(--j-line)}"), 1)
    expect("a shadow", css(".x{box-shadow:0 1px 2px #000}"), 1)
    expect("a border under a total", css(".j-sum{border-bottom:1px solid}"), 1)
    expect("a box round a total", css(".total{border:1px solid}"), 1)
    expect("a border on the ground", css("body{border:1px solid}"), 1)
    expect("an outline on content", css("div{outline:1px solid}"), 1)
    expect("a top border off a total", css(".x{border-top:1px solid}"), 1)
    expect("a mixed list", css(".a, button{border:1px solid}"), 1)
    expect("a fill under a selected choice", css(".j-btn.is-on{background:rgba(255,176,31,.2)}"), 1)
    expect("a control's panel fill", css("button{background:#0e0f11}"), 1)
    expect("a press's flash and the tabs' gold line", css("button.j-row:active{background:var(--j-line-soft)}.j-tabs::after{background:var(--j-gold)}"), 0)
    expect("inside @media", css("@media (min-width:600px){.c{border:1px solid}}"), 1)
    expect("content inside a control", css("button .card{border:1px solid}"), 1)
    expect("content beside a choice", css(".j-pick + .note{background:#111}"), 1)
    expect("a container of a focused control", css(".panel:focus-within{outline:1px solid}"), 1)
    expect("content named by :not(button)", css(".card:not(button){border:1px solid}"), 1)
    expect("content that has an input", css(".row:has(input){border:1px solid}"), 1)
    expect("a box inside a total", css(".total .card{border-top:1px solid}"), 1)
    expect("a control inside content", css(".card button{border:1px solid}"), 0)
    expect("the kit's press", css(".j-screen button:not(:disabled):active{background:var(--j-line-soft)}"), 0)
    expect("the kit's class overridden", css(".j-row{border-bottom:1px solid}"), 1)
    expect("a line number", css("\n\n.c{\n  border:1px solid}"), 1)
    if css("\n\n.c{\n  border:1px solid}") and not css("\n\n.c{\n  border:1px solid}")[0].startswith("t.css:4:"):
        bad += 1
        print("FAIL selftest: the line number is not the declaration's:", css("\n\n.c{\n  border:1px solid}"))
    # Markup: utility classes, inline styles, <style> blocks.
    expect("a utility card", mk('<div className="rounded-lg border p-4">'), 1)
    expect("a utility fill and shadow", mk('<section class="bg-zinc-900 shadow-md">'), 2)
    expect("a hover-only border", mk('<li className="hover:border-white/10">'), 1)
    expect("a utility control's border", mk('<button className="border">'), 0)
    expect("a utility control's fill", mk('<button className="border bg-zinc-900">'), 1)
    expect("a div dressed as a choice", mk('<div class="j-btn j-pick">Hem</div>'), 1)
    expect("a span dressed as a typed line", mk('<span className="j-field">'), 1)
    expect("a text box drawn as a choice", mk('<input class="j-btn j-pick" type="text">'), 1)
    expect("an untyped input drawn as a choice", mk('<input className="j-btn j-pick">'), 1)
    expect("a textarea drawn as a choice", mk('<textarea class="j-pick">'), 1)
    expect("a typed line", mk('<input class="j-field" type="number" inputmode="decimal">'), 0)
    expect("a choice", mk('<button class="j-btn is-on">Hem</button>'), 0)
    expect("a radio choice", mk('<input type="radio" class="j-pick">'), 0)
    expect("a tab", mk('<div class="j-tabs" role="tablist"><button role="tab" class="j-tab">'), 0)
    expect("a role=button control", mk('<div role="button" className="border">'), 0)
    expect("utilities that draw nothing", mk('<div className="bg-cover bg-center bg-no-repeat bg-clip-text border-collapse outline-offset-2 ring-offset-2">'), 0)
    expect("utility nothing", mk('<div className="border-0 bg-transparent shadow-none">'), 0)
    expect("an inline border", mk('<div style="border:1px solid red">'), 1)
    expect("an inline JSX border", mk("<div style={{ border: '1px solid', color: 'red' }}>"), 1)
    expect("an inline JSX nothing", mk("<div style={{ borderWidth: 0 }}>"), 0)
    expect("a <style> card", mk("<html>\n<style>\n.card{border:1px solid}\n</style>"), 1)
    expect("a markup comment", mk('<!-- <div class="border"> --><p>x</p>'), 0)
    # Scripts: the markup a script writes, and the classes and styles it puts on what it makes.
    js = lambda t: lock_file("t.js", t)
    expect("a card in a template string", js('root.innerHTML = `<div class="card border p-4">${x}</div>`;'), 1)
    expect("a card in an escaped string", js('el.innerHTML = "<section class=\\"bg-zinc-900\\">";'), 1)
    expect("JSX in a .js file", js('export const A = () => <div className="rounded border">x</div>;'), 1)
    expect("a div dressed as a choice by a script", js("html += '<div class=\"j-btn j-pick\">Hem</div>';"), 1)
    expect("an inline border a script writes", js('row.innerHTML = `<p style="border:1px solid red">`;'), 1)
    expect("a <style> block a script writes", js('head.innerHTML = `<style>.card{border:1px solid}</style>`;'), 1)
    expect("a made div given a border class", js('const d = document.createElement("div");\nd.className = "card border";'), 1)
    expect("a made div given classes one by one", js("const d = document.createElement('div');\nd.classList.add('p-4', 'shadow-md', 'bg-zinc-900');"), 2)
    expect("a made span dressed as a typed line", js('var s = document.createElement("span"); s.setAttribute("class", "j-field");'), 1)
    expect("a made div's style", js('const d = document.createElement("div"); d.style.border = "1px solid"; d.style.boxShadow = "none";'), 1)
    expect("a fill on an element the script did not make", js('el.classList.add("bg-zinc-900"); el.style.background = "#111";'), 2)
    expect("a border on an element the script did not make is the reviewer's", js('el.className = "border"; el.style.border = "1px solid";'), 0)
    expect("a made button's border", js('const b = document.createElement("button"); b.className = "j-btn is-on border"; b.style.border = "1px solid";'), 0)
    expect("a made button's fill", js('const b = document.createElement("button"); b.className = "bg-zinc-900";'), 1)
    expect("a made textarea drawn as a choice", js('const t = document.createElement("textarea"); t.className = "j-pick";'), 1)
    expect("the kit's own classes written by a script", js('root.innerHTML = `<button class="j-row"><span class="j-name">${n}</span></button><div class="j-row j-sum">`;'), 0)
    expect("script that compares, not markup", js('if (a < b && c > d) { x = "border"; }\n/* <div class="border"> */'), 0)
    if js('\n\nroot.innerHTML = `\n<div class="border">`;') != ['t.js:4: a box drawn by a utility class (\'border\' on <div>)']:
        bad += 1
        print("FAIL selftest: a script's fault does not name its line:", js('\n\nroot.innerHTML = `\n<div class="border">`;'))
    # The walk: the kit's own file, node_modules and a product's library are not the build.
    import tempfile
    with tempfile.TemporaryDirectory() as d:
        for rel, body in {"src/app.css": ".j-sum{border-top:1px solid}", "src/juku-style.css": ".card{border:1px solid}",
                          "node_modules/x/a.css": ".card{border:1px solid}", "hemz-library/design/a.html": '<div class="border">',
                          "src/A.tsx": '<div className="card border">',
                          "src/draw.js": "root.innerHTML = '<p class=\"j-name\">x</p>';"}.items():
            os.makedirs(os.path.join(d, os.path.dirname(rel)), exist_ok=True)
            with open(os.path.join(d, rel), "w") as fh:
                fh.write(body)
        f, seen = build([d])
        expect("the walk", f, 1)
        if seen != 3:
            bad += 1
            print(f"FAIL selftest: the walk read {seen} files, not 3 (a script is read)")
    # The kit: nothing from outside; table (b) holds only the stylesheet's values.
    here = os.path.dirname(os.path.abspath(__file__))
    page = os.path.join(here, "..", "library", "juku-style.md")
    sheet = os.path.join(here, "..", "library", "juku-style.css")
    if os.path.exists(page) and os.path.exists(sheet):
        p, s = open(page, encoding="utf-8").read(), open(sheet, encoding="utf-8").read()
        expect("the kit as it stands", kit(p, s), 0)
        expect("an @import in the kit", kit(p, s + "\n@import url(x.css);"), 2)
        expect("a url() in the kit", kit(p, s + "\n.a{background:url(https://example.com/k?)}"), 1)
        expect("a data: url in the kit", kit(p, s + "\n.a{background:url(data:image/png;base64,AA)}"), 0)
        expect("a table value off the sheet", kit(p.replace("| 64px tall", "| 65px tall", 1), s), 1)
    else:
        bad += 1
        print("FAIL selftest: library/juku-style.md and library/juku-style.css are not beside product-reads/")
    print("selftest ok" if not bad else f"selftest: {bad} failed")
    return 1 if bad else 0


def main(argv):
    if argv[1:] == ["--selftest"]:
        return selftest()
    if len(argv) >= 3 and argv[1] == "build":
        faults, seen = build(argv[2:])
        if seen == 0:
            faults.append("no stylesheet or markup found under " + " ".join(argv[2:]) + "; the lock passes nothing it did not read")
    elif len(argv) in (2, 3) and argv[1] == "kit":
        root = argv[2] if len(argv) == 3 else os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
        try:
            page = open(os.path.join(root, "library", "juku-style.md"), encoding="utf-8").read()
            sheet = open(os.path.join(root, "library", "juku-style.css"), encoding="utf-8").read()
        except OSError as e:
            print(f"FAIL: the kit is not whole: {e}")
            return 1
        faults = kit(page, sheet)
    else:
        print(__doc__)
        return 2
    for f in faults:
        print("FAIL:", f)
    if not faults:
        print("ok")
    return 1 if faults else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
