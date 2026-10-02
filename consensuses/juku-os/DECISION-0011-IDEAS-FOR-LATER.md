# Decision 0011: ideas for later have a home, and a joint review

**Consensus of the CTO (Claude, Juku OS Cowork session, Sonnet 5.5) and the consultant (Astra, GPT-6.1 Sol, high effort), 2 October 2026, three rounds, no courier.** The Chairman carried nothing between us. What lands is one new page, `library/ideas-for-later.md`, the matching edits to `library/consultant.md` and `library/consultant-instructions.md`, and four small edits to `README.md`; this record is the reasoning. It holds no product idea text: the rulebook is public.

## The ruling

The Chairman, 2 October 2026, after a builder session mentioned improvements once in chat and lost them (Hemz OS, the slice of PR #130): *"What I think we need is to have all of your ideas for later documented somewhere for review between Claude and ChatGPT and for them to reach a consensus on."* He lifted the 10 October freeze for this change only. It stands under CHARTER 13 as his explicit ruling about how he wants the system to work.

## What was agreed

1. **Where.** In each product's own `roadmap.json`, as `proposed` items, a status the products already define as the CTO's suggestion, not agreed until he says. No second file, no second map, no list across products (this repository is public; product text is private). Ideas about the rulebook itself stay as open pull requests, as today.
2. **What a session writes.** One line, in the pull request's handover, when the idea surfaces; copied at the closing or parking roadmap edit into `roadmap.json` with `id` `I<PR number><letter>`, a `plain` line `Captured <date>; why; surfaced by <slice>, <PR>`, `status` `proposed`, `level` P4 where the product keeps levels, every other field null. It never blocks or widens the slice. A search by meaning of the roadmap and its `retired` list comes first; a match with new evidence updates the line and keeps its first capture date, a match without it writes nothing. A wrong result seen now is a defect, not an idea.
3. **How review is triggered.** Asked for, never scheduled (the 10 September hard stop). At the roadmap read that opens a session the CTO asks the consultant when no agreed item is ready, five or more `proposed` items stand, one has stood 30 days, or the Chairman asks. One exchange per product, all its open ideas, to consensus. Neither side disposes of an idea alone. Where the consultant cannot be reached the review stays pending and shipping goes on.
4. **What consensus produces.** One of three: *put to him* (a product question: money, a permission, what the product does, how it looks, anything irreversible) for one word, *agreed* or *not yet*; *a routine repair* that restores what exists and adds no capability, which the CTO does under the normal checks; or *retired*, one line kept in the roadmap's top-level `retired` list with its reason and what would reopen it. Only product questions reach him.
5. **Kept small.** Five is a review threshold, not a cap; thirty days forces a joint review at the next active session, never a solo dismissal. After a month the test is whether ideas are preserved and decided, not how many ship. If review effort outweighs delivery the page is reverted (CHARTER 13), not left dormant.
6. **Where it is written.** `library/ideas-for-later.md` owns it. `library/consultant.md` names idea review as a fourth, narrow job (its own "three jobs and no others" sentence is replaced; architecture, research and model-design consultancy stay gone), and `library/consultant-instructions.md`, the block pasted into the consultant's own settings, says the same in its own words. The CTO found that second copy by searching for the superseded sentence (CHARTER 7), after the consultant's round 3; the consultant is shown the wording before merge. `README.md` gains the index row, one line under *What every product carries*, and the record of the freeze lift. `HOW-WE-BUILD.md` and `library/carries-sessions.md` are untouched. A product needs no edit before its next roadmap edit.

## What changed whose mind

- **Astra moved the CTO** on: no solo expiry (the CTO had let a 30-day-old idea be decided alone); five as a threshold, not a quota; legacy `proposed` items counting; "at least one shipped" dropped as a pass test; "not yet" retired with a condition rather than rejected; a routine repair kept on the roadmap until it merges; defects repaired first, not filed as ideas; a capture date inside `plain`, original date kept on update; the outcome of a review recorded in the handover and the roadmap edit, never in chat alone; a reopened idea returning to `proposed`, not hiding in `retired`; "anything irreversible" and "checks, review and visual acceptance still apply" added.
- **The CTO moved Astra** on: a new page rather than editing `library/carries-sessions.md` (431 spare bytes of 4,000 against about 3,500 needed, and fitting it meant rewriting four unrelated rules under the tidying freeze, which `library/changing-the-rulebook.md` warns against; CHARTER 7 allows a new document when the existing owner cannot hold the subject clearly); an id of `I<PR number><letter>` rather than a counter, which needs no lookup and cannot collide between parallel sessions.

## Agreement, and the strongest objection left

Astra, round 3: *AGREED*, wording and scope exactly as presented, no fourth round. The strongest objection left, and it stands: review effort could grow faster than product value. The one-month keep-or-revert test is therefore part of the decision, run at the first review a product holds on or after 2 November 2026 (asked for, never scheduled), counting ideas preserved and decided against the effort the reviews cost.

## Rejected

- A separate ideas file per product: a second map, one more place to look, and the board would have to learn it.
- One ideas list for all of Juku: the rulebook is public and product text is private; one pile invites cross-product noise.
- A cap of five open ideas, and a 30-day solo decision (both the CTO's round-one proposals, withdrawn).

## Seed test: four ideas from one Hemz OS slice, by kind only

- Closure days missing from a rota: a product-truth question for the shop's owner, after first reproducing whether a wrong promise is already observable, which would make it a defect and not an idea.
- A message that names the wrong cause when time away moves a promise: a routine repair, provided the cause is known and may be shown to that viewer; it never invents or reveals a private reason.
- Two similar buttons on one sheet: not a routine repair; behaviour, hierarchy and appearance follow the design route, and a material visual change reaches him as a picture.
- An idea already the next roadmap step: caught as a duplicate by the write-time search and never written.

## Checked, not assumed

- Hemz OS, Myst and Phena roadmaps read live through the Chairman's Chrome on 2 October 2026. Only Hemz has a `retired` list (empty, read by nothing); only Phena keeps a `level`; Hemz has four `proposed` items, two of them stale (one parked on his own earlier answer, one superseded), which is why the list is counted and aged.
- Astra read Hemz's and Myst's `check.sh` by source (the CTO's own read of Hemz's was cut short by the browser): neither validates a `retired` key or a null or P4 level; both only parse the JSON and bound the `next` length. That is source inspection, not a CI run. The CTO read Phena's repository: no `check.sh` and no `.github` directory, so no check of its own can reject either.
- The build board's reader keeps nine named fields per item and ignores everything else, so an `I`-item renders as "Suggested" with no code change.
- `check.sh` of this repository passes on the final files, locally; the page is 3,492 bytes of 4,000 and `library/consultant.md` 3,216.

## Still unproved

- Whether sessions actually write the one line and search first; the first Hemz review (where two existing `proposed` items are stale) is the test, and is not part of this change.
- Whether five or more is the right size, or the 30-day age; one month's evidence will say, and the page says what failure looks like.
- This session ran as Sonnet 5.5, not the model the Project's instructions name for a first round; the debate was not stepped up. The consultant held no objection that needed it.
