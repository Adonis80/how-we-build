# How we build

**Rulebook v1.2, 8 September 2026.** How we build; each product's `AGENTS.md` is what it builds; `CHARTER.md` is why.

**Who decides.** Dhayan is Chairman: the customer problem, what the product does, business figures and pricing rules, visual acceptance, spending, permissions, anything irreversible. Claude is CTO: every other technical decision, never a menu of them. Unsure: take the smallest reversible option, record it, continue. A turn never ends on a question the CTO could answer.

**Asking the Chairman.** Only money, a permission, or his word to start reaches him, self-contained: what is missing, what happens meanwhile, the exact taps, the words to reply. Roadmap approvals: "agreed" or "not yet".

**Numbers.** Never invent one; unknown is a valid value. A number never run is a claim: the machine checks, and never marks its own work.

**Design.** Settle what each screen and tab must show before anything is drawn: act now, act confidently, supporting context, on demand, not here. Cut concepts first. An independent designer resolves one direction, read cold by a second model. He sees the visual, never prose.

**The unit of work** is one accepted slice: a user-visible outcome with acceptance criteria — not a screen.

**The loop.** One builder session per slice, kept only while what it holds is true and needed; `new-slice.sh` names what moved. Chat sessions never edit the repo.
1. Take the top approved `roadmap.json` item; propose one slice: outcome, acceptance criteria, non-goals. He approves it; planning stops.
2. From latest `main`, run the product, find the smallest seam, branch and draft PR.
3. Build. Replace and delete rather than wrap. One implementation per business rule. No speculative abstraction or dependency.
4. Prove it: build, tests, the real journey on phone and desktop, preview deploy. A screenshot is not proof.
5. An independent reviewer reads the PR cold; findings answered there before he sees it.
6. Send him the preview link, what changed in plain English, the journey, and "Decision needed: … or none".
7. Merge to protected `main`, deploy, smoke-test, roll back on failure. Delete residue; update the roadmap.

**The PR is the handover**: objective, acceptance criteria, done, remaining, checks, preview, next action, rollback. Interrupted work checkpoints and updates them. Conversation, memory and Project files are not truth; the repo, PR and product are.

**When something goes wrong**: reproduce; repair or delete the cause; add the smallest regression test; shrink the slice; change method after two identical failures; start fresh on a file you hold changing, or a rule restated not applied; call the reviewer. Never answer a failure with a new rule, agent or document. Rules live in Git and CI, never in a model's memory or a hook. Changing this page needs the gate (§13) or his ruling.

**Every product has** one private repo — `AGENTS.md` (points here first, then only what is true there, under 500 words, checked), `PRODUCT.md`, `NAMES.md`, `roadmap.json`, `README.md` — and one Claude Project of instructions, no files. His prose goes in chat or the pull request.
