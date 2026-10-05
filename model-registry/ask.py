#!/usr/bin/env python3
"""One read through an OpenAI-compatible endpoint, for a role the registry resolves.

    ask.py REGISTRY ROLE SYSTEM_FILE SCHEMA_JSON SECONDS < prompt > answer.json
    ask.py derive ANSWER_FILE

The interface is the chat-completions one that OpenRouter, a LiteLLM proxy and
most direct providers all speak, so the provider is an entry in the registry and
never code (decision 0008). Where a provider takes the effort, and anything else
it wants in the body, is the registry's too (`effort_param`, `extra`).

The answer is written in the Claude Code tool's own shape, so the reviewer
workflows read either caller the same way: on success
{"result": <the model's answer, as written>, "model", "usage": {"input_tokens",
"output_tokens"}, "total_cost_usd"}, exit 0, with "stop_reason": "max_tokens"
when the provider cut it off for length; otherwise {"is_error": true,
"subtype", "result": <what went wrong, in the provider's words>}, exit 1.

No silent substitution: an answer from any model but the one pinned is refused,
exactly as if the provider had not answered. Nothing here prints the prompt, the
answer or the key. Standard library only.

THE VERDICT IS DERIVED, NEVER GIVEN (decision 0014, position C, replacing the
model's own verdict word, whose last signed value on #148's round 4 said
blocking over a text that said nothing blocks). The model returns findings,
each with a severity, blocking or advisory, and a review; `ask.py derive FILE`
rewrites an answer file, whichever caller wrote it, so that its `result` is the
verdict the findings make: any blocking finding, blocking; else any finding,
advisory; else clean. It is the one place a verdict is made. A field called
`verdict` in the model's answer is ignored, and the summary says so, except
that one saying blocking over findings that do not is a clearance not taken.
Nothing in the prose is read for meaning.

It fails closed. A missing, malformed, unknown-severity or cut-off answer
signs no clearance, and its fallback reads. A refusal is never handed to a
reader who might clear the change (#110): every blocking finding is found
however the answer is wrapped (braces in the prose around it, a raw line break
inside it, a wrapper object around it), the worst speaks, the refusal keeps
every other word of the answer, and an answer that says `"severity":
"blocking"` in the open but will not decode (cut off inside it, or broken by an
unescaped quote) is signed as a refusal with the whole answer for its review
(#115, #116, #119). A clearance is taken only when it is the one answer, whole,
with nothing beside it but fences. The job's summary gets the answer's shape.

ITS LIMIT (#116's third read). If #115's findings were in the model's
reasoning rather than its answer, nothing here recovers them, and a stub is
still published as a refusal without them: which it was is not established
until a shape line shows it, so #115 is not closed by this file.
"""
import json
import os
import re
import sys
import urllib.error
import urllib.request

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import resolve  # noqa: E402  (the registry's own resolver, beside this file)


def _set(body, dotted, value):
    """body[a][b] = value for dotted 'a.b'."""
    keys = dotted.split(".")
    for k in keys[:-1]:
        body = body.setdefault(k, {})
    body[keys[-1]] = value


def _merge(into, extra):
    for k, v in extra.items():
        if isinstance(v, dict) and isinstance(into.get(k), dict):
            _merge(into[k], v)
        else:
            into[k] = v


def served_is_pinned(served, pinned):
    """The model that answered is the one pinned, or its own dated snapshot of it."""
    return bool(re.fullmatch(re.escape(pinned) + r"(-\d{8})?", served or ""))


SEVERITIES = ("blocking", "advisory")
# A kept refusal's review is cut here: the workflow posts it whole as a comment,
# which GitHub refuses past 65,536 characters (#116's third read).
KEPT_CAP = 50000
# `"severity": "blocking"` in the open, its first quote not escaped: inside any
# JSON string it could only appear escaped, so a review that quotes it does not
# match. The retired `"verdict": "blocking"` counts too, for an answer that
# will not decode: a refusal in either spelling is never lost.
REFUSAL_SAID = re.compile(r'(?<!\\)"(?:severity|verdict)"\s*:\s*"blocking"', re.I)


def severity(f):
    """A finding's severity, whatever its case ("Blocking" is a refusal); "" for what is no finding."""
    return str(f.get("severity", "")).strip().lower() if isinstance(f, dict) else ""


