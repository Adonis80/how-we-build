# Review rubric

For any reviewer — a fresh session, or the consultant briefed cold. Judge the spec and the boards against the brief, `SCREEN-LAW.md` and the product's own constitution. Nothing else is in scope.

**Ask of every element and step:**

1. Is this decision genuinely necessary — could known data, a default, or inference remove it?
2. Does hiding this reduce effort, or merely relocate it?
3. Can the user see enough context to act confidently, and do they keep their place afterwards?
4. Does each collapsed summary say what was captured and what it changes?
5. Is any step caused only by poor grouping? Any icon ambiguous without its label?
6. Are phone and desktop the same mental model?
7. Are empty, unknown, estimated, confirmed, failed truthfully distinct?
8. Does anything exist mainly because the system has always had it?
9. Does any element narrate the engine instead of serving the user?
10. Do the product's own non-negotiables hold on every board — the rules its constitution says can never break?

**Verdict:** PASS · PASS WITH REQUIRED CHANGES · FAIL.
Each finding: severity (blocking / important / optional) · the rule or need affected · the evidence · the user cost · the smallest correction.

**Bounds:** no new requirements unless from the brief, the screen law, the product's constitution, or accessibility. Prefer removal over explanatory UI, the minimal diff over a fresh design. Stop at PASS. Two rounds maximum; then it escalates to the CTO, and the Chairman only if business truth is in question.
