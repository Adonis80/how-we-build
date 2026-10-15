# The upgrade log

Scope: this repository, and what it runs for every product. Open when: proposing an upgrade, or the Chairman asks what changed.

One line per upgrade, newest first: the date, what changed, why, its proof, and the pull requests (his ruling, 15 October 2026, [#222](https://github.com/Adonis80/how-we-build/issues/222)). A pull request that changes what runs — the gate's files, a workflow, the model registry, the product reads, or the build board — adds its line here in the same pull request; `review-gate.py` holds it, red until the line is there. Words alone need none. A proof not yet shown says so, and its line is brought up to date when it is.

- **15 October 2026** — This log, held by the gate. *Why:* one place that says what changed and why, without anyone remembering to write it. *Proof:* `review-gate.py`'s main-run cases: an unlogged gate or board change is red, a logged one opens. [#225](https://github.com/Adonis80/how-we-build/pull/225)
- **15 October 2026, in review** — The board's proposals card: every open proposal and product idea in one ranked queue, with its stage and a debate-due banner. *Why:* his approved design (Option D), on the live read, adding no deploy. *Proof:* not yet — its read and his look at its screenshot are pending; this line is completed when it merges. [#224](https://github.com/Adonis80/how-we-build/pull/224)
- **15 October 2026** — The build board reads live when opened and deploys only when its own code changes. *Why:* it made 32 of the account's 40 Vercel deploys in a day, crowding the products. *Proof:* a probe on the host ran the function and read GitHub and OpenRouter in 301 ms; read clean on e0c9fae; a full day with no board deploy is not yet shown. [#223](https://github.com/Adonis80/how-we-build/pull/223)
