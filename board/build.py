#!/usr/bin/env python3
"""The Roadmap, rendered: read live when it is opened, or one JSON of reads in, one index.html out.

What the page shows and may claim is decision 0007 and its addendum
(https://github.com/Adonis80/how-we-build/issues/97); the section marks below
(§n, An) are its clauses. Above the pages, #222's proposals card (Option D), in place of
decision 0012's folded list: the open `proposal` issues here and every
product's `proposed` items in one queue (decision 0020), a view only.

DEPLOYED, IT IS THE ROADMAP'S FUNCTION (#222, his ruling, 15 October 2026: the
Roadmap "must not use deploys, use resources, or compete with a real product").
`.github/workflows/build-board.yml` deploys this file as `api/build.py`, behind
the PIN gate, only when the Roadmap's own code changes; each time the page is
opened, `handler` reads the products' roadmaps, this repository's pull requests
and open `proposal` issues, and OpenRouter's spend there and then, with GETs alone, and keeps the page a
minute. The keys are the project's own: ROADMAP_READ_TOKEN, a read-only GitHub
token, and OPENROUTER_KEY. A source that cannot be read is said on its page;
nothing a source holds reaches a log.

    python3 board/build.py <reads.json> <index.html>
    python3 board/build.py --selftest

Write both files outside the checkout: either one inside it is a `git add`
away from putting a private roadmap in this public repository.

The reads, in the shape `read_live` makes them:

    {"checked_at": "2026-09-26T17:40:00Z",
     "products": [{"name": "Hemz OS", "last_edited": "<ISO time>",
                   "roadmap": <roadmap.json on main, parsed>}, ...],
     "rulebook": {"open": [{"number", "title", "body", "draft", "created_at",
                            "url", "review": [{"status", "conclusion"}, ...]}],
                  "merged": [{"number", "title", "url", "merged_at"}, ...]},
     "proposals": [{"number", "title", "body", "created_at", "url"}, ...],
     "spend": {"days": [{"date": "YYYY-MM-DD", "usage": <USD>}, ...]}}

A product or the rulebook that could not be read is {"name": ..., "unread": true}
or {"unread": true}, and its page says so.

`spend` is OpenRouter's daily activity; null when no key is connected, and
{"unread": true} when a key is but the read failed. The card says which.

`review` is the juku-reviewer check runs on the pull request's head, newest
first. Of a body, only its `Priority:` and `Ready:` lines are published (§8); of a proposal's,
only its `Plain:` line or its priority's reason.
"""
import concurrent.futures
import html
import json
import os
import re
import sys
import time
import urllib.parse
import urllib.request
from datetime import datetime, timedelta, timezone
from http.server import BaseHTTPRequestHandler

try:
    from zoneinfo import ZoneInfo
    LONDON = ZoneInfo("Europe/London")
except Exception:  # no tz database: say UTC rather than guess
    LONDON = None

RULEBOOK = "Juku OS"
ROWS = (RULEBOOK, "Hemz OS", "Myst", "Phena")          # §1: four rows, this order
# THE PRODUCTS: the README's map, and nothing else; review-gate.py holds this list to the
# map both ways, and its names to ROWS.
PRODUCTS = (("Adonis80/Hemz-OS", "Hemz OS"), ("Adonis80/myst", "Myst"), ("Adonis80/phena", "Phena"))
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
    other, never dropped (#113's read): a milestone missing from his Roadmap is a false line."""
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
    word = STATUS_WORD.get(status, "Status not one the Roadmap reads")
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


def fold(count, word, inner, label=None):
    return ('<li class="node s-done fold"><details class="item"><summary><span class="t">%d %s</span>'
            '<span class="st">%s</span></summary>%s</details></li>' % (count, word, label or word.capitalize(), inner))


def unread_row(name, what):
    """A source that could not be read when the page opened: said, never shown as nothing."""
    return row(name, "Not read just now", "%s could not be read when this page opened. Open it again in a minute."
               % e(what), ""), 0


def product_row(p):
    name = p["name"]
    if p.get("unread"):
        return unread_row(name, "Its roadmap")
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
            group("Status not one the Roadmap reads", unknown) +
            ('<section><h3>Money milestone</h3><ul class="money">%s</ul></section>' % money if money else "") +
            '<p class="edited">Roadmap last edited %s</p>' % e(when(p["last_edited"])))
    return row(name, counts, headline(items), body, progress, "Roadmap · in sequence"), n["decisions"]


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
    if isinstance(rb, dict) and rb.get("unread"):
        return unread_row(RULEBOOK, "Its pull requests")
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
    progress = ('<div class="pprog"><span>No roadmap: its plan is its open pull requests</span>'
                '<span class="pnum">%d queued</span></div>' % len(queue))
    return row(RULEBOOK, counts, line, asks + spine, progress, "Pull requests · in sequence"), len(waiting)


# ---------------------------------------------------------------- proposals

