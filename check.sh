#!/usr/bin/env bash
# Local structural/regression checks; PR CI also requires a review receipt.
set -euo pipefail
cd "$(dirname "$0")"
export PYTHONDONTWRITEBYTECODE=1
python3 -B scripts/check_repo.py
python3 -B -m unittest discover -s scripts -p 'test_*.py'
case "${GITHUB_EVENT_NAME:-}" in
  pull_request|pull_request_review) python3 -B scripts/review_gate.py ;;
esac
printf '%s\n' 'check.sh: all applicable checks passed'