def _carrying(obj):
    """Every object carrying findings, at any depth: a wrapper hides none."""
    if isinstance(obj, dict):
        if "findings" in obj:
            yield obj
        for v in obj.values():
            yield from _carrying(v)
    elif isinstance(obj, list):
        for v in obj:
            yield from _carrying(v)


def answers(content):
    """(every object carrying findings, in order; the text around them, as written).

    Each `{` is decoded where it stands, leniently — a raw line break inside a
    string is read rather than refused — so a brace in the prose neither hides
    an object nor spoils it.
    """
    if not isinstance(content, str):
        return [], ""
    dec, found, prose, i, kept = json.JSONDecoder(strict=False), [], [], 0, 0
    while True:
        j = content.find("{", i)
        if j < 0:
            break
        try:
            obj, end = dec.raw_decode(content, j)
        except ValueError:
            i = j + 1
            continue
        inner = list(_carrying(obj))
        if inner:
            found.extend(inner)
            prose.append(content[kept:j])
            kept = end
        i = end
    prose.append(content[kept:])
    return found, "\n\n".join(p.strip() for p in prose if p.strip())


def beside(prose):
    """What was written beside the answer, fences and whitespace aside: weighed, never published so."""
    return re.sub(r"\s", "", re.sub(r"```[A-Za-z]*", "", prose or ""))


def _listed(answer):
    """The findings an answer carries, as a list: anything else is no list."""
    fs = answer.get("findings")
    return fs if isinstance(fs, list) else []


def _typed(findings):
    """The findings as they are posted: severity and text, nothing the model added."""
    return [{"severity": severity(f) or "unknown", "text": str(f.get("text") or "") if isinstance(f, dict) else str(f)}
            for f in findings]


def kept_refusal(found, prose, cut, content):
    """The refusal to sign, carrying every word of the answer it came in."""
    refusals = [a for a in found if any(severity(f) == "blocking" for f in _listed(a))]
    if not refusals:
        return {"verdict": "blocking", "findings": [],
                "review": "*The answer said blocking, but its findings did not decode%s. The caller signs it "
                "as a refusal and keeps the whole answer as its review:*\n\n%s"
                % (", and the provider cut it off for length" if cut else "", content.strip())}
    first = refusals[0]
    review = str(first.get("review") or "")
    others = [str(a.get("review") or "").strip() for a in refusals[1:] + [a for a in found if a not in refusals]]
    words = "\n\n".join(w for w in others + [prose] if w)
    if words or cut:
        review = "%s\n\n---\n*%s*%s" % (
            review,
            "Written beside the findings, and kept by the caller so the refusal carries its findings"
            + (", as far as the answer went before the provider cut it off for length" if cut else "") + ":"
            if words else "The provider cut this answer off for length after the words above.",
            "\n\n" + words if words else "")
    # No review at all stays no review: the signer fails a refusal with none, as it
    # did before #110, and an empty string would read as one.
    return dict({"verdict": "blocking", "findings": _typed([f for a in found for f in _listed(a)])},
                **({"review": review} if review else {}))


def derive(content, cut=False):
    """(the verdict object, None), or (None, (subtype, why)) for an answer that clears nothing.

    The verdict is made here from the findings alone. No number goes in a
    `why`: the workflow's why() reads 401, 403, 429 and 529 in it as the
    provider's own refusals (#116's first read).
    """
    content = content if isinstance(content, str) else ""
    found, prose = answers(content)
    if not found:
        if REFUSAL_SAID.search(content):
            return kept_refusal(found, prose, cut, content), None
        if cut:
            return None, ("truncated", "the model ran out of room before its answer ended, so its verdict is not taken")
        return None, ("no_verdict", "the model answered no findings object")
    own = [str(a["verdict"]).strip().lower() for a in found if "verdict" in a]
    blocked = any(severity(f) == "blocking" for a in found for f in _listed(a))
    if blocked:
        # The worst speaks, and keeps every word of the answer (#110, #116).
        refusal = kept_refusal(found, prose, cut, content)
        refusal["ignored"] = ["verdict"] if own else []
        if len(refusal.get("review", "")) > KEPT_CAP:
            refusal["review"] = refusal["review"][:KEPT_CAP] + \
                "\n\n*The rest is cut by the caller: a comment holds only so much.*"
        return refusal, None
    if cut:
        return None, ("truncated", "the model ran out of room before its answer ended, so its verdict is not taken")
    findings = [f for a in found for f in _listed(a)]
    if (any(not isinstance(a.get("findings"), list) or not isinstance(a.get("review"), str) for a in found)
            or any(severity(f) not in SEVERITIES or not str(f.get("text") or "").strip() for f in findings)):
        return None, ("malformed", "the model answered findings or a review outside the schema")
    if len(found) > 1 or beside(prose):
        return None, ("outside", "the model wrote beside its answer object, so a verdict that would clear "
                                 "the change is not taken")
    if "blocking" in own:
        return None, ("disagrees", "the model's own word was blocking over findings that do not make it so, "
                                   "so a verdict that would clear the change is not taken")
    return {"verdict": "advisory" if findings else "clean", "review": found[0]["review"],
            "findings": _typed(findings), "ignored": ["verdict"] if own else []}, None


