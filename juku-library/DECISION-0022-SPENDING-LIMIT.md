# Decision 0022: GitHub's spending limit is hit; minutes are cut, not bought

**His ruling, 21 October 2026, given to a Hemz OS session, word for word.**

```
Head office ruling. GitHub's spending limit is hit; no new spend (money out waits for money in). Cut minutes instead, in this order:
1. Merge A first, with #178's browser workaround so main doesn't break when the limit resets. Until then, prove each PR by running every suite inside this session and attaching the log. If you can't run them here, park and say so.
2. Once a read passes, advisories are never pushed into that PR. They go into roadmap.json as the next item. That was 25 of the 53 avoidable rounds.
3. A reviewer hiccup retries the read only, never the full check.
4. Report, measured or "unknown": billed minutes used this month, the date the limit resets, and the projected monthly minutes after 1–3.
```

**Where each part lives.**
- A is Hemz-OS#178 (A18), which carries the browser workaround. Its handover there records the in-session proof.
- 1's proof while the limit holds: `library/reviewer.md`, What it spends. The reader still asks the product's own `verify` before a read (`review-product.yml`), so a private product's read waits for the reset; a proven pull request parks at its read meanwhile.
- 2: `library/reviewer.md`, The verdict.
- 3: `library/product-joins.md`, step 6. It replaces "a run that died before it began, by a new mark": a new mark ran every suite again for a read that never happened.
- 4 is a report, not a rule: on Hemz-OS#178.
