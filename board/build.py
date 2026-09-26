#!/usr/bin/env python3
"""The build board, rendered: one JSON of reads in, one index.html out.

What the page shows and may claim is decision 0007 and its addendum
(https://github.com/Adonis80/how-we-build/issues/97); the section marks below
(§n, An) are its clauses. `.github/workflows/build-board.yml` makes the reads
and deploys the page with board/'s gate. This file fetches nothing and prints
nothing a source holds: a fault names a product and a key, never a value,
because the log it lands in is public and the roadmaps are not.

    python3 board/build.py <reads.json> <index.html>
    python3 board/build.py --selftest

The reads, as the workflow writes them:

    {"checked_at": "2026-09-26T17:40:00Z",
     "products": [{"name": "Hemz OS", "last_edited": "<ISO time>",
                   "roadmap": <roadmap.json on main, parsed>}, ...],
     "rulebook": {"open": [{"number", "title", "body", "draft", "created_at",
                            "url", "review": [{"status", "conclusion"}, ...]}],
                  "merged": [{"number", "title", "url", "merged_at"}, ...]}}

`review` is the juku-reviewer check runs on the pull request's head, newest
first. Of a body, only its `Priority:` and `Ready:` lines are published (§8).
"""
import html
import json
import re
import sys
from datetime import datetime, timezone

try:
    from zoneinfo import ZoneInfo
    LONDON = ZoneInfo("Europe/London")
except Exception:  # no tz database: say UTC rather than guess
    LONDON = None

RULEBOOK = "Juku OS"
ROWS = (RULEBOOK, "Hemz OS", "Myst", "Phena")          # §1: four rows, this order
AGREED = ("done", "building", "next", "agreed")        # §2: the denominator
DECISION = "Decision needed:"                          # §3: the only test
MERGED_SHOWN = 10                                      # §7
PR_LINK = re.compile(r"^https://github\.com/Adonis80/how-we-build/pull/[1-9][0-9]*$")
ITEM_FIELDS = ("id", "title", "plain", "status", "gate", "proof", "next", "decided_on", "decided_by")
MONTHS = ("January", "February", "March", "April", "May", "June", "July", "August",
          "September", "October", "November", "December")


class Unreadable(Exception):
    """A source not in the shape this page reads. Carries a key path, never a value."""


def e(s):
    return html.escape("" if s is None else str(s), quote=True)


def day(text):
    """A source's own date, in the page's style; left as written if it is not one."""
    try:
        return when(text)
    except (TypeError, ValueError):
        return text


def when(iso, clock=False):
    """An absolute date (§5), and with `clock` the time and timezone too."""
    t = datetime.fromisoformat(str(iso).replace("Z", "+00:00"))
    if t.tzinfo is None:
        t = t.replace(tzinfo=timezone.utc)
    t = t.astimezone(LONDON) if LONDON else t.astimezone(timezone.utc)
    day = "%d %s %d" % (t.day, MONTHS[t.month - 1], t.year)
    return "%s, %s %s" % (day, t.strftime("%H:%M"), t.tzname() or "UTC") if clock else day


# ---------------------------------------------------------------- products

def items_of(name, road):
    if not isinstance(road, dict) or not isinstance(road.get("items"), list):
        raise Unreadable("%s: roadmap.json has no `items` list" % name)
    out = []
    for i, it in enumerate(road["items"]):
        if not isinstance(it, dict):
            raise Unreadable("%s: items[%d] is not an object" % (name, i))
        for k in ITEM_FIELDS:
            if it.get(k) is not None and not isinstance(it[k], str):
                raise Unreadable("%s: items[%d].%s is not text" % (name, i, k))
        if not (it.get("title") or "").strip():
            raise Unreadable("%s: items[%d] has no title" % (name, i))
        out.append({k: it.get(k) for k in ITEM_FIELDS})
    return out


def needs_decision(it):
    return (it.get("gate") or "").lstrip().startswith(DECISION)


