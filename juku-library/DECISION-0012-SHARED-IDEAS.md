# Decision 0012: an idea that helps more than one product goes to the rulebook, and the board lists every product's suggestions

**Consensus of the CTO (Claude, Juku OS Cowork session, Sonnet 5.5) and the consultant (Astra, GPT-6.1 Sol, high effort), 3 October 2026, three rounds, no courier; the decision record is [issue #145](https://github.com/Adonis80/how-we-build/issues/145).** The Chairman carried nothing between us. It closes the two gaps [decision 0011](DECISION-0011-IDEAS-FOR-LATER.md) left. 0011's record is not edited; this one supersedes it in two places only, named below. It holds no product text: the rulebook is public.

## The ruling

The Chairman, 3 October 2026: *"lift the freeze for the cross-product ideas fix"*, and *"make sure that context is always lightweight"*. The 10 October freeze lifts for this one change only (CHARTER 13). It authorises this decision, not the implementation of any idea and not any other pull request here.

## What was agreed

1. **The rule.** At capture and at review, an idea about the rulebook, or about a rule, check, template or tool more than one product already shares, is a rulebook pull request, not a roadmap item. Reuse alone does not qualify: otherwise similar customer features would be lifted into shared machinery. A mixed idea splits; the product part stays on its roadmap. This route transfers ownership of the proposal; it authorises no implementation and overrides no freeze.
2. **Public, so general.** The write-time search covers the roadmap, `retired` and rulebook pull requests, closed ones too, by subject. Only the general change is published, never product evidence (text, screenshots, links, filenames, errors).
3. **One owner at every moment.** Until its pull request exists the idea waits on the roadmap, `next` `pending transfer`. On opening, the pull request number goes in the handover and the pull request owns the idea. At the next roadmap edit one final `retired` line, `lifted to the rulebook, #N`, replaces the item; reconsideration happens in the pull request, never on the roadmap, so a rejected proposal is not product work. A failed publication leaves the original intact. An agreed transfer waits without repeat review and resumes when its obstacle clears.
4. **Where it is written.** `library/ideas-for-later.md` (3,989 of 4,000 bytes; Open when unchanged, so the README row still matches). Its 2 October ruling quote moved to the README's ideas line; its restated list of what reaches the Chairman became a pointer to *Who decides* in `HOW-WE-BUILD.md`, the gap left standing on #144. Also trimmed, no requirement dropped: the picture clause (`HOW-WE-BUILD.md` already says an outcome or a picture reaches him) and one style sentence. `HOW-WE-BUILD.md` is untouched.
5. **The board.** One folded card, "N suggested ideas", above the project pages: every product's `proposed` items, his own included, grouped in the board's row order, rendered from the roadmaps the board already reads. A view only: no copy, no file, no new field, no fifth page, no new duty on sessions, no change to any count (0007 §2). 0007 §8's disclosure contract holds despite the PIN. This supersedes 0011's rejection of "one ideas list for all of Juku" for this derived view only: 0011 refused it for the public repository; the board is private. It rides in its own pull request.

## What changed whose mind

- **Astra moved the CTO** on: the test living in the page, with reuse alone not qualifying; the search reaching closed rulebook pull requests; "no product text" meaning a general proposal written afresh; the lifted line being final, not a second owner; the pull request number recorded in the handover so a stopped session can recover; agreed transfers resuming without repeat review (her round-3 sentence, taken as given); the freeze exemption naming this decision only; the card named, folded, every item, no new duty; 0012 saying outright that it supersedes 0011 for the view.
- **The CTO moved Astra** on nothing of substance. She found the packaging sound (page first, board its own pull request) and the board shape as proposed.

## Agreement, and the strongest objection left

Astra, round 3: one wording objection, taken verbatim; everything else closed. She held OPEN only to confirm that one sentence. The Chairman's limit for this task is three rounds, so no fourth was run; the independent reader sees the final words. Her strongest objection, met: clearing a publication obstacle must not commission another settled debate. **Left standing:** the page has 11 bytes spare, so its next change must pay in cuts; and 0011's one-month keep-or-revert test still applies to the whole.

## Checked, not assumed

- The board's own selftest passes with the card, and fails when the card drops an item awaiting his decision (run against a deliberately broken copy). The real board with real roadmaps is unproved until a refresh runs after the merge.
- `library/build-board.md` has 28 spare bytes; the clause for the card lives in `board/build.py`'s header and here.
- Still unproved: whether sessions apply the shared test without lifting too much, or too little; one month's evidence will say.
