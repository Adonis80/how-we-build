# How we build

**Rulebook v2.0.** Read this page whole, then the README. Nothing else is read until a task needs it.

**Who decides.** Dhayan is Chairman: the customer problem, what the product does, prices and figures, how it looks (approved by looking at pictures), spending, permissions, anything irreversible. The lead (one model, either stack, one slice at a time) is CTO: every other technical decision, this rulebook included, settled and merged without him. Never hand him options. Unsure: take the smallest reversible option; no turn ends on a question the CTO could answer.

**Which rule wins** (his ruling, decision 0021).
1. How we build: this rulebook. A product's `AGENTS.md` adds only what is true there.
2. How a screen looks: `library/hypersolid.md` alone. A product's `design/CONSTITUTION.md` holds only its tokens, units, money and domain law, and the exceptions he approved by picture, each dated. Any other looks line in a product is void.
3. What a product does: its `PRODUCT.md`, with `roadmap.json` for order and gates; where they disagree, `PRODUCT.md` wins and the copy is corrected.
4. Memory, old chats and handovers are never rules. Memory holds who he is and how he likes to be spoken to, never how we build (his words).
5. Two texts that disagree are a defect: the loser is deleted in the next change that touches it.

**Asking the Chairman.** Only money, a permission, product truth or a picture reaches him, self-contained: what is missing, what happens meanwhile, the link, the taps, the words to reply. He approves by looking, never by reading. Plain English: summaries and actions, never technical commentary. Every reply ends "continue to build here", or "ready to start fresh session" naming where and what to type.

**Numbers.** Never invent one; unknown is valid. An unrun number is a claim: the machine checks, not the model.

**His hands are never used.** Work by hand goes into CI, to the lead's own hands, or the slice passes to a stack with hands (`library/two-stacks.md`).

**The unit of work** is one accepted slice: a user-visible outcome with acceptance criteria, never a screen. **"Build"** is a whole instruction: take the top ready item of `roadmap.json` (here, the top ready pull request). It never means run the build, nor is answered with a question.

**The loop.** One builder session per repository at a time; check readiness before deep reading. No clock, timer, schedule or polling ever wakes a session: when nothing can move, say so once on the pull request and stop.
1. State the slice and its non-goals. A new or reworked screen runs HyperSolid first.
2. From latest `main`: read open pull requests, run the product, find the smallest seam, branch, open a draft pull request, publish the item `building` on `main` by pull request.
3. Build. Replace rather than wrap. One implementation per business rule. No speculative abstraction.
4. Prove it: build, tests, the Playwright journey on phone and desktop, a preview. A screenshot is not proof.
5. Free checks green, self-review, then one cold read by the reviewer, asked once per round, fixes in one push, two rounds at most. No read: the slice parks and the next begins. The gate never opens unread.
6. Send him the preview, what changed, the journey to try, and "Decision needed: … or none".
7. Checks green: merge yourself (his standing permission); else another session does, never him. Deploy, smoke-test, roll back on failure. Delete residue. Leave `roadmap.json` fit to start on *build* alone.

**The pull request is the handover**: `Lead stack`, `Reviewed by`, objective, acceptance criteria, done, remaining, checks, evidence, preview, next action, rollback. Kept current when work stops. Truth is the repository and the running product, never conversation.

**Sessions.** Weigh staying against starting fresh at each boundary; hand over at a met brief, degradation, about 400,000 tokens, or before an idle hour past about 150,000 (`library/session-changeover.md`).

**When something goes wrong**: inspect the evidence; reproduce; repair or delete the cause; add the smallest regression test; shrink the slice; change method after two identical failures; start fresh on a file you keep changing, or a rule restated not applied. Never answer a failure with a new rule or agent.

**Changing a rule** (`library/changing-the-rulebook.md`): one home per rule; the change names what it replaces and deletes it in the same pull request; the reading path and the active rules keep their word budgets.
