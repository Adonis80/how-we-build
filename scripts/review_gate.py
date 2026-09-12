#!/usr/bin/env python3
"""Require a verifiable Codex receipt on the live PR head; never an approval."""
import json
import os
import re
import sys
import urllib.error
import urllib.request

BOT = 'chatgpt-codex-connector[bot]'
SHA = re.compile(r'[0-9a-f]{40}')
REVIEWED = re.compile(r'^\s*(?:\*\*)?Reviewed commit:(?:\*\*)?\s*`([0-9a-f]{7,40})`\s*$')
SUMMARY = '<!-- codex-pull-request-review-summary -->'
COMPLETED = re.compile(r'^\|\s*📝 \*\*Code Review\*\*\s*\|\s*✅ \*\*Completed\*\*[^|]*\|\s*`([0-9a-f]{7,40})`\s*\|[^|]*\|\s*$')


def comment_refs(comment):
    if (comment.get('user') or {}).get('login') != BOT:
        return []
    body = comment.get('body') or ''
    refs = []
    for line in body.splitlines():
        match = REVIEWED.fullmatch(line)
        if not match and SUMMARY in body:
            match = COMPLETED.fullmatch(line)
        if match:
            refs.append(match.group(1))
    return refs


def has_receipt(head, reviews, comments, resolve):
    """Only submitted reviews count; a dismissed/negative latest review blocks fallback."""
    current = [r for r in reviews if
               (r.get('user') or {}).get('login') == BOT and
               r.get('commit_id') == head and r.get('state') != 'PENDING']
    if current:
        latest = max(current, key=lambda r: r.get('id', 0))
        return bool(latest.get('submitted_at')) and latest.get('state') in ('COMMENTED', 'APPROVED')
    for comment in comments:
        for ref in comment_refs(comment):
            # Full SHA must match exactly; abbreviated refs must resolve uniquely via GitHub.
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
        req = urllib.request.Request(self.base + path, headers={
            'Authorization': 'Bearer ' + self.token,
            'Accept': 'application/vnd.github+json',
            'X-GitHub-Api-Version': '2022-11-28',
        })
        with urllib.request.urlopen(req, timeout=20) as response:
            return json.load(response)

    def pages(self, path):
        result = []
        for page in range(1, 1001):
            batch = self.get(f'{path}?per_page=100&page={page}')
            if not isinstance(batch, list):
                raise ValueError('invalid API collection')
            result.extend(batch)
            if len(batch) < 100:
                return result
        raise ValueError('review history exceeds pagination limit')


def main():
    repo, number, head, token = (os.environ.get(k, '') for k in
                               ('GITHUB_REPOSITORY', 'PR_NUMBER', 'HEAD_SHA', 'GH_TOKEN'))
    if not (re.fullmatch(r'[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+', repo) and
            re.fullmatch(r'[1-9][0-9]*', number) and SHA.fullmatch(head) and token):
        print('FAIL: review check needs valid GITHUB_REPOSITORY, PR_NUMBER, full HEAD_SHA and GH_TOKEN')
        return 1
    api = GitHub(repo, token)
    try:
        pr = api.get(f'/pulls/{number}')
        if pr['head']['sha'] != head or pr['state'] != 'open':
            print('FAIL: event does not name the live open PR head')
            return 1
        reviews = api.pages(f'/pulls/{number}/reviews')
        comments = api.pages(f'/issues/{number}/comments')
        if has_receipt(head, reviews, comments, lambda ref: api.get(f'/commits/{ref}')['sha']):
            print(f'ok: Codex review receipt verified for {head}; findings and cross-vendor review still require resolution')
            return 0
        print(f'FAIL: no valid Codex review receipt for {head}; request once, then rerun check after completion')
        return 1
    except (OSError, ValueError, KeyError, TypeError) as exc:
        # Never print URLs, headers, API bodies or credentials in errors.
        print(f'FAIL: could not verify review ({type(exc).__name__}); keep the gate closed')
        return 1


if __name__ == '__main__':
    sys.exit(main())
