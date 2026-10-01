#!/usr/bin/env python3
"""The build board, rendered: one JSON of reads in, one index.html out.

What the page shows and may claim is decision 0007 and its addendum
(https://github.com/Adonis80/how-we-build/issues/97); the section marks below
(§n, An) are its clauses. `.github/workflows/build-board.yml` makes the reads
and hands them here; a refresh by hand writes the same shape. This file
fetches nothing and prints
nothing a source holds: a fault names a product and a key, never a value,
because the log it lands in is public and the roadmaps are not.

    python3 board/build.py <reads.json> <index.html>
    python3 board/build.py --selftest

Write both files outside the checkout: either one inside it is a `git add`
away from putting a private roadmap in this public repository.

The reads, in the shape #117's workflow is to write them:

    {"checked_at": "2026-09-26T17:40:00Z",
     "products": [{"name": "Hemz OS", "last_edited": "<ISO time>",
                   "roadmap": <roadmap.json on main, parsed>}, ...],
     "rulebook": {"open": [{"number", "title", "body", "draft", "created_at",
                            "url", "review": [{"status", "conclusion"}, ...]}],
                  "merged": [{"number", "title", "url", "merged_at"}, ...]},
     "spend": {"days": [{"date": "YYYY-MM-DD", "usage": <USD>}, ...]}}

`spend` is OpenRouter's daily activity; null when no key is connected, and
{"unread": true} when a key is but the read failed. The card says which.

`review` is the juku-reviewer check runs on the pull request's head, newest
first. Of a body, only its `Priority:` and `Ready:` lines are published (§8).
"""
import html
import json
import os
import re
import sys
from datetime import datetime, timedelta, timezone

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


def asks_him(text):
    """§3's prefix, with "Decision needed: none" (step 6's own words) asking nothing."""
    text = (text or "").replace("*", "").lstrip()
    return text.startswith(DECISION) and not re.match(r"none\b", text[len(DECISION):].strip(" *"), re.I)


def needs_decision(it):
    return asks_him(it.get("gate"))


def milestones(name, road):
    """§8: each money milestone's sentence (`when`) and whether `reached_on` is set; nothing else.
    Read in the one shape the products keep, `money_milestones.items`, and refused in any
    other, never dropped (#113's read): a milestone missing from his board is a false line."""
    if "money_milestones" not in road:
        return []
    mm = road["money_milestones"]
    if not isinstance(mm, dict) or not isinstance(mm.get("items"), list):
        raise Unreadable("%s: money_milestones has no `items` list" % name)
    found = []
    for i, m in enumerate(mm["items"]):
        if not isinstance(m, dict) or not isinstance(m.get("when"), str) or not m["when"].strip():
            raise Unreadable("%s: money_milestones.items[%d].when is not text" % (name, i))
        found.append((m["when"], bool(m.get("reached_on"))))
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
    free = [it for it in items if not needs_decision(it)]
    nxt = next((it for it in free if it["status"] == "next"), None) or \
        next((it for it in free if it["status"] == "agreed"), None)
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


def facts(rows):
    """The detail's label and value grid; an empty field is left out, never shown blank."""
    return "<dl>%s</dl>" % "".join("<dt>%s</dt><dd>%s</dd>" % (e(k), v) for k, v in rows if v)


def item_html(it, open_=False):
    """One timeline node, three taps deep (his ruling, 1 October 2026, on the design he
    approved): the title; then the plain sentence; then Proof, Gate, Next and who agreed
    it, as a label and value grid. Native <details> both times: it opens without script."""
    status = it["status"] or ""
    word = STATUS_WORD.get(status, "Status not one the board reads")
    who = it.get("decided_by")
    who = ("the " + who) if who in ("CTO", "Chairman") else who
    agreed = " · ".join(e(x) for x in (who, day(it["decided_on"]) if it.get("decided_on") else None) if x)
    grid = facts([("Proof", e(it.get("proof") or "")), ("Gate", e(it.get("gate") or "")),
                  ("Next", e(it.get("next") or "")), ("Suggested" if status == "proposed" else "Agreed", agreed)])
    plain = '<p class="plain">%s</p>' % e(it["plain"]) if it.get("plain") else ""
    ident = '<span class="id">%s</span>' % e(it["id"]) if it.get("id") else ""
    return ('<li class="node s-%s"><details class="item"%s><summary>%s<span class="t">%s</span>'
            '<span class="st">%s</span></summary><div class="body">%s<details class="more"><summary>More'
            '</summary>%s</details></div></details></li>'
            % (e(status or "none"), " open" if open_ else "", ident, e(it["title"]), e(word), plain, grid))


def timeline(cls, items, first_open=None):
    if not items:
        return ""
    return '<ol class="tl %s">%s</ol>' % (cls, "".join(item_html(it, it is first_open) for it in items))


