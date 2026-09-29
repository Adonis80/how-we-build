# How a product joins

Scope: every product under this rulebook. Open when: adding a product to the map, or setting up its repository.

1. Its repository's `AGENTS.md` begins with one line: `Rulebook: https://github.com/Adonis80/how-we-build — read HOW-WE-BUILD.md before anything else, then What every product carries in its README.` Below that, only what is true for that product, ending with a short `## Review guidelines` section: the pointer to the brief (*The independent reviewer*), the least of it the tool needs in front of it, and the hazards particular to that product.
2. Its Claude Project's instructions are the template (`library/project-template-product.md`), blanks filled.
3. One line in *Products under this rulebook* in the README, one in *Where each product's plan lives*, and its name in `ROWS` in `board/build.py`, in the order decision 0007 sets; the board's selftest holds `ROWS` to the first list, and that file is part of the review gate, so this pull request gets the risky read.
4. The `juku-reviewer` App installed on the repository — a session's own hands, by API, never his tap. The route that reviews a product's pull requests from here reads only the products on its own list (*What every product carries*); until a product that joins is on it, it has no read its gate can count, so its slices park at step 5.
