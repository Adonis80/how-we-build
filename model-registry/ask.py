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


def verdict_text(content):
    """The answer's JSON object as text: fenced or wrapped in prose, it is unwrapped."""
    if not isinstance(content, str):
        return None
    for text in (content, re.sub(r"^\s*```(?:json)?\s*|\s*```\s*$", "", content)):
        try:
            return json.dumps(json.loads(text))
        except ValueError:
            pass
    start, end = content.find("{"), content.rfind("}")
    if 0 <= start < end:
        try:
            return json.dumps(json.loads(content[start:end + 1]))
        except ValueError:
            pass
    return None


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
        content = resp["choices"][0]["message"]["content"]
    except (KeyError, IndexError, TypeError):
        content = None
    text = verdict_text(content)
    if text is None:
        return {"is_error": True, "subtype": "no_verdict",
                "result": "the model answered no verdict object"}, 1
    usage = resp.get("usage") or {}
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
    return out(obj, rc)


if __name__ == "__main__":
    sys.exit(main(sys.argv))
