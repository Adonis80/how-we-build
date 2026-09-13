#!/usr/bin/env bash
# The rulebook's one guard. Python keeps filenames, review records and logs exact.
set -euo pipefail
cd "$(dirname "$0")"
export PYTHONDONTWRITEBYTECODE=1
python3 -B - "$@" <<'PY'
import io
import json
import os
from pathlib import Path
import re
import sys
import tempfile
import unittest
import urllib.request

ROOT = Path.cwd()
ROOT_ENTRIES = {
    '.github': 'dir', 'design': 'dir', 'AGENTS.md': 'file', 'CHARTER.md': 'file',
    'HOW-WE-BUILD.md': 'file', 'README.md': 'file', 'check.sh': 'file',
}
DESIGN_FILES = {
    'ARCHITECT.md', 'BRIEF_TEMPLATE.md', 'REVIEW_RUBRIC.md',
    'SCREEN-LAW.md', 'SCREEN_SPEC_TEMPLATE.md',
}
SECRET = re.compile(rb'(ghp_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,}|sk-[A-Za-z0-9]{20,}|xox[baprs]-[A-Za-z0-9-]{10,}|-----BEGIN [A-Z ]*PRIVATE KEY-----|eyJ[A-Za-z0-9_-]{20,}\.[A-Za-z0-9_-]{20,})')
BOT = 'chatgpt-codex-connector[bot]'
FULL_SHA = re.compile(r'[0-9a-f]{40}')
REVIEWED_LINE = re.compile(r'^\s*(?:\*\*)?Reviewed commit:(?:\*\*)?\s*`([0-9a-f]{7,40})`\s*$')
SUMMARY_MARKER = '<!-- codex-pull-request-review-summary -->'


def repo_errors(root):
    errors = []
    try:
        root_items = {p.name: p for p in root.iterdir() if p.name != '.git'}
    except OSError:
        return ['repository cannot be read']
    if set(root_items) != set(ROOT_ENTRIES):
        errors.append('required root entries are missing or unexpected entries exist')
    for name, kind in ROOT_ENTRIES.items():
        path = root_items.get(name)
        if path is None:
            continue
        if path.is_symlink() or (kind == 'file' and not path.is_file()) or (kind == 'dir' and not path.is_dir()):
            errors.append('a required root entry has the wrong type')
    design = root_items.get('design')
    if design and design.is_dir() and not design.is_symlink():
        try:
            design_items = {p.name: p for p in design.iterdir()}
        except OSError:
            design_items = {}
            errors.append('design directory cannot be read')
        if set(design_items) != DESIGN_FILES:
            errors.append('required design entries are missing or unexpected entries exist')
        if any(p.is_symlink() or not p.is_file() for p in design_items.values()):
            errors.append('a design entry has the wrong type')
    for relative, cap in (('HOW-WE-BUILD.md', 600), ('design/SCREEN-LAW.md', 450)):
        path = root / relative
        if not path.is_file() or path.is_symlink():
            continue
        try:
            words = len(path.read_text(encoding='utf-8').split())
        except (OSError, UnicodeError):
            errors.append('a capped instruction file is unreadable UTF-8')
        else:
            if words > cap:
                errors.append(f'{relative} exceeds its {cap}-word cap')
    found_secret = False
    for folder, directories, files in os.walk(root, followlinks=False):
        directories[:] = [d for d in directories if d != '.git']
        base = Path(folder)
        if any((base / d).is_symlink() for d in directories):
            errors.append('a directory symlink is not allowed')
            directories[:] = [d for d in directories if not (base / d).is_symlink()]
        for name in files:
            path = base / name
            if path.is_symlink():
                errors.append('a file symlink is not allowed')
                continue
            try:
                if SECRET.search(path.read_bytes()):
                    found_secret = True
            except OSError:
                errors.append('a repository file cannot be read')
    if found_secret:
        errors.append('secret-like content detected; value suppressed')
    return errors


def comment_refs(comment):
    if (comment.get('user') or {}).get('login') != BOT:
        return []
    body = comment.get('body') or ''
    refs = []
    for line in body.splitlines():
        match = REVIEWED_LINE.fullmatch(line)
        if match:
            refs.append(match.group(1))
            continue
        if SUMMARY_MARKER not in body:
            continue
        cells = [cell.strip() for cell in line.split('|')]
        if (len(cells) >= 6 and cells[1] == '📝 **Code Review**' and
                cells[2].startswith('✅ **Completed**')):
            match = re.fullmatch(r'`([0-9a-f]{7,40})`', cells[3])
            if match:
                refs.append(match.group(1))
    return refs


def reviewed_head(head, reviews, comments, resolve):
    for review in reviews:
        if ((review.get('user') or {}).get('login') == BOT and
                review.get('commit_id') == head and review.get('submitted_at') and
                review.get('state') in {'APPROVED', 'CHANGES_REQUESTED', 'COMMENTED'}):
            return True
    for comment in comments:
        for ref in comment_refs(comment):
            if len(ref) == 40:
                if ref == head:
                    return True
            elif head.startswith(ref) and resolve(ref) == head:
                return True
    return False


class GitHub:
    def __init__(self, repo, token):
        self.base = f'https://api.github.com/repos/{repo}'
        self.token = token

    def get(self, path):
        request = urllib.request.Request(self.base + path, headers={
            'Authorization': 'Bearer ' + self.token,
            'Accept': 'application/vnd.github+json',
            'X-GitHub-Api-Version': '2022-11-28',
        })
        with urllib.request.urlopen(request, timeout=20) as response:
            return json.load(response)

    def pages(self, path):
        output = []
        for page in range(1, 1001):
            batch = self.get(f'{path}?per_page=100&page={page}')
            if not isinstance(batch, list):
                raise ValueError('invalid GitHub collection')
            output.extend(batch)
            if len(batch) < 100:
                return output
        raise ValueError('GitHub collection exceeded safe page limit')


