# Project instructions

Scope: every Project under this rulebook, the consultant's too. Open when: setting up or checking a Project.

**We don't use instructions** (his rulings: 3 November 2026, *"All instructions. Should not be contained in the project's instructions. Rather, we point to GitHub as the one source of truth"*, [#305](https://github.com/Adonis80/how-we-build/issues/305); 4 November 2026, *"We don't use instructions"*, [#305](https://github.com/Adonis80/how-we-build/issues/305#issuecomment-6623939914)). A product's Claude Project carries no rule, no permission and no file: a copy is stale the moment anyone pushes (his ruling, 6 September 2026). A product's Project holds one pointer, every blank filled, nothing saved while any `<…>` remains:

```
# <Product>

How we build: https://github.com/Adonis80/how-we-build — read HOW-WE-BUILD.md first.
GitHub is the one source of truth; nothing here is a rule.

What we build: https://github.com/Adonis80/<repo> (private) — read its AGENTS.md,
PRODUCT.md and roadmap.json live.
```

A session that finds its product's Project holding more than the pointer first moves anything true only of that product (its fallback when attaching fails, say) to its `AGENTS.md` or `README.md` by pull request, then sets the pointer; otherwise it changes a Claude Project's text only when the pointer itself is wrong (a renamed repository, a blank, a typo), and never asks him to. **The Juku OS Project is the exception, by his choice** (4 November 2026, above, said of that Project): its text is his own and may hold more than a pointer; no session checks it against this page or rewrites it, and where it and this repository differ, this repository wins (*Which rule wins*). The Juku OS Project reads this repository and uses the README's map as the whole register, opening a product repository only for live detail; each product's Project reads its own repository and this one (his ruling, 11 September 2026). Reuse this register; never start a second map.

**When attaching a repository fails**, a product's route is its `README.md`'s; the Juku OS Project's is the Mac: the connected folder `~/Documents/Claude/Projects`, the key in `.alma-secrets/github-token`, read into a shell variable and never printed.

**Where to read is not permission to read**: each Project's own GitHub connection is proved by fetching live commits and open pull requests from inside it.

**Setting one up; he is handed no paste** (his ruling, 14 September 2026). A Claude Project: the Claude app's built-in browser, signed in by him, `claude.ai/projects` → *New project*, its name and one line saying what it is, *Create project* → *Instructions* → *Edit instructions* → the pointer whole → *Save instructions*, then reload, reopen, read back and say what it set; typing into it is not done. If the browser is not signed in he gets that one tap and nothing else. Only a session with no Mac connected hands him the pointer to paste. Whenever any text he pastes somewhere changes, he is given the complete new text, never a sentence to find and splice in.

**The consultant's Project in ChatGPT keeps its block** (decision 0015; his rulings above were made of Claude Projects, #305 of Hemz OS's and 4 November of Juku OS's, and its block is the consultant's only brief): its standing instructions are the block in `library/consultant.md`, each `<role>` filled from that registry role as "picker label (effort)". A session pins one commit of protected `main`, compares the installed text with that block, and, finding them different, sets them through the Chrome extension, whole, the commit named in its handover, nothing saved while any `<…>` remains, and reads them back; a read-back proves the picker label, never the model behind it.
