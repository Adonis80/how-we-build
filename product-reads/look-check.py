#!/usr/bin/env python3
"""The look check: the kit's self-check run on a rendered preview (library/juku-style.md,
(e); his ruling of 5 November 2026 on how-we-build#363, the style lock, held
on the rendered build: "Locks, not reminders.").

The style lock reads a product's source; this reads what a phone and a desktop are
actually shown. It opens a preview in Playwright's Chromium, phone (390 x 844) and
desktop (1280 x 800), saves a screenshot of each in DIR for the builder (nothing yet sends
them to the reviewer), and fails, naming
each fault, where the rendered screen breaks the kit:

  - a box: an element in the content (inside .j-stage) that is no control and not
    the (i) sheet, drawn with a visible border, outline, shadow or fill;
  - a line off a total: a visible top border anywhere but on a total (.j-sum), or a
    total without one;
  - colour off its meaning: a figure holding a currency sign not in the money colour
    (--j-gold), or a figure holding a unit of measure (cm mm in m ") not in the
    measure colour (--j-turq);
  - no (i): no control in the bar (.j-bar) labelled i or info;
  - a phrase the product forbids on screen (--never TEXT, repeatable: Hemz passes
    "Tell Hemzy");
  - no crumb, or an empty one, in the level shown;
  - the working off the foot: the level shown has no .j-foot, or its bottom is
    above three quarters of the viewport;
  - no zoom behind: after tapping the first row that drills in (button.j-row), no
    level is .is-behind-1, or it is not scaled below 1. A screen with no such row
    says so and passes this one.

  look-check.py URL OUTDIR [--never TEXT]...
  look-check.py --selftest

A product's verify runs it on its preview, where Playwright is installed. The
selftest renders the kit's own stylesheet in fixtures; where no browser can be
launched it says so plainly and checks only what needs none. Exit 0 passes; 1
names each fault.
"""
import os
import re
import sys

PHONE = {"width": 390, "height": 844}
DESKTOP = {"width": 1280, "height": 800}
CURRENCY = "£$€"
UNIT = re.compile(r"\d\s*(cm|mm|in|m|\")(?![a-z])", re.I)

