#!/usr/bin/env python3
"""One read through an OpenAI-compatible endpoint, for a role the registry resolves.

    ask.py REGISTRY ROLE SYSTEM_FILE SCHEMA_JSON SECONDS < prompt > answer.json
    ask.py derive ANSWER_FILE
    ask.py incomplete ANSWER_FILE
    ask.py record open LEDGER ROLE MODEL INTERFACE      prints the attempt's id
    ask.py record close LEDGER ATTEMPT EXIT ANSWER_FILE
    ask.py record summary LEDGER

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

A READ THAT NEEDS MORE SAYS SO (decision 0014, F(2)). A finding of severity
`needs-context` names at most NEEDED files the read was not given. With no
blocking finding beside it, the verdict is `needs-context`: the workflow signs
nothing, adds those files and reads once more, and `ask.py incomplete FILE`
turns a second shortfall into a refusal, "incomplete read: needed X". A real
blocking finding always speaks first.

ONE RECORD PER ATTEMPT (decision 0014, A). `record open` writes an attempt to
the job's ledger before its request is sent; the caller writes what the
provider returned, usage and generation id, before the answer is parsed; and
`record close` ends it with its outcome. A record never closed, or closed with
its response lost, is unresolved. Cash (a provider billed per request) and plan
(an allowance) are kept apart and never added; a cost not known is `unknown`,
never 0. A route refused before sending opens no record.

THE SPENDING CHECK (decision 0014, D). Before any cash request, primary,
fallback or re-read: settled cash this week, from the provider's own key
endpoint, plus what is reserved in flight, plus this request's most it can cost,
must not pass the weekly limit (the secret REVIEW_CASH_WEEKLY), nor the key's
own remaining limit. Every request carries an output-token limit and a price
limit, so its most is known. Unknown headroom means no request. A refusal, here
or the provider's own limit, is `budget_refused`: the read parks, and nothing
falls back. What the Chairman holds privately, the weekly limit, the key's
limit, the headroom and the week's settled spend, reaches no log from here;
each request's own reported cost does, on the spend line, as it has since
decision 0008.

ITS LIMIT (#116's third read). If #115's findings were in the model's
reasoning rather than its answer, nothing here recovers them, and a stub is
still published as a refusal without them: which it was is not established
until a shape line shows it, so #115 is not closed by this file.
"""
import json
import os
import re
import sys
import time
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


SEVERITIES = ("blocking", "advisory", "needs-context")
# A read that needs more names at most this many files, and is given them once.
NEEDED = 3
# What the workflow publishes is cut here, on every path: one comment holds the
# review, the findings beneath it and a spend line, and GitHub refuses a comment
# past 65,536 characters (#116's third read; #119's first read: a comment it
# refused skips the wake, and a blocking verdict sits unseen under a green). So a
# review is cut at REVIEW_CAP, a finding's text at FINDING_CAP, and no more than
# FINDINGS_SHOWN findings go in, blocking ones first; the verdict counts them all.
REVIEW_CAP = 40000
FINDING_CAP = 500
FINDINGS_SHOWN = 30
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


def _cut(text, cap):
    """The text, cut to `cap` characters with a marker where it was."""
    return text if len(text) <= cap else text[:cap] + "\n\n*The rest is cut by the caller: a comment holds only so much.*"


def _shown(findings):
    """(the findings as they are posted, how many are left out): severity and text, nothing the model added.

    Blocking ones first, so a long list never hides one; each text is cut, and
    only so many go in. The verdict is made from all of them, before this.
    """
    typed = [{"severity": severity(f) or "unknown",
              "text": str(f.get("text") or "") if isinstance(f, dict) else str(f)} for f in findings]
    typed.sort(key=lambda f: {"blocking": 0, "needs-context": 1, "advisory": 2}.get(f["severity"], 3))
    for f in typed[:FINDINGS_SHOWN]:
        if len(f["text"]) > FINDING_CAP:
            f["text"] = f["text"][:FINDING_CAP] + " [cut]"
    return typed[:FINDINGS_SHOWN], max(0, len(typed) - FINDINGS_SHOWN)


# A path the read may ask for: relative, inside the repository, plain characters.
PATH = re.compile(r"(?!/)(?!.*(?:^|/)\.\.(?:/|$))[A-Za-z0-9._/-]{1,200}")


