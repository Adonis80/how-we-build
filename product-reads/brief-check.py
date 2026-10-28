#!/usr/bin/env python3
"""The design handoff's own guard (library/hypersolid.md, step 3; his ruling, 28 October 2026).

Every message to a screen designer (the Space visualizer, or Claude Design) passes
this before it is sent: a brief, a correction, or a frames ask. It holds what a
model reading the brief cannot be trusted to hold by remembering: the goal goes,
the plan never does (#266: "give it the map and let the visualiser come up with
the design ... dont dictate the visuals").

  brief-check.py brief FILE        a first brief
  brief-check.py correction FILE   one correction after a design came back
  brief-check.py frames FILE       the frames ask, once the look is accepted
  brief-check.py --selftest

Text in double quotes is exempt from the word list (his own words, or a name as
it stands on screen), never from the word count. Exit 0 passes; 1 names each fault.
"""
import re
import sys

VERBATIM = ("This is a professional operational workspace; clarity and confidence matter more "
            "than decoration. Choose the visual composition yourself. Use only this brief's names, "
            "figures and rules, never earlier chats; ordinary wording may be proposed, but show a "
            "missing fact as unknown and never invent a name, concept or figure.")

# The brief's slots, in order. "Look:" carries the tokens and is not counted.
SLOTS = ["Who:", "The job:", "What matters most:", "Real content:", "Rules:", "Look:"]
BRIEF_WORDS = 150      # every slot but Look and the verbatim line
MOST_ITEMS = 3         # "What matters most": at most three, separated by ";"
RULE_ITEMS = 3         # "Rules": at most three, separated by ";"
CORRECTION_WORDS = 40
FRAME_LINES = 6
FRAME_WORDS = 15

# The plan, never the goal: where things go, what they are drawn as, how they look,
# and what belongs to later steps (states, frames, the spoken path).
PLAN_WORDS = [
    # position and arrangement
    "above", "below", "beside", "beneath", "left", "right", "top", "bottom", "corner",
    "column", "columns", "row", "rows", "grid", "layout", "sidebar", "header", "footer",
    "next to", "underneath", "stacked", "sticky", "pinned to", "sideways", "scroll",
    "first frame", "second frame",
    # components
    "card", "cards", "tile", "tiles", "button", "buttons", "tab", "tabs", "dropdown",
    "drop-down", "modal", "popup", "pop-up", "chip", "chips", "pill", "pills", "badge",
    "badges", "banner", "toggle", "slider", "carousel", "accordion", "checkbox", "icon",
    "icons", "panel", "panels", "drawer", "bottom sheet", "toast", "stepper", "text box",
    # style and adjectives
    "clean", "modern", "sleek", "minimal", "minimalist", "bold", "elegant", "premium",
    "beautiful", "stunning", "calm", "dense", "spacious", "airy", "rounded", "square",
    "square-cornered", "uppercase", "hairline", "hairlines", "shadow", "gradient", "glass",
    "glassy", "font size", "type scale", "px", "padding", "margin",
    # later steps' content
    "spoken path", "frame", "frames", "state matrix", "states:", "parity",
]
# Allowed only in the frames ask: it names frames, and the spoken path is drawn there (step 4).
FRAMES_OK = {"frame", "frames", "spoken path"}


def unquoted(text):
    """The text outside double quotes (straight or curly)."""
    return re.sub(r'"[^"]*"|“[^”]*”', " ", text)


def words(text):
    return len(re.findall(r"[A-Za-z0-9£$€%.,'’+\-/:#()]+", text))


def plan_hits(text, allow=()):
    t = unquoted(text).lower()
    hits = []
    for w in PLAN_WORDS:
        if w in allow:
            continue
        if re.search(r"(?<![a-z0-9])" + re.escape(w) + r"(?![a-z0-9])", t):
            hits.append(w)
    return hits


def check_brief(text):
    faults = []
    body = text.replace(VERBATIM, "")
    if VERBATIM not in text:
        faults.append("the closing line is not there word for word")
    pos = [body.find(s) for s in SLOTS]
    for s, p in zip(SLOTS, pos):
        if p < 0:
            faults.append(f'slot "{s}" is missing')
    found = [p for p in pos if p >= 0]
    if found != sorted(found):
        faults.append("the slots are out of order: " + ", ".join(SLOTS))
    if pos[-1] >= 0:
        counted, look = body[:pos[-1]], body[pos[-1]:]
    else:
        counted, look = body, ""
    n = words(counted)
    if n > BRIEF_WORDS:
        faults.append(f"{n} words before Look; at most {BRIEF_WORDS}")

    def slot(name):
        i = body.find(name)
        if i < 0:
            return ""
        rest = body[i + len(name):]
        ends = [rest.find(s) for s in SLOTS if rest.find(s) >= 0]
        return rest[:min(ends)] if ends else rest

    for name, cap in (("What matters most:", MOST_ITEMS), ("Rules:", RULE_ITEMS)):
        items = [x for x in unquoted(slot(name)).split(";") if x.strip()]
        if len(items) > cap:
            faults.append(f'"{name}" has {len(items)} items; at most {cap}, separated by ";"')
    hits = plan_hits(counted)
    if hits:
        faults.append("plan, not goal (quote it if it is his own words): " + ", ".join(hits))
    if look and not re.search(r"#[0-9A-Fa-f]{6}", look):
        faults.append("Look carries no colour token")
    return faults


