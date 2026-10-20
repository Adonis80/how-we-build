# The independent reviewer: parking

Scope: every repository under this rulebook, in either stack. Open when: about to park a slice, or the reviewer seems out.

**Ask, then park on the answer.** A session parks a slice only on a refusal it was given itself, on that pull request, that hour; never on a note, a roadmap line or another session's report that the reviewer is out. One ask settles it in seconds.

**When the gate can count no read** (the reviewer unreachable, its allowance spent, the service down), the gate does not open and is not waived. The slice parks: one comment names the blocker, then no further pushes or asks. Nothing watches for the reviewer's return, on any clock; the next session to start asks on the oldest parked pull request (or first in the repository's own order) and finds out. Parked work never stops the line: the next item is taken. When the reviewer returns, parked pull requests re-enter review in order, one ask each. Beyond the Reviewer-down issue, he hears of it only when it moves something he was promised.

**When a rollout breaks the reviewer.** After a machinery merge, `.github/workflows/canary.yml` sends one tiny real read; red, it opens the Reviewer-down issue and `check.sh` holds every machinery pull request until a canary passes; `.github/workflows/monitor.yml` opens it too for an ask no read follows. The change is reverted unless a smaller repair is shown safer. **The emergency route**, for reviewer repair or revert only: an admin merges with GitHub's own bypass, the pull request linking the outage issue and the exact repair commit and naming the check bypassed, recorded as an emergency exception, never a clean review; a canary runs after it lands.
