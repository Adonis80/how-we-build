# Ideas for later

Scope: every product session, and the consultant. Open when: a session spots an improvement it will not build now, a session closes, or a `proposal` issue is raised, ranked or debated.

**Where.** A product idea is a `proposed` item in that product's `roadmap.json`: the CTO's suggestion, not agreed until he says. An idea about the rulebook, or about a rule, check, template or tool more than one product already shares, is an issue here labelled `proposal`, written generally with no product text; a mixed idea splits. Until its issue exists the idea stays in the roadmap with `next` `pending transfer`; then one `retired` line, `lifted to the rulebook, #N`, replaces it.

**Writing one.** One line under `Ideas:` in the pull request's handover, copied into `roadmap.json` at the closing or parking roadmap edit: `id` `I<PR number><letter>`, `title`, `plain` `Captured YYYY-MM-DD; why; surfaced by <item>, #<PR>`, `status` `proposed`, `level` P4, every other field null. It never blocks or widens the slice. First search the roadmap, `retired`, and the proposals and pull requests here, closed too: a match with new evidence updates its owner; without new evidence nothing is written. A violation of an existing requirement is a defect, repaired first, never an idea. Every closing handover asks *Any material system improvement found?*; "none" is valid; never invent one.

**A proposal's life.** Its body keeps `Priority: <P1–P4> — <reason>` (`library/changing-the-rulebook.md`), its decision, its next action and, once work starts, its pull request. The queue ranks by priority, then dependency, then age. It is debated in the head-office debate (`library/consultant.md`) in a batch once 3 await debate or one has waited 7 days, counted when an active session opens, never on a timer. Agreement makes it eligible; its pull request opens when work starts; it never outranks authorised revenue work.

**Review of a product's ideas.** Asked for, never scheduled: at the opening roadmap read, when no agreed item is ready, five or more `proposed` items stand, one has stood 30 days, or he asks. The consultant and the CTO take every open idea in one markdown exchange until they agree; the outcome goes in the handover and the roadmap edit. Each idea ends as one of three: *put to him* (when it is his to decide: `gate` begins `Decision needed:`, his word *agreed* or *not yet*); *a routine repair* (restores what exists, adds no capability; taken in the next slice touching that area); or *retired*, one line in the roadmap's `retired` list with its reopening condition.

**Nothing is built before its review agrees**, except a proven defect's repair. No consultant: the review stays pending and shipping goes on.

**Kept small.** At the first review on or after 2 November 2026 the review effort is weighed against delivery, and this page is kept or reverted.