def _files(f):
    """The files a finding names, as a list of strings; [] for none or a shape that is no list."""
    fs = f.get("files") if isinstance(f, dict) else None
    return [str(x) for x in fs if isinstance(x, str) and x.strip()] if isinstance(fs, list) else []


def needed(findings):
    """The files the needs-context findings name, each once, in order, only paths a read may fetch, at most NEEDED."""
    out = []
    for f in findings:
        for p in _files(f):
            p = p.strip()
            if PATH.fullmatch(p) and p not in out:
                out.append(p)
    return out[:NEEDED]


def kept_refusal(found, prose, cut, content):
    """The refusal to sign, carrying every word of the answer it came in (cut to what a comment holds)."""
    refusals = [a for a in found if any(severity(f) == "blocking" for f in _listed(a))]
    if not refusals:
        review = ("*The answer said blocking, but its findings did not decode%s. The caller signs it "
                  "as a refusal and keeps the whole answer as its review:*\n\n%s"
                  % (", and the provider cut it off for length" if cut else "", content.strip()))
    else:
        review = str(refusals[0].get("review") or "")
        others = [str(a.get("review") or "").strip() for a in refusals[1:] + [a for a in found if a not in refusals]]
        words = "\n\n".join(w for w in others + [prose] if w)
        if words or cut:
            review = "%s\n\n---\n*%s*%s" % (
                review,
                "Written beside the findings, and kept by the caller so the refusal carries its findings"
                + (", as far as the answer went before the provider cut it off for length" if cut else "") + ":"
                if words else "The provider cut this answer off for length after the words above.",
                "\n\n" + words if words else "")
    shown, omitted = _shown([f for a in found for f in _listed(a)])
    # No review at all stays no review: the signer fails a refusal with none, as it
    # did before #110, and an empty string would read as one.
    return dict({"verdict": "blocking", "findings": shown, "omitted": omitted},
                **({"review": _cut(review, REVIEW_CAP)} if review else {}))


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
        return dict(kept_refusal(found, prose, cut, content), ignored=["verdict"] if own else []), None
    if cut:
        return None, ("truncated", "the model ran out of room before its answer ended, so its verdict is not taken")
    findings = [f for a in found for f in _listed(a)]
    if (any(not isinstance(a.get("findings"), list) or not isinstance(a.get("review"), str) for a in found)
            or any(severity(f) not in SEVERITIES or not str(f.get("text") or "").strip() for f in findings)
            or any(severity(f) == "needs-context" and not _files(f) for f in findings)):
        return None, ("malformed", "the model answered findings or a review outside the schema")
    if len(found) > 1 or beside(prose):
        return None, ("outside", "the model wrote beside its answer object, so a verdict that would clear "
                                 "the change is not taken")
    if "blocking" in own:
        return None, ("disagrees", "the model's own word was blocking over findings that do not make it so, "
                                   "so a verdict that would clear the change is not taken")
    shown, omitted = _shown(findings)
    # A read short of context clears nothing and refuses nothing yet: it names
    # what it needed, and is read once more with it (F(2)).
    short = [f for f in findings if severity(f) == "needs-context"]
    if short:
        return {"verdict": "needs-context", "needs": needed(short), "review": _cut(str(found[0]["review"]), REVIEW_CAP),
                "findings": shown, "omitted": omitted, "ignored": (["verdict"] if own else [])}, None
    return {"verdict": "advisory" if findings else "clean", "review": _cut(found[0]["review"], REVIEW_CAP),
            "findings": shown, "omitted": omitted, "ignored": ["verdict"] if own else []}, None


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
    # No output-token limit and no price limit go with the request (6 October
    # 2026): sent with them, as #153 built it, OpenRouter found no GLM 5.3
    # endpoint to serve it ("HTTP 404 ... No endpoints found that can handle the
    # requested parameters", #154's read). The spending check still bounds each
    # request by the registry's price and output ceiling before it is sent.
    return body