def check_review():
    repo = os.environ.get('GITHUB_REPOSITORY', '')
    number = os.environ.get('PR_NUMBER', '')
    head = os.environ.get('HEAD_SHA', '')
    token = os.environ.get('GH_TOKEN', '')
    if not (re.fullmatch(r'[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+', repo) and
            re.fullmatch(r'[1-9][0-9]*', number) and FULL_SHA.fullmatch(head) and token):
        return 'review check needs repository, PR number, full head SHA and token'
    api = GitHub(repo, token)
    try:
        pull = api.get(f'/pulls/{number}')
        if pull.get('state') != 'open' or (pull.get('head') or {}).get('sha') != head:
            return 'event does not name the live open pull-request head'
        reviews = api.pages(f'/pulls/{number}/reviews')
        comments = api.pages(f'/issues/{number}/comments')
        if reviewed_head(head, reviews, comments, lambda ref: api.get(f'/commits/{ref}')['sha']):
            return None
        return 'no submitted Codex review receipt exists for the current head'
    except (OSError, ValueError, KeyError, TypeError):
        return 'review verification failed closed'


def fixture():
    temp = tempfile.TemporaryDirectory()
    root = Path(temp.name)
    (root / '.github').mkdir()
    (root / 'design').mkdir()
    for name, kind in ROOT_ENTRIES.items():
        path = root / name
        if kind == 'file':
            path.write_text('safe', encoding='utf-8')
    for name in DESIGN_FILES:
        (root / 'design' / name).write_text('safe', encoding='utf-8')
    return temp, root


class GuardRegressions(unittest.TestCase):
    def test_clean_fixture(self):
        temp, root = fixture(); self.addCleanup(temp.cleanup)
        self.assertEqual(repo_errors(root), [])

    def test_missing_required_root_file_fails(self):
        temp, root = fixture(); self.addCleanup(temp.cleanup)
        (root / 'AGENTS.md').unlink()
        self.assertTrue(repo_errors(root))

    def test_missing_required_design_file_fails(self):
        temp, root = fixture(); self.addCleanup(temp.cleanup)
        (root / 'design' / 'ARCHITECT.md').unlink()
        self.assertTrue(repo_errors(root))

    def test_combined_allowed_names_cannot_bypass_root_list(self):
        temp, root = fixture(); self.addCleanup(temp.cleanup)
        (root / 'AGENTS.md CHARTER.md').write_text('safe')
        self.assertTrue(repo_errors(root))

    def test_control_character_cannot_bypass_design_list(self):
        temp, root = fixture(); self.addCleanup(temp.cleanup)
        (root / 'design' / 'ARCHITECT.md\nREADME.md').write_text('safe')
        self.assertTrue(repo_errors(root))

    def test_secret_value_is_suppressed(self):
        temp, root = fixture(); self.addCleanup(temp.cleanup)
        value = 'ghp_' + ('x' * 25)
        (root / 'README.md').write_text(value)
        output = '\n'.join(repo_errors(root))
        self.assertIn('value suppressed', output)
        self.assertNotIn(value, output)

    def test_only_submitted_review_states_count(self):
        head = 'a' * 40
        for state in ('APPROVED', 'CHANGES_REQUESTED', 'COMMENTED'):
            item = {'user': {'login': BOT}, 'commit_id': head, 'submitted_at': 'now', 'state': state}
            self.assertTrue(reviewed_head(head, [item], [], lambda _: head))
        for state in ('PENDING', 'DISMISSED'):
            item = {'user': {'login': BOT}, 'commit_id': head, 'submitted_at': 'now', 'state': state}
            self.assertFalse(reviewed_head(head, [item], [], lambda _: head))

    def test_receipt_must_resolve_to_exact_head(self):
        head = 'a' * 40
        good = {'user': {'login': BOT}, 'body': f'**Reviewed commit:** `{head[:10]}`'}
        self.assertTrue(reviewed_head(head, [], [good], lambda _: head))
        self.assertFalse(reviewed_head(head, [], [good], lambda _: ('a' * 10) + ('b' * 30)))
        loose = {'user': {'login': BOT}, 'body': f'Completed eventually `{head}`'}
        self.assertFalse(reviewed_head(head, [], [loose], lambda _: head))


def self_test():
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(GuardRegressions)
    result = unittest.TextTestRunner(stream=sys.stdout, verbosity=1).run(suite)
    return result.wasSuccessful()


if sys.argv[1:] == ['--self-test']:
    sys.exit(0 if self_test() else 1)
if sys.argv[1:]:
    print('FAIL: usage: bash check.sh [--self-test]')
    sys.exit(2)
if not self_test():
    sys.exit(1)
errors = repo_errors(ROOT)
for error in errors:
    print('FAIL: ' + error)
if not errors:
    print('ok: file tree, word caps and secret suppression')
if os.environ.get('GITHUB_EVENT_NAME') in {'pull_request', 'pull_request_review'}:
    review_error = check_review()
    if review_error:
        print('FAIL: ' + review_error)
        errors.append(review_error)
    else:
        print('ok: submitted Codex review receipt verified for current head')
if not errors:
    print('check.sh: all clear')
sys.exit(bool(errors))
PY
