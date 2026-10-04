# Decision 0013: a new product gets its independent reviewer automatically

**Agreed by the CTO (Claude Opus 5.5, Juku OS Cowork session) and the consultant (Astra, GPT-6.1 Sol, high effort), 3 October 2026, four rounds (the fourth because round 3 changed two things).** The Chairman carried nothing between us. Status: agreed design, not yet built; the build lands in this pull request.

## The ruling

The Chairman, 3 October 2026: *"I should not be needing to add the reviewer to every repo and every product. It should be doing that automatically. For example, I am about to create multiple new projects under the Juku OS system. And that should automatically be set up with a reviewer without me manually needing to do that."* The CTO reads this as a direct ruling on the reviewer, its own exception to the 10 October freeze (as #130); the build is the smallest change that meets it. The same day he set the `juku-reviewer` App's repository access to "All repositories" (taken on his word; the session's token cannot list installations).

## What failed

Asking the reviewer to read Phena's pull request (Adonis80/phena#5) was refused: the route accepts one product, Hemz OS, hard-coded twice. Myst still gates on Codex; Phena has no gate. `library/product-joins.md` says the App is installed "by API, never his tap", which a session's token cannot do.

## What was agreed, in build order

1. **Check the access we already have.** Before any build, test whether the session's token can create a repository, write code and workflow files into it, and open and merge a pull request there. If so, nothing is asked of him. If not, he is asked once for a separate setup token (Repository creation plus only the rights step 1 shows are needed, all repositories), told plainly that it can write code and workflows in all his repositories and sits on his Mac. Never per product.
2. **Harden `review-product.yml`.** Every way of asking goes through it, Hemz OS's `ask.yml` included. Before any paid read it checks: the product is an exact `Adonis80/<name>` entry in the README's "Products under this rulebook" on main (a broken or duplicated list stops it); one read per pull request at a time, never cancelled; the pull request is open and not a draft; the commit asked about is its latest and is marked ready (step 5); the product's `verify` check passed on that commit; that commit has not been read. The old safeguards stay: a token scoped to one repository, the public-door lock on the key, no private text in the public log. A change to the product list is the risky class.
3. **Failed reads first.** Before the automatic ask is switched on, a finished verdict, a read still running, and a failed or abandoned request are told apart. Where it is unclear whether a read was paid for, nothing retries by itself; the builder sorts it out, never the Chairman.
4. **The automatic asker and the setup script.** A timed workflow in the rulebook looks at each listed product's open pull requests and asks for reads; the reviewer workflow re-checks everything above. Builders can still ask directly through the same checks. The setup script makes a product repository, or takes over one that exists, installs a starter kit copied from one reviewed rulebook commit (`gate.yml`, `wake.yml`, a `verify` workflow, `review-gate.py`; no `REVIEW_DISPATCH_TOKEN`), opens the join pull request, and is safe to re-run. The asker is off until step 3 passes. Copies are fixed to one reviewed commit; "always the latest" is out for the first version, because a shared workflow called from a private repository runs as that repository and inherits no key.
5. **Ready is one exact commit.** After its own review a builder adds an empty commit that changes no file. Its message carries `Review-Ready: yes` and `Review-Parent: <full ID of the commit beneath it>`; the reviewer workflow checks one parent, the same files as the parent, and a matching parent. No other commit may carry those lines.
6. **Join, then prove.** The join pull request merges with the product marked "joining". Its first real pull request is the proof: gate red unread, `verify` green, one signed read of the exact commit, the wake, gate green; a duplicate ask buys no second read, and a new commit without the ready mark stays unread. Only then is it "joined". No made-up test pull request.
7. Hemz OS's builders switch to the ready commit before the new checks go live; Hemz keeps `ask.yml`, which becomes harmless.
8. **Not in this change:** moving Myst (off Codex) and Phena (no gate) onto the kit. The asker must not suddenly buy reads for their open pull requests.

Words with it: the builder rule for the ready commit; the joining and joined states and the repaired "never his tap" line in `library/product-joins.md`; the freeze sentence in the README. Code session on Adonis80/how-we-build for steps 2 to 6; one pull request, read once at max.

## What changed whose mind

- **Astra moved the CTO** off "ask when pushes go quiet": a builder can push half the fixes, go quiet, then push the rest, and pay for two reads, so readiness is an explicit mark. Off no guard on duplicate reads: a timer and a direct ask could pay for the same read. Off "always use the latest rulebook version" (private repositories inherit no key). Off widening the everyday token: use a separate setup token and state the exposure.
- **The CTO moved Astra** from a ready comment to a ready line in the commit message (no extra write, no typed ID); to keep the timed asker (cloud workers can push but may hold no token that starts rulebook workflows, and a per-repository token is what is being removed); to prove the route on a product's first real pull request instead of a made-up one.
- **Astra then amended the CTO's ready commit:** an empty ready commit survives a change to the work beneath it, so it names its parent. The CTO added checking existing access first; Astra accepted.

## Agreement, and the strongest objection left

Astra, round 4: *AGREED*. Strongest objection left: the whole path from creating a repository to its first review is untested; until a new product goes from created to first review with no step from the Chairman, his requirement is not met. It is a test the build must pass, not a reason to add design. A second, accepted risk: "All repositories" on the App is not a fence; a stolen key could reach every repository, ignoring the product list.

## Cost

No new spend: the rulebook is public, and each product's gate runs on its own free allowance. Each new product costs about two reads: its join pull request and its first real one.

## Amendment, 4 October 2026 (the record above is not edited; where it says otherwise, this stands)

**The timer, by the Chairman's ruling.** *"I agree with your recommended option A. One timer in the rulebook only. Proceed to build."* One scheduled workflow in this repository, `ask-product-reads.yml`, every ten minutes, checks each listed product for ready commits and dispatches reads through `review-product.yml`. It lifts his 10 September stop on clocks (`library/carries-sessions.md`) for that one workflow only. No product gets a timer, a token or a schedule, and no session gets a clock. This replaces step 4's "The asker is off until step 3 passes" and the earlier plan to add the clock in a pull request of its own once a real product had shown a failed read and a running one apart: he ruled the clock on for this build, after the failed-read handling (step 3) passes. It passes as a test, not live: `product-reads/ask.py` and `review-gate.py` run seven timed runs against a made-up product, in which each ready commit is asked about once, and a read begun, lost, ended without a verdict or answered with findings is never retried, only a builder's `again` does that. The first live tick, once this is on `main`, is the proof, and a product's first real pull request is still step 6's.

**What the timer needed that step 4 did not say.** A commit a run of `review-product.yml` was already started for is never asked about again, whatever became of the run (the run's name carries the pull request and the commit). A question GitHub does not answer, or answers in a shape the asker does not read, is a failed run and never "nothing is ready". The second is the second read's advisory 4b; the first is the cost of a clock, since without it a refused ask would be made again every ten minutes.

**Step 5, as built.** "No other commit may carry those lines" is dropped. It made a second round impossible: after a read with findings, a fix and a new mark above the old one is the round, and a read already made of the earlier mark stops nothing. The head must still be a valid mark (one parent, the parent's tree, the parent named).

**The Cost paragraph is wrong on one point.** Every private repository draws on the account's one pool of 2,000 Actions minutes a month (`library/reviewer-asking.md`), so each new product's `gate`, `verify` and `wake` are not free: at least two minutes a push. The kit's gate no longer runs on `edited`, which changed nothing it answers on.

**Step 7, changed.** Hemz OS keeps nothing that asks twice: before this merges its builders have the ready commit and its own `ask.yml`, which asks every green push, is retired, so one asker asks. The CTO lines that up; the merge waits on it.

**Who asks, today.** The timer, once this is merged; and by hand, a session with write access here dispatching `review-product.yml`. The README's "with no step from him" is a goal until a product has gone from created to its first review without one.