# THE PROPOSALS CARD (his approval, 15 October 2026, #222: Option D). One card above the
# project pages: every open `proposal` issue here, and every product's `proposed` item, in
# one queue (decision 0020), on the same live read. Pure HTML and CSS, under 10 KB; it replaces decision 0012's folded list of suggested ideas.
ISSUE_LINK = re.compile(r"^https://github\.com/Adonis80/how-we-build/issues/[1-9][0-9]*$")
STAGES = (("b", "Being built"), ("w", "Waiting for debate"), ("a", "Agreed"))
# An open pull request that says it builds, closes, fixes, resolves or implements #N; one that only cites it does not.
BUILDS = re.compile(r"\b(?:builds|closes|fixes|resolves|implements)\s+\[?#([1-9][0-9]*)\b", re.I)
SHOWN = 6
DUE_COUNT, DUE_DAYS = 3, 7                              # decision 0020's trigger (trial thresholds)
PQ_CSS = (
    # His second look (16 October 2026): the layout kept, the colours started fresh as one dark
    # scheme. Neutral near-black surfaces and neutral ink; three stage colours from one validated
    # dark set (blue, amber, teal: lightness, chroma, colour-blind separation and contrast checked);
    # one blue the high-contrast accent; text never in a stage colour. Wider screens put each
    # row's stage and age on its title's line.
    ".pq{--bg:#141619;--row:#1b1e22;--line:rgba(255,255,255,.08);--ink:#f0efec;--ink2:#c3c2b7;--ink3:#898781;"
    "--b:#3987e5;--w:#c98500;--a:#199e70;--hi:#86b6ef;background:var(--bg);border:1px solid var(--line);"
    "border-radius:16px;padding:20px 18px;margin:0 0 16px;color:var(--ink)}"
    ".pq-h{display:flex;justify-content:space-between;align-items:baseline;gap:12px}.pq h2{margin:0;font-size:20px;"
    "font-weight:600;letter-spacing:-.01em}.pq-c{color:var(--ink2);font-size:14px}"
    ".pq-bar{display:flex;gap:2px;height:8px;margin:16px 0 12px}.pq-bar i{border-radius:4px}.pq-bar .e{flex:1;"
    "background:#2a2d33}.pq .b{--s:var(--b)}.pq .w{--s:var(--w)}.pq .a{--s:var(--a)}"
    ".pq-bar i,.pq-k li::before,.pq-p::before{background:var(--s)}"
    ".pq-k{display:flex;flex-wrap:wrap;gap:6px 18px;list-style:none;margin:0;padding:0;font-size:13px;color:var(--ink2)}"
    ".pq-k li::before,.pq-p::before{content:\"\";display:inline-block;width:8px;height:8px;border-radius:50%;margin-right:7px}"
    ".pq-k b{color:var(--ink);font-weight:600}"
    ".pq-due{margin:16px 0 0;border-radius:10px;background:rgba(201,133,0,.12);border:1px solid rgba(201,133,0,.45)}"
    ".pq-due summary{display:flex;align-items:center;gap:10px;padding:11px 12px;color:var(--ink);font-weight:600}"
    ".pq-due summary::before{content:\"!\";display:grid;place-items:center;flex:none;width:20px;height:20px;"
    "border-radius:50%;background:var(--w);color:#141619;font-size:13px;font-weight:700}"
    ".pq-due p{margin:0;padding:0 12px 12px 42px;color:var(--ink2)}"
    ".pq-l{list-style:none;margin:16px 0 0;padding:0;counter-reset:n var(--n0,0)}"
    ".pq-r{position:relative;padding-left:36px;counter-increment:n}.pq-r::before{content:counter(n);position:absolute;"
    "left:0;top:11px;width:24px;height:24px;border-radius:50%;display:grid;place-items:center;font-size:12px;"
    "background:#2a2d33;color:var(--ink2)}.pq-r::after{content:\"\";position:absolute;left:11.5px;top:37px;"
    "bottom:-5px;width:1px;background:#2a2d33}.pq-r:last-child::after{display:none}"
    ".pq-r details{border-radius:10px;background:var(--row);border:1px solid transparent;margin:0 0 8px}"
    ".pq-r summary{display:flex;flex-wrap:wrap;align-items:center;gap:6px 12px;padding:11px 12px;min-height:44px}"
    ".pq-r summary:hover{background:rgba(255,255,255,.03);border-radius:10px}"
    ".pq-t{flex:1 1 100%;font-weight:500;line-height:1.35}"
    ".pq-p{display:inline-flex;align-items:center;font-size:12px;padding:3px 9px;border-radius:999px;"
    "background:rgba(255,255,255,.06);color:var(--ink2)}.pq-a{font-size:13px;color:var(--ink3)}"
    ".pq-r p{margin:0;padding:0 12px 12px;color:var(--ink2);line-height:1.5}.pq-r a{color:var(--hi)}"
    ".p1::before{background:var(--b);color:#fff;box-shadow:0 0 0 3px rgba(57,135,229,.25)}"
    ".p1 details{border-color:rgba(57,135,229,.6);box-shadow:0 0 18px rgba(57,135,229,.18)}"
    ".pq-more>summary{color:var(--hi);padding:8px 0 0 36px;font-size:14px}.pq-0{color:var(--ink2);margin:0}"
    ".pq summary{cursor:pointer;list-style:none}.pq summary::-webkit-details-marker{display:none}"
    ".pq summary:focus-visible{outline:2px solid var(--hi);outline-offset:2px;border-radius:10px}"
    "@media (min-width:640px){.pq{padding:24px 24px}.pq-t{flex:1 1 auto}.pq-a{min-width:9em;text-align:right}}")


def level_of(text):
    """`Priority: P1` .. `P4`, emphasis dropped; anything else is no level, and sorts last."""
    m = field(text, "Priority", r"(P[1-4])\b")
    return m.group(1).upper() if m else None


def plain_of(body):
    """A proposal's one plain sentence: its `Plain:` line, else its Priority line's reason, else nothing."""
    m = field(body, "Plain", r"(.+)")
    if m:
        return m.group(1).strip()
    m = field(body, "Priority", r"P[1-4]\b[\s,.:—–-]*(?:[a-z][\w ,'-]*?\.\s+)?([A-Z].+?[.!?])(?:\s|$)")
    return m.group(1) if m else ""


def waited(iso, now):
    """How long it has waited, in whole days; None when its start is unknown."""
    try:
        t = datetime.fromisoformat(str(iso).replace("Z", "+00:00"))
    except (TypeError, ValueError):
        return None
    t = t if t.tzinfo else t.replace(tzinfo=timezone.utc)
    return max(0, (now - t).days)


def proposals_queue(issues, open_prs, ideas, now):
    """Decision 0020's one queue: the issues, staged and ranked, then each product's ideas."""
    building = set()
    for pr in open_prs or []:
        building |= {int(n) for n in BUILDS.findall("%s %s" % (pr.get("title"), pr.get("body")))}
    rows, ideas_rows = [], []
    for it in issues:
        body = it.get("body") or ""
        stage = "b" if it["number"] in building else \
            "a" if re.search(r"^\W*Decision:\W*agreed\b", body, re.I | re.M) else "w"
        rows.append({"stage": stage, "level": level_of(body), "title": it.get("title"), "plain": plain_of(body),
                     "url": it.get("url"), "who": RULEBOOK, "days": waited(it.get("created_at"), now),
                     "at": it.get("created_at") or ""})
    for name in ROWS:
        for it in ideas.get(name) or []:
            m = re.search(r"Captured (\d{4}-\d{2}-\d{2})", it.get("plain") or "")
            ideas_rows.append({"stage": "w", "level": None, "title": it["title"], "plain": it.get("plain") or "",
                         "url": None, "who": name, "days": waited(m.group(1), now) if m else None,
                         "at": m.group(1) if m else "~"})
    return sorted(rows, key=lambda r: (r["level"] or "P9", r["at"])) + sorted(ideas_rows, key=lambda r: r["at"])


def pq_row(r):
    days = "waiting %s" % ("today" if r["days"] == 0 else "1 day" if r["days"] == 1 else "%d days" % r["days"]) \
        if r["days"] is not None else "waiting, start not recorded"
    where = ' <a href="%s">Open ↗</a>' % e(r["url"]) if isinstance(r["url"], str) and ISSUE_LINK.match(r["url"]) else ""
    return ('<li class="pq-r %s%s"><details><summary><span class="pq-t">%s</span><span class="pq-p">%s</span>'
            '<span class="pq-a">%s · %s</span></summary><p>%s%s</p></details></li>'
            % (r["stage"], " p1" if r["level"] == "P1" else "", e(r["title"]), dict(STAGES)[r["stage"]],
               e(r["who"]), days, e(r["plain"] or "No plain sentence recorded yet."), where))


