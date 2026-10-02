# How a screen gets designed

Scope: every product with a screen, in either stack. Open when: a screen is new or reworked, before any code for it.

His ruling, 2 October 2026: this is the one order for all visual front-end work. The Chairman steers the look and approves by looking; he never reads a spec. Where `CHARTER.md` §5 and §7 name Claude Design as the visual workbench, this page wins.

1. **Pick the style.** Start from the global Juku style, `library/juku-style.md`. The Chairman says how this product's style differs; adapt it a little and keep the core design philosophy. The product's style is written into its `design/` folder.
2. **Brief the visualizer.** The CTO writes a short brief to GPT Space, in its visualizer mode, saying what the page must show: who uses it, the real task, the real states and figures, the fixed business rules. Never the layout. `design/BRIEF_TEMPLATE.md` is the checklist; fill only what matters. The visualizer's job is to brainstorm the most spectacular, beautiful and creative charts and graphics for it. It draws; it never changes a business rule or invents a number.
3. **Review rounds.** The Chairman sends screenshots of what the visualizer made. The CTO answers the visualizer with guidance. Repeat until the Chairman and the CTO agree.
4. **Save the agreed design.** The CTO saves it in the product's repo at `design/agreed/<screen>/`: the screenshots, each with a plain title that makes it easy to find, and a short note naming the screen and the date agreed.
5. **Replicate it.** A builder session builds the agreed design into the real product, not into a separate artefact, then proves it as usual: the real journey on phone and desktop, a preview, the reviewer.

**What stays.** Every screen obeys `design/SCREEN-LAW.md` and the product's own constitution. A routine change to an existing screen goes straight into the product from the saved style and agreed designs, with no new round. A screenshot of a design is never proof that the product works.

**What is out of the default path.** The Interaction Architect session and the screen spec. Their files stay until a later pull request removes them.
