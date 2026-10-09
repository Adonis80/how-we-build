# What every product carries: the product read, and the model switch

Scope: every product repository. Open when: asking for a product read from here, or switching the model behind a role.

**The route** is `review-product.yml` ([decision 0002](https://github.com/Adonis80/how-we-build/issues/58)): the reviewer runs from here, where the environment door is real because this repository is public, and signs onto the product's pull request through the App. A read is asked by dispatching it on `main` with the product, the pull request's number and its exact head commit; first run [35902409140](https://github.com/Adonis80/how-we-build/actions/runs/35902409140), 23 September 2026. In a product the ask is of its ready commit, with the product's own `verify` passed on it, and the rulebook's timer sends it: `library/product-joins.md`.

**What a product read carries.** Of the product's own pages, the `roadmap.json` item whose id the pull request's title opens with and the `PRODUCT.md` sections that item names, naming every other item and section with its size ([#86](https://github.com/Adonis80/how-we-build/pull/86)); an item that names no section carries none. Beside the files a change touches, their relative JS, TS and Python imports and a page's scripts, one hop (decision 0010, 1a). That a product's own wake re-runs its gate when a verdict lands is not yet shown on a cited run; the first read that shows it is cited here.

**Never a sentence permitting a merge while the check is red**: one check carries the file lists and the secret scan too, so any such permission waives those with it.

**A model switched in one edit** (his requirement, 22 September 2026; met by decision 0008): both reviewers, this repository's and the product route, ask `model-registry/` for a role and name no model. How to ask, inspect and switch: `library/model-registry.md`.
