# The review machinery

Scope: this repository, and the route it runs for products. Open when: changing `check.sh`, `review-gate.py` or a workflow, porting the badge to a product, or installing the App.

**The badge.** A read must arrive under a login a branch cannot wear, as a signal a branch cannot erase. Only a GitHub App can create a check run, and nobody with write access can forge, edit or delete one. So the reviewer signs as the `juku-reviewer` App, and its verdict is that check run's own `conclusion` on its own `head_sha`. Nothing is parsed out of prose. The comment the workflow also posts is for people, and the gate reads none of it.

**The door.** The App's private key lives in a repository environment named `reviewer`, whose deployment branch policy admits `main` alone, and the reviewer's job names it. A run whose ref is a branch is refused the job before it starts. The reviewer reaches `main` because it triggers on `issue_comment` alone, whose ref is the default branch. `.github/workflows/door.yml` is the standing proof: push a branch named `proof/door-*` and watch it refused, or run it on `main` and watch it read the key. A green door run on a branch means the badge is forgeable, and nothing merges until the policy is back.

**The machine is six files.** `review-gate.py` holds the register and the wiring checks. `.github/workflows/` holds the reviewer, the wake it calls, the door's proof and the product reviewer (`review-product.yml`). `check.sh` runs the lot.

**A gate change is judged by the gate it proposes.** `check.yml` runs the head's own `check.sh`, and with one reviewer nobody stands behind it. The check prints a `note:` line on any such pull request, green or red: read the diff, not the green. What ends this is a second reviewer answering, not a sentence. A reviewer written down before it can answer would hold every commit shut.

**The product route.** `review-product.yml` reads a product's pull request from here, where the door is real because this repository is public, and signs the verdict onto the product's head through the App. A writer dispatches it on `main` with the product, the pull request's number and its exact head commit. It reads only the products on its own list, which must be on the README's map. Its first run, 35902409140, read Hemz OS's port clean and signed it there. Still to be shown: the product's wake re-running its gate when a verdict lands. Whether the App is installed on Myst is not checked from here.

A sentence permitting a merge while the check is red is never the answer. One check also carries the word caps, the file lists and the secret scan, so such a permission waives those too.

**Installing the App is the session's hands** (his ruling): one call, `PUT /user/installations/{installation_id}/repositories/{repository_id}`, which can do nothing else. His part is only the identity code GitHub emails before the App's settings open. Generating the key, sealing it into the `reviewer` environment and deleting it from disk are the session's.

**Next reviewers, none built.** Open-weight models join by the same route (his ruling): OpenRouter, with GLM 5.2 first, as the main backup. Fable 5.1 is named as a reviewer but has no App, check-run name or workflow yet. What the six classes are owed once it answers is settled in the pull request that wires it.

**A model switched in one edit** is his requirement and not met. Changing the model behind any role (the lead, the reviewer, a specialist) should touch one file. Today the reviewer's is set in `review-gate.py`, repeated as a flag in `review.yml` and `review-product.yml`, and run by one vendor's tool on its credential. A switch touches three gate files and a secret. No registry exists; the first build is the smallest thing that passes.
