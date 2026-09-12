#!/usr/bin/env python3
"""Small deterministic guard for this rulebook, including untracked entries."""
from pathlib import Path
import re
import sys

from project_bootstrap import load_contract, render

ROOT = Path(__file__).resolve().parents[1]
TREE = {
    '': {'AGENTS.md', 'CHARTER.md', 'HOW-WE-BUILD.md', 'README.md', 'LEGACY-ROADMAP.md', 'check.sh', 'design', 'scripts', '.github'},
    'design': {'ARCHITECT.md', 'BRIEF_TEMPLATE.md', 'REVIEW_RUBRIC.md', 'SCREEN-LAW.md', 'SCREEN_SPEC_TEMPLATE.md'},
    'scripts': {'project_bootstrap.py', 'review_gate.py', 'check_repo.py', 'test_checks.py'},
    '.github': {'workflows'},
    '.github/workflows': {'check.yml'},
}
SECRET = re.compile(rb'(ghp_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,}|sk-[A-Za-z0-9]{20,}|xox[baprs]-[A-Za-z0-9-]{10,}|-----BEGIN [A-Z ]*PRIVATE KEY-----|eyJ[A-Za-z0-9_-]{20,}\.[A-Za-z0-9_-]{20,})')


def check_tree(root):
    errors = []

    def visit(relative):
        folder = root / relative
        try:
            entries = {p.name: p for p in folder.iterdir()}
        except OSError:
            errors.append(f'{relative or "root"}: cannot list directory')
            return
        if not relative:
            entries.pop('.git', None)
        missing = TREE[relative] - entries.keys()
        for name in sorted(missing):
            errors.append(f'{relative}/{name}: required entry missing')
        if entries.keys() - TREE[relative]:
            errors.append(f'{relative or "root"}: unexpected entry (including untracked files)')
        for name in sorted(TREE[relative] & entries.keys()):
            path = entries[name]
            rel = f'{relative}/{name}'.lstrip('/')
            if path.is_symlink():
                errors.append(f'{rel}: symlinks are not allowed')
            elif rel in TREE:
                if path.is_dir():
                    visit(rel)
                else:
                    errors.append(f'{rel}: expected directory')
            elif not path.is_file():
                errors.append(f'{rel}: expected regular file')
            else:
                try:
                    data = path.read_bytes()
                    data.decode('utf-8')
                    match = SECRET.search(data)
                    if match:
                        line = data[:match.start()].count(b'\n') + 1
                        errors.append(f'{rel}:{line}: suspected secret (value redacted)')
                except (OSError, UnicodeError):
                    errors.append(f'{rel}: cannot read UTF-8 file')
    visit('')
    # Do not follow invalid/missing/symlink paths during secondary checks.
    if errors:
        return errors
    for filename, cap in [('HOW-WE-BUILD.md', 500), ('design/SCREEN-LAW.md', 450)]:
        words = len((root / filename).read_text(encoding='utf-8').split())
        if words > cap:
            errors.append(f'{filename}: {words} words exceeds cap {cap}')
    try:
        projects, _ = load_contract(root)
        for key in projects:
            render(key, root)
    except (ValueError, KeyError, OSError, UnicodeError):
        errors.append('README.md: invalid project registry/instruction template')
    return errors


def main():
    errors = check_tree(ROOT)
    for error in errors:
        print('FAIL: ' + error)
    if not errors:
        print('ok: fixed file tree, instruction caps, secret patterns and all Project bootstraps')
    return bool(errors)


if __name__ == '__main__':
    sys.exit(main())
