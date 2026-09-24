# How a screen gets designed

Scope: every product with a screen, in either stack. Open when: a screen is new or reworked, before any code for it.

Beautiful is not a step at the end. A screen earns its look by being the smallest coherent thing that does the job, and the order below is what produces that. It is the same order for every product; only the constitution differs.

1. **The brief.** The CTO writes it from current product truth: who uses it, the real-world task, the fixed business rules, the data already known, the states that matter, what success looks like measurably, the non-goals. It describes the problem, never the layout. One brief exists at a time; it is an input, not a record.
2. **The Interaction Architect.** Its role page is `design/ARCHITECT.md` here. A fresh session every time, reading four things only — the brief, `design/SCREEN-LAW.md` with the product's own constitution, the product's design system (tokens and approved patterns), and the spec template it fills. No chat history, no old attempts, no pile. Its order is: reduce the concepts before arranging any pixels; fix the information hierarchy (act now / act confidently / supporting context / on demand / not on this screen); choose the smallest interaction model; then write the short screen spec. It may challenge a brief that over-complicates the workflow, in one line per challenge. It may not change a business rule, invent a number, or optimise for novelty or tap count alone.
3. **The visual.** Phone-first artboards of the real states, with real derived figures — never a happy path alone. This is what Claude Design is for, and the canvas link becomes the spec's `prototype_ref`. An advisory session may produce it; only an attached builder session puts it into the product.
4. **The Chairman approves by looking.** He sees the visual and nothing else. The brief and the spec stay between the roles; he is never asked to read or approve written interaction prose.
5. **Build the approved direction into the real product** — not into a separate finished artefact.

Claude Design is a workbench, not the authority: the accepted design system, the current product and the Chairman's acceptance are. A routine change to an existing screen goes straight into the product from the design system, with no canvas at all. And no polished canvas is made before the interaction logic behind it is settled — a beautiful screen can price wrong.

The screen spec is the durable record — contract, hierarchy, layout tree, states, responsive behaviour, access, acceptance, decisions — and the reviewer judges against it, the screen law and the product's constitution.

**The pages live here, once.** `design/SCREEN-LAW.md` is the screen law every product's screens obey, capped at 450 words and machine-checked. `design/ARCHITECT.md` is the role. `design/BRIEF_TEMPLATE.md`, `design/SCREEN_SPEC_TEMPLATE.md` and `design/REVIEW_RUBRIC.md` are the three forms the work takes. A product copies none of them. It writes only its own constitution — its money rules, its units, its domain law — which points here for the rest, and its own screen specs.