def milestones(road):
    """§8: the milestone sentence and whether `reached_on` is set; nothing else."""
    found = []
    for key, val in road.items():
        if "milestone" not in key.lower():
            continue
        for m in (val if isinstance(val, list) else [val]):
            if not isinstance(m, dict):
                continue
            words = next((m[k] for k in ("milestone", "sentence", "text", "what", "reminder", "title", "plain")
                          if isinstance(m.get(k), str) and m[k].strip()), None)
            if words:
                found.append((words, bool(m.get("reached_on"))))
    return found


def tally(items):
    n = {s: sum(1 for it in items if it["status"] == s) for s in AGREED + ("proposed",)}
    n["agreed_total"] = sum(n[s] for s in AGREED)
    n["queued"] = n["next"] + n["agreed"]              # §2: the bar groups these
    n["decisions"] = sum(1 for it in items if needs_decision(it))
    return n


def headline(items):
    """One plain line: what is in hand, or next eligible (A2's wording)."""
    hand = [it for it in items if it["status"] == "building"]
    if hand:
        more = " and %d more" % (len(hand) - 1) if len(hand) > 1 else ""
        return '<span class="dot" aria-hidden="true"></span>In hand: %s%s' % (e(hand[0]["title"]), more)
    nxt = next((it for it in items if it["status"] == "next"), None) or \
        next((it for it in items if it["status"] == "agreed"), None)
    line = "No work recorded as in hand"
    return line + (". Next eligible: %s" % e(nxt["title"]) if nxt else ".")


def bar(n):
    total = n["agreed_total"]
    if not total:
        return '<div class="bar empty" role="img" aria-label="No agreed work recorded"></div>'
    parts = [("done", n["done"], "done"), ("hand", n["building"], "in hand"), ("queued", n["queued"], "queued")]
    label = ", ".join("%d %s" % (v, w) for _, v, w in parts) + " of %d agreed" % total
    spans = "".join('<span class="%s" style="width:%.3f%%"></span>' % (c, 100.0 * v / total)
                    for c, v, _ in parts if v)
    return '<div class="bar" role="img" aria-label="%s">%s</div>' % (e(label), spans)


STATUS_WORD = {"done": "Done", "building": "In hand", "next": "Up next", "agreed": "Queued",
               "proposed": "Suggested"}


def item_html(it):
    status = it["status"] or ""
    word = STATUS_WORD.get(status, "Status not recorded")
    agreed = "Suggested on" if status == "proposed" else "Agreed on"
    who = it.get("decided_by")
    who = ("the " + who) if who in ("CTO", "Chairman") else who
    rows = [("What has to be true first", it.get("gate")),
            ("What would prove it done", it.get("proof")),
            ("What it makes possible next", it.get("next"))]
    dl = "".join("<dt>%s</dt><dd>%s</dd>" % (e(k), e(v) if v else '<span class="none">Not written</span>')
                 for k, v in rows)
    said = ""
    if it.get("decided_on"):
        said = '<p class="said">%s %s%s</p>' % (agreed, e(day(it["decided_on"])), " by " + e(who) if who else "")
    ident = '<span class="id">%s</span>' % e(it["id"]) if it.get("id") else ""
    return ('<details class="item s-%s"><summary>%s<span class="t">%s</span><span class="st">%s</span></summary>'
            '<div class="body">%s<dl>%s</dl>%s</div></details>'
            % (e(status or "none"), ident, e(it["title"]), e(word),
               '<p class="plain">%s</p>' % e(it["plain"]) if it.get("plain") else "", dl, said))


def group(title, items, extra=""):
    if not items:
        return ""
    return '<section><h3>%s <span class="n">%d</span></h3>%s%s</section>' % (
        e(title), len(items), "".join(item_html(it) for it in items), extra)


