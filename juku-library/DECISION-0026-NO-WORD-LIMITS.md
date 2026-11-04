# Decision 0026: no word limits; a hierarchy of information

**His words, 4 November 2026, 21:03, given in a Hemz OS Project code session**, as recorded the same evening on [#314](https://github.com/Adonis80/how-we-build/issues/314#issuecomment-6642065352) and queued on [#325](https://github.com/Adonis80/how-we-build/issues/325#issuecomment-6642070550):

```
The rule book is wrong. There should not be a word limit. Instead, we will have a hierarchy of information. The reason for the original word limit was your sessions were attempting to load the entire rulebook into its context, which ruined its context. But the solution isn't to cap the words on the rulebook. The solution was to turn the rulebook into a hierarchy of information, so the sessions do not load the entire rulebook. Rather, they are able to sort through the hierarchy and only load the absolute minimum amount of context required to do the job at high quality. The problem of trimming words is that is a catastrophic failure point, which has led to the instructions being worthless and causing wasted time and money.
```

**Why he said it.** On Hemz OS#282 and #283 the constitution's 450-word cap made two sessions cut words: the first cut his dated 28 October approval and the reviewer blocked it; the re-cut moved token values off the page to fit.

**What it replaces.** Decision 0021's Part B2, the reading path's word budget, and every other word cap: a product constitution's 450 words and 80 before its first heading, a product `AGENTS.md`'s 500, and the cut a change owed for the words it added.

**Where it lives.** `library/changing-the-rulebook.md`, *No word limits; a hierarchy of information*, with the line in `HOW-WE-BUILD.md`, *Changing a rule*. `check.sh` holds the hierarchy: every library page named in the README's index with when to open it. `AGENTS.md`, exam question 12, holds it in the cold review.

**What it does not cover.** One home per rule, the `Replaces:` line, a constitution's five headings and its dated approvals all stand. A design brief's slots (`product-reads/brief-check.py`) are a brief to a designer, not a rule page, and are not changed here.
