#!/usr/bin/env python3
"""Render/compare Project launch instructions; never access provider accounts."""
import argparse
import hashlib
from pathlib import Path
import re
from string import Template
import sys

ROOT = Path(__file__).resolve().parents[1]


def block(text, name):
    start, end = f'<!-- juku-{name}:start -->', f'<!-- juku-{name}:end -->'
    if text.count(start) != 1 or text.count(end) != 1:
        raise ValueError(f'{name}: expected exactly one marked block')
    before, rest = text.split(start)
    if end in before or end not in rest:
        raise ValueError(f'{name}: invalid marker order')
    return rest.split(end)[0].strip()


def load_contract(root=ROOT):
    text = (root / 'README.md').read_text(encoding='utf-8')
    rows = block(text, 'projects').splitlines()
    if len(rows) < 3 or rows[:2] != [
        '| Key | Project | Repository | Scope |', '|---|---|---|---|'
    ]:
        raise ValueError('registry: invalid header or empty registry')
    projects, repos, names = {}, set(), set()
    for line in rows[2:]:
        cells = [part.strip() for part in line.split('|')]
        if len(cells) != 6 or cells[0] or cells[-1]:
            raise ValueError('registry: invalid row')
        key, name, repo, scope = cells[1:-1]
        if not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', key):
            raise ValueError('registry: invalid key')
        if not name or not re.fullmatch(r'[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+', repo):
            raise ValueError('registry: invalid name/repository')
        if scope not in ('global', 'product'):
            raise ValueError('registry: invalid scope')
        if key in projects or repo.casefold() in repos or name.casefold() in names:
            raise ValueError('registry: duplicate key, name or repository')
        projects[key] = dict(project_name=name, repository=repo, scope=scope)
        repos.add(repo.casefold())
        names.add(name.casefold())
    globals_ = [p for p in projects.values() if p['scope'] == 'global']
    if len(globals_) != 1 or globals_[0]['repository'] != 'Adonis80/how-we-build':
        raise ValueError('registry: exactly one Juku OS global repository required')
    raw = block(text, 'instructions')
    if not raw.startswith('```text\n') or not raw.endswith('\n```'):
        raise ValueError('instructions: expected text fence')
    template = Template(raw[len('```text\n'):-len('\n```')])
    fields = {m.group('named') or m.group('braced') for m in template.pattern.finditer(template.template)}
    if fields != {'project_name', 'repository', 'source_scope'}:
        raise ValueError('instructions: unknown or missing template fields')
    return projects, template


def render(key, root=ROOT):
    projects, template = load_contract(root)
    project = projects[key]
    scope = (
        'This is the global rulebook, not a product application. Read registered private product repositories only when the task needs them; verify each permission independently. Juku OS has no product roadmap.'
        if project['scope'] == 'global' else
        'Read this product repository plus the global rulebook. Product truth and roadmap live here. Do not load sibling product repositories by default; never publish private product facts in the public rulebook.'
    )
    body = template.substitute(project_name=project['project_name'], repository=project['repository'], source_scope=scope).strip() + '\n'
    digest = hashlib.sha256(body.encode()).hexdigest()
    return f'<!-- juku-bootstrap sha256:{digest} -->\n' + body


def normalise(text):
    return text.replace('\r\n', '\n').rstrip('\n')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('project', nargs='?')
    parser.add_argument('--list', action='store_true')
    parser.add_argument('--check', type=Path, metavar='READBACK')
    args = parser.parse_args()
    try:
        projects, _ = load_contract()
        if args.list and not args.project and not args.check:
            for key, p in projects.items():
                print(f"{key}\t{p['project_name']}\t{p['repository']}")
            return 0
        if args.list or args.project not in projects:
            parser.error('select a registered project, or use --list alone')
        expected = render(args.project)
        if args.check:
            if normalise(args.check.read_text(encoding='utf-8')) != normalise(expected):
                print('FAIL: saved instructions differ from this checkout; refresh from merged main')
                return 1
            print('ok: saved instructions match; account access is a separate verification')
        else:
            print(expected, end='')
        return 0
    except (OSError, UnicodeError, ValueError) as exc:
        print(f'FAIL: bootstrap contract could not be read ({type(exc).__name__})', file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