def product_row(p):
    name = p["name"]
    items = items_of(name, p.get("roadmap"))
    n = tally(items)
    asks = [it for it in items if needs_decision(it)]
    rest = [it for it in items if not needs_decision(it)]
    by = lambda s: [it for it in rest if it["status"] == s]
    unknown = [it for it in rest if it["status"] not in STATUS_WORD]
    counts = "%d of %d agreed done" % (n["done"], n["agreed_total"])
    if n["proposed"]:
        counts += " · %d suggested" % n["proposed"]
    if n["decisions"]:
        counts += ' · <b class="ask">%d need%s your decision</b>' % (n["decisions"], "" if n["decisions"] > 1 else "s")
    money = "".join('<li>%s <span class="%s">%s</span></li>' % (e(w), "hit" if r else "open",
                                                             "Reached" if r else "Not reached yet")
                    for w, r in milestones(p["roadmap"]))
    body = (group("Needs your decision", asks) + group("In hand", by("building")) +
            group("Up next", by("next")) + group("Agreed and queued", by("agreed")) +
            group("Suggested", by("proposed")) + group("Done", by("done")) +
            group("Status not recorded", unknown) +
            ('<section><h3>Money milestone</h3><ul class="money">%s</ul></section>' % money if money else "") +
            '<p class="edited">Roadmap last edited %s</p>' % e(when(p["last_edited"])))
    return row(name, bar(n), counts, headline(items), body), n["decisions"]


# ---------------------------------------------------------------- Juku OS

def body_line(body, key):
    m = re.search(r"\*{0,2}%s:\*{0,2}[ \t]*([^\n]*)" % key, body or "")
    return m.group(1).strip() if m else None


def readiness(pr):
    """(ready: 'yes' | 'no' | None, its reason or '', priority 'P1'..'P4' or None). §8: nothing else."""
    pri = body_line(pr.get("body"), "Priority")
    pri = re.match(r"(P[1-4])\b", pri or "")
    line = body_line(pr.get("body"), "Ready")
    m = re.match(r"(yes|no)\b(.*)", line or "", re.I)
    if not m:
        return None, "", pri.group(1) if pri else None
    reason = re.split(r"\*\*", m.group(2))[0]
    reason = re.sub(r"[*`]", "", reason).strip(" \t.,:;—–-")
    return m.group(1).lower(), reason[:240], pri.group(1) if pri else None


def pr_state(pr):
    """§7, first match wins, from fields the repository already holds."""
    ready, reason, _ = readiness(pr)
    if ready is None:
        return "Readiness not recorded"
    if ready == "no":
        return "Waiting on the Chairman" if DECISION in reason else "Parked"
    if pr.get("draft"):
        return "Draft"
    runs = pr.get("review") or []
    if not runs:
        return "Review not recorded"
    last = runs[0]
    if last.get("status") != "completed":
        # An older success never overrides a newer pending attempt.
        return "Further review pending" if any(r.get("status") == "completed" for r in runs[1:]) else "Review pending"
    return {"success": "Review check passed", "failure": "Review check failed"}.get(last.get("conclusion"),
                                                                                  "Review incomplete")


def queue_order(prs):
    """Ready first, then priority, then oldest (the queue this repository keeps)."""
    def key(pr):
        ready, _, pri = readiness(pr)
        return (0 if ready == "yes" else 1, pri or "P9", pr.get("created_at") or "")
    return sorted(prs, key=key)


def link(url, words):
    return '<a href="%s">%s</a>' % (e(url), words) if isinstance(url, str) and PR_LINK.match(url) else ""


def pr_html(pr):
    ready, reason, pri = readiness(pr)
    state = pr_state(pr)
    facts = [("Priority", pri or "Not recorded"),
             ("Ready", (ready + (" — " + reason if reason else "")) if ready else "Not recorded")]
    dl = "".join("<dt>%s</dt><dd>%s</dd>" % (e(k), e(v)) for k, v in facts)
    where = link(pr.get("url"), "Where the work is")
    return ('<details class="item pr"><summary><span class="id">#%d</span><span class="t">%s</span>'
            '<span class="st">%s%s</span></summary><div class="body"><dl>%s</dl>%s</div></details>'
            % (int(pr["number"]), e(pr.get("title")), e(state), " · " + e(pri) if pri else "", dl,
               '<p class="said">%s</p>' % where if where else ""))


