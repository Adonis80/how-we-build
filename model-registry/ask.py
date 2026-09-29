#!/usr/bin/env python3
"""One read through an OpenAI-compatible endpoint, for a role the registry resolves.

    ask.py REGISTRY ROLE SYSTEM_FILE SCHEMA_JSON SECONDS < prompt > answer.json

The interface is the chat-completions one that OpenRouter, a LiteLLM proxy and
most direct providers all speak, so the provider is an entry in the registry and
never code (decision 0008). Where a provider takes the effort, and anything else
it wants in the body, is the registry's too (`effort_param`, `extra`).

The answer is written in the Claude Code tool's own shape, so the reviewer
workflows read either caller the same way: on success
{"result": <the verdict as JSON text>, "model", "usage": {"input_tokens",
"output_tokens"}, "total_cost_usd"}, exit 0; otherwise {"is_error": true,
"subtype", "result": <what went wrong, in the provider's words>}, exit 1.

No silent substitution: an answer from any model but the one pinned is refused,
exactly as if the provider had not answered. Nothing here prints the prompt, the
answer or the key. Standard library only.

No silent loss either (#115, 26 September 2026: twice a `blocking` verdict was
published whose review stopped at "one finding below", 9,389 and 6,492 tokens
out, while full reads of the same commits carried the findings). Every
top-level object in the answer that decodes whole and carries a verdict is
found, braces in the prose around it notwithstanding, and the worst one speaks,
as the gate's own verdict() keeps the worst. A refusal whose object decodes
whole is kept with the prose the model wrote beside it, however short, and says
so if the provider cut the answer off for length: such a refusal is never
handed to a reader who might clear the change (#110). A clearance is taken only
when it is the one verdict in the answer, whole, with next to nothing beside it;
otherwise it is no answer, and its fallback reads. The job's summary gets the
answer's shape, so the next stub says which way it came.

ITS LIMIT (#116's second read). A refusal whose own object does not decode —
cut off inside it, or broken by a raw line break or an unescaped quote — is
found by nothing here, is no answer, and goes to the fallback as it always
did. Closing that is its own change.
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


# Words beside a clearance past this many characters, not counting whitespace
# or fences, are the model writing outside its verdict rather than a wrapper
# such as "Here it is:" — so a one-sentence finding beside a clearance sends
# the read to the fallback (#116's second read: 200 let one through, and its
# example, "Blocking: the key is printed on line 42.", is 33). A wordy wrapper
# costs a fallback read; it never clears a change.
OUTSIDE_BAR = 30


def verdicts(content):
    """(every JSON object carrying a verdict, in order; the text around them).

    Each `{` is decoded where it stands, so a brace in the prose — `${{ … }}`,
    a quoted dict — neither hides the object nor spoils it.
    """
    if not isinstance(content, str):
        return [], ""
    dec, found, prose, i, kept = json.JSONDecoder(), [], [], 0, 0
    while True:
        j = content.find("{", i)
        if j < 0:
            break
        try:
            obj, end = dec.raw_decode(content, j)
        except ValueError:
            i = j + 1
            continue
        if isinstance(obj, dict) and "verdict" in obj:
            found.append(obj)
            prose.append(content[kept:j])
            kept = end
        i = end
    prose.append(content[kept:])
    around = "\n\n".join(p.strip() for p in prose if p.strip())
    return found, re.sub(r"```(?:json)?", "", around).strip()


def outside(prose):
    return len(re.sub(r"\s", "", prose or "")) > OUTSIDE_BAR


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
    found, prose = verdicts(content)
    # No number in a `result` below: the workflow's why() reads 401, 403, 429
    # and 529 in it as the provider's own refusals (#116's first read).
    refusal = next((v for v in found if v.get("verdict") == "blocking"), None)
    if refusal is not None:
        # The worst verdict speaks, and keeps every word beside it (#110, #116).
        said = dict(refusal)
        if prose or cut:
            said["review"] = ("%s\n\n---\n*%s*%s" % (
                said.get("review") or "",
                "Written outside the verdict object, and kept by the caller so the refusal "
                "carries its findings" + (", as far as the answer went before the provider cut "
                                          "it off for length" if cut else "") + ":" if prose else
                "The provider cut this answer off for length after the words above.",
                "\n\n" + prose if prose else ""))
        text = json.dumps(said)
    elif cut:
        return {"is_error": True, "subtype": "truncated",
                "result": "the model ran out of room before its answer ended, so its verdict is not taken"}, 1
    elif not found:
        return {"is_error": True, "subtype": "no_verdict",
                "result": "the model answered no verdict object"}, 1
    elif len(found) > 1 or outside(prose):
        return {"is_error": True, "subtype": "outside",
                "result": "the model wrote beside its verdict object, so a verdict that would clear "
                          "the change is not taken"}, 1
    else:
        text = json.dumps(found[0])
    return {"result": text, "model": served, "provider": resp.get("provider", ""),
            "usage": {"input_tokens": usage.get("prompt_tokens"),
                      "output_tokens": usage.get("completion_tokens")},
            "total_cost_usd": usage.get("cost")}, 0


def main(argv):
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
        found, prose = verdicts(content)
        with open(path, "a", encoding="utf-8") as f:
            f.write("caller: finish %s; %d verdict object(s); answer %d characters, %d beside the "
                    "object; reasoning %s tokens\n" % (finish, len(found), len(content), len(prose),
                                                        thought if isinstance(thought, int) else "unknown"))
    except Exception:  # a diagnostic never costs a verdict
        pass


if __name__ == "__main__":
    sys.exit(main(sys.argv))