def check_correction(text):
    faults = []
    n = words(text)
    if n > CORRECTION_WORDS:
        faults.append(f"{n} words; a correction is at most {CORRECTION_WORDS}")
    if len([s for s in re.split(r"[.!?](?:\s|$)", text.strip()) if s.strip()]) > 2:
        faults.append("a correction is one sentence, two at most")
    hits = plan_hits(text)
    if hits:
        faults.append("paint, not a pointer back to the live picture or the missing fact: " + ", ".join(hits))
    return faults


def check_frames(text):
    faults = []
    lines = [l for l in text.splitlines() if l.strip()]
    head, items = (lines[0], lines[1:]) if lines and not re.match(r"\s*(\d+[.)]|[-*])", lines[0]) else ("", lines)
    if words(head) > 25:
        faults.append(f"the opening line is {words(head)} words; at most 25")
    if len(items) > FRAME_LINES:
        faults.append(f"{len(items)} frames asked; at most {FRAME_LINES} an ask")
    for i, l in enumerate(items, 1):
        if words(l) > FRAME_WORDS:
            faults.append(f"frame {i} is {words(l)} words; one line of at most {FRAME_WORDS} naming the moment")
    hits = plan_hits(text, allow=FRAMES_OK)
    if hits:
        faults.append("plan, not the moment to draw: " + ", ".join(hits))
    return faults


CHECKS = {"brief": check_brief, "correction": check_correction, "frames": check_frames}

GOOD_BRIEF = ("Design one phone screen for Hemz OS. Who: the owner. The job: set up a new shop. "
              "What matters most: where setup stands; the next thing to give. "
              "Real content: hourly rate £98.83. Rules: locking is the owner's own tap. "
              "Look: keep the live picture's feel; gold (#FFB01F) money. " + VERBATIM)


def selftest():
    cases = [
        ("brief", GOOD_BRIEF, True),
        ("brief", GOOD_BRIEF.replace("the next thing to give", "the next thing in a gold card"), False),
        ("brief", GOOD_BRIEF.replace("Real content: hourly rate £98.83.", "Real content: " + "word " * 160), False),
        ("brief", GOOD_BRIEF.replace(VERBATIM, ""), False),
        ("brief", GOOD_BRIEF.replace("Rules: locking", "Rules: a; b; c; locking"), False),
        ("brief", GOOD_BRIEF.replace("set up a new shop", '"swipe through every category"'), True),
        ("brief", GOOD_BRIEF.replace("Who: the owner. ", ""), False),
        ("correction", "Closer to the live picture on this page, which the owner prefers.", True),
        ("correction", "Use square-cornered boxes and uppercase labels like the live screen.", False),
        ("correction", "Closer to the live picture. " * 8, False),
        ("frames", "Now add, in order:\n1. Rate said, not yet locked\n2. Rate locked\n3. Staff open it", True),
        ("frames", "Add:\n" + "\n".join(f"{i}. moment" for i in range(1, 9)), False),
        ("frames", "Add:\n1. The rate in a gold card above the chart", False),
        ("frames", "Add:\n1. Spoken path, proposed: say the rate, hear it back", True),
        ("brief", GOOD_BRIEF.replace("the next thing to give", "the spoken path"), False),
    ]
    bad = 0
    for kind, text, ok in cases:
        got = not CHECKS[kind](text)
        if got != ok:
            bad += 1
            print(f"SELFTEST FAIL: {kind} expected {'pass' if ok else 'fail'}: {text[:70]!r}")
    print("selftest ok" if not bad else f"selftest: {bad} failed")
    return 1 if bad else 0


def main(argv):
    if argv[1:] == ["--selftest"]:
        return selftest()
    if len(argv) != 3 or argv[1] not in CHECKS:
        print(__doc__)
        return 2
    text = open(argv[2], encoding="utf-8").read()
    faults = CHECKS[argv[1]](text)
    for f in faults:
        print("FAIL:", f)
    print("pass" if not faults else f"{len(faults)} fault(s): fix before sending")
    return 1 if faults else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