def proposals_card(issues, open_prs, ideas, now):
    """The card he approved: the count, the stage bar, the debate banner, the numbered queue."""
    if issues is None or isinstance(issues, dict) and issues.get("unread"):
        return ('<section class="pq" aria-label="Proposals"><div class="pq-h"><h2>Proposals</h2></div>'
                '<p class="pq-0">The proposals could not be read when this page opened.</p></section>')
    rows = proposals_queue(issues or [], open_prs, ideas, now)
    n = {k: sum(1 for r in rows if r["stage"] == k) for k, _ in STAGES}
    if not rows:
        return ('<section class="pq" aria-label="Proposals"><div class="pq-h"><h2>Proposals</h2><span class="pq-c">0 open'
                '</span></div><div class="pq-bar" role="img" aria-label="Nothing waiting"><i class="e"></i></div>'
                '<p class="pq-0">Nothing waiting</p></section>')
    label = ", ".join("%d %s" % (n[k], w.lower()) for k, w in STAGES)
    bar = "".join('<i class="%s" style="flex:%d"></i>' % (k, n[k]) for k, _ in STAGES if n[k])
    key = "".join('<li class="%s">%s <b>%d</b></li>' % (k, w, n[k]) for k, w in STAGES)
    waiting = [r for r in rows if r["stage"] == "w" and r["who"] == RULEBOOK]
    due = ""
    if len(waiting) >= DUE_COUNT or any((r["days"] or 0) >= DUE_DAYS for r in waiting):
        due = ('<details class="pq-due"><summary>Debate due - %d idea%s waiting</summary><p>A debate is due once %d '
               'proposals wait for it or one has waited %d days (decision 0020).</p></details>'
               % (len(waiting), "" if len(waiting) == 1 else "s", DUE_COUNT, DUE_DAYS))
    top = '<ol class="pq-l">%s</ol>' % "".join(pq_row(r) for r in rows[:SHOWN])
    more = ('<details class="pq-more"><summary>Show %d more</summary><ol class="pq-l" style="--n0:%d">%s</ol></details>'
            % (len(rows) - SHOWN, SHOWN, "".join(pq_row(r) for r in rows[SHOWN:]))) if len(rows) > SHOWN else ""
    return ('<section class="pq" aria-label="Proposals"><div class="pq-h"><h2>Proposals</h2><span class="pq-c">%d open'
            '</span></div><div class="pq-bar" role="img" aria-label="%s">%s</div><ul class="pq-k">%s</ul>%s%s%s</section>'
            % (len(rows), e(label), bar, key, due, top, more))


# ---------------------------------------------------------------- spend

# THE SPEND CARD (his ruling, 1 October 2026: "lift the freeze for the spend card";
# budget "$40", for all projects). OpenRouter is prepaid, so the cycle is the
# calendar month. A split per project later is this one setting.
BUDGET_USD = 40
DAY = re.compile(r"^\d{4}-\d{2}-\d{2}")
usd = lambda x: int(x + 0.5)                            # half up: $22.50 is $23, never banker's $22


def is_day(text):
    """A real calendar day: a date of the right shape that does not exist is unread, never a crash (#134's second read, 2)."""
    try:
        datetime.strptime(text, "%Y-%m-%d")
        return True
    except ValueError:
        return False


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
    stamp = "updated %d %s, %s %s" % (local.day, MONTHS[local.month - 1][:3], local.strftime("%H:%M"),
                                      local.tzname() or "UTC")
    last_day = "%d %s" % (days_in, month)
    rows = spend.get("days") if isinstance(spend, dict) else None
    ok = isinstance(rows, list) and all(isinstance(r, dict) and isinstance(r.get("date"), str) and
                                        DAY.match(r["date"]) and is_day(r["date"][:10]) and
                                        isinstance(r.get("usage"), (int, float)) and
                                        not isinstance(r.get("usage"), bool) for r in rows)
    if not ok:
        why = ("No OpenRouter key is connected" if spend is None else
               "OpenRouter's spend was not read this time" if isinstance(spend, dict) and spend.get("unread") else
               "OpenRouter's answer was not in a shape the Roadmap reads")
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
            '<p class="sp-proj">%s</p><p class="sp-basis">Spent to yesterday · based on the last 7 days</p><div class="sp-foot">'
            '<span>%s</span><span>%s</span></div></section>'
            % (state, chip, usd(spent), BUDGET_USD, usd(share), usd(time), e(month), fill - past, fill - past,
               past, time, usd(share), usd(time), e(proj), e(left), e(stamp)))


# ---------------------------------------------------------------- the page

def row(name, counts, line, body, progress="", seq=""):
    """One project page, the view he approved (1 October 2026): its name with ‹ › beside
    it, what it counts and what is in hand, overall progress, and its timeline. The Roadmap
    is these pages side by side, swiped or stepped through; render() adds the ‹ ›."""
    return ('<div class="crumb">Roadmap / Project</div><div class="ph"><h2 class="pname">%s</h2>{NAV}</div>'
            '<p class="psub">%s</p><p class="pline">%s</p>%s<h3 class="seq">%s</h3>%s'
            % (e(name), counts, line, progress, e(seq), body))