# Runs in the page; returns a list of faults. Controls draw their own edges.
PROBE = r"""
([never, currency, unitSrc]) => {
  const faults = [];
  const unit = new RegExp(unitSrc, 'i');
  const root = getComputedStyle(document.querySelector('.j-screen') || document.documentElement);
  const probe = (v) => { const s = document.createElement('span'); s.style.color = v;
    document.body.appendChild(s); const c = getComputedStyle(s).color; s.remove(); return c; };
  const gold = probe(root.getPropertyValue('--j-gold').trim() || 'rgb(1,2,3)');
  const turq = probe(root.getPropertyValue('--j-turq').trim() || 'rgb(1,2,3)');
  // A row that drills in is a button, but it is content: it and all inside it are checked.
  const isControl = (el) => { const c = el.closest('button,input,select,textarea,option,[role=button],[role=tab],[role=switch],[role=radio],[role=checkbox],[role=option],.j-btn,.j-pick,.j-icon-btn,.j-field,.j-tabs,.j-info');
    return !!c && !c.classList.contains('j-row'); };
  const visible = (el) => { const r = el.getBoundingClientRect(); const s = getComputedStyle(el);
    return r.width > 0 && r.height > 0 && s.visibility !== 'hidden' && s.display !== 'none'; };
  const name = (el) => el.tagName.toLowerCase() + (el.className && typeof el.className === 'string' ? '.' + el.className.trim().split(/\s+/).join('.') : '');
  const level = document.querySelector('.j-level.is-on') || document.querySelector('.j-stage') || document.body;
  for (const el of (document.querySelector('.j-stage') || document.body).querySelectorAll('*')) {
    if (!visible(el) || isControl(el)) continue;
    const s = getComputedStyle(el);
    const top = parseFloat(s.borderTopWidth) > 0 && s.borderTopStyle !== 'none';
    const sides = ['Right', 'Bottom', 'Left'].some(k => parseFloat(s['border' + k + 'Width']) > 0 && s['border' + k + 'Style'] !== 'none');
    const fill = s.backgroundColor !== 'rgba(0, 0, 0, 0)' && s.backgroundColor !== 'transparent' && !el.classList.contains('j-level');  // a deeper level's veil is the ground
    const shade = s.boxShadow && s.boxShadow !== 'none';
    const outline = parseFloat(s.outlineWidth) > 0 && s.outlineStyle !== 'none';
    if (sides || fill || shade || outline) faults.push(`a box round content: <${name(el)}> drawn with ${[sides && 'a border', fill && 'a fill', shade && 'a shadow', outline && 'an outline'].filter(Boolean).join(', ')}`);
    if (top && !el.classList.contains('j-sum')) faults.push(`a line off a total: <${name(el)}> has a top border`);
  }
  for (const el of document.querySelectorAll('.j-sum')) {
    if (!visible(el)) continue;
    const s = getComputedStyle(el);
    if (!(parseFloat(s.borderTopWidth) > 0 && s.borderTopStyle !== 'none')) faults.push(`a total without its hairline: <${name(el)}>`);
  }
  // A figure is an element whose own text holds a digit; its unit may be a child (.j-val-unit,
  // .j-big-unit), so the figure is read with its unit children, and each of those is checked too.
  const own = (el) => [...el.childNodes].filter(n => n.nodeType === 3).map(n => n.textContent).join('');
  const units = (el) => [...el.children].filter(c => [...c.classList].some(k => /-unit$/.test(k)));
  for (const el of level.querySelectorAll('*')) {
    if (!visible(el) || !/\d/.test(own(el))) continue;
    const us = units(el);
    const t = (own(el) + ' ' + us.map(u => u.textContent).join(' ')).replace(/\s+/g, ' ').trim();
    const want = [...currency].some(ch => t.includes(ch)) ? ['money', gold] : (unit.test(t) ? ['measure', turq] : null);
    if (!want) continue;
    for (const x of [el, ...us]) {
      const c = getComputedStyle(x).color;
      if (c !== want[1]) faults.push(`${want[0] === 'money' ? 'money' : 'a measure'} off its colour: "${t}" (<${name(x)}>) is ${c}, not the ${want[0]} colour ${want[1]}`);
    }
  }
  const bar = document.querySelector('.j-bar');
  const info = bar && [...bar.querySelectorAll('button,[role=button],a')].some(b => /^\(?i\)?$|info/i.test((b.getAttribute('aria-label') || b.textContent || '').trim()));
  if (!info) faults.push('no (i): no control in .j-bar labelled i or info');
  const text = document.body.innerText || '';
  for (const n of never) if (text.toLowerCase().includes(n.toLowerCase())) faults.push(`a phrase this product never shows is on screen: "${n}"`);
  const crumb = level.querySelector('.j-crumb');
  if (!crumb || !crumb.textContent.trim()) faults.push('no crumb in the level shown');
  const foot = level.querySelector('.j-foot');
  if (!foot) faults.push('the working is not at the foot: the level shown has no .j-foot');
  else if (foot.getBoundingClientRect().bottom < innerHeight * 0.75) faults.push(`the working is not at the foot: .j-foot ends at ${Math.round(foot.getBoundingClientRect().bottom)}px of ${innerHeight}`);
  return faults;
}
"""

ZOOM = r"""
async () => {
  const level = document.querySelector('.j-level.is-on') || document;
  const row = level.querySelector('button.j-row');
  if (!row) return 'none';
  row.click();
  await new Promise(r => setTimeout(r, 700));
  const behind = document.querySelector('.j-level.is-behind-1');
  if (!behind) return 'no level is .is-behind-1 after tapping a row';
  const m = new DOMMatrixReadOnly(getComputedStyle(behind).transform);
  return m.a < 1 ? '' : 'the level behind is not zoomed back (its scale is ' + m.a + ')';
}
"""


def look(url, outdir, never, shoot=True):
    from playwright.sync_api import sync_playwright
    faults = []
    with sync_playwright() as p:
        browser = p.chromium.launch()
        try:
            for label, size in (("phone", PHONE), ("desktop", DESKTOP)):
                page = browser.new_page(viewport=size)
                page.goto(url, wait_until="networkidle")
                if shoot:
                    os.makedirs(outdir, exist_ok=True)
                    page.screenshot(path=os.path.join(outdir, f"look-{label}.png"), full_page=True)
                faults += [f"{label}: {f}" for f in page.evaluate(PROBE, [never, CURRENCY, UNIT.pattern])]
                z = page.evaluate(ZOOM)
                if z == "none":
                    print(f"{label}: no row drills in on this screen; the zoom behind is not tried")
                elif z:
                    faults.append(f"{label}: {z}")
                if shoot and z != "none":
                    page.screenshot(path=os.path.join(outdir, f"look-{label}-drilled.png"))
                page.close()
        finally:
            browser.close()
    return faults


KIT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "library", "juku-style.css")