def group(title, items, cls="apart"):
    if not items:
        return ""
    head = '<h3>%s <span class="n">%d</span></h3>' % (e(title), len(items)) if title else ""
    return '<section class="%s-set">%s%s</section>' % (cls, head, timeline(cls, items))


def fold(count, word, inner):
    return ('<li class="node s-done fold"><details class="item"><summary><span class="t">%d %s</span>'
            '<span class="st">%s</span></summary>%s</details></li>' % (count, word, word.capitalize(), inner))


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
                    for w, r in milestones(p["name"], p["roadmap"]))
    # The timeline (his ruling, 1 October 2026): his decisions first, apart; then one
    # line holding everything done, folded, in source order; then in hand (the first
    # open at its sentence), up next and queued on one line; suggested set apart.
    done, live = by("done"), by("building") + by("next") + by("agreed")
    spine = ('<ol class="tl">%s%s</ol>' % (fold(len(done), "done", timeline("inner", done)) if done else "", "".join(
        item_html(it, it is (by("building") or [None])[0]) for it in live))) if done or live else ""
    total = n["agreed_total"]
    progress = ('<div class="pprog"><span>Overall progress</span><span class="pnum">%d%% · %d/%d done</span></div>%s'
                % (round(100.0 * n["done"] / total) if total else 0, n["done"], total, bar(n)))
    body = (group("Needs your decision", asks, "asks") + spine + group("", by("proposed")) +
            group("Status not one the board reads", unknown) +
            ('<section><h3>Money milestone</h3><ul class="money">%s</ul></section>' % money if money else "") +
            '<p class="edited">Roadmap last edited %s</p>' % e(when(p["last_edited"])))
    return row(name, bar(n), counts, headline(items), body, progress, "Roadmap · in sequence"), n["decisions"]


# ---------------------------------------------------------------- Juku OS

def field(body, key, value):
    """The first `key:` whose rest of line, emphasis dropped, opens with `value`.

    The first that parses, not the first that appears: a description may name
    the field in prose ("a `Ready:` line is a pointer") before it gives it
    (#113's second read).
    """
    for m in re.finditer(r"\*{0,2}%s:\*{0,2}[ \t]*([^\n]*)" % key, body or ""):
        got = re.match(value, m.group(1).replace("*", "").strip(), re.I)
        if got:
            return got
    return None


def readiness(pr):
    """(ready: 'yes' | 'no' | None, its reason or '', priority 'P1'..'P4' or None). §8: nothing else."""
    pri = field(pr.get("body"), "Priority", r"(P[1-4])\b")
    m = field(pr.get("body"), "Ready", r"(yes|no)\b(.*)")
    if not m:
        return None, "", pri.group(1).upper() if pri else None
    # The reason runs to the next field on the same line, if one follows.
    reason = re.split(r"\s(?:Lead stack|Reviewed by|Priority):", m.group(2))[0]
    reason = reason.replace("`", "").strip(" \t.,:;—–-")
    # Whole here: §3 is tested on all of it, and it is cut only where shown (#113's fifth read).
    return m.group(1).lower(), reason, pri.group(1).upper() if pri else None


def pr_state(pr):
    """§7, first match wins, from fields the repository already holds."""
    ready, reason, _ = readiness(pr)
    if ready is None:
        return "Readiness not recorded"
    if ready == "no":
        at = reason.find(DECISION)
        return "Waiting on the Chairman" if at >= 0 and asks_him(reason[at:]) else "Parked"
    if pr.get("draft"):
        return "Draft"
    runs = pr.get("review") or []
    if not runs:
        return "Review not recorded"
    # As the gate reads them (check_run_verdict): only a completed success or
    # failure is a verdict, and a failure anywhere on the head wins (#113's reads).
    said = [r.get("conclusion") for r in runs if r.get("status") == "completed"
            and r.get("conclusion") in ("success", "failure")]
    if "failure" in said:
        return "Review check failed"
    pending = any(r.get("status") != "completed" for r in runs)
    if said:
        return "Further review pending" if pending and runs[0].get("status") != "completed" else "Review check passed"
    return "Review pending" if pending else "Review incomplete"


def queue_order(prs):
    """Ready first, then priority, then oldest (the queue this repository keeps)."""
    def key(pr):
        ready, _, pri = readiness(pr)
        return (0 if ready == "yes" else 1, pri or "P9", pr.get("created_at") or "")
    return sorted(prs, key=key)


def link(url, words):
    return '<a href="%s">%s</a>' % (e(url), words) if isinstance(url, str) and PR_LINK.match(url) else ""