CSS = """:root{color-scheme:dark;--bg:#06070f;--bg2:#0a0b14;--panel:rgba(255,255,255,.035);--panel2:rgba(255,255,255,.06);--line:rgba(255,255,255,.1);--ink:#f2f4f7;--ink2:#a4adb8;--ink3:#6b7684;--cyan:#53eafd;--cyan-glow:rgba(103,232,249,.35);--mint:#5ee9b5;--grey:#3a4350;--dash:#4a5563;--sans:"Geist",system-ui,-apple-system,"Segoe UI",sans-serif;--mono:"Geist Mono",ui-monospace,SFMono-Regular,Menlo,monospace;--r:10px}
*{box-sizing:border-box}body{margin:0;background:var(--bg);background-image:radial-gradient(ellipse 80% 50% at 50% -10%,rgba(83,234,253,.07),transparent 60%);color:var(--ink);font-family:var(--sans);font-size:15px;line-height:1.5;padding-inline:16px;padding-block:22px 56px;-webkit-font-smoothing:antialiased;font-variant-numeric:tabular-nums}
.wrap{max-width:720px;margin:0 auto}.eyebrow,.id,.n,.st,.edited,.said{font-family:var(--mono);font-size:11px;letter-spacing:.08em;color:var(--ink3)}.eyebrow{letter-spacing:.22em;text-transform:uppercase}
h1{font-size:clamp(26px,6.5vw,34px);font-weight:600;letter-spacing:-.02em;line-height:1.15;margin:6px 0 10px}.lede{color:var(--ink);margin:10px 0 4px}.snap{font-family:var(--mono);font-size:12px;color:var(--ink3);margin:0 0 22px}

summary{cursor:pointer;list-style:none}summary::-webkit-details-marker{display:none}summary:focus-visible{outline:2px solid var(--cyan);outline-offset:2px;border-radius:var(--r)}

.ask{color:var(--cyan);font-weight:500}.dot{display:inline-block;width:8px;height:8px;border-radius:50%;background:var(--cyan);box-shadow:0 0 8px var(--cyan-glow);margin-right:8px;vertical-align:middle}
.bar{display:flex;height:6px;border-radius:3px;background:rgba(255,255,255,.05);overflow:hidden}.bar span{display:block;height:100%}.bar .done{background:var(--mint)}.bar .hand{background:var(--cyan)}.bar .queued{background:var(--grey)}
section{margin-top:16px}h3{font-size:12px;font-weight:500;letter-spacing:.14em;text-transform:uppercase;color:var(--ink2);margin:0 0 8px}
.item{border:1px solid var(--line);border-radius:8px;margin:0 0 8px;background:var(--bg2)}.item>summary{display:flex;flex-wrap:wrap;gap:4px 10px;align-items:baseline;padding:10px 12px}.item .t{flex:1 1 60%}.item .st{margin-left:auto}
.body{padding:0 12px 12px;color:var(--ink2)}.plain{color:var(--ink);margin:0 0 8px}dl{margin:0}dt{font-size:12px;color:var(--ink3);margin-top:8px}dd{margin:2px 0 0}.none{color:var(--ink3)}
.tabs{display:flex;gap:6px;overflow-x:auto;scrollbar-width:none;margin:0 0 12px}.tabs::-webkit-scrollbar{display:none}.tabs a{flex:none;font-size:14px;color:var(--ink2);text-decoration:none;border:1px solid var(--line);border-radius:999px;padding:8px 14px}.tabs a.on{color:var(--bg);background:var(--ink);border-color:var(--ink)}
.pages{display:flex;align-items:flex-start;overflow-x:auto;scroll-snap-type:x mandatory;scrollbar-width:none;transition:height .25s;margin:0 -16px;padding:0 16px;scroll-padding:0 16px;gap:16px}.pages::-webkit-scrollbar{display:none}
.page{flex:0 0 100%;min-width:0;scroll-snap-align:start;background:var(--bg);border:1px solid var(--line);border-radius:20px;padding:22px 20px 24px}
.crumb{font-family:var(--mono);font-size:12px;letter-spacing:.16em;text-transform:uppercase;color:var(--ink2);margin-bottom:18px}.pline{color:var(--ink);margin:6px 0 0}
.ph{display:flex;align-items:center;justify-content:space-between;gap:12px}.pname{font-size:clamp(30px,8vw,40px);font-weight:600;letter-spacing:-.03em;line-height:1.1;margin:0}.psub{color:var(--ink2);margin:8px 0 0}
.pnav{display:flex;gap:8px;flex:none}.step{display:grid;place-items:center;width:44px;height:44px;border-radius:50%;border:1px solid rgba(255,255,255,.18);color:var(--ink);font-size:22px;line-height:1;text-decoration:none}.step.off{opacity:.2}
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
@media (prefers-reduced-motion:reduce){.tl .item>summary::after,.pages{transition:none}}
.spend{background:var(--panel);border:1px solid var(--line);border-radius:16px;padding:22px 20px;margin:0 0 16px;--st:var(--mint)}.spend.st-hot{--st:#f2c46d}.spend.st-over{--st:#f39b86}.spend.st-none{--st:var(--ink3)}
.sp-head{display:flex;justify-content:space-between;align-items:baseline;gap:8px}.sp-title{font-size:17px;font-weight:600}.sp-chip{white-space:nowrap;font-size:14px;color:var(--st)}.sp-chip::before{content:"";display:inline-block;width:8px;height:8px;border-radius:50%;background:var(--st);margin-right:8px;vertical-align:middle}
.sp-big{font-size:44px;font-weight:400;letter-spacing:-.02em;line-height:1;margin:22px 0 22px}.sp-big span{font-size:16px;color:var(--ink2);letter-spacing:0;margin-left:8px}
.sp-track{position:relative;height:10px;border-radius:5px;background:var(--grey)}.sp-fill,.sp-past{position:absolute;top:0;bottom:0;border-radius:5px}.sp-fill{left:0;background:var(--st)}.st-hot .sp-fill,.st-over .sp-fill{opacity:.4}.sp-past{background:var(--st)}
.sp-mark{position:absolute;top:-7px;bottom:-7px;width:3px;margin-left:-1.5px;border-radius:2px;background:var(--ink);box-shadow:0 0 0 3px var(--panel)}
.sp-legend{display:flex;justify-content:space-between;font-family:var(--mono);font-size:13px;color:var(--ink2);margin-top:12px}.sp-pct{color:var(--st)}.sp-proj{color:var(--st);font-size:17px;font-weight:500;margin:20px 0 0}.sp-basis{color:var(--ink2);margin:4px 0 0}
.sp-foot{display:flex;flex-wrap:wrap;justify-content:space-between;white-space:nowrap;gap:4px 12px;border-top:1px solid var(--line);margin-top:24px;padding-top:14px;font-size:14px;color:var(--ink3)}
a{color:var(--cyan)}ul{margin:0;padding-left:18px}.hist li,.money li{margin:6px 0;color:var(--ink2)}.hit{color:var(--mint)}.open{color:var(--ink3)}.edited{margin-top:16px}"""


# Two conveniences on top of what opens without it (§9): a swipe, or the buttons,
# moves to the next or previous product, and a second tap on an open item's title
# opens its detail rather than closing it. Fixed text: nothing from a source reaches it.
BOARD_JS = """(function(){var box=document.querySelector('.pages');if(!box)return;var pages=[].slice.call(box.children),
tabs=[].slice.call(document.querySelectorAll('.tabs a')),cur=-1;
function fit(){var i=Math.round(box.scrollLeft/box.clientWidth);i=Math.max(0,Math.min(pages.length-1,i));box.style.height=pages[i].offsetHeight+'px';
if(i!==cur){cur=i;tabs.forEach(function(a,k){a.classList.toggle('on',k===i)})}}
box.addEventListener('scroll',function(){window.requestAnimationFrame(fit)},{passive:true});
if(window.ResizeObserver)pages.forEach(function(p){new ResizeObserver(fit).observe(p)});window.addEventListener('resize',fit);
[].forEach.call(document.querySelectorAll('a.step,.tabs a'),function(a){a.addEventListener('click',function(ev){var p=document.getElementById(a.getAttribute('href').slice(1));
if(!p)return;ev.preventDefault();p.scrollIntoView({block:'nearest',inline:'start',behavior:matchMedia('(prefers-reduced-motion: reduce)').matches?'auto':'smooth'});
var top=document.querySelector('.tabs').getBoundingClientRect().top;if(top<0)window.scrollBy(0,top-8)})});
[].forEach.call(document.querySelectorAll('.tl .item>summary'),function(s){s.addEventListener('click',function(ev){var it=s.parentNode,
m=it.querySelector(':scope>.body>.more');if(!m)return;if(it.open&&!m.open){ev.preventDefault();m.open=true}else if(it.open)m.open=false})});fit()})();"""


