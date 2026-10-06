# Decision 0014: every session looks for efficiency savings; the words-only duty and handover habits first

**Agreed by the CTO (Claude, Juku OS Cowork session) and the consultant (Astra), 4 October 2026, three rounds, then revised by the CTO after a max-effort break test; the decision record is [issue #151](https://github.com/Adonis80/how-we-build/issues/151).** The record below is kept as agreed. This repository is public, so passages about the Chairman's spending are left out or bracketed; reported costs are reported model costs, not proved cash.

## The ruling

The Chairman, 4 October 2026: *"I lift the 10 October freeze for the four efficiency changes only: the words-only duty, the verdict repair, the cost accounting and spending check, and the registry.json addition."* Each change is its own pull request, from its own brief, and none is bundled.

- **In force, from the first pull request:** the words-only duty and its handover habits (positions I, B and J as rules): `library/carries-sessions.md`, `library/carries-evidence.md`, `library/two-stacks.md` and the README's *What every product carries*. The duty rides the month review of `library/ideas-for-later.md`, as one experiment with it (CHARTER 13).
- **Agreed, not yet built:** the verdict repair (C), attempt accounting and spending admission (A, D) and the `registry.json` addition (F). Positions E, G and H are not changes to build now. Nothing below is a rule until a page says it.

## The record

### Efficiency investigation: agreed answer, after the break test (4 October 2026)

Status: AGREED with Astra in three rounds, then REVISED by the CTO after a max-effort break attempt returned "does not stand as written". The revisions below (marked BREAK FIX) were adopted by the CTO from that report; they were not re-debated. Nothing here changes the rulebook. The rulebook is frozen until 10 October 2026 unless the Chairman names an exemption in his own words.

Who: the CTO (Claude, Sonnet 5.5, Cowork session) and the consultant (Astra: GPT-6.1 Sol at High for the three rounds; GPT-6 Astra at Max for the break). Records live in the ChatGPT project "Juku Review": chats "Review efficiency investigation" (R1, R2, R3_AGREED) and "Break Test Review Efficiency".

#### The question

The Chairman: tokens are wasted in coding and in review. A one-line change seems to load the whole repo into the coder and the reviewer. The protocol is not working. Make every project always look for efficiency savings, in the rulebook if possible.

#### What is true (live `main`, commit 2ba3772)

1. No open pull request covers this (open: #148, #140, #121, #119).
2. The rulebook's own reviewer gives any code or risky change every `.md/.sh/.py/.yml` file plus the cumulative PR diff. That is deliberate here (decision 0010 item 1a: right for the rulebook, where a rule can contradict a page the diff does not touch). It is not truly everything: `model-registry/registry.json` is left out. The product reviewer already picks the slice's pages and one hop of imports (#86); its selector cannot simply be copied (it drops files over 150 KB, which would drop the 264 KB gate).
3. Four reads of #148 recorded USD 9.88923485 final-attempt reported cost. The two Sonnet fallback reads are USD 9.233301 of it (93.37%). The two GLM reads handed about the same 1.24 MB cost USD 0.18 and USD 0.48. So the model and lane matter more than bytes. Rounds 1 and 2 were 1.14 and 1.19 MB. The round-4 latest commit is a few KB however counted (1,966 bytes as a bare diff, 2,875 with its message, 2,986 as a patch file); an earlier count of 3,663 could not be reproduced. Either way the read is hundreds of times the change. These are reported model costs, not proved cash: the Sonnet route runs on the plan, so moving a read to a cash-billed API could cost more cash even though the reported figure is lower.
4. Product reviews cannot use the cheap provider (the caller accepts only the Claude interface; private code is not cleared for another provider), so every product read goes to Sonnet.
5. The cost record keeps only the last attempt; the adapter drops cache and reasoning detail, and early error paths drop usage that was returned. A read that fell back has an incomplete cost record.
6. Round 4's signed verdict said blocking while its text said nothing blocks. Confirmed. The cause (verdict listed first in the output form) is a hypothesis only.
7. The CTO's own coder briefs said "read X whole" and carried full patches inline, against the README. No coder usage trace exists, so no general claim about coder waste is made.
8. Not established: what makes up Sonnet's 1.41 million input and 225,000 output tokens; [the date the lead reader's allowance ran out] (the code session said 2 October; the records show 3 and 4 October); whether avoiding Sonnet saved cash. [Omitted: one further sentence about a provider key, held privately.]

#### The decision, as revised

A. Measure, free. One record per attempt, including failed and malformed ones; cash and plan allowance kept apart; unknown stays unknown, never zero. Completes decision 0010 item 1. BREAK FIX: the record is opened before sending (attempt id, start state), keeps returned usage and generation ids before the answer is parsed, is closed with outcome and settlement state, and an interrupted record is "unresolved". A route refused locally (today's product `no_interface`) is not a sent request. Once such records exist the handover carries an all-attempts total and an unresolved count.

B. Handover line, now. "Reported cost, final attempts only", by check-run link and commit, marked complete, partial or unknown; never zero for missing. First row: four final-attempt costs total USD 9.88923485; Sonnet USD 9.233301 (93.37%); completeness and cash class not established.

C. Verdict from typed findings. Findings carry severity; the workflow derives the verdict (any blocking, else any advisory, else clean). Missing, malformed, unknown-severity or cut-off answers sign no clearance. A recoverable blocking finding inside a truncated answer stays a refusal. No second verdict authority, no reading prose like "nothing blocks". The whole path changes together (both callers, adapter, signer, guards) and is proved with stubs that fail when the rule is removed. Does not retroactively clear round 4's signed refusal.

D. Spending admission. BREAK FIX (was "check funds, cap and budget separately"). A check is not a reservation. Before any call (primary, fallback or evaluation), the rule is: settled spend + unresolved or reserved spend + the next request's bound must not exceed the approved envelope, across every caller that draws on it. Reserve before sending; settle against evidence; a cancelled or lost response stays unresolved until reconciled. A proven hard cap at the provider key, or one-at-a-time admission, may stand in if it enforces the same limit. The request needs an output-token limit and a price limit (today it sets neither). A recorded budget refusal must let a slice park without buying a model refusal (reviewer-parking rule). Unknown headroom authorises no primary call, not only no fallback.

E. Code-sharing permission. BREAK FIX. Asked only after the request is checked before it leaves: the final outgoing request is validated against the approved repository, purpose, model and privacy settings, and a registry edit cannot silently widen the grant (a local test showed provider "extras" can override the model after the registry check passes). The permission is explained as what it is: `data_collection: deny` is a setting, not proof of zero retention; the permission covers either OpenRouter's eligible provider pool or a restricted set, and says which. Money and code-sharing stay two separate decisions. Not asked yet.

F. Context by the affected contract. A short named contract-partner list is a trusted starting bundle (chosen from the trusted rule, both directions, rule pages searched too), widened from the diff, not a boundary. The broad rulebook read stays pending measurement (reconsider on cost, latency, repeat reads, adequacy and reliability). BREAK FIX: (1) adding `registry.json` to the rulebook read is a correctness repair that does not wait for savings evidence. (2) Before any context experiment, the recovery path for a missing-context refusal is specified: today the gate keeps the worst signed result per commit, so a better-informed read cannot clear the same commit, and nothing lets a reviewer request more context. A context-only shortfall is either a validated incomplete read that cannot clear (a real blocker still survives) or the cost of a new commit is counted; retries are bounded.

G. Cold independent review stays. Repair-only second reads stay narrow (Tell Hemz, decision 0010 item 4) with Astra's invalidation conditions; general delta review is withdrawn.

H. Max effort and the signed-gate rules stay until decision 0010 item 5's comparison reports. BREAK FIX: that comparison predeclares what it must show, including misses (all three readers can agree on a defective change), is a bounded pilot not general proof, isolates route and context changes, counts retries, false blockers, unresolved reads and time to a usable verdict, and does not become a date gate for a wider rollout.

I. Standing duty. BREAK FIX on scope. No timer, quota, ledger or investigation to fill a line. When material waste or a saving surfaces during authorised work, the closing or parking handover records it, its evidence or uncertainty and the smallest next action. A proven violation is a defect. An unbuilt improvement goes through the ideas procedure with an `efficiency:` prefix. The duty's own material cost is carried in the same handover. Owner: the CTO, at the first review on or after 2 November 2026. Keep only if measured saving (tokens or cash actually seen, never nominal prices or work avoided) exceeds the recorded cost of measuring, extra reviews and rework, with delivery delay and escaped defects checked. Charter §13's one-experiment rule and §15 apply.

J. Coder briefs, now (CTO practice, no pull request). Passages and the commit named; patches by branch, not inline; an expected-files forecast (a forecast, not a limit); mandatory entry documents still read as their rules say; sample one small and one large real coder session before any general rule.

#### Authority for each piece. BREAK FIX

The freeze lets through only what the Chairman names or the narrow attempted-task exception covers. Approval of one piece is not approval of another.

- Free now, no exemption: analysis of existing records; local probes; B (a handover line in a PR description); J; correcting #148's stale handover.
- Needs a freeze exemption, each named: (1) the words-only duty and handover habits (I, B, J as rules); (2) the verdict repair (C); (3) attempt accounting and admission (A, D); (4) the `registry.json` addition to the rulebook read (F).
- Needs the Chairman's money ruling: [the spending definition] and the envelope (now ruled; figures held privately); any change to the Sonnet fallback; any change to max effort (not asked).
- Needs his permission, later: E.

#### Order of work

1. Now, free: correct #148's handover, compile existing records marked incomplete, J, and [one further item about a provider key, held privately].
2. Chairman's two answers (below). Then bounded, separate pull requests, each with free behavioural proof: words-only duty first (cheap read); then verdict repair; then attempt accounting with admission and limits; then the registry.json addition. Not bundled.
3. Before code-sharing is asked: pre-send request validation exists and can be shown.
4. Evidence-led context experiment, only after the missing-context recovery path is specified.
5. Month review of the duty (first on or after 2 November).

#### What changed whose mind

Astra (Sol) changed the CTO on: bytes versus lane; delta reading (withdrawn); the product selector's limit and the registry gap; refusal-preservation in C; "all attempts" being an overclaim; the breadth of E; that correctness repairs must not wait for a savings payback. The CTO changed Astra on: leaving the broad rulebook read in place pending measurement. (Astra's round 3 record: [one definition about the Chairman's spending, held privately], her own round-2 amendment.) Astra (Max, break test) changed the CTO on: D as an admission rule; the authority list; E's pre-send enforcement and honest wording; F's missing-context recovery path; A's record-before-send; H's miss test; I's own cost and exit test; and that reported cost is not cash.

#### Strongest objection left

A selector or savings ritual that creates more reviews and rework than the context it removes. Guard: bounded repairs, free behavioural proof, no bundling, the duty counting its own cost, and the month net-benefit test.

#### Break test verdict

"DOES NOT STAND" as first written: two blockers (D, authority) and five weaknesses, all taken above. It could not break C's invariant on paper, cold independent review, withdrawing general delta review, separating cash from allowance, or sampling coder sessions. Not verified by it: account settings, provider retention, raw round-4 response, any later Chairman ruling, coder usage.

#### Chairman's answers, 4 October 2026

1. Freeze lifted for the four named changes, in his words (quoted in the PR-A brief).
2. Money: ruled by the Chairman. The figures are held privately because this repository is public; they are not recorded here. The spending-admission pull request will be briefed with them separately.

#### Overlap with other work (checked live 4 October 2026)

- No open pull request is an efficiency pull request. The code session's own 5 proposals were never filed; it was told not to file them.
- #119 (parked draft, `ask.py`): "a refusal is kept however it is broken". Same ground as position C. Rule: the verdict-repair pull request starts from #119's checkpoint (3914e43), brought up to date and proved to bite; it is not rewritten.
- #121 and Hemz-OS#94 (parked, GLM coder lane): a cheaper coder route outside this record. Not duplicated here. It is the main coder-cost lever; revisit after 10 October. It may draw on the same OpenRouter key.
- #148 (decision 0013, reviewers for new products): no overlap.

#### Precedence

This record wins over the code session's earlier proposals. It binds sessions through (1) the paste the Chairman carries now, and (2) the decision record PR-A files into the rulebook, after which the rulebook binds every session. Every later brief starts by listing open pull requests and branches on efficiency, spend or verdict, and builds on any it finds instead of starting over.

#### What the Chairman was asked (nothing else)

1. Lift the freeze for four named efficiency changes only, in his own words.
2. Confirm [what the spending limit counts], and name the amount (answered; figures held privately).