def rulebook_row(rb):
    open_ = queue_order([pr for pr in rb.get("open") or [] if isinstance(pr, dict) and "number" in pr])
    merged = sorted([pr for pr in rb.get("merged") or [] if isinstance(pr, dict) and pr.get("merged_at")],
                    key=lambda pr: pr["merged_at"], reverse=True)[:MERGED_SHOWN]
    waiting = [pr for pr in open_ if pr_state(pr) == "Waiting on the Chairman"]
    ready = next((pr for pr in open_ if readiness(pr)[0] == "yes"), None)
    line = ("Next ready: #%d %s" % (int(ready["number"]), e(ready.get("title")))) if ready else \
        "No pull request recorded as ready."
    counts = "%d open pull request%s" % (len(open_), "" if len(open_) == 1 else "s")
    if waiting:
        counts += ' · <b class="ask">%d need%s your decision</b>' % (len(waiting), "" if len(waiting) > 1 else "s")
    hist = "".join('<li><span class="id">#%d</span> %s <span class="st">merged %s</span> %s</li>'
                   % (int(pr["number"]), e(pr.get("title")), e(when(pr["merged_at"])), link(pr.get("url"), "Where the work is"))
                   for pr in merged)
    body = ((('<section><h3>Needs your decision <span class="n">%d</span></h3>%s</section>'
              % (len(waiting), "".join(pr_html(pr) for pr in waiting))) if waiting else "") +
            ('<section><h3>The queue <span class="n">%d</span></h3>%s</section>'
             % (len(open_), "".join(pr_html(pr) for pr in open_ if pr not in waiting)) if open_ else "") +
            ('<section><h3>Merged, newest first</h3><ul class="hist">%s</ul></section>' % hist if hist else ""))
    return row(RULEBOOK, "", counts, line, body), len(waiting)


# ---------------------------------------------------------------- the page

def row(name, bar_html, counts, line, body):
    return ('<details class="row" name="product"><summary><span class="name">%s</span>%s'
            '<span class="counts">%s</span><span class="line">%s</span></summary>'
            '<div class="depth">%s</div></details>' % (e(name), bar_html, counts, line, body))