def render(reads):
    checked = when(reads["checked_at"], clock=True)
    now = datetime.fromisoformat(str(reads["checked_at"]).replace("Z", "+00:00"))
    rb = reads.get("rulebook")
    open_prs = rb.get("open") if isinstance(rb, dict) and isinstance(rb.get("open"), list) else []
    rows, asked, ideas = {}, {}, {}
    for p in reads.get("products") or []:
        if p.get("name") not in ROWS or p["name"] == RULEBOOK:
            raise Unreadable("a product named outside the Roadmap's pages")
        rows[p["name"]], asked[p["name"]] = product_row(p)
        ideas[p["name"]] = [] if p.get("unread") else [
            it for it in items_of(p["name"], p.get("roadmap")) if it["status"] == "proposed"]
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
    # THE ROADMAP IS THE PAGES (his ruling, 1 October 2026: "just build the UIs we agreed"):
    # the spend card, then one project page at a time, swiped sideways or stepped with
    # ‹ ›. Each step is a link to the next page, so it all moves without script too.
    ids = ["p-%d" % i for i in range(len(ROWS))]
    step = lambda i, ch, word: ('<a class="step" href="#%s" aria-label="%s %s">%s</a>' % (ids[i], word, e(ROWS[i]), ch)
                                if 0 <= i < len(ROWS) else '<span class="step off" aria-hidden="true">%s</span>' % ch)
    tabs = "".join('<a href="#%s"%s>%s</a>' % (ids[i], ' class="on"' if i == 0 else "", e(n)) for i, n in enumerate(ROWS))
    pages = "".join('<section class="page" id="%s" aria-label="%s">%s</section>'
                    % (ids[i], e(n), rows[n].replace("{NAV}", '<nav class="pnav">%s%s</nav>'
                                                    % (step(i - 1, "‹", "Back to"), step(i + 1, "›", "On to")), 1))
                    for i, n in enumerate(ROWS))
    return ('<!doctype html><html lang="en"><head><meta charset="utf-8">'
            '<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">\n'
            '<meta name="robots" content="noindex,nofollow"><meta name="theme-color" content="#06070f">\n'
            '<title>Juku Roadmap</title>\n'
            '<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n'
            '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Geist:wght@400;500;600&family=Geist+Mono:wght@400;500&display=swap">\n'
            '<style>%s</style></head>\n<body data-board><main class="wrap">'
            '<div class="eyebrow">Juku OS · Roadmap</div>'
            '<p class="lede">%s</p><p class="snap">Read live %s.</p>'
            '%s%s<nav class="tabs" aria-label="Projects">%s</nav><div class="pages">%s</div></main><script>%s</script>'
            '</body></html>\n' % (CSS + PQ_CSS, e(lede), e(checked), spend_card(reads.get("spend"), reads["checked_at"]),
                                   proposals_card(reads.get("proposals"), open_prs, ideas, now), tabs, pages, BOARD_JS))


# ---------------------------------------------------------------- the live read

# What the function reads, each time the page is opened (#222). GETs alone, each with a time
# limit, to two hosts: GitHub, with the read-only ROADMAP_READ_TOKEN, and OpenRouter's daily
# activity, the one read the spend card's management key is used for, never its keys.
GITHUB = "https://api.github.com"
SPEND_URL = "https://openrouter.ai/api/v1/activity"
RULEBOOK_REPO = "Adonis80/how-we-build"
REVIEWER_APP_ID = 5000405                              # the juku-reviewer App, as review-gate.py names it
REVIEWER_CHECK = "juku-reviewer"
READ_SECONDS = 5                                       # each request's limit; the function has 30 (vercel.json)
KEEP_SECONDS = 60                                      # the page kept between opens: the short cache
BRANCH = re.compile(r"^[A-Za-z0-9._/-]+$")
SHA = re.compile(r"^[0-9a-f]{40}$")


class _Stay(urllib.request.HTTPRedirectHandler):
    """A redirect is refused, never followed: the key would go with it, wherever it pointed (#223's read)."""

    def redirect_request(self, *args, **kwargs):
        return None


_OPEN = urllib.request.build_opener(_Stay)


def _get(url, key, raw=False):
    """One GET with a time limit: parsed JSON, or the bytes with `raw`. Nothing else is ever sent."""
    head = {"Authorization": "Bearer " + key, "User-Agent": "juku-build-board"}
    if url.startswith(GITHUB + "/"):
        head["Accept"] = "application/vnd.github.raw+json" if raw else "application/vnd.github+json"
    with _OPEN.open(urllib.request.Request(url, headers=head), timeout=READ_SECONDS) as r:
        body = r.read()
    return body if raw else json.loads(body)


# What a read that fails can throw: a refusal, a lost answer, or an answer not in shape.
MISSED = (OSError, ValueError, KeyError, IndexError, TypeError, AttributeError, Unreadable)


def read_product(get, token, repo, name):
    """One product's roadmap on its main, and when it was last edited; or unread."""
    try:
        main = get("%s/repos/%s" % (GITHUB, repo), token)["default_branch"]
        if not BRANCH.match(main or ""):
            raise ValueError
        ref = urllib.parse.quote(main, safe="")
        road = json.loads(get("%s/repos/%s/contents/roadmap.json?ref=%s" % (GITHUB, repo, ref), token, raw=True))
        if not isinstance(road, dict):
            raise ValueError
        items_of(name, road)
        milestones(name, road)
        edited = get("%s/repos/%s/commits?path=roadmap.json&sha=%s&per_page=1" % (GITHUB, repo, ref),
                     token)[0]["commit"]["committer"]["date"]
        return {"name": name, "last_edited": str(edited), "roadmap": road}
    except MISSED:
        return {"name": name, "unread": True}


