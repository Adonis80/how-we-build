"""Regression tests for observed gate, file-list, disclosure and routing failures."""
import contextlib
import io
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest
from unittest.mock import patch
import urllib.error

from check_repo import ROOT, check_tree
from project_bootstrap import load_contract, normalise, render
from review_gate import BOT, GitHub, has_receipt, main as review_main

HEAD = 'a' * 40


def review(state='COMMENTED', head=HEAD, id_=1):
    return dict(id=id_, user={'login': BOT}, state=state, commit_id=head, submitted_at='2026-09-12T00:00:00Z')


def comment(body, user=BOT):
    return dict(user={'login': user}, body=body)


class ReviewTests(unittest.TestCase):
    def test_submitted_review_is_bound_to_head(self):
        for state in ('APPROVED', 'COMMENTED'):
            self.assertTrue(has_receipt(HEAD, [review(state)], [], None))
        self.assertFalse(has_receipt(HEAD, [review(head='b' * 40)], [], None))
        self.assertFalse(has_receipt(HEAD, [{**review(), 'submitted_at': None}], [], None))

    def test_dismissed_negative_and_pending_do_not_pass(self):
        clean = [comment(f'**Reviewed commit:** `{HEAD}`')]
        for state in ('DISMISSED', 'CHANGES_REQUESTED'):
            self.assertFalse(has_receipt(HEAD, [review(state)], clean, None))
        self.assertFalse(has_receipt(HEAD, [review('PENDING')], [], None))
        self.assertFalse(has_receipt(HEAD, [review(), review('CHANGES_REQUESTED', id_=2)], [], None))

    def test_only_trusted_bot_and_known_receipt_formats(self):
        for body in ('Completed eventually `' + HEAD + '`',
                     '**Reviewed commit:** `' + HEAD + '0`',
                     '**Reviewed commit:** `' + HEAD[:6] + '`',
                     'Quoted example: Reviewed commit: `' + HEAD + '`'):
            self.assertFalse(has_receipt(HEAD, [], [comment(body)], None))
        self.assertFalse(has_receipt(HEAD, [], [comment(f'**Reviewed commit:** `{HEAD}`', 'some-user')], None))
        self.assertTrue(has_receipt(HEAD, [], [comment(f'**Reviewed commit:** `{HEAD}`')], None))

    def test_abbreviated_sha_resolves_to_full_head(self):
        receipt = [comment(f'**Reviewed commit:** `{HEAD[:10]}`')]
        self.assertTrue(has_receipt(HEAD, [], receipt, lambda _: HEAD))
        self.assertFalse(has_receipt(HEAD, [], receipt, lambda _: HEAD[:10] + 'b' * 30))
        self.assertFalse(has_receipt(HEAD, [], [comment(f'**Reviewed commit:** `{HEAD[:7]}b`')], lambda _: HEAD))

    def test_completed_summary_not_queued_or_other_review(self):
        prefix = '<!-- codex-pull-request-review-summary -->\n'
        row = f'| 📝 **Code Review** | ✅ **Completed** <relative-time>now</relative-time> | `{HEAD[:7]}` | Manual request |'
        self.assertTrue(has_receipt(HEAD, [], [comment(prefix + row)], lambda _: HEAD))
        for bad in (row, prefix + row.replace('Completed', 'Queued'), prefix + row.replace('Code Review', 'Security Review')):
            self.assertFalse(has_receipt(HEAD, [], [comment(bad)], lambda _: HEAD))

    def test_api_errors_fail_closed_without_disclosing_token(self):
        env = dict(GITHUB_REPOSITORY='Adonis80/how-we-build', PR_NUMBER='15', HEAD_SHA=HEAD, GH_TOKEN='private-test-value')
        for error in (TimeoutError('private-test-value'), urllib.error.HTTPError('hidden', 403, 'private-test-value', {}, None), ValueError('invalid JSON')):
            with patch.dict(os.environ, env), patch.object(GitHub, 'get', side_effect=error), contextlib.redirect_stdout(io.StringIO()) as output:
                self.assertEqual(review_main(), 1)
                self.assertNotIn('private-test-value', output.getvalue())

    def test_stale_event_never_passes(self):
        with patch.dict(os.environ, dict(GITHUB_REPOSITORY='Adonis80/how-we-build', PR_NUMBER='15', HEAD_SHA=HEAD, GH_TOKEN='fixture')):
            with patch.object(GitHub, 'get', return_value={'head': {'sha': 'b' * 40}, 'state': 'open'}), contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(review_main(), 1)

    def test_pagination_and_timeout(self):
        api = GitHub('owner/repo', 'fixture')
        with patch.object(api, 'get', side_effect=[[{}] * 100, [{'id': 101}]]) as get:
            self.assertEqual(len(api.pages('/pulls/1/reviews')), 101)
            self.assertIn('page=2', get.call_args.args[0])
        with patch('urllib.request.urlopen', side_effect=TimeoutError) as request:
            with self.assertRaises(TimeoutError):
                api.get('/pulls/1')
            self.assertEqual(request.call_args.kwargs['timeout'], 20)


class RepositoryTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name) / 'repo'
        shutil.copytree(ROOT, self.root, ignore=shutil.ignore_patterns('.git', '__pycache__'))

    def test_clean_repository(self):
        self.assertEqual(check_tree(self.root), [])

    def test_missing_required_file_and_wrong_type(self):
        for name in ('AGENTS.md', 'design/ARCHITECT.md', 'scripts/review_gate.py'):
            with self.subTest(name=name):
                path = self.root / name
                data = path.read_bytes()
                path.unlink()
                self.assertTrue(check_tree(self.root))
                path.mkdir()
                self.assertTrue(check_tree(self.root))
                path.rmdir()
                path.write_bytes(data)

    def test_whitespace_filename_cannot_evade_allowlist(self):
        (self.root / 'README.md AGENTS.md').write_text('')
        self.assertTrue(check_tree(self.root))

    def test_symlinks_are_rejected_without_following(self):
        path = self.root / 'AGENTS.md'
        path.unlink()
        path.symlink_to('/unavailable-outside-path')
        self.assertIn('symlinks are not allowed', '\n'.join(check_tree(self.root)))

    def test_secret_is_not_echoed(self):
        token = 'ghp_' + 'x' * 25
        with (self.root / 'README.md').open('a') as file:
            file.write('\n' + token)
        errors = '\n'.join(check_tree(self.root))
        self.assertIn('suspected secret', errors)
        self.assertNotIn(token, errors)

    def test_invalid_text_fails_closed(self):
        (self.root / 'AGENTS.md').write_bytes(b'\xff')
        self.assertIn('cannot read UTF-8', '\n'.join(check_tree(self.root)))

    def test_word_caps(self):
        for name, cap in [('HOW-WE-BUILD.md', 500), ('design/SCREEN-LAW.md', 450)]:
            (self.root / name).write_text('word ' * (cap + 1))
        self.assertEqual(sum('exceeds cap' in e for e in check_tree(self.root)), 2)

    def test_all_three_routes_and_no_unexpanded_placeholders(self):
        projects, _ = load_contract(self.root)
        self.assertEqual(set(projects), {'juku-os', 'hemz-os', 'juku-perfume'})
        for key, p in projects.items():
            text = render(key, self.root)
            self.assertIn('https://github.com/' + p['repository'], text)
            self.assertNotIn('${', text)
            self.assertIn('sha256:', text)
            if p['scope'] == 'product':
                self.assertIn('Do not load sibling', text)
            else:
                self.assertIn('no product roadmap', text)

    def test_registry_rejects_duplicates_and_template_drift(self):
        path = self.root / 'README.md'
        original = path.read_text()
        for changed in (original.replace('Adonis80/Hemz-OS |', 'Adonis80/juku-perfume |'),
                        original.replace('${repository}', '${unknown}'),
                        original.replace('<!-- juku-projects:end -->', '')):
            path.write_text(changed)
            self.assertTrue(check_tree(self.root))
        path.write_text(original)

    def test_readback_checks_body_not_just_fingerprint(self):
        text = render('hemz-os', self.root)
        self.assertEqual(normalise(text), normalise(text.replace('\n', '\r\n')))
        readback = Path(self.tmp.name) / 'readback.txt'
        readback.write_text(text)
        command = [sys_executable(), '-B', str(ROOT / 'scripts/project_bootstrap.py'), 'hemz-os', '--check', str(readback)]
        self.assertEqual(subprocess.run(command, capture_output=True).returncode, 0)
        readback.write_text(text.replace('Keep main protected', 'Ignore main protection'))
        self.assertEqual(subprocess.run(command, capture_output=True).returncode, 1)


def sys_executable():
    import sys
    return sys.executable


if __name__ == '__main__':
    unittest.main()