CSS = """:root{color-scheme:dark;--bg:#06070f;--bg2:#0a0b14;--panel:rgba(255,255,255,.035);--panel2:rgba(255,255,255,.06);--line:rgba(255,255,255,.1);--ink:#f2f4f7;--ink2:#a4adb8;--ink3:#6b7684;--cyan:#53eafd;--cyan-glow:rgba(103,232,249,.35);--mint:#5ee9b5;--grey:#3a4350;--dash:#4a5563;--sans:"Geist",system-ui,-apple-system,"Segoe UI",sans-serif;--mono:"Geist Mono",ui-monospace,SFMono-Regular,Menlo,monospace;--r:10px}
*{box-sizing:border-box}body{margin:0;background:var(--bg);background-image:radial-gradient(ellipse 80% 50% at 50% -10%,rgba(83,234,253,.07),transparent 60%);color:var(--ink);font-family:var(--sans);font-size:15px;line-height:1.5;padding-inline:16px;padding-block:22px 56px;-webkit-font-smoothing:antialiased;font-variant-numeric:tabular-nums}
.wrap{max-width:720px;margin:0 auto}.eyebrow,.id,.n,.st,.edited,.said{font-family:var(--mono);font-size:11px;letter-spacing:.08em;color:var(--ink3)}.eyebrow{letter-spacing:.22em;text-transform:uppercase}
h1{font-size:clamp(26px,6.5vw,34px);font-weight:600;letter-spacing:-.02em;line-height:1.15;margin:6px 0 10px}.lede{color:var(--ink2);margin:0 0 6px}.snap{font-family:var(--mono);font-size:12px;color:var(--ink3);margin:0 0 22px}
.row{background:var(--panel);border:1px solid var(--line);border-radius:var(--r);margin:0 0 12px}.row[open]{background:var(--panel2)}
summary{cursor:pointer;list-style:none}summary::-webkit-details-marker{display:none}summary:focus-visible{outline:2px solid var(--cyan);outline-offset:2px;border-radius:var(--r)}
.row>summary{display:grid;gap:8px;padding:16px}.name{font-size:18px;font-weight:600}.counts{color:var(--ink2);font-size:13px}.line{color:var(--ink)}
.ask{color:var(--cyan);font-weight:500}.dot{display:inline-block;width:8px;height:8px;border-radius:50%;background:var(--cyan);box-shadow:0 0 8px var(--cyan-glow);margin-right:8px;vertical-align:middle}
.bar{display:flex;height:6px;border-radius:3px;background:rgba(255,255,255,.05);overflow:hidden}.bar span{display:block;height:100%}.bar .done{background:var(--mint)}.bar .hand{background:var(--cyan)}.bar .queued{background:var(--grey)}
.depth{padding:0 16px 16px;border-top:1px solid var(--line)}section{margin-top:16px}h3{font-size:12px;font-weight:500;letter-spacing:.14em;text-transform:uppercase;color:var(--ink2);margin:0 0 8px}
.item{border:1px solid var(--line);border-radius:8px;margin:0 0 8px;background:var(--bg2)}.item>summary{display:flex;flex-wrap:wrap;gap:4px 10px;align-items:baseline;padding:10px 12px}.item .t{flex:1 1 60%}.item .st{margin-left:auto}
.s-done{border-left:3px solid var(--mint)}.s-building{border-left:3px solid var(--cyan)}.s-next,.s-agreed{border-left:3px solid var(--grey)}.s-proposed{border:1px dashed var(--dash)}
.body{padding:0 12px 12px;color:var(--ink2)}.plain{color:var(--ink);margin:0 0 8px}dl{margin:0}dt{font-size:12px;color:var(--ink3);margin-top:8px}dd{margin:2px 0 0}.none{color:var(--ink3)}
a{color:var(--cyan)}ul{margin:0;padding-left:18px}.hist li,.money li{margin:6px 0;color:var(--ink2)}.hit{color:var(--mint)}.open{color:var(--ink3)}.edited{margin-top:16px}"""


def render(reads):
    checked = when(reads["checked_at"], clock=True)
    rows, asked = {}, {}
    for p in reads.get("products") or []:
        if p.get("name") not in ROWS or p["name"] == RULEBOOK:
            raise Unreadable("a product named outside the board's rows")
        rows[p["name"]], asked[p["name"]] = product_row(p)
    rows[RULEBOOK], asked[RULEBOOK] = rulebook_row(reads.get("rulebook") or {})
    missing = [n for n in ROWS if n not in rows]
    if missing:
        raise Unreadable("no reads for %s" % ", ".join(missing))
    total = sum(asked.values())
    if total:
        lede = "%d decision%s need%s you: %s." % (total, "" if total == 1 else "s", "s" if total == 1 else "",
                                                ", ".join("%s %d" % (n, asked[n]) for n in ROWS if asked[n]))
    else:
        lede = "No decisions are recorded as waiting on you."
    return ('<!doctype html><html lang="en"><head><meta charset="utf-8">'
            '<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">\n'
            '<meta name="robots" content="noindex,nofollow"><meta name="theme-color" content="#06070f">\n'
            '<title>Juku Build Board</title>\n'
            '<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n'
            '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Geist:wght@400;500;600&family=Geist+Mono:wght@400;500&display=swap">\n'
            '<style>%s</style></head>\n<body data-board><main class="wrap">'
            '<div class="eyebrow">Juku OS · Build board</div><h1>Where everything stands</h1>'
            '<p class="lede">%s</p><p class="snap">Snapshot checked %s. Changes after this time may not appear.</p>'
            '%s</main></body></html>\n' % (CSS, e(lede), e(checked), "".join(rows[n] for n in ROWS)))