def read_rulebook(get, token, pool):
    """This repository's own pull requests, open with the reviewer's check runs, and merged; or unread.

    A fork's is left off his Roadmap (this repository is public). Each check run is kept only if
    it is the reviewer's by App and name, on this head, as the gate's check_run_verdict keeps
    it, not on the query's word (#113's fourth read); newest first (§7)."""
    own = lambda p: ((p.get("head") or {}).get("repo") or {}).get("full_name") == RULEBOOK_REPO
    try:
        pulls = [p for p in get("%s/repos/%s/pulls?state=open&per_page=100" % (GITHUB, RULEBOOK_REPO), token) if own(p)]

        def one(p):
            sha = p["head"]["sha"]
            if not SHA.match(sha or ""):
                raise ValueError
            runs = get("%s/repos/%s/commits/%s/check-runs?check_name=%s&app_id=%d&filter=all&per_page=100"
                       % (GITHUB, RULEBOOK_REPO, sha, REVIEWER_CHECK, REVIEWER_APP_ID), token)["check_runs"]
            runs = sorted((r for r in runs if (r.get("app") or {}).get("id") == REVIEWER_APP_ID and
                           r.get("name") == REVIEWER_CHECK and r.get("head_sha") == sha),
                          key=lambda r: r.get("started_at") or "", reverse=True)
            return {"number": p["number"], "title": p.get("title"), "body": p.get("body") or "",
                    "draft": bool(p.get("draft")), "created_at": p.get("created_at"), "url": p.get("html_url"),
                    "review": [{"status": r.get("status"), "conclusion": r.get("conclusion")} for r in runs]}
        open_ = list(pool.map(one, pulls))
        closed = get("%s/repos/%s/pulls?state=closed&sort=updated&direction=desc&per_page=50" % (GITHUB, RULEBOOK_REPO), token)
        merged = [{"number": p["number"], "title": p.get("title"), "url": p.get("html_url"), "merged_at": p["merged_at"]}
                  for p in closed if p.get("merged_at") and own(p)]
        return {"open": open_, "merged": merged}
    except MISSED:
        return {"unread": True}


def read_proposals(get, token):
    """This repository's open issues labelled `proposal`, pull requests left out (the API lists both); or unread."""
    try:
        got = get("%s/repos/%s/issues?labels=proposal&state=open&per_page=100" % (GITHUB, RULEBOOK_REPO), token)
        return [{"number": int(i["number"]), "title": i.get("title"), "body": i.get("body") or "",
                 "created_at": i.get("created_at"), "url": i.get("html_url")} for i in got if "pull_request" not in i]
    except MISSED:
        return {"unread": True}


def read_spend(get, key):
    """OpenRouter's daily activity: null with no key, unread when the read fails."""
    if not key:
        return None
    try:
        return {"days": [{"date": r["date"], "usage": r["usage"]} for r in get(SPEND_URL, key)["data"]]}
    except MISSED:
        return {"unread": True}