def outgoing(body, got):
    """Why the request may not leave as built, or None.

    Checked on the body exactly as it would be sent, after the provider's own
    settings are merged in (decision 0014, E; the Chairman's condition of 6
    October 2026), so a registry edit cannot widen what leaves: the pinned model
    and no other, no list of models to substitute, and the ask for providers who
    promise not to store or train on the prompt. That is the provider's promise,
    not proof of what it does.
    """
    if body.get("model") != got["model"]:
        return "the request names another model than the one pinned"
    for k in ("models", "route"):
        if k in body:
            return "the request carries %s, which would let the provider serve another model" % k
    if (body.get("provider") or {}).get("data_collection") != "deny":
        return "the request does not ask for providers who promise not to store or train on it"
    return None


# THE CAP PROBE (decision 0014's recovery, PR 3). The canary, dispatched by hand
# on main, may add one limit to a read to learn whether an endpoint serves it:
# the output-token cap or the price filter, from the registry. No reviewer sets
# CANARY_PROBE; a probe this list does not know is refused before sending.
PROBES = {
    "output-cap": lambda body, lim: body.__setitem__("max_tokens", lim["output_tokens"]),
    "price-cap": lambda body, lim: _set(body, "provider.max_price",
                                        {"prompt": lim["input_price"], "completion": lim["output_price"]}),
}


# THE SPENDING CHECK (decision 0014, D). A read in flight elsewhere may yet
# send this many cash requests: the role's, and the one re-read of an answer
# that came back short. Nothing stands behind the role since #156, so there is
# no fallback's. review-gate.py holds it to the most today's route sends.
RUN_ATTEMPTS = 2
# Tokens a request's framing adds beyond its bytes: a token is at least a byte.
FRAMING_TOKENS = 1000


def limits(reg, model_id):
    """(the model's output-token limit and price limit, its context), or None when the registry does not give them all."""
    m = (reg.get("models") or {}).get(model_id) or {}
    price = m.get("price_usd_per_million") or {}
    out, ctx = m.get("max_output_tokens"), m.get("context_tokens")
    if not (_number(price.get("input")) and _number(price.get("output")) and isinstance(out, int) and out > 0
            and isinstance(ctx, int) and ctx > 0):
        return None
    return {"input_price": price["input"], "output_price": price["output"], "output_tokens": out, "context": ctx}


def bound(lim, body_bytes):
    """The most one request can cost: every byte a token at the input price, every allowed output token at the output price."""
    tokens_in = min(body_bytes + FRAMING_TOKENS, lim["context"])
    return (tokens_in * lim["input_price"] + lim["output_tokens"] * lim["output_price"]) / 1e6


def admit(base_url, key, lim, body_bytes, ledger, attempt, weekly, inflight, fetch=None):
    """(the request's bound, None, what it was checked against) when admitted, else (None, why, ""). Neither carries any figure: no limit, headroom or settled spend.

    Settled cash this week comes from the provider's own key endpoint; in-flight
    reservations are this job's unresolved cash attempts at their bounds, and
    every other read in flight at the most a read can send; then this request's
    bound. This job's finished cash attempts are counted too, at their cost (or
    bound, if none came back), and in full: a rise in the provider's figure may
    be another job's, and nothing it reports ties a rise to this job's own
    requests, so none is credited. A request already shown is counted twice
    for the rest of the job, which errs toward refusing. All of it must fit
    under the weekly limit, when it is set, and the key's own remaining limit,
    when the key has one. Unknown anything is no call.
    """
    fetch = fetch or urllib.request.urlopen
    if lim is None:
        return None, "the registry gives this model no output-token limit, price limit or context, so its most is unknown", ""
    this = bound(lim, body_bytes)
    try:
        others = int(inflight)
        if others < 0:
            raise ValueError
    except (TypeError, ValueError):
        return None, "the reads in flight elsewhere could not be counted, so the headroom is unknown", ""
    reserved = others * RUN_ATTEMPTS * bound(lim, lim["context"])
    finished = 0.0
    for a in attempts(ledger):
        if a["attempt"] == str(attempt) or a.get("billing") != "cash" or not a.get("sent", True):
            continue
        if a["unresolved"]:
            if not _number(a.get("bound")):
                return None, "an earlier attempt in this job is unresolved with no bound, so the headroom is unknown", ""
            reserved += a["bound"]
            continue
        cost = a["cost"] if _number(a.get("cost")) else a.get("bound")
        if not _number(cost):
            return None, "an earlier attempt in this job finished with no cost and no bound, so the headroom is unknown", ""
        finished += cost
    try:
        req = urllib.request.Request(base_url.rstrip("/") + "/key", headers={"Authorization": "Bearer " + key})
        with fetch(req, timeout=30) as r:
            data = json.load(r).get("data")
    except Exception:  # noqa: BLE001  (any failure to ask is headroom unknown)
        return None, "the provider's key endpoint did not answer, so the cash settled this week is unknown", ""
    if not isinstance(data, dict):
        return None, "the provider's key endpoint answered no data, so the cash settled this week is unknown", ""
    caps, basis = [], []
    if weekly not in (None, ""):
        try:
            limit = float(weekly)
            if not limit > 0:
                raise ValueError
        except ValueError:
            return None, "the weekly limit is set but is not a positive amount", ""
        if not _number(data.get("usage_weekly")):
            return None, "the provider did not say what was spent this week", ""
        caps.append(limit - data["usage_weekly"] - finished)
        basis.append("the week's spend the provider reported against the weekly limit")
    if data.get("limit_remaining") is not None:
        if not isinstance(data["limit_remaining"], (int, float)) or isinstance(data["limit_remaining"], bool):
            return None, "the provider's remaining limit is not an amount", ""
        caps.append(data["limit_remaining"] - finished)
        basis.append("the key's own remaining limit")
    if not caps:
        return None, "no weekly limit is set and the key has no limit of its own, so the headroom is unknown", ""
    if reserved + this > min(caps):
        return None, "this request at its most, with what is in flight, would pass the cash limit", ""
    return this, None, " and ".join(basis)


