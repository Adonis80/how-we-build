# How a product joins

Scope: a product joining this rulebook, and every product's `AGENTS.md`. Open when: a product is added, or a product's review section is written or checked.

1. Its repository's `AGENTS.md` begins with one line: `Rulebook: https://github.com/Adonis80/how-we-build — read HOW-WE-BUILD.md before anything else, then What every product carries in its README.` Below that comes only what is true for that product. It ends with a `## Review guidelines` section: a pointer to `library/reviewer.md`, the block below, and the hazards particular to that product.
2. Its Claude Project's instructions are `project-template.md`, blanks filled (`projects.md`).
3. One line in the README's *Products under this rulebook*.
4. The `juku-reviewer` App installed on the repository, by the session's own hands (`review-machinery.md`), and the product added to `review-product.yml`'s list. Until it is on that list it has no read its gate can count, so its slices park at step 5.

**The review section** is a copy of the least of the brief that the reviewing tool needs in front of it, kept because the tool cannot follow a link. A pointer alone was tried, and the marks of the brief vanished from the reviews. It changes only when `reviewer.md` does.

```
## Review guidelines
- Cold read: form your view from the diff, the tests, `PRODUCT.md` and `roadmap.json` first, and read the pull request's own account last. Never inherit the author's conclusions.
- Look for what is wrong, missing, duplicated, untested, or quietly wider than the slice. Say what you checked and what you did not, and how sure you are. Do not manufacture disagreement.
- Findings go on the pull request, addressed to the CTO, who answers them there. Two rounds at most. Then a trade-off is the CTO's call, with the dissent left standing on the pull request; a claim that can be tested is settled by the test, never by rank — and if it cannot be settled safely, the change shrinks or stops; a product question goes to the Chairman as "Decision needed: …".
- A review clears only the commit it read; a later push voids it.
- Plain English. Never write a file into the repository.
```
