# The independent reviewer: the brief

Scope: every repository under this rulebook, in either stack. Open when: writing a repository's AGENTS.md or its Review guidelines, or a rule lands mid-session.

**A change here reaches a session at its start or at a boundary, never mid-slice.** A session fixes the rulebook revision it works under at boot and at each boundary it continues past, where it compares `main` with that revision and adopts what changed (*Session changeover*); a rule landed at noon does not bind a slice begun at eleven, because a session whose ground moved under it mid-slice would be a session with no ground. The consequence is only that a new rule shows up at the next boundary or session, not in the slice in front of you.

The reviewer takes its brief from the repository's own `AGENTS.md`, read from the protected branch rather than from the head under review, so a pull request cannot write its own reviewer's instructions. The brief lives here, once. A pointer alone was tried on two real reviews and the marks of the brief vanished from them — no addressee, no account of what was checked, no confidence — while a review with the brief in front of it carried all three. So a product's `AGENTS.md` ends with a short `## Review guidelines` section: the pointer here, the least of the brief the tool needs in front of it, and the hazards particular to that product. Those few lines are a copy, kept only because the tool cannot follow a link, and they change only when this brief does.

```
## Review guidelines
- Cold read: form your view from the diff, the tests, `PRODUCT.md` and `roadmap.json` first, and read the pull request's own account last. Never inherit the author's conclusions.
- Look for what is wrong, missing, duplicated, untested, or quietly wider than the slice. Say what you checked and what you did not, and how sure you are. Do not manufacture disagreement.
- Findings go on the pull request, addressed to the CTO, who answers them there, each marked blocking or advisory by the reviewer. A read whose findings are all advisory opens the gate on any round, here as in a product (his ruling, 24 September 2026, asked whether a reviewer's advisory findings should stop holding the gate in this repository too: *"yes advisory"*). Two rounds at most. Then a trade-off is the CTO's call, with the dissent left standing on the pull request; a claim that can be tested is settled by the test, never by rank — and if it cannot be settled safely, the change shrinks or stops; a product question goes to the Chairman as "Decision needed: …".
- A review clears only the commit it read; a later push voids it.
- Plain English. Never write a file into the repository.
```