def answer(resp, pinned):
    """(answer dict, exit status) from a provider's parsed response."""
    if not isinstance(resp, dict):
        return {"is_error": True, "subtype": "no_answer", "result": "the provider answered no object"}, 1
    if resp.get("error"):
        e = resp["error"]
        said = e.get("message", "") if isinstance(e, dict) else str(e)
        code = e.get("code", "") if isinstance(e, dict) else ""
        if limited(code, said):
            return {"is_error": True, "subtype": "provider_limit",
                    "result": "budget refused: the provider's own limit refused the request"}, 1
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


def limited(code, said):
    """A refusal by a spending limit, the key's or the account's: HTTP 402, or the key's limit by name."""
    return str(code) == "402" or bool(re.search(r"key limit exceeded|insufficient credits", str(said), re.I))


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
                got["verdict"], len(got["findings"]) + got.get("omitted", 0),
                "; the model's own verdict field was ignored" if got.get("ignored") else ""))
    tmp = path + ".derived"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(obj, f)
        f.write("\n")
    os.replace(tmp, path)


def incomplete_file(path):
    """A read still short of context after its one re-read: its needs-context verdict becomes a refusal.

    "incomplete read: needed X" goes first among its findings and its review, so
    the refusal says what it lacked. Any other answer file is left as it is.
    """
    try:
        with open(path, encoding="utf-8") as f:
            obj = json.load(f)
        got = json.loads(obj.get("result") or "")
    except (OSError, ValueError, TypeError, AttributeError):
        return
    if not isinstance(got, dict) or got.get("verdict") != "needs-context":
        return
    files = got.get("needs") or []
    said = "incomplete read: needed %s" % (", ".join(files) if files else "files it did not name as paths")
    got = dict(got, verdict="blocking",
               findings=[{"severity": "blocking", "text": said}] + list(got.get("findings") or []),
               review=_cut("%s.\n\n%s" % (said[0].upper() + said[1:], got.get("review") or ""), REVIEW_CAP))
    got.pop("needs", None)
    obj["result"] = json.dumps(got)
    tmp = path + ".derived"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(obj, f)
        f.write("\n")
    os.replace(tmp, path)
    # Counted, never named: a product's file names are its own, and this summary is public.
    note("signed blocking: an incomplete read, %d file(s) named" % len(files))


# ONE RECORD PER ATTEMPT (decision 0014, A): an append-only ledger, one JSON
# event a line. Cash is what a provider bills per request; plan is an
# allowance. They are never added together.
BILLING = {"openai-compatible": "cash", "claude-code": "plan"}
# What an attempt's exit or its answer's subtype says happened: (the outcome,
# whether the request was sent, whether what it cost is settled).
OUTCOMES = {
    "budget_refused": ("budget refused", False, True),
    "provider_limit": ("budget refused by the provider's limit", True, True),
    "unreachable": ("unreachable, response lost", True, False),
    "no_credential": ("not sent: no credential", False, True),
    "unresolved": ("not sent: unresolved", False, True),
    "request_refused": ("not sent: the request failed its check before sending", False, True),
}