def build(got, provider, system, prompt, schema):
    """The request body for one read."""
    body = {
        "model": got["model"],
        "messages": [{"role": "system", "content": system}, {"role": "user", "content": prompt}],
        "response_format": {"type": "json_schema",
                            "json_schema": {"name": "verdict", "strict": True, "schema": schema}},
    }
    _set(body, provider.get("effort_param") or "reasoning_effort", got["effort"])
    _merge(body, provider.get("extra") or {})
    return body


def answer(resp, pinned):
    """(answer dict, exit status) from a provider's parsed response."""
    if not isinstance(resp, dict):
        return {"is_error": True, "subtype": "no_answer", "result": "the provider answered no object"}, 1
    if resp.get("error"):
        e = resp["error"]
        said = e.get("message", "") if isinstance(e, dict) else str(e)
        code = e.get("code", "") if isinstance(e, dict) else ""
        return {"is_error": True, "subtype": "provider_error",
                "result": "the provider refused (%s): %s" % (code, said)}, 1
    served = str(resp.get("model", ""))
    if not served_is_pinned(served, pinned):
        return {"is_error": True, "subtype": "wrong_model",
                "result": "answered by %r, not the pinned %r" % (served, pinned)}, 1
    try:
        choice = resp["choices"][0]
        content = choice["message"]["content"]
    except (KeyError, IndexError, TypeError):
        choice, content = {}, None
    usage = resp.get("usage") or {}
    cut = isinstance(choice, dict) and choice.get("finish_reason") == "length"
    # What the model wrote is handed on as written; the verdict is made from it
    # by derive(), the same way for either caller. No number in a `result`
    # below: why() reads 401, 403, 429 and 529 in it as the provider's own
    # refusals (#116's first read).
    if not isinstance(content, str) or not content.strip():
        return {"is_error": True, "subtype": "no_verdict",
                "result": "the model answered no content"}, 1
    out = {"result": content, "model": served, "provider": resp.get("provider", ""),
           "usage": {"input_tokens": usage.get("prompt_tokens"),
                     "output_tokens": usage.get("completion_tokens")},
           "total_cost_usd": usage.get("cost")}
    if cut:
        out["stop_reason"] = "max_tokens"
    return out, 0


def derive_file(path):
    """Rewrite an answer file in place: its `result` becomes the derived verdict, or says why none is.

    Whichever caller wrote the file, a read the tool failed is left as the tool
    left it, and anything else is judged by derive() alone. Whatever goes wrong
    here is an answer with no verdict, never an answer the model's own words
    could pass for one.
    """
    try:
        with open(path, encoding="utf-8") as f:
            obj = json.load(f)
    except (OSError, ValueError):
        obj = None
    if not isinstance(obj, dict):
        obj = {"is_error": True, "subtype": "no_answer", "result": "the read left no answer to make a verdict from"}
    elif obj.get("is_error"):
        # A read the tool failed carries the tool's words and no object the model
        # could have written a verdict in: that is no answer, whatever it holds.
        try:
            if isinstance(json.loads(obj.get("result")), (dict, list)):
                obj["result"] = ""
        except (TypeError, ValueError):
            pass
    else:
        # The tool's own schema-checked answer, where it gives one, is what the
        # model answered; the text beside it is not.
        structured = obj.get("structured_output")
        content = json.dumps(structured) if isinstance(structured, dict) else obj.get("result")
        got, why = derive(content, obj.get("stop_reason") == "max_tokens")
        if got is None:
            obj = dict({k: v for k, v in obj.items() if k not in ("result", "structured_output")},
                       is_error=True, subtype=why[0], result=why[1])
            note("derived no verdict: the answer was %s" % why[0])
        else:
            obj = dict({k: v for k, v in obj.items() if k not in ("structured_output", "result")}, result=json.dumps(got))
            note("derived %s from %d finding(s)%s" % (
                got["verdict"], len(got["findings"]),
                "; the model's own verdict field was ignored" if got.get("ignored") else ""))
    tmp = path + ".derived"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(obj, f)
        f.write("\n")
    os.replace(tmp, path)


