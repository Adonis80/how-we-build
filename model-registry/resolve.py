#!/usr/bin/env python3
"""Resolve a role to the model that holds it, from the one registry (decision 0008).

    resolve.py REGISTRY ROLE          every field, one `key=value` a line
    resolve.py REGISTRY ROLE FIELD    that field alone
    resolve.py REGISTRY --check       the registry checked whole; ok, or why not

Fields: role, model, name, provider, interface, base_url, credential, effort,
effort_checked, fallback, version. `fallback` is the role to read on when this
one does not answer, or empty: never a model, so a switch is still one edit.

It fails closed. A role it cannot resolve cleanly — unknown, a model not in the
registry or not active, a provider or interface it does not know, an effort the
model does not list — is an error and a non-zero exit, never a default.
Standard library only: it runs on a bare runner, beside a secret.
"""
import json
import re
import sys

INTERFACES = ("claude-code", "openai-compatible")
USABLE = ("active", "fallback", "canary")
STATUSES = ("candidate", "canary", "active", "fallback", "deprecated", "blocked")
FIELDS = ("role", "model", "name", "provider", "interface", "base_url", "credential", "effort",
          "effort_checked", "fallback", "version")
# A role name is the only thing another file may say, so it is a plain word.
ROLE_NAME = re.compile(r"^[a-z][a-z0-9-]*$")
DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


class Unresolved(Exception):
    pass


def load(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def _entry(reg, name):
    """The role `name`, or a fallback written inline as {model, effort}."""
    if isinstance(name, dict):
        return "(inline fallback)", name
    roles = reg.get("roles") or {}
    if not isinstance(name, str) or not ROLE_NAME.match(name) or name not in roles:
        raise Unresolved("no role %r in the registry" % (name,))
    return name, roles[name]


def resolve(reg, name):
    """Every field of role `name`, as a dict of strings."""
    role, entry = _entry(reg, name)
    model_id = entry.get("model")
    model = (reg.get("models") or {}).get(model_id)
    if not isinstance(model, dict):
        raise Unresolved("%s names model %r, which the registry does not list" % (role, model_id))
    if model.get("status") not in USABLE:
        raise Unresolved("%s names %s, whose status is %r: only %s may hold a role"
                         % (role, model_id, model.get("status"), "/".join(USABLE)))
    provider_name = model.get("provider")
    provider = (reg.get("providers") or {}).get(provider_name)
    if not isinstance(provider, dict):
        raise Unresolved("%s is served by %r, which the registry does not list" % (model_id, provider_name))
    interface = provider.get("interface")
    if interface not in INTERFACES:
        raise Unresolved("%s speaks %r; the callers speak %s" % (provider_name, interface, "/".join(INTERFACES)))
    if not re.match(r"^[A-Z][A-Z0-9_]*$", str(provider.get("credential", ""))):
        raise Unresolved("%s names no credential" % provider_name)
    if interface == "openai-compatible" and not str(provider.get("base_url", "")).startswith("https://"):
        raise Unresolved("%s gives no https base_url" % provider_name)
    effort = entry.get("effort")
    efforts = model.get("efforts")
    if not isinstance(effort, str) or not effort:
        raise Unresolved("%s names no effort" % role)
    if efforts is not None and effort not in efforts:
        raise Unresolved("%s asks %s for effort %r, which it does not list (%s)"
                         % (role, model_id, effort, "/".join(efforts)))
    fallback = entry.get("fallback")
    if isinstance(fallback, dict):
        fallback = ""  # inline fallbacks serve roles nothing calls yet; a caller names a role
    elif fallback is None:
        fallback = ""
    elif not isinstance(fallback, str) or fallback not in (reg.get("roles") or {}):
        raise Unresolved("%s falls back to %r, which is not a role" % (role, fallback))
    got = {
        "role": role, "model": model_id, "name": model.get("name", ""), "provider": provider_name,
        "interface": interface, "base_url": provider.get("base_url", ""),
        "credential": provider["credential"], "effort": effort,
        "effort_checked": "yes" if efforts is not None else "no", "fallback": fallback,
        "version": str(reg.get("version", "")),
    }
    # Each value becomes one line of a workflow's outputs: a line break in one
    # would be an output of its own.
    for key, value in got.items():
        if not isinstance(value, str) or "\n" in value or "\r" in value:
            raise Unresolved("%s's %s is not one line of text" % (role, key))
    return got


def check(reg):
    """Every fault in the registry, as sentences. Empty is clean."""
    faults = []
    for key in ("version", "reviewed"):
        if not reg.get(key):
            faults.append("no %s" % key)
    if reg.get("reviewed") and not DATE.match(str(reg["reviewed"])):
        faults.append("reviewed is not a date")
    for mid, model in sorted((reg.get("models") or {}).items()):
        if model.get("status") not in STATUSES:
            faults.append("%s has status %r" % (mid, model.get("status")))
        if not DATE.match(str(model.get("checked", ""))) or not model.get("source"):
            faults.append("%s does not say when it was checked and where" % mid)
    for name in sorted(reg.get("roles") or {}):
        if not ROLE_NAME.match(name):
            faults.append("role %r is not a plain word" % name)
        try:
            resolve(reg, name)
            entry = reg["roles"][name]
            if isinstance(entry.get("fallback"), dict):
                resolve(reg, entry["fallback"])
        except Unresolved as e:
            faults.append(str(e))
        # A fallback chain ends: a role that falls back to itself, at any depth,
        # is a loop no read would leave.
        seen, at = [], name
        while isinstance(at, str) and at:
            if at in seen:
                faults.append("%s falls back in a loop: %s" % (name, " > ".join(seen + [at])))
                break
            seen.append(at)
            at = ((reg.get("roles") or {}).get(at) or {}).get("fallback")
    return faults


def main(argv):
    if len(argv) not in (3, 4):
        print(__doc__.strip().split("\n\n")[1], file=sys.stderr)
        return 2
    try:
        reg = load(argv[1])
    except (OSError, ValueError) as e:
        print("the registry could not be read: %s" % e, file=sys.stderr)
        return 1
    if argv[2] == "--check":
        faults = check(reg)
        for f in faults:
            print("registry: %s" % f, file=sys.stderr)
        if not faults:
            print("ok: the registry names %d role(s) and %d model(s), each role resolving cleanly"
                  % (len(reg.get("roles") or {}), len(reg.get("models") or {})))
        return 1 if faults else 0
    try:
        got = resolve(reg, argv[2])
    except Unresolved as e:
        print("unresolved: %s" % e, file=sys.stderr)
        return 1
    if len(argv) == 4:
        if argv[3] not in FIELDS:
            print("no field %r; the fields are %s" % (argv[3], ", ".join(FIELDS)), file=sys.stderr)
            return 2
        print(got[argv[3]])
        return 0
    for key in FIELDS:
        print("%s=%s" % (key, got[key]))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
