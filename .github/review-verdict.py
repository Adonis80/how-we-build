#!/usr/bin/env python3
"""Turn the reviewer's answer into one of two words, or refuse.

The workflow writes the verdict line itself, from this. So this is the point
where a run that went wrong has to become a red gate rather than a quiet clean
pass, and every shape it does not recognise is a refusal.

Read on stdin: the envelope `claude -p --output-format json` prints. Written on
stdout: `clean` or `findings`, and nothing else. The review itself goes to the
path given as the first argument.
"""

import json
import sys

VERDICTS = ("clean", "findings")


def extract(envelope):
    """(verdict, review) — or ValueError, which is a red gate.

    `--json-schema` makes the model answer in the shape below, but the envelope
    carries it as either an object or the JSON text of one depending on how the
    run ended, and a run that failed carries `is_error` with a string result. So
    every one of those is handled here, and anything else is refused by name.
    """
    if not isinstance(envelope, dict):
        raise ValueError("the reviewer did not return an envelope")
    if envelope.get("is_error"):
        raise ValueError("the reviewer returned an error: %s"
                         % str(envelope.get("result"))[:200])
    out = envelope.get("result")
    if isinstance(out, str):
        try:
            out = json.loads(out)
        except ValueError:
            raise ValueError("the reviewer's answer was not the two fields, but prose")
    if not isinstance(out, dict):
        raise ValueError("the reviewer did not return the two fields")
    verdict = out.get("verdict")
    review = out.get("review")
    if verdict not in VERDICTS:
        raise ValueError("the reviewer returned no verdict this gate understands: %r" % (verdict,))
    if not isinstance(review, str) or not review.strip():
        raise ValueError("the reviewer returned a verdict with no review under it")
    return verdict, review.strip()


def _selftest():
    ok = {"verdict": "clean", "review": "I read it against the rulebook."}
    cases = [
        ({"result": ok}, ("clean", "I read it against the rulebook."), "the answer as an object"),
        ({"result": json.dumps(ok)}, ("clean", "I read it against the rulebook."),
         "the same answer as JSON text"),
        ({"result": json.dumps({"verdict": "findings", "review": "The cap is spent twice."})},
         ("findings", "The cap is spent twice."), "findings"),
        ({"is_error": True, "result": "overloaded"}, ValueError, "a run that errored"),
        ({"result": "Looks good to me!"}, ValueError, "prose instead of the two fields"),
        ({"result": json.dumps({"verdict": "approve", "review": "x"})}, ValueError,
         "a verdict this gate does not know"),
        ({"result": json.dumps({"verdict": "CLEAN", "review": "x"})}, ValueError,
         "the right word in the wrong case"),
        ({"result": json.dumps({"verdict": "clean"})}, ValueError, "a verdict with no review"),
        ({"result": json.dumps({"verdict": "clean", "review": "   "})}, ValueError,
         "a verdict with an empty review"),
        ({"result": None}, ValueError, "an empty result"),
        ({}, ValueError, "an envelope with nothing in it"),
        ([], ValueError, "not an envelope at all"),
    ]
    bad = 0
    for envelope, want, what in cases:
        try:
            got = extract(envelope)
        except ValueError:
            got = ValueError
        if got != want:
            bad += 1
            print("  selftest: %s — expected %s, got %s" % (what, want, got))
    if bad:
        print("review-verdict selftest failed: %d case(s)" % bad)
        return 1
    print("ok: the reviewer's answer becomes one of two words, and %d other shapes are refused"
          % sum(1 for c in cases if c[1] is ValueError))
    return 0


def main(argv):
    if len(argv) == 2 and argv[1] == "--selftest":
        return _selftest()
    if len(argv) != 2:
        print("usage: review-verdict.py <review-out-path> | --selftest", file=sys.stderr)
        return 2
    try:
        verdict, review = extract(json.load(sys.stdin))
    except ValueError as e:
        print(str(e), file=sys.stderr)
        return 1
    except Exception as e:  # malformed JSON on stdin is the same kind of refusal
        print("the reviewer's answer could not be read: %s" % e, file=sys.stderr)
        return 1
    with open(argv[1], "w", encoding="utf-8") as f:
        f.write(review + "\n")
    sys.stdout.write(verdict)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