def note(text):
    """A line to the job's summary alone, never to stderr and never at the cost of a verdict."""
    try:
        path = os.environ.get("GITHUB_STEP_SUMMARY")
        if path:
            with open(path, "a", encoding="utf-8") as f:
                f.write("caller: %s\n" % text)
    except Exception:  # a diagnostic never costs a verdict
        pass


def main(argv):
    if len(argv) == 3 and argv[1] == "derive":
        derive_file(argv[2])
        return 0
    if len(argv) != 6:
        print(__doc__.strip().split("\n\n")[1], file=sys.stderr)
        return 2
    registry, role, system_file, schema_json, seconds = argv[1:6]

    def out(obj, rc):
        json.dump(obj, sys.stdout)
        sys.stdout.write("\n")
        if rc:
            print("ask: %s" % obj.get("result", ""), file=sys.stderr)
        return rc

    try:
        reg = resolve.load(registry)
        got = resolve.resolve(reg, role)
    except (OSError, ValueError, resolve.Unresolved) as e:
        return out({"is_error": True, "subtype": "unresolved", "result": str(e)}, 1)
    if got["interface"] != "openai-compatible":
        return out({"is_error": True, "subtype": "unresolved",
                    "result": "%s is served through %s, not this caller" % (role, got["interface"])}, 1)
    key = os.environ.get(got["credential"], "")
    if not key:
        return out({"is_error": True, "subtype": "no_credential",
                    "result": "no %s in the reviewer environment" % got["credential"]}, 1)
    provider = reg["providers"][got["provider"]]
    with open(system_file, encoding="utf-8") as f:
        system = f.read()
    body = build(got, provider, system, sys.stdin.read(), json.loads(schema_json))
    req = urllib.request.Request(
        got["base_url"].rstrip("/") + "/chat/completions",
        data=json.dumps(body).encode("utf-8"),
        headers={"Authorization": "Bearer " + key, "Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=max(30, int(seconds) - 5)) as r:
            resp = json.load(r)
    except urllib.error.HTTPError as e:
        try:
            said = json.load(e).get("error", {}).get("message", "")
        except (ValueError, AttributeError):
            said = ""
        return out({"is_error": True, "subtype": "http_error",
                    "result": "HTTP %s from %s: %s" % (e.code, got["provider"], said)}, 1)
    except (urllib.error.URLError, OSError, ValueError) as e:
        return out({"is_error": True, "subtype": "unreachable",
                    "result": "%s could not be reached: %s" % (got["provider"], e)}, 1)
    obj, rc = answer(resp, got["model"])
    shape(resp)
    return out(obj, rc)


def shape(resp):
    """The answer's shape, to the job's summary alone.

    Never to stderr, which the workflow's why() reads for 401, 403, 429 and 529
    (#116's second read), and never at the cost of a verdict: whatever goes
    wrong here is swallowed, since the answer is already decided.
    """
    try:
        path = os.environ.get("GITHUB_STEP_SUMMARY")
        if not path:
            return
        choice = resp["choices"][0]
        content = choice["message"]["content"] or ""
        finish = re.sub(r"[^a-z_]", "", str(choice.get("finish_reason") or "none").lower())[:20]
        details = (resp.get("usage") or {}).get("completion_tokens_details") or {}
        thought = details.get("reasoning_tokens")
        found, prose = answers(content)
        with open(path, "a", encoding="utf-8") as f:
            f.write("caller: finish %s; %d answer object(s); answer %d characters, %d beside the "
                    "object; reasoning %s tokens\n" % (finish, len(found), len(content), len(prose),
                                                        thought if isinstance(thought, int) else "unknown"))
    except Exception:  # a diagnostic never costs a verdict
        pass


if __name__ == "__main__":
    sys.exit(main(sys.argv))
