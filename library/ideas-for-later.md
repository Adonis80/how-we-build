# Ideas for later

Scope: every product session, and the consultant. Open when: a session spots an improvement it will not build now, or a roadmap read shows ideas due for review.

**His ruling, 2 October 2026:** *"all of your ideas for later documented somewhere for review between Claude and ChatGPT and for them to reach a consensus on"*; [decision 0011](../consensuses/juku-os/DECISION-0011-IDEAS-FOR-LATER.md).

**Where.** The product's own `roadmap.json`, as `proposed` items, which already means the CTO's suggestion, not agreed until he says. No new file, list or map.

**Writing one.** When it surfaces, one line under `Ideas:` in the pull request's handover. At the closing or parking roadmap edit it is copied into `roadmap.json`: `id` `I<PR number><letter>` (`I130a`; a letter is given once per origin pull request, counting those already in its handover, and never reused), `title` what, `plain` `Captured YYYY-MM-DD; why; surfaced by P32, #130`, `status` `proposed`, `level` P4 where the product keeps one, every other field null. It never blocks or widens the slice. Three a slice is normal; a fourth distinct idea is still written. First search by meaning the roadmap and `retired`: a match with new evidence updates that line and keeps its first capture date; a match without it writes nothing. A wrong result seen now is a defect, repaired first, never filed as an idea.

**Review.** Asked for, never scheduled: no clock, no automation. At the roadmap read that opens a session the CTO asks the consultant when no agreed item is ready, five or more `proposed` items stand, one has stood 30 days, or the Chairman asks. The consultant reads the live roadmap and `retired` first. One markdown exchange per product, every open idea in it, until the two agree; neither disposes of an idea alone. Its outcome is recorded in the pull request's handover and the roadmap edit it leads to, never in chat alone. Legacy `proposed` items count, dated by the item where it records one, else "age unknown; reviewed YYYY-MM-DD". If the consultant cannot be reached the review stays pending and shipping goes on.

**Each idea ends as one of three.**

1. *Put to him*, when it is a product question: money, a permission, what the product does, how it looks, anything irreversible. The gate reads `Decision needed:`, his word is *agreed* or *not yet*, and a material visual change reaches him as a picture. *Agreed* makes it a normal P or A item, its `plain` keeping the I-number, its level set. *Not yet* is retired, with its reopening condition.
2. *A routine repair*: it restores what exists to what it claims and adds no capability. Its level is set at that review and it does not wait for product approval; checks, review and visual acceptance still apply. The item and a short `next` stay until it merges, then the item goes.
3. *Retired*: one line in the roadmap's top-level `retired` list, started at the next roadmap edit where absent: `I130a, title, YYYY-MM-DD: reason; reopens when <condition or new evidence>`. A suppression note, never a changelog. When its condition or new evidence arrives, the idea returns to `proposed` for joint review.

**Kept small.** This is scaffolding (CHARTER 15). After a month, per product: every idea raised is in the roadmap, retired or merged, none in chat alone; every review a trigger fired is done or marked pending; no technical question reached him. Review effort is then weighed against delivery, and the page kept or reverted (CHARTER 13).