def pr_html(pr, merged=False):
    """A pull request on the same line: its title and state; one tap for Priority, Ready and the link."""
    where = link(pr.get("url"), "Where the work is ↗")
    if merged:
        grid = facts([("Merged", e(when(pr["merged_at"]))), ("Link", where)])
        st, cls = "Merged", "done"
    else:
        ready, reason, pri = readiness(pr)
        grid = facts([("Priority", e(pri or "Not recorded")),
                      ("Ready", e((ready + (" — " + reason[:240] if reason else "")) if ready else "Not recorded")),
                      ("Link", where)])
        st, cls = pr_state(pr) + (" · " + pri if pri else ""), "next"
    return ('<li class="node s-%s pr"><details class="item"><summary><span class="id">#%d</span>'
            '<span class="t">#%d %s</span><span class="st">%s</span></summary><div class="body">%s</div></details></li>'
            % (cls, int(pr["number"]), int(pr["number"]), e(pr.get("title")), e(st), grid))


def rulebook_row(rb):
    # Refused rather than shown as "0 open", as a product's broken roadmap is (#113's fourth read).
    if not isinstance(rb, dict) or not all(isinstance(rb.get(k), list) for k in ("open", "merged")):
        raise Unreadable("%s: the reads hold no `open` and `merged` lists" % RULEBOOK)
    for k in ("open", "merged"):
        for i, pr in enumerate(rb[k]):
            if not isinstance(pr, dict) or not isinstance(pr.get("number"), int):
                raise Unreadable("%s: %s[%d] has no number" % (RULEBOOK, k, i))
    open_ = queue_order(list(rb["open"]))
    merged = sorted([pr for pr in rb.get("merged") or [] if isinstance(pr, dict) and pr.get("merged_at")],
                    key=lambda pr: pr["merged_at"], reverse=True)[:MERGED_SHOWN]
    waiting = [pr for pr in open_ if pr_state(pr) == "Waiting on the Chairman"]
    queue = [pr for pr in open_ if pr not in waiting]
    ready = next((pr for pr in open_ if readiness(pr)[0] == "yes"), None)
    line = ("Next ready: #%d %s" % (int(ready["number"]), e(ready.get("title")))) if ready else \
        "No pull request recorded as ready."
    counts = "%d open pull request%s" % (len(open_), "" if len(open_) == 1 else "s")
    if waiting:
        counts += ' · <b class="ask">%d need%s your decision</b>' % (len(waiting), "" if len(waiting) > 1 else "s")
    asks = ('<section class="asks-set"><h3>Needs your decision <span class="n">%d</span></h3><ol class="tl asks">%s</ol>'
            '</section>' % (len(waiting), "".join(pr_html(pr) for pr in waiting))) if waiting else ""
    inner = '<ol class="tl inner">%s</ol>' % "".join(pr_html(pr, merged=True) for pr in merged)
    spine = ('<ol class="tl">%s%s</ol>' % (fold(len(merged), "merged", inner) if merged else "",
                                           "".join(pr_html(pr) for pr in queue))) if merged or queue else ""
    progress = ('<div class="pprog"><span>Its plan is its open pull requests</span>'
                '<span class="pnum">%d queued</span></div>' % len(queue))
    nobar = '<div class="nobar">No roadmap: its plan is its open pull requests</div>'
    return row(RULEBOOK, nobar, counts, line, asks + spine, progress, "Pull requests · in sequence"), len(waiting)


# ---------------------------------------------------------------- spend

# THE SPEND CARD (his ruling, 1 October 2026: "lift the freeze for the spend card";
# budget "$40", for all projects). OpenRouter is prepaid, so the cycle is the
# calendar month. A split per project later is this one setting.
BUDGET_USD = 40
DAY = re.compile(r"^\d{4}-\d{2}-\d{2}")
usd = lambda x: int(x + 0.5)                            # half up: $22.50 is $23, never banker's $22