def _events(ledger):
    """Every event in the ledger, in order; a line that is not an event is skipped."""
    out = []
    try:
        with open(ledger, encoding="utf-8") as f:
            for line in f:
                try:
                    e = json.loads(line)
                except ValueError:
                    continue
                if isinstance(e, dict) and e.get("attempt"):
                    out.append(e)
    except OSError:
        pass
    return out


def log_event(ledger, event):
    """Append one event; a ledger that cannot be written never costs a read."""
    if not ledger:
        return
    try:
        with open(ledger, "a", encoding="utf-8") as f:
            f.write(json.dumps(dict(event, at=int(time.time()))) + "\n")
            f.flush()
            os.fsync(f.fileno())
    except OSError:
        pass


def attempts(ledger):
    """Each attempt, folded from its events: open, reserve, returned, close."""
    got = {}
    for e in _events(ledger):
        a = got.setdefault(str(e["attempt"]), {"attempt": str(e["attempt"])})
        kind = e.get("event")
        if kind == "open":
            a.update(role=e.get("role"), model=e.get("model"), billing=e.get("billing", "unknown"))
        elif kind == "reserve":
            a.update(bound=e.get("bound"), basis=e.get("basis"))
        elif kind == "returned":
            a.update(returned=True, generation=e.get("generation"), usage=e.get("usage"))
            if _number(e.get("cost")):
                a["cost"] = e["cost"]
        elif kind == "close":
            a.update(closed=True, outcome=e.get("outcome"), sent=e.get("sent", True),
                     settled=e.get("settled", True))
            if _number(e.get("cost")):
                a["cost"] = e["cost"]
    for a in got.values():
        a["unresolved"] = not a.get("closed") or not a.get("settled", True)
    return [got[k] for k in sorted(got, key=int)]


def _number(x):
    return isinstance(x, (int, float)) and not isinstance(x, bool) and x >= 0


def record_open(ledger, role, model, interface):
    n = str(len([e for e in _events(ledger) if e.get("event") == "open"]) + 1)
    log_event(ledger, {"attempt": n, "event": "open", "role": role, "model": model, "route": interface,
                       "billing": BILLING.get(interface, "unknown")})
    return n


def record_close(ledger, attempt, rc, answer_file):
    """Close an attempt with its outcome, from the exit and the answer file it left."""
    try:
        with open(answer_file, encoding="utf-8") as f:
            obj = json.load(f)
    except (OSError, ValueError):
        obj = None
    obj = obj if isinstance(obj, dict) else {}
    sub = str(obj.get("subtype") or "")
    if rc == 0:
        outcome, sent, settled = "answered", True, True
    elif rc in (124, 137):
        outcome, sent, settled = "stopped, response lost", True, False
    elif sub in OUTCOMES:
        outcome, sent, settled = OUTCOMES[sub]
    elif obj:
        outcome, sent, settled = "failed: %s" % (re.sub(r"[^a-z_]", "", sub.lower())[:30] or "no subtype"), True, True
    else:
        outcome, sent, settled = "no answer left", True, False
    event = {"attempt": str(attempt), "event": "close", "outcome": outcome, "sent": sent, "settled": settled}
    if not sent:
        event["cost"] = 0
    elif _number(obj.get("total_cost_usd")):
        event["cost"] = obj["total_cost_usd"]
    log_event(ledger, event)


def _usd(x):
    return ("%.6f" % x).rstrip("0").rstrip(".") if _number(x) else "unknown"