def read_live(env, get=_get, clock=time.time):
    """Every source at once, stamped before the first is asked (#117's second read, 6)."""
    at = datetime.fromtimestamp(clock(), timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    token = env.get("ROADMAP_READ_TOKEN") or ""
    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:
        if token:
            products = [pool.submit(read_product, get, token, repo, name) for repo, name in PRODUCTS]
            rulebook = pool.submit(read_rulebook, get, token, pool)
            proposals = pool.submit(read_proposals, get, token)
        spend = pool.submit(read_spend, get, env.get("OPENROUTER_KEY") or "")
        return {"checked_at": at,
                "products": [f.result() for f in products] if token else [{"name": n, "unread": True} for _, n in PRODUCTS],
                "rulebook": rulebook.result() if token else {"unread": True},
                "proposals": proposals.result() if token else {"unread": True},
                "spend": spend.result()}


_kept = {"at": None, "page": None}


def page_now(env=None, get=_get, clock=time.time):
    """The Roadmap as it stands, read again once the page kept is a minute old."""
    if _kept["page"] is not None and clock() - _kept["at"] < KEEP_SECONDS:
        return _kept["page"]
    page = render(read_live(os.environ if env is None else env, get, clock))
    _kept.update(at=clock(), page=page)
    return page


FAILED = ('<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="robots" content="noindex,nofollow">'
          '<meta name="viewport" content="width=device-width,initial-scale=1"><title>Juku Roadmap</title></head>'
          '<body style="background:#06070f;color:#f2f4f7;font-family:system-ui,sans-serif;padding:24px">'
          '<p>The Roadmap could not be drawn just now. Open it again in a minute.</p></body></html>')


class handler(BaseHTTPRequestHandler):
    """The host's entry point: every open, behind the PIN gate, gets the Roadmap read live."""

    def do_GET(self):
        try:
            body, code = page_now().encode("utf-8"), 200
        except Exception:  # never a trace: it could carry what a source holds
            body, code = FAILED.encode("utf-8"), 503
        self.send_response(code)
        for k, v in (("Content-Type", "text/html; charset=utf-8"), ("Cache-Control", "private, no-store"),
                     ("X-Robots-Tag", "noindex, nofollow"), ("Content-Length", str(len(body)))):
            self.send_header(k, v)
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *args):
        pass                                           # the host's log gets no request lines


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
         "§8: text is escaped, and the page's one script is the Roadmap's own fixed text")
    hold("</" not in BOARD_JS, "the Roadmap's script carries nothing that could close its tag")
    # The timeline (his ruling, 1 October 2026), on Myst's made-up roadmap.
    myst = page[page.index('<h2 class="pname">Myst</h2>'):page.index('<h2 class="pname">Phena</h2>')]
    myst = myst[myst.index('<h3 class="seq">'):]
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
    hold("not in a shape the Roadmap reads" in card([{"date": "2026-09-01", "usage": "5"}]),
         "an answer it cannot read is said, never guessed at")
    hold("not in a shape the Roadmap reads" in card([d(1, 5.0), {"date": "2026-09-31", "usage": 1.0}]),
         "a day that does not exist is said as unread, never stops the Roadmap")
    hold("Spent to yesterday · based on the last 7 days" in ok_ and "to yesterday" not in card(None) and
         ("updated 16 Sep, 13:00 BST" in ok_ or LONDON is None),
         "the card says its figure runs to yesterday, and its stamp carries the timezone (#135's read, 2)")
    hold('class="spend' in page and "No OpenRouter key is connected" in page, "the Roadmap carries the card, read or not")
    hold("<body data-board>" in page, "the marker #117's smoke test is to look for, so a Roadmap served to a stranger is caught")
    hold(readiness(pr(12, "**Priority:** **P2**. **Ready:** no — **Decision needed:** which host."))[2] == "P2",
         "a bolded priority reads as its level")
    hold("UNSELECTED BODY TEXT" not in page, "§8: a pull request's body is never published beyond its two lines")
    hold("javascript:" not in page and 'href="https://github.com/Adonis80/how-we-build/pull/111"' in page,
         "§8: only this repository's pull-request links are linked")
    hold(page.count('class="node s-done pr"') == MERGED_SHOWN and "#100 " not in page and "#101 " not in page,
         "§7: ten merged shown, newest first")
    hold("Read live 26 September 2026, 18:40 BST." in page or LONDON is None,
         "§5: the page says when it was read, its date, time and timezone")
    hold("Not reached yet" in page and "Revenue passes one thousand a month." in page,
         "§8: the money milestone's sentence and whether it is reached")
    hold("3 of 9 agreed done · 1 suggested" in page, "§1: a row's counts")
    hold("<dt>Agreed</dt><dd>the Chairman · 7 September 2026</dd>" in page or LONDON is None,
         "§4: `decided_on` is labelled agreed on, as an absolute date")
    hold([page.index('<h2 class="pname">%s</h2>' % r) for r in ROWS] ==
         sorted(page.index('<h2 class="pname">%s</h2>' % r) for r in ROWS), "§1: four projects, Juku OS first")
    hold(page.count('<section class="page"') == 4 and 'href="#p-1" aria-label="On to Hemz OS"' in page and
         '<span class="step off" aria-hidden="true">‹</span>' in page and "{NAV}" not in page,
         "the Roadmap is four project pages, each stepping to its neighbours by a link that needs no script")
    # THE PROPOSALS CARD (his approval, 15 October 2026, #222's Option D): the rulebook's open
    # `proposal` issues and every product's `proposed` items in one queue above the pages.
    edit = lambda rd: {"name": rd[0], "last_edited": "2026-09-25T17:00:00Z", "roadmap": {"items": rd[1]}}
    iss = lambda n, body, at="2026-09-20T10:00:00Z", **kw: dict({"number": n, "title": "Issue %d" % n, "body": body,
                                                                "created_at": at,
                                                                "url": "https://github.com/Adonis80/how-we-build/issues/%d" % n}, **kw)
    issues = [iss(301, "Priority: P3 — build. Plain: The third, waiting.", at="2026-09-01T00:00:00Z"),
              iss(302, "Priority: P1 — a proven defect. Plain: The first, being built."),
              iss(303, "Priority: P2 — repair. A sentence in the priority line.\nDecision: agreed, 2026-09-21."),
              iss(304, "No level at all.", title=evil, url="javascript:alert(1)")]
    rb = dict(reads["rulebook"], open=reads["rulebook"]["open"] + [pr(120, "Builds #302. " + ok)])
    q2 = render(dict(reads, rulebook=rb, proposals=issues, products=[
        edit(("Phena", [it("P1", "proposed", title="Phena idea", plain="Captured 2026-09-24; why.")])),
        edit(("Myst", road["items"])),
        edit(("Hemz OS", [it("H1", "proposed", title="Hemz idea"), it("H3", "building")]))]))
    card = q2[q2.index('<section class="pq"'):q2.index('<nav class="tabs"')]
    hold(card.index(html.escape(evil)) < card.index("Hemz idea") and card.index(html.escape(evil)) < card.index("Phena idea") and
         card.index("Phena idea") < card.index("Item X4"), "the card: every product's ideas after every issue, oldest first")
    cited = proposals_queue([iss(310, "Priority: P3 — build.")], [pr(130, "As #310 says, and on #222. " + ok)], {}, datetime(2026, 9, 26, tzinfo=timezone.utc))
    hold(cited[0]["stage"] == "w", "the card: a pull request that only cites a proposal does not make it being built")
    hold("could not be read when this page opened" in proposals_card(None, [], {}, datetime(2026, 9, 26, tzinfo=timezone.utc)),
         "the card: reads with no proposals at all say so, never nothing waiting")
    hold(card.index("Issue 302") < card.index("Issue 303") < card.index("Issue 301") < card.index(html.escape(evil)) and
         evil not in card and "javascript:" not in card,
         "the card: ranked by priority, then oldest; no level sorts last; escaped; only this repository's issue links")
    hold('<li class="pq-r b p1">' in card and card.count(" p1") == 1 and '<li class="pq-r a">' in card and
         card.count('<li class="pq-r w') == 5, "the card: an issue an open pull request names is being built, a "
         "`Decision: agreed` line is agreed, the rest wait for debate; P1 alone glows")
    hold("The first, being built." in card and "A sentence in the priority line." in card and
         "No plain sentence recorded yet." in card, "the card: each row's one sentence, from its Plain line or its priority's reason")
    hold("7 open" in card and 'aria-label="1 being built, 5 waiting for debate, 1 agreed"' in card and
         "Show 1 more" in card, "the card: its count and its stage bar by stage, the seventh row folded")
    hold("Debate due - 2 ideas waiting" in card and "waiting 25 days" in card and "Phena" in card and "Hemz OS" in card,
         "the card: debate due when one proposal has waited 7 days, the rule behind the tap; products' ideas beside them")
    many = render(dict(reads, proposals=[iss(400 + i, "Priority: P4 — observe.", at="2026-09-26T00:00:00Z") for i in range(9)]))
    many = many[many.index('<section class="pq"'):many.index('<nav class="tabs"')]
    hold(many.count('<li class="pq-r') == 10 and "Show 4 more" in many and "Debate due - 9 ideas waiting" in many and
         "waiting today" in many, "the card: the top six shown, the rest folded under Show N more")
    hold(len((PQ_CSS + many).encode("utf-8")) < 10240, "the card is under 10 KB with ten rows, its styles included")
    empty = render(dict(reads, proposals=[], products=[edit(("Hemz OS", [])), edit(("Myst", [])), edit(("Phena", []))]))
    hold("Nothing waiting" in empty and 'class="e"' in empty and "Debate due" not in empty, "the card: empty, a grey bar and Nothing waiting")
    hold("could not be read when this page opened" in render(dict(reads, proposals={"unread": True})),
         "the card: proposals that could not be read are said")
    hold(q2.count('<section class="page"') == 4 and "0 of 1 agreed done · 1 suggested" in q2 and
         "3 of 9 agreed done · 1 suggested" in q2 and "<script" not in card,
         "the card adds no page, changes no count, and needs no script")
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
        bad.append("a Roadmap missing a row was rendered")
    except Unreadable as x:
        hold("Phena" in str(x), "a missing row names itself")
    # THE LIVE READ (#222): every source asked with GETs alone, each to its own host with its own
    # key; a fork's pull request and another App's check run left off; a source that fails said
    # on its page while the rest still show; no read key, the Roadmap still opens and says so.
    def fake(fail=()):
        calls = []
        sha = "a" * 40
        prs = [{"number": 41, "title": "Ours", "body": ok, "draft": False, "created_at": "2026-10-01T00:00:00Z",
                "html_url": "https://github.com/Adonis80/how-we-build/pull/41",
                "head": {"sha": sha, "repo": {"full_name": RULEBOOK_REPO}}},
               {"number": 42, "title": "A fork's", "body": ok, "html_url": "https://github.com/Adonis80/how-we-build/pull/42",
                "head": {"sha": "b" * 40, "repo": {"full_name": "stranger/how-we-build"}}}]
        runs = {"check_runs": [
            {"app": {"id": REVIEWER_APP_ID}, "name": REVIEWER_CHECK, "head_sha": sha, "status": "completed",
             "conclusion": "success", "started_at": "2026-10-01T01:00:00Z"},
            {"app": {"id": 15368}, "name": REVIEWER_CHECK, "head_sha": sha, "status": "completed",
             "conclusion": "failure", "started_at": "2026-10-01T02:00:00Z"},
            {"app": {"id": REVIEWER_APP_ID}, "name": REVIEWER_CHECK, "head_sha": "c" * 40, "status": "completed",
             "conclusion": "failure", "started_at": "2026-10-01T03:00:00Z"}]}

        def get(url, key, raw=False):
            calls.append((url, key, raw))
            if any(f in url for f in fail):
                raise OSError("refused")
            if url == SPEND_URL:
                return {"data": [{"date": "2026-10-01", "usage": 1.5, "model": "kept out"}]}
            path = url[len(GITHUB):].split("?")[0]
            if path.endswith("/contents/roadmap.json"):
                return json.dumps({"items": [it("R1", "building"), it("R2", "proposed")]}).encode()
            if "/commits/" in path:
                return runs
            if path.endswith("/commits"):
                return [{"commit": {"committer": {"date": "2026-10-02T09:00:00Z"}}}]
            if path.endswith("/issues"):
                return [{"number": 50, "title": "A proposal", "body": "Priority: P2 — repair.", "created_at": "2026-10-01T00:00:00Z",
                         "html_url": "https://github.com/Adonis80/how-we-build/issues/50"},
                        {"number": 51, "title": "A pull request the issues list carries", "pull_request": {}}]
            if path.endswith("/pulls"):
                return prs if "state=open" in url else [dict(prs[0], merged_at="2026-10-03T00:00:00Z"),
                                                        dict(prs[1], merged_at="2026-10-03T00:00:00Z")]
            return {"default_branch": "main"}
        return get, calls

    env = {"ROADMAP_READ_TOKEN": "read-key", "OPENROUTER_KEY": "spend-key"}
    get, calls = fake()
    live = read_live(env, get, clock=lambda: 1790000000)
    hold(live["checked_at"] == "2026-09-21T14:13:20Z" and [p.get("name") for p in live["products"]] == list(ROWS[1:]) and
         all(p.get("last_edited") == "2026-10-02T09:00:00Z" for p in live["products"]),
         "the live read: stamped by the clock before it reads, each product on the map read, by name")
    hold(all(k == ("spend-key" if u == SPEND_URL else "read-key") for u, k, _ in calls) and
         all(u.startswith(GITHUB + "/") or u == SPEND_URL for u, _, _ in calls) and
         sum(1 for u, _, _ in calls if u == SPEND_URL) == 1,
         "the live read: GitHub asked with the read key alone, OpenRouter once, with its key alone")
    hold([p["number"] for p in live["rulebook"]["open"]] == [41] and [p["number"] for p in live["rulebook"]["merged"]] == [41] and
         live["rulebook"]["open"][0]["review"] == [{"status": "completed", "conclusion": "success"}],
         "the live read: a fork's pull request left off; only the reviewer's own check run, on this head, kept")
    hold(live["spend"] == {"days": [{"date": "2026-10-01", "usage": 1.5}]}, "the live read: of the spend, its days alone")
    hold([i["number"] for i in live["proposals"]] == [50] and any("labels=proposal&state=open" in u for u, _, _ in calls),
         "the live read: the open `proposal` issues, a pull request the list carries left out")
    hold("<body data-board>" in render(live) and "Item R1" in render(live), "the live read renders as the Roadmap")
    get, calls = fake(fail=("Adonis80/myst",))
    half = render(read_live(env, get))
    myst = half[half.index('<h2 class="pname">Myst</h2>'):half.index('<h2 class="pname">Phena</h2>')]
    hold("Its roadmap could not be read when this page opened" in myst and "Item R1" not in myst and
         half.count("Item R1") == 4, "a product that cannot be read is said on its page; the others still show")
    get, calls = fake(fail=(SPEND_URL, "/pulls", "/issues"))
    down = read_live(env, get)
    hold(down["spend"] == {"unread": True} and down["rulebook"] == {"unread": True} and down["proposals"] == {"unread": True} and
         "Its pull requests could not be read" in render(down), "a spend or pull-request read that fails is said, never guessed")
    get, calls = fake()
    none = read_live({}, get)
    hold(not [u for u, _, _ in calls] and none["spend"] is None and all(p.get("unread") for p in none["products"]) and
         "No OpenRouter key is connected" in render(none), "no keys: nothing is asked, and the Roadmap opens saying so")
    bent = {"items": [{"title": "t", "gate": 3}]}
    get, calls = fake()
    hold(read_product(lambda u, k, raw=False: json.dumps(bent).encode() if raw else get(u, k), "k", "Adonis80/myst", "Myst")
         == {"name": "Myst", "unread": True}, "a roadmap not in shape reads as unread, never as a broken Roadmap")
    hold(_Stay().redirect_request(None, None, 302, "Found", {}, "https://elsewhere.example/") is None and
         any(isinstance(h, _Stay) for h in _OPEN.handlers), "the live read follows no redirect, so no key leaves its host")
    tick = [1000.0]
    get, calls = fake()
    _kept.update(at=None, page=None)
    first = page_now(env, get, clock=lambda: tick[0])
    n = len(calls)
    tick[0] += KEEP_SECONDS - 1
    hold(page_now(env, get, clock=lambda: tick[0]) is first and len(calls) == n, "the page is kept for a minute between opens")
    tick[0] += 2
    page_now(env, get, clock=lambda: tick[0])
    hold(len(calls) == 2 * n, "and read again once the minute is up")
    _kept.update(at=None, page=None)
    for b in bad:
        print("  roadmap: " + b)
    if not bad:
        print("ok: the Roadmap renders decision 0007 from its reads — §1's four rows, §2's denominator, §3's "
              "prefix, §5's snapshot, %d cases of §7's readiness states, the queue's order and §8's contract — "
              "and refuses a roadmap it cannot read, naming the key and never the value; and its live read asks "
              "each source with GETs alone, its own key to its own host, keeps the page a minute, and says what it could not read"
              % len(states))
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
        print("::error::the Roadmap was not rendered: %s. Nothing is deployed; the last snapshot stands." % x)
        return 1
    except (OSError, ValueError, KeyError, TypeError) as x:
        print("::error::the Roadmap was not rendered: the reads were not in shape (%s). Nothing is deployed."
              % type(x).__name__)
        return 1
    with open(argv[2], "w", encoding="utf-8") as f:
        f.write(page)
    print("rendered %d bytes" % len(page.encode("utf-8")))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