# ---------------------------------------------------------------- selftest

def _selftest():
    bad = []

    def hold(ok, what):
        if not ok:
            bad.append(what)

    def it(i, status, gate="After the last.", **kw):
        return dict({"id": i, "title": "Item " + i, "plain": "Plain " + i, "status": status, "gate": gate,
                     "proof": None, "next": "Next " + i, "decided_on": "2026-09-07", "decided_by": "Chairman"}, **kw)

    road = {"_what_this_is": "x", "items": [
        it("A1", "done"), it("P1", "done"), it("P2", "done"), it("P3", "proposed"),
        it("P7", "building"), it("P4", "building"), it("P5", "building"), it("A2", "building"),
        it("P6", "agreed"), it("A3", "agreed")]}
    n = tally(items_of("Myst", road))
    # §2 on Myst's own shape of 26 September: three done of nine agreed, one suggested.
    hold((n["done"], n["agreed_total"], n["proposed"], n["queued"]) == (3, 9, 1, 2),
         "§2: agreed work counts done, building, next and agreed; proposed stands apart")
    # §3: the prefix alone, on any status, and nothing that merely names him.
    d = items_of("X", {"items": [it("1", "proposed", gate=" Decision needed: the price."),
                                 it("2", "agreed", gate="Needs the Chairman's word on the price."),
                                 it("3", "done", gate="decision needed: lower case")]})
    hold([needs_decision(x) for x in d] == [True, False, False],
         "§3: only a gate beginning `Decision needed:` asks him, whatever the status")
    hold("No work recorded as in hand" in headline(items_of("X", {"items": [it("1", "agreed")]})) and
         "Nothing in hand" not in headline(items_of("X", {"items": []})),
         "A2: with nothing building the page says no work is recorded as in hand, never that nothing is")

    def pr(num, body, draft=False, review=(), created="2026-09-2%d" % 1):
        return {"number": num, "title": "PR %d" % num, "body": body, "draft": draft, "created_at": created,
                "url": "https://github.com/Adonis80/how-we-build/pull/%d" % num,
                "review": [{"status": s, "conclusion": c} for s, c in review]}

    ok = "**Priority:** P3, build. **Ready:** yes."
    states = [
        (pr(1, "no lines at all"), "Readiness not recorded"),
        (pr(2, "**Priority:** P2. **Ready:** no — Decision needed: which host."), "Waiting on the Chairman"),
        (pr(3, "**Priority:** P2. **Ready:** no — waiting on hands."), "Parked"),
        (pr(4, ok, draft=True, review=[("completed", "success")]), "Draft"),
        (pr(5, ok), "Review not recorded"),
        (pr(6, ok, review=[("in_progress", None)]), "Review pending"),
        (pr(7, ok, review=[("in_progress", None), ("completed", "success")]), "Further review pending"),
        (pr(8, ok, review=[("completed", "success")]), "Review check passed"),
        (pr(9, ok, review=[("completed", "failure"), ("completed", "success")]), "Review check failed"),
        (pr(10, ok, review=[("completed", "neutral")]), "Review incomplete"),
    ]
    for p, want in states:
        hold(pr_state(p) == want, "§7: #%d should read %r, reads %r" % (p["number"], want, pr_state(p)))
    order = [p["number"] for p in queue_order([
        pr(21, "**Priority:** P1. **Ready:** no — parked.", created="2026-09-01"),
        pr(22, "**Priority:** P3. **Ready:** yes.", created="2026-09-02"),
        pr(23, "**Priority:** P2. **Ready:** yes.", created="2026-09-05"),
        pr(24, "**Priority:** P3. **Ready:** yes.", created="2026-09-01")])]
    hold(order == [23, 24, 22, 21], "the queue: ready first, then priority, then oldest (got %s)" % order)

    evil = "<script>alert(1)</script>"
    reads = {"checked_at": "2026-09-26T17:40:00Z",
             "products": [{"name": "Hemz OS", "last_edited": "2026-09-25T17:04:07Z",
                           "roadmap": {"items": [it("P1", "building", title=evil)],
                                       "money_milestones": [{"milestone": "Revenue passes one thousand a month.",
                                                             "reached_on": None}]}},
                          {"name": "Myst", "last_edited": "2026-09-21T22:14:34Z", "roadmap": road},
                          {"name": "Phena", "last_edited": "2026-09-24T23:59:43Z", "roadmap": {"items": []}}],
             "rulebook": {"open": [pr(111, ok + "\nUNSELECTED BODY TEXT", review=[("completed", "success")]),
                                   dict(pr(112, ok), url="javascript:alert(1)")],
                          "merged": [dict(pr(100 + i, ""), merged_at="2026-09-%02dT10:00:00Z" % (10 + i))
                                     for i in range(12)]}}
    page = render(reads)
    hold("<script" not in page and html.escape(evil) in page, "§8: text is escaped and the page runs no script")
    hold("UNSELECTED BODY TEXT" not in page, "§8: a pull request's body is never published beyond its two lines")
    hold("javascript:" not in page and 'href="https://github.com/Adonis80/how-we-build/pull/111"' in page,
         "§8: only this repository's pull-request links are linked")
    hold(page.count('class="st">merged ') == MERGED_SHOWN and "#100" not in page and "#101" not in page,
         "§7: ten merged shown, newest first")
    hold("Snapshot checked 26 September 2026, 18:40 BST" in page or LONDON is None,
         "§5: the snapshot says its date, time and timezone")
    hold("Not reached yet" in page and "Revenue passes one thousand a month." in page,
         "§8: the money milestone's sentence and whether it is reached")
    hold("3 of 9 agreed done · 1 suggested" in page, "§1: a row's counts")
    hold("Agreed on 7 September 2026 by the Chairman" in page or LONDON is None,
         "§4: `decided_on` is labelled agreed on, as an absolute date")
    hold([page.index('<span class="name">%s</span>' % r) for r in ROWS] ==
         sorted(page.index('<span class="name">%s</span>' % r) for r in ROWS), "§1: four rows, Juku OS first")
    hold(page.count('name="product"') == 4, "§9: one shared name, so one product opens at a time")
    for broken, what in (({"items": {}}, "no `items` list"), ({"items": [{"title": "t", "gate": 3}]}, ".gate is not text"),
                         ({"items": [{"status": "done"}]}, "has no title")):
        try:
            items_of("Myst", broken)
            bad.append("a broken roadmap (%s) was read" % what)
        except Unreadable as x:
            hold(what in str(x) and "Myst" in str(x), "a fault names the product and the key: %s" % x)
    try:
        render(dict(reads, products=reads["products"][:2]))
        bad.append("a board missing a row was rendered")
    except Unreadable as x:
        hold("Phena" in str(x), "a missing row names itself")
    for b in bad:
        print("  board: " + b)
    if not bad:
        print("ok: the board renders decision 0007 from its reads — §1's four rows, §2's denominator, §3's "
              "prefix, §5's snapshot, %d of §7's readiness states, the queue's order and §8's contract — "
              "and refuses a roadmap it cannot read, naming the key and never the value" % len(states))
    return 1 if bad else 0


def main(argv):
    if argv[1:] == ["--selftest"]:
        return _selftest()
    if len(argv) != 3:
        print("usage: build.py <reads.json> <index.html> | --selftest")
        return 2
    try:
        with open(argv[1], encoding="utf-8") as f:
            page = render(json.load(f))
    except Unreadable as x:
        print("::error::the board was not rendered: %s. Nothing is deployed; the last snapshot stands." % x)
        return 1
    except (OSError, ValueError, KeyError, TypeError) as x:
        print("::error::the board was not rendered: the reads were not in shape (%s). Nothing is deployed."
              % type(x).__name__)
        return 1
    with open(argv[2], "w", encoding="utf-8") as f:
        f.write(page)
    print("rendered %d bytes" % len(page.encode("utf-8")))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