def summary(ledger):
    """The spend line's attempts: each one, the cash total of all of them, the plan's apart, and how many are unresolved."""
    rows, totals = [], {}
    for a in attempts(ledger):
        cost = a.get("cost") if a.get("sent", True) else 0
        if a["unresolved"]:
            cost = None
        rows.append("#%s %s %s %s: %s, %s" % (a["attempt"], a.get("role") or "?", a.get("model") or "?",
                                             a.get("billing") or "unknown",
                                             a.get("outcome") or "unresolved", "%s USD" % _usd(cost)
                                             if cost is not None else "cost unknown")
                    + (", checked on %s" % a["basis"] if a.get("basis") else ""))
        t = totals.setdefault(a.get("billing") or "unknown", [0.0, 0])
        if _number(cost):
            t[0] += cost
        else:
            t[1] += 1

    def total(kind):
        t = totals.get(kind)
        if not t:
            return "0 USD, no %s attempt" % kind
        return "%s USD" % _usd(t[0]) if not t[1] else "unknown (%s USD known, %d attempt(s) unknown)" % (_usd(t[0]), t[1])
    unresolved = sum(1 for a in attempts(ledger) if a["unresolved"])
    return "attempts: %s; cash, all attempts: %s; plan, all attempts: %s (allowance, never added to cash); unresolved: %d" % (
        "; ".join(rows) or "none", total("cash"), total("plan"), unresolved)


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
    if len(argv) == 3 and argv[1] == "incomplete":
        incomplete_file(argv[2])
        return 0
    if len(argv) >= 3 and argv[1] == "record":
        if argv[2] == "open" and len(argv) == 7:
            print(record_open(*argv[3:7]))
            return 0
        if argv[2] == "close" and len(argv) == 7:
            try:
                rc = int(argv[5])
            except ValueError:
                rc = 1
            record_close(argv[3], argv[4], rc, argv[6])
            return 0
        if argv[2] == "summary" and len(argv) == 4:
            print(summary(argv[3]))
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
    ledger, attempt = os.environ.get("ATTEMPTS", ""), os.environ.get("ATTEMPT", "")
    lim = limits(reg, got["model"])
    body = build(got, provider, system, sys.stdin.read(), json.loads(schema_json))
    probe = os.environ.get("CANARY_PROBE", "")
    if probe not in ("", "none"):
        if probe not in PROBES or lim is None:
            return out({"is_error": True, "subtype": "request_refused",
                        "result": "refused before sending: no probe %r with the registry's limits" % probe}, 1)
        PROBES[probe](body, lim)
    # THE REQUEST AS IT WOULD LEAVE, checked before anything is sent: no prompt,
    # and no call to the key endpoint either.
    stop = outgoing(body, got)
    if stop:
        note("refused before sending: %s" % stop)
        return out({"is_error": True, "subtype": "request_refused", "result": "refused before sending: %s" % stop}, 1)
    data = json.dumps(body).encode("utf-8")
    # THE SPENDING CHECK, before the request and never after (decision 0014, D).
    most, why, basis = admit(got["base_url"], key, lim, len(data), ledger, attempt,
                      os.environ.get("REVIEW_CASH_WEEKLY", ""), os.environ.get("INFLIGHT", ""))
    if why:
        note("budget refused before sending: %s" % why)
        return out({"is_error": True, "subtype": "budget_refused", "result": "budget refused: %s" % why}, 1)
    log_event(ledger, {"attempt": attempt, "event": "reserve", "bound": most, "basis": basis})
    req = urllib.request.Request(
        got["base_url"].rstrip("/") + "/chat/completions",
        data=data,
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
        log_event(ledger, {"attempt": attempt, "event": "returned", "status": e.code})
        if e.code == 402 or limited("", said):
            return out({"is_error": True, "subtype": "provider_limit",
                        "result": "budget refused: the provider's own limit refused the request"}, 1)
        return out({"is_error": True, "subtype": "http_error",
                    "result": "HTTP %s from %s: %s" % (e.code, got["provider"], said)}, 1)
    except (urllib.error.URLError, OSError, ValueError) as e:
        return out({"is_error": True, "subtype": "unreachable",
                    "result": "%s could not be reached: %s" % (got["provider"], e)}, 1)
    # What the provider returned is kept before a word of it is parsed (A).
    usage = resp.get("usage") if isinstance(resp, dict) else None
    log_event(ledger, {"attempt": attempt, "event": "returned",
                       "generation": resp.get("id") if isinstance(resp, dict) else None,
                       "usage": usage if isinstance(usage, dict) else None,
                       "cost": usage.get("cost") if isinstance(usage, dict) else None})
    obj, rc = answer(resp, got["model"])
    if isinstance(usage, dict) and "usage" not in obj:
        obj["usage"] = {"input_tokens": usage.get("prompt_tokens"), "output_tokens": usage.get("completion_tokens")}
        obj["total_cost_usd"] = usage.get("cost")
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