def spend_card(spend, checked_at):
    """The Track card: spend this month against the budget and the month gone.

    OpenRouter's activity covers completed UTC days, so this month's spend is to
    yesterday and its share of the month counts completed days. The projection
    runs the last seven completed days' rate to the month's end; anything the
    reads cannot support says so rather than show a number.
    """
    now = datetime.fromisoformat(str(checked_at).replace("Z", "+00:00")).astimezone(timezone.utc)
    first = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    nxt = (first.replace(day=28) + timedelta(days=4)).replace(day=1)
    days_in, gone = (nxt - first).days, now.day - 1
    month = MONTHS[now.month - 1]
    left = "%d day%s to reset" % (days_in - gone, "" if days_in - gone == 1 else "s")
    local = now.astimezone(LONDON) if LONDON else now
    stamp = "updated %d %s, %s" % (local.day, MONTHS[local.month - 1][:3], local.strftime("%H:%M"))
    last_day = "%d %s" % (days_in, month)
    rows = spend.get("days") if isinstance(spend, dict) else None
    ok = isinstance(rows, list) and all(isinstance(r, dict) and isinstance(r.get("date"), str) and
                                        DAY.match(r["date"]) and isinstance(r.get("usage"), (int, float)) and
                                        not isinstance(r.get("usage"), bool) for r in rows)
    if not ok:
        why = ("No OpenRouter key is connected" if spend is None else
               "OpenRouter's spend was not read this time" if isinstance(spend, dict) and spend.get("unread") else
               "OpenRouter's answer was not in a shape the board reads")
        return ('<section class="spend st-none" aria-label="OpenRouter spend"><div class="sp-head">'
                '<span class="sp-title">OpenRouter</span><span class="sp-chip">Data incomplete</span></div>'
                '<div class="sp-big">? <span>/ $%d budget</span></div><p class="sp-proj">%s</p><p class="sp-basis">'
                'Nothing is shown as spent until it is read.</p><div class="sp-foot"><span>%s</span><span>%s</span>'
                '</div></section>' % (BUDGET_USD, e(why), e(left), e(stamp)))
    day = lambda r: datetime.strptime(r["date"][:10], "%Y-%m-%d").replace(tzinfo=timezone.utc)
    today = now.replace(hour=0, minute=0, second=0, microsecond=0)
    spent = sum(r["usage"] for r in rows if first <= day(r) < today)
    last7 = sum(r["usage"] for r in rows if today - timedelta(days=7) <= day(r) < today)
    projected = spent + last7 / 7.0 * (days_in - gone)
    share, time = 100.0 * spent / BUDGET_USD, 100.0 * gone / days_in
    if projected > BUDGET_USD:
        state, chip = "over", "Overshooting"
        proj = "Projected $%d · $%d over budget" % (usd(projected), usd(projected - BUDGET_USD))
    elif share > time:
        state, chip, proj = "hot", "Running hot", "Projected $%d by %s" % (usd(projected), last_day)
    else:
        state, chip, proj = "ok", "On track", "Projected $%d by %s" % (usd(projected), last_day)
    fill = min(share, 100.0)
    past = max(0.0, fill - time)
    return ('<section class="spend st-%s" aria-label="OpenRouter spend"><div class="sp-head"><span class="sp-title">'
            'OpenRouter</span><span class="sp-chip">%s</span></div><div class="sp-big">$%d '
            '<span>/ $%d budget</span></div><div class="sp-track" role="img" aria-label="%d%% of the budget '
            'spent, %d%% of %s gone"><span class="sp-fill" style="width:%.2f%%"></span><span class="sp-past" '
            'style="left:%.2f%%;width:%.2f%%"></span><span class="sp-mark" style="left:%.2f%%"></span></div>'
            '<div class="sp-legend"><span class="sp-pct">%d%% spent</span><span>%d%% of cycle</span></div>'
            '<p class="sp-proj">%s</p><p class="sp-basis">Based on the last 7 days</p><div class="sp-foot">'
            '<span>%s</span><span>%s</span></div></section>'
            % (state, chip, usd(spent), BUDGET_USD, usd(share), usd(time), e(month), fill - past, fill - past,
               past, time, usd(share), usd(time), e(proj), e(left), e(stamp)))


# ---------------------------------------------------------------- the page

