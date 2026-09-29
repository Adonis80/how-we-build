# Decision 0010 — review spend, the plan map, and the self-refreshing board

Consensus of Claude (CTO seat) and Astra (GPT-6), 29 September 2026, three rounds, no courier.
Chairman's ruling the same day: the freeze until 10 October lifts for these items only.
Owner of this consensus: Claude builds, Astra audits that each item landed in merged wording,
workflow behaviour and the review records.

## Rulings

1. **Where each product's plan lives.** The rulebook's front page carries a map with one line per
   product: the product, a link to its plan, and how it appears on the build board. Juku OS's line
   says its plan appears on the board through its open pull requests and that it has no roadmap.json.
   A missing roadmap file must never be read as "no plan".
2. **The board finishes, it is not rewritten.** Pull requests #113 and #117 are the self-refreshing
   build board. No new pull request for the same thing. roadmaps.juku.pro (with an "s") opens the same
   board as roadmap.juku.pro; the change rides in #117 or #99, whichever already covers the address.
3. **Review spend, in this order.** Cheapest and safest levers first; splitting last.
   1. Analyse the existing per-read cost records (the reviewer already logs class, role, model,
      effort, tokens and USD) and settle in writing what the USD 6 weekly limit counts: subscription
      allowance and cash charges reported separately. Only an undefined rule goes to the Chairman.
      The records also settle the split of each read's cost between input and thinking, and whether
      the provider charged cached rates for the re-sent brief; both are hypotheses until they do.
   1a. **What the reader is handed (round three, on the Chairman's question).** The rule is written:
      a pages-only change gets the thin read (touched pages, README, HOW-WE-BUILD.md, check.sh;
      everything else named and left out, failing closed if more was needed); any change classed code
      or risky gets the diff plus every .md/.sh/.py/.yml page in the repository, whole, and the brief
      re-sent cold each read. Right for the rulebook, where a rule can contradict a page the diff does
      not touch. Wrong for a product, where a code change is handed every document and workflow page
      and none of the app source it connects to. Amendment, product repositories only: code and risky
      changes get the diff, the touched files whole, AGENTS.md and the applicable review rules, and the
      source the diff directly connects to (one hop) as the starting bundle. One hop is not the safety
      boundary: the reader must ask for affected callers, tests, database rules or configuration when
      needed, including connections imports cannot reveal; missing needed context blocks approval;
      naming left-out files aids discovery and does not establish completeness. The rulebook's own
      routing is unchanged: thin read for its page changes, every page for its code and risky changes.
      Per Astra this is the better next experiment than lowering effort: remove irrelevant context,
      supply relevant source, then check cost and findings on the two agreed jobs.
   2. Free checks and a builder self-review run before any paid read. One paid read is the aim,
      never a promise.
   3. Every change carries the line "Personal data or payments affected: yes/no — reason", where
      hiding, capturing, logging and deleting data all count as yes. The path list stays as the
      floor; the reviewer must challenge the declaration; "no" never overrides a sensitive path or
      observed behaviour. Personal-data and payments work reads at max effort; so does anything
      uncertain.
   4. Tell Hemz's second read covers the fixes only, against the previously reviewed version, the
      original findings and the connections the fixes touch, widened if the risk spreads. It ships
      when checks and review pass. It is the first job stuck on cost and fits the freeze exception.
   5. Two-job quality comparison: on two suitable changes, one with sensitive screen-to-server
      behaviour, read the identical version three ways — cheap reader, expensive at high, expensive
      at max — verify every finding against the code and tests, and record the evaluation spend
      separately. Neither reader is ground truth; both can miss the same bug. Effort tiers (high for
      database and server, max for payments and personal data) are adopted only if the findings
      support them.
   6. Split-routing (sensitive part to the expensive reader, the rest to the cheap one) is
      considered last, only if ordinary review spend still breaks the budget after 1–5, and only
      where the seam between screens and the sensitive part can be bounded. Jobs stay complete and
      small; never split a job to reach the cheaper reader.

## Owners and next steps

| Item | Owner | Next |
|---|---|---|
| Plan map on the front page | code session, rulebook repo | one pull request, README only |
| Board #113 and #117, "s" address | code session, rulebook repo | add the keys #117 waits on; preview for the Chairman's look |
| Spend analysis and USD 6 definition | CM, Hemz OS | report from the existing records |
| Free checks and self-review first | code session, rulebook repo | one rule line, all products |
| Behaviour declaration | code session, rulebook repo | template line plus reviewer prompt |
| Product read bundle (1a) | code session, rulebook repo, then each product's copy | one precise change to the reviewer, products only; CM confirms Hemz carries the same file |
| Tell Hemz fixes-only read | CM, Hemz OS | run it, ship |
| Two-job comparison | CM, Hemz OS | pick the two jobs, run three reads each |
| Split-routing | nobody yet | opens only if 1–5 leave the budget broken |

Astra's audit runs after each item merges. Agreement here does not certify an unseen implementation.
