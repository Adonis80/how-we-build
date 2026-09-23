# Claude Projects

Scope: every product's Project and the Juku OS Project. Open when: a Project's instructions carry an older template date than the README's boot line, or a Project is being set up.

**At the start of a session in a Project**, if its instructions carry an older template date than the README's boot line, the session sets them to the current template, filled in for the product, before anything else, once.

**A Project holds its instructions and nothing else** (his ruling). No files, and nothing in its knowledge or context: not the rulebook, not a product's files. A Project's GitHub option copies file contents in and cannot write back, so the copy is stale the moment anyone pushes, and two copies of one truth is the failure this structure exists to end. Sessions read the rulebook and the product repo live. The instructions are the only place a session can be told how to reach a private repo, and they keep no history: if they are ever lost or wrong, set them again from here.

**The session sets them; he is handed no paste** (his ruling). It works in the Claude app's built-in browser, signed in to `claude.ai` by him: `claude.ai/projects` → *New project* → the name and one line saying what it is → *Create project* → *Instructions* → *Edit instructions* → the template, whole → *Save instructions*. An existing Project is the same route from its own page. The session then reloads the page, reopens the instructions, reads them back and says what it set. Having typed into it is not done. If that browser is not signed in, he is handed that one tap and nothing else. Anything product-specific found in old instructions goes into the product's `AGENTS.md` by pull request.

**Text for him is handed over whole.** Where there is no other way (a session with no Mac connected), he is given the complete new text to replace the old with, never a sentence to find and splice in.

**The templates** carry a date in their first line, and the README's boot line names the current one, so a session compares one date rather than the whole text. `project-template.md` is a product's Project; `juku-os-project.md` is the Juku OS Project's, which is not a product: it builds nothing, and it is where the system's own words change.