def row(name, bar_html, counts, line, body, progress="", seq=""):
    """Closed, a row of the list; open, the project view he approved: the crumb back to
    the board, the name with its ‹ › beside it, overall progress, and the timeline."""
    return ('<details class="row" name="product"><summary><span class="crumb">‹ Build board / Project</span>'
            '<span class="name">%s</span>%s<span class="counts">%s</span><span class="line">%s</span></summary>'
            '<div class="depth"><div class="ph"><h2 class="pname">%s</h2><div class="pnav"></div></div>'
            '<p class="psub">%s</p>%s<h3 class="seq">%s</h3>%s</div></details>'
            % (e(name), bar_html, counts, line, e(name), counts, progress, e(seq), body))


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
.body{padding:0 12px 12px;color:var(--ink2)}.plain{color:var(--ink);margin:0 0 8px}dl{margin:0}dt{font-size:12px;color:var(--ink3);margin-top:8px}dd{margin:2px 0 0}.none{color:var(--ink3)}
.nobar{font-family:var(--mono);font-size:11px;letter-spacing:.06em;color:var(--ink3);border-top:1px dashed var(--dash);padding-top:6px}
.crumb{display:none}.row[open]{background:var(--bg);border-radius:20px;border-color:var(--line)}.row[open]>summary{padding:22px 20px 0}
.row[open]>summary>:not(.crumb){display:none}.row[open]>summary .crumb{display:block;font-family:var(--mono);font-size:12px;letter-spacing:.16em;text-transform:uppercase;color:var(--ink2)}
.row[open] .depth{border-top:0;padding:18px 20px 22px}
.ph{display:flex;align-items:center;justify-content:space-between;gap:12px}.pname{font-size:clamp(30px,8vw,40px);font-weight:600;letter-spacing:-.03em;line-height:1.1;margin:0}.psub{color:var(--ink2);margin:8px 0 0}
.pnav{display:flex;gap:8px;flex:none}.pnav button{width:44px;height:44px;border-radius:50%;border:1px solid rgba(255,255,255,.18);background:none;color:var(--ink);font-size:20px;line-height:1;cursor:pointer}.pnav button:disabled{opacity:.25;cursor:default}
.pprog{display:flex;justify-content:space-between;gap:12px;color:var(--ink2);margin:26px 0 10px}.pnum{font-family:var(--mono);color:var(--ink);white-space:nowrap}
.seq{font-family:var(--mono);font-size:12px;font-weight:400;letter-spacing:.16em;color:var(--ink2);margin:30px 0 4px}
.tl{list-style:none;margin:8px 0 0;padding:0}.node{position:relative;padding-left:30px}
.node::before{content:"";position:absolute;left:5.5px;top:28px;bottom:-24px;width:1px;background:var(--grey)}.node:last-child::before{display:none}.s-done::before{background:var(--mint)}
.node::after{content:"";position:absolute;left:0;top:22px;width:12px;height:12px;border-radius:50%;background:var(--grey)}.node.s-done::after{background:var(--mint)}.node.s-building::after{background:var(--cyan);box-shadow:0 0 12px var(--cyan-glow)}
.fold::after{box-shadow:0 0 0 2px var(--bg),0 0 0 3px var(--mint)}.apart-set,.asks-set{margin-top:18px}.apart>.node::before,.asks>.node::before{display:none}.apart>.node::after{background:none;border:1px dashed var(--ink3)}.asks>.node::after{background:none;border:2px solid var(--cyan)}
.tl .item{border:0;background:none;margin:0;border-radius:0}.tl .item>summary{display:flex;align-items:center;gap:14px;min-height:56px;padding:6px 0}.tl .item>summary::after{content:"›";color:var(--ink2);font-size:20px;width:16px;text-align:center;transition:transform .2s}.tl .item[open]>summary::after{transform:rotate(90deg)}
.tl .t{flex:1;font-size:17px;font-weight:500;color:var(--ink)}.tl .st{font-size:12px;letter-spacing:.08em;text-transform:uppercase;color:var(--ink2);text-align:right}.node.s-done>.item>summary .st{color:var(--mint)}.node.s-building>.item>summary .st{color:var(--cyan)}.tl .id{display:none}
.tl .body{padding:0 0 14px;color:var(--ink2)}.tl .plain{color:#d7dce2;font-size:16px;line-height:1.55;margin:0 0 4px}
.more>summary{display:inline-block;font-size:14px;color:var(--cyan);padding:6px 0;min-height:32px}.more>summary::after{content:" ›"}.more[open]>summary{display:none}
.tl dl{display:grid;grid-template-columns:84px 1fr;gap:10px 16px;border-top:1px solid var(--line);margin-top:12px;padding-top:14px}.tl dt{font-size:15px;color:var(--ink3);margin:0}.tl dd{font-size:15px;color:var(--ink);margin:0}
.node.pr>.item>summary{flex-wrap:wrap;row-gap:0}.node.pr>.item>summary .t{flex:1 1 calc(100% - 40px)}.node.pr>.item>summary::after{order:2}.node.pr>.item>summary .st{order:3;flex-basis:100%;text-align:left;padding-bottom:4px}
.inner{margin:0 0 8px}.inner .node{padding-left:22px}.inner .node::after{width:7px;height:7px;top:25px;left:2px}.inner .node::before{display:none}
@media (prefers-reduced-motion:reduce){.tl .item>summary::after{transition:none}}
.spend{background:var(--panel);border:1px solid var(--line);border-radius:16px;padding:22px 20px;margin:0 0 16px;--st:var(--mint)}.spend.st-hot{--st:#f2c46d}.spend.st-over{--st:#f39b86}.spend.st-none{--st:var(--ink3)}
.sp-head{display:flex;justify-content:space-between;align-items:baseline;gap:8px}.sp-title{font-size:17px;font-weight:600}.sp-chip{white-space:nowrap;font-size:14px;color:var(--st)}.sp-chip::before{content:"";display:inline-block;width:8px;height:8px;border-radius:50%;background:var(--st);margin-right:8px;vertical-align:middle}
.sp-big{font-size:44px;font-weight:400;letter-spacing:-.02em;line-height:1;margin:22px 0 22px}.sp-big span{font-size:16px;color:var(--ink2);letter-spacing:0;margin-left:8px}
.sp-track{position:relative;height:10px;border-radius:5px;background:var(--grey)}.sp-fill,.sp-past{position:absolute;top:0;bottom:0;border-radius:5px}.sp-fill{left:0;background:var(--st)}.st-hot .sp-fill,.st-over .sp-fill{opacity:.4}.sp-past{background:var(--st)}
.sp-mark{position:absolute;top:-7px;bottom:-7px;width:3px;margin-left:-1.5px;border-radius:2px;background:var(--ink);box-shadow:0 0 0 3px var(--panel)}
.sp-legend{display:flex;justify-content:space-between;font-family:var(--mono);font-size:13px;color:var(--ink2);margin-top:12px}.sp-pct{color:var(--st)}.sp-proj{color:var(--st);font-size:17px;font-weight:500;margin:20px 0 0}.sp-basis{color:var(--ink2);margin:4px 0 0}
.sp-foot{display:flex;justify-content:space-between;white-space:nowrap;gap:4px 12px;border-top:1px solid var(--line);margin-top:24px;padding-top:14px;font-size:14px;color:var(--ink3)}
a{color:var(--cyan)}ul{margin:0;padding-left:18px}.hist li,.money li{margin:6px 0;color:var(--ink2)}.hit{color:var(--mint)}.open{color:var(--ink3)}.edited{margin-top:16px}"""


# Two conveniences on top of what opens without it (§9): a swipe, or the buttons,
# moves to the next or previous product, and a second tap on an open item's title
# opens its detail rather than closing it. Fixed text: nothing from a source reaches it.
BOARD_JS = """(function(){var rows=[].slice.call(document.querySelectorAll('details.row'));
function go(i){var n=rows[i];if(!n)return;n.open=true;n.scrollIntoView({block:'start',behavior:matchMedia('(prefers-reduced-motion: reduce)').matches?'auto':'smooth'})}
rows.forEach(function(r,i){var d=r.querySelector('.depth'),x=null,y=0;if(!d)return;
d.addEventListener('touchstart',function(ev){x=ev.touches[0].clientX;y=ev.touches[0].clientY},{passive:true});
d.addEventListener('touchend',function(ev){if(x===null)return;var dx=ev.changedTouches[0].clientX-x,dy=ev.changedTouches[0].clientY-y;x=null;
if(Math.abs(dx)>60&&Math.abs(dx)>2*Math.abs(dy))go(dx<0?i+1:i-1)},{passive:true});
var nav=d.querySelector('.pnav');[[i-1,'\u2039'],[i+1,'\u203A']].forEach(function(s){var b=document.createElement('button'),t=rows[s[0]];
b.type='button';b.textContent=s[1];if(t)b.setAttribute('aria-label','Open '+t.querySelector('.name').textContent);else{b.disabled=true;b.setAttribute('aria-hidden','true')}
b.addEventListener('click',function(){go(s[0])});nav.appendChild(b)})});
[].forEach.call(document.querySelectorAll('.tl .item>summary'),function(s){s.addEventListener('click',function(ev){var it=s.parentNode,
m=it.querySelector(':scope>.body>.more');if(!m)return;if(it.open&&!m.open){ev.preventDefault();m.open=true}else if(it.open)m.open=false})})})();"""


def render(reads):
    checked = when(reads["checked_at"], clock=True)
    rows, asked = {}, {}
    for p in reads.get("products") or []:
        if p.get("name") not in ROWS or p["name"] == RULEBOOK:
            raise Unreadable("a product named outside the board's rows")
        rows[p["name"]], asked[p["name"]] = product_row(p)
    rows[RULEBOOK], asked[RULEBOOK] = rulebook_row(reads.get("rulebook"))
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
            '%s%s</main><script>%s</script></body></html>\n' % (CSS, e(lede), e(checked), spend_card(reads.get("spend"), reads["checked_at"]), "".join(rows[n] for n in ROWS),
                                                            BOARD_JS))


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
        it("X1", "done"), it("X2", "done"), it("X3", "done"), it("X4", "proposed"),
        it("X5", "building"), it("X6", "building"), it("X7", "building"), it("X8", "building"),
        it("X9", "agreed"), it("X10", "agreed")]}
    n = tally(items_of("Myst", road))
    # §2 on a made-up roadmap of Myst's size: three done of nine agreed, one suggested.
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
        (pr(11, ok, review=[("completed", "success"), ("completed", "failure")]), "Review check failed"),
        (pr(12, "**Priority:** **P2**. **Ready:** no — **Decision needed:** which host."), "Waiting on the Chairman"),
        (pr(13, "A `Ready:` line is a pointer, and `Priority:` a level.\n**Priority:** P3. **Ready:** yes.",
            review=[("completed", "success")]), "Review check passed"),
        (pr(10, ok, review=[("completed", "neutral")]), "Review incomplete"),
        # As the gate reads them: a neutral, cancelled or timed-out run is no verdict (#113's fourth read).
        (pr(14, ok, review=[("completed", "neutral"), ("completed", "success")]), "Review check passed"),
        (pr(15, ok, review=[("completed", "cancelled"), ("completed", "success")]), "Review check passed"),
        (pr(16, ok, review=[("in_progress", None), ("completed", "neutral")]), "Review pending"),
        (pr(17, "**Priority:** P2. **Ready:** no — " + "waiting on the host's answer. " * 10 +
            "Decision needed: which host."), "Waiting on the Chairman"),
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
             "products": [{"name": "Hemz OS", "last_edited": "2026-09-25T17:00:00Z",
                           "roadmap": {"items": [it("H1", "building", title=evil)],
                                       "money_milestones": {"items": [{"id": "M1", "when": "Revenue passes one thousand a month.",
                                                                       "reached_on": None}]}}},
                          {"name": "Myst", "last_edited": "2026-09-21T22:00:00Z", "roadmap": road},
                          {"name": "Phena", "last_edited": "2026-09-24T23:00:00Z", "roadmap": {"items": []}}],
             "rulebook": {"open": [pr(111, ok + "\nUNSELECTED BODY TEXT", review=[("completed", "success")]),
                                   dict(pr(112, ok), url="javascript:alert(1)")],
                          "merged": [dict(pr(100 + i, ""), merged_at="2026-09-%02dT10:00:00Z" % (10 + i))
                                     for i in range(12)]}}
    page = render(reads)
    hold(page.count("<script") == 1 and "<script>%s</script>" % BOARD_JS in page and html.escape(evil) in page,
         "§8: text is escaped, and the page's one script is the board's own fixed text")
    hold("</" not in BOARD_JS, "the board's script carries nothing that could close its tag")
    # The timeline (his ruling, 1 October 2026), on Myst's made-up roadmap.
    myst = page[page.index('<span class="name">Myst</span>'):page.index('<span class="name">Phena</span>')]
    myst = myst[myst.index('<div class="depth">'):]
    hold('<span class="t">3 done</span>' in myst and myst.index("3 done") < myst.index("Item X1") <
         myst.index("Item X2") < myst.index("Item X3") < myst.index("Item X5"),
         "the timeline folds what is done into one line, first, in source order")
    hold(myst.count('<details class="item" open>') == 1 and
         myst.index('<details class="item" open>') < myst.index("Item X5") < myst.index("Item X6"),
         "the first item in hand opens at its sentence; nothing else does")
    hold(myst.index("Item X8") < myst.index("Item X9") < myst.index('<ol class="tl apart">') < myst.index("Item X4"),
         "in hand, then queued, on the line; suggested set apart after it")
    hold(myst.count('<details class="more">') == 10 and "Plain X5</p><details class=\"more\"><summary>More" in myst,
         "each item opens to its sentence, then to its detail behind More")
    hold("No roadmap: its plan is its open pull requests" in page, "Juku OS says why it carries no bar")
    # The spend card (his ruling, 1 October 2026), on 16 September of a 30-day month: 15 days gone.
    at = "2026-09-16T12:00:00Z"
    d = lambda n, usd: {"date": "2026-09-%02d" % n, "usage": usd}
    card = lambda days: spend_card(None if days is None else {"days": days}, at)
    ok_ = card([d(1, 5.0), d(9, 2.0), d(10, 2.0), d(15, 3.0), dict(d(16, 50.0)), {"date": "2026-08-31", "usage": 9.0}])
    hold("st-ok" in ok_ and "$12 <span>/ $40" in ok_ and "30% spent" in ok_ and "50% of cycle" in ok_ and
         "Projected $27 by 30 September" in ok_ and "15 days to reset" in ok_,
         "the card: this month's completed days only, against the month gone, at seven days' rate")
    hot = card([d(1, 22.0), d(14, 0.5)])
    hold("st-hot" in hot and "Projected $24 by 30 September" in hot, "running hot: ahead of the month, within budget at the recent rate")
    over = card([d(1, 10.0), d(12, 7.0), d(13, 7.0)])
    hold("st-over" in over and "Projected $54 · $14 over budget" in over, "overshooting names how far over")
    hold("st-none" in card(None) and "No OpenRouter key is connected" in card(None) and "$" + "0" not in card(None),
         "no key is said, never shown as nothing spent")
    hold("was not read this time" in spend_card({"unread": True}, at),
         "a key whose read failed is told apart from no key at all")
    hold("not in a shape the board reads" in card([{"date": "2026-09-01", "usage": "5"}]),
         "an answer it cannot read is said, never guessed at")
    hold('class="spend' in page and "No OpenRouter key is connected" in page, "the board carries the card, read or not")
    hold("<body data-board>" in page, "the marker #117's smoke test is to look for, so a board served to a stranger is caught")
    hold(readiness(pr(12, "**Priority:** **P2**. **Ready:** no — **Decision needed:** which host."))[2] == "P2",
         "a bolded priority reads as its level")
    hold("UNSELECTED BODY TEXT" not in page, "§8: a pull request's body is never published beyond its two lines")
    hold("javascript:" not in page and 'href="https://github.com/Adonis80/how-we-build/pull/111"' in page,
         "§8: only this repository's pull-request links are linked")
    hold(page.count('class="node s-done pr"') == MERGED_SHOWN and "#100 " not in page and "#101 " not in page,
         "§7: ten merged shown, newest first")
    hold("Snapshot checked 26 September 2026, 18:40 BST" in page or LONDON is None,
         "§5: the snapshot says its date, time and timezone")
    hold("Not reached yet" in page and "Revenue passes one thousand a month." in page,
         "§8: the money milestone's sentence and whether it is reached")
    hold("3 of 9 agreed done · 1 suggested" in page, "§1: a row's counts")
    hold("<dt>Agreed</dt><dd>the Chairman · 7 September 2026</dd>" in page or LONDON is None,
         "§4: `decided_on` is labelled agreed on, as an absolute date")
    hold([page.index('<span class="name">%s</span>' % r) for r in ROWS] ==
         sorted(page.index('<span class="name">%s</span>' % r) for r in ROWS), "§1: four rows, Juku OS first")
    hold(page.count('name="product"') == 4, "§9: one shared name, so one product opens at a time")
    hold(readiness(pr(14, "**Priority:** p1. **Ready:** yes."))[2] == "P1", "a lower-case priority reads, and sorts, as its level")
    hold(pr_state(pr(15, "**Priority:** P3. **Ready:** no — Decision needed: none.")) == "Parked" and
         not needs_decision({"gate": "Decision needed: none"}), "\"Decision needed: none\" asks him nothing")
    hold("Next eligible: Item 2" in headline(items_of("X", {"items": [it("1", "next", gate="Decision needed: which host."),
                                                                      it("2", "agreed")]})),
         "next eligible never names an item waiting on him")
    q = render(dict(reads, rulebook={"open": [pr(31, "**Priority:** P2. **Ready:** no — Decision needed: which host."),
                                              pr(32, ok)], "merged": []}))
    hold('<span class="pnum">1 queued</span>' in q, "the queue counts only what it lists, not what waits on him")
    for shape, what in (({"money_milestones": [{"when": "M"}]}, "money_milestones has no `items` list"),
                        ({"money_milestones": {"items": [{"reached_on": "2026-09-01"}]}},
                         "money_milestones.items[0].when is not text")):
        try:
            milestones("Myst", shape)
            bad.append("a money milestone in a shape it cannot read was dropped rather than refused (%s)" % what)
        except Unreadable as x:
            hold("Myst" in str(x) and what in str(x), "a milestone it cannot read names its key: %s" % x)
    hold(milestones("Myst", {"money_milestones": {"items": [{"when": "M", "reached_on": "2026-09-01"}]}}) ==
         [("M", True)] and milestones("Myst", {"items": []}) == [], "a reached milestone reads; none is none")
    hold(needs_decision({"gate": "**Decision needed:** the price."}),
         "§3: a bolded prefix asks him in a gate as in a pull request's Ready line")
    for rb, what in ((None, "no `open` and `merged` lists"), ({"open": [], "merged": {}}, "no `open` and `merged` lists"),
                     ({"open": [{"title": "t"}], "merged": []}, "open[0] has no number")):
        try:
            render(dict(reads, rulebook=rb))
            bad.append("the rulebook's reads, broken (%s), were shown" % what)
        except Unreadable as x:
            hold(what in str(x), "the rulebook's broken reads are refused: %s" % x)
    here = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    for inside in (os.path.join(here, "reads.json"), os.path.join(here, ".github", "index.html"), here):
        hold(inside_checkout(inside), "a path inside the checkout is refused: %s" % os.path.relpath(inside, here))
    hold(not inside_checkout(os.path.join(os.path.dirname(here), "elsewhere", "index.html")),
         "a path outside the checkout is written")
    try:
        with open(os.path.join(here, "README.md"), encoding="utf-8") as f:
            section = f.read().split("## Products under this rulebook", 1)[1].split("\n## ", 1)[0]
        mapped = tuple(re.findall(r"^- \*\*([^*]+)\*\* — ", section, re.M))
        hold(sorted(mapped) == sorted(ROWS[1:]),
             "ROWS names the README's products, no more and no fewer; §1 sets their order (got %s)" % (mapped,))
    except (OSError, IndexError):
        bad.append("the README's product map could not be read to hold ROWS to it")
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
              "prefix, §5's snapshot, %d cases of §7's readiness states, the queue's order and §8's contract — "
              "and refuses a roadmap it cannot read, naming the key and never the value" % len(states))
    return 1 if bad else 0


def inside_checkout(path):
    """True when `path` resolves inside this repository (#113's fourth read, 3)."""
    root = os.path.realpath(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    p = os.path.realpath(path)
    return p == root or p.startswith(root + os.sep)


def main(argv):
    if argv[1:] == ["--selftest"]:
        return _selftest()
    if len(argv) != 3:
        print("usage: build.py <reads.json> <index.html> | --selftest  (both outside the checkout)")
        return 2
    if any(inside_checkout(a) for a in argv[1:]):
        print("::error::the reads and the page are written outside this checkout, never in it: "
              "a private roadmap here is one `git add` from a public repository. Nothing was read.")
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