GOOD = """<!doctype html><html><head><meta charset=utf-8><style>{css}</style></head>
<body class="j-page"><div class="j-screen"><div class="j-stage">
<section class="j-level is-on"><div class="j-head"><p class="j-crumb">THE FORMULA</p><h1 class="j-title">Hem</h1></div>
<div class="j-eqn j-foot">
<button class="j-row" onclick="document.querySelector('.j-level').className='j-level is-behind-1';document.querySelectorAll('.j-level')[1].className='j-level is-deep is-on'"><span class="j-name">Length</span><span class="j-val j-turq">12<span class="j-val-unit j-turq"> cm</span></span></button>
<div class="j-row j-sum"><span class="j-name">Total</span><span class="j-gold">£24.00</span></div>
</div></section>
<section class="j-level is-deep is-off"><div class="j-head"><p class="j-crumb">THE FORMULA · LENGTH</p></div><div class="j-eqn j-foot"><div class="j-row">x</div></div></section>
</div><div class="j-bar"><span class="j-bar-rule"></span><button class="j-icon-btn" aria-label="info">i</button></div></div></body></html>"""


def selftest():
    bad = 0
    if not UNIT.search("12 cm") or UNIT.search("12 cmx") or not UNIT.search('30"'):
        bad += 1
        print("FAIL selftest: the unit pattern")
    try:
        import playwright.sync_api  # noqa: F401
        from playwright.sync_api import sync_playwright
        with sync_playwright() as p:
            p.chromium.launch().close()
    except Exception as e:  # no browser here: say so, never pass it silently as checked
        print(f"look-check selftest: no browser here ({e.__class__.__name__}); the rendered cases are not run, "
              "a product's verify runs them where Playwright is installed")
        print("selftest ok (unit pattern only)" if not bad else f"selftest: {bad} failed")
        return 1 if bad else 0
    import tempfile
    css = open(KIT, encoding="utf-8").read()
    cases = [
        ("the kit's own screen", GOOD, 0),
        ("a card", GOOD.replace('<div class="j-row j-sum">', '<div style="border:1px solid red"><div class="j-row j-sum">').replace("</div>\n</div></section>", "</div></div>\n</div></section>", 1), "some"),
        ("a divider", GOOD.replace('<div class="j-row j-sum">', '<div class="j-row" style="border-top:1px solid #333">y</div><div class="j-row j-sum">'), "some"),
        ("a box on a row that drills in", GOOD.replace('<button class="j-row"', '<button class="j-row" style="border:1px solid #333"'), "some"),
        ("a deeper level, shown", GOOD.replace("is-on\"><div class=\"j-head\"><p class=\"j-crumb\">THE FORMULA</p>", "is-off\"><div class=\"j-head\"><p class=\"j-crumb\">THE FORMULA</p>").replace("j-level is-deep is-off", "j-level is-deep is-on", 1), 0),
        ("a figure's unit off its colour", GOOD.replace('<span class="j-val-unit j-turq">', '<span class="j-val-unit j-gold">'), 1),
        ("money in turquoise", GOOD.replace('class="j-gold">£24.00', 'class="j-turq">£24.00'), 1),
        ("a measure in gold", GOOD.replace('class="j-val j-turq">12', 'class="j-val j-gold">12'), 1),
        ("no (i)", GOOD.replace('<button class="j-icon-btn" aria-label="info">i</button>', ''), 1),
        ("a forbidden phrase", GOOD.replace(">Hem<", ">Tell Hemzy<"), 1),
        ("no crumb", GOOD.replace('<p class="j-crumb">THE FORMULA</p>', ''), 1),
        ("no foot", GOOD.replace('<div class="j-eqn j-foot">', '<div class="j-eqn">', 1), 1),
        ("no zoom", GOOD.replace("is-behind-1'", "is-off'"), 1),
    ]
    with tempfile.TemporaryDirectory() as d:
        for label, html, want in cases:
            path = os.path.join(d, "s.html")
            with open(path, "w", encoding="utf-8") as fh:
                fh.write(html.replace("{css}", css))
            got = [f for f in look("file://" + path, d, ["Tell Hemzy"], shoot=False) if f.startswith("phone:")]
            ok = bool(got) if want == "some" else len(got) == want
            if not ok:
                bad += 1
                print(f"FAIL selftest: {label}: expected {want} phone fault(s), got {got}")
    print("selftest ok" if not bad else f"selftest: {bad} failed")
    return 1 if bad else 0


def main(argv):
    if argv[1:] == ["--selftest"]:
        return selftest()
    args, never = [], []
    it = iter(argv[1:])
    for a in it:
        if a == "--never":
            never.append(next(it, ""))
        else:
            args.append(a)
    if len(args) != 2:
        print(__doc__)
        return 2
    faults = look(args[0], args[1], [n for n in never if n])
    for f in faults:
        print("FAIL:", f)
    print("ok" if not faults else f"{len(faults)} fault(s); screenshots in {args[1]}")
    return 1 if faults else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
