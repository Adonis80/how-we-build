Read HOW-WE-BUILD.md before working. This repository is the rulebook, not a product. Provider setup and the Juku OS build entry point are in README.md.

Changes go through a PR against protected main. A new rule, file, check or agent needs CHARTER.md §13's gate or Dhayan's explicit ruling; record the evidence in the PR. Deletion and wording repairs need no new permission. The CTO never merges its own additions here.

Run bash check.sh before committing. It includes the regression suite. In CI the review receipt is an additional check, not an approval or a substitute for resolving findings.

## Review guidelines

Review the diff and existing canonical files before reading the PR's account. Address the CTO. Each finding says what was checked, what was not and confidence. Check for conflicting instructions, duplicated truth, weakened business/design/proof requirements, inaccurate claims about provider access, and review-gate bypasses. A provider limitation belongs in its adapter; private product facts never belong in this public repository. Cross-vendor review is required for gate changes. Prefer executable checks over prose reminders, and deletion over more machinery.
