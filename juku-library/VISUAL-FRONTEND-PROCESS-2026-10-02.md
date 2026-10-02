# The visual front-end process: how every Juku OS product designs its screens

**Consensus of the CTO (Claude, Juku OS Cowork session) and the consultant (GPT-6.1 Sol, high effort), 2 October 2026, three rounds, after an earlier check with the consultant (GPT-6 Astra, high effort, four rounds). The rule itself is `library/screen-design.md`, in [pull request #143](https://github.com/Adonis80/how-we-build/pull/143); this page is the frozen record of how it was settled.**

## The Chairman's instruction

All visual front-end work follows one order: the Juku style, a brief to the GPT Space visualizer, review rounds by screenshot, the agreed design saved in the product's library, then the build. He amended it twice: Claude Design is used only for open questions, not as a mandatory copy step ("I agree this is superior"); and the separate Juku style page is outdated, so the style is only his two original files, the *Juku Complexity Distillation Prompt* and the *Juku HyperSolid Style*, both folded into the page. He asked both models to read those two files and reach a consensus, and to confirm the process applies to any product built with Juku OS.

His words, whole: *"all projects need to know this is now the default way we design front end UIs. tell me if it conflicts with what the rules currently say. if so, then replace the instructions with mine below. you can change the wording to make it easier to follow."* Later: *"I agree this is superior to my idea of asking Claude Code to replicate"* and *"remove reference to the Juku style .md file in the library because that is outdated now. I want you to get all of your visual style from the very first files I uploaded"*. The README's freeze note records the lift for this one change.

## What was agreed

Both models state the same final text, below. It works as written for a marketing website, a PWA, a SaaS dashboard, a booking or calculator tool, an admin or internal tool, a native-feeling mobile app and a text-heavy site. The 3D layer is optional by its own words ("where it improves the product"), a light web app is the default and native only if needed, so no product type is forced into 3D.

**What changed whose mind.** The CTO moved on: the round cap and a builder-only note beside the screenshots (Astra); a "shipped" set of screenshots and figures checked against worked examples (Astra); 3D optional, native allowed, and the parts of his two files the first draft had dropped (Sol). The consultant moved on: keeping "adapt it a little", "never a separate artefact", "the preview is final", and a concrete two-second speed target, all his rulings or needed to be testable. **Strongest objection left:** none from either side; Astra's point that dropping the Claude Design copy step loses nothing was taken once he agreed.

## How a product picks it up

Every session reads the rulebook README at its start and opens `library/screen-design.md` when a screen is new or reworked. `library/carries-evidence.md` says a product's `design/` folder and `<product>-library/design/<screen>/` follow that page, and a product that lacks something on the carries list makes itself current in its next pull request. Until then the rulebook wins over a product's own words.

**Open follow-ups, one per product, each in that product's next pull request, in code mode attached to that repository (words only for Phena):** Hemz OS: its `AGENTS.md` line "Material UI → the Interaction Architect (`design/`)" points at the rulebook page instead, and its `check.sh` allows prose notes under `hemz-library/design/<screen>/` (it refuses prose outside its allowed list today). Myst: its `check.sh` has the same prose allowlist, so it allows `myst-library/design/<screen>/` too; nothing in its `AGENTS.md` names the old method. Phena: its `AGENTS.md` line is replaced the same way; it has no check script, and its River rules stay in its `design/` folder. The first screen through the five steps in any product is what proves them. The two-second speed limit needs its exact test in `design/SCREEN-LAW.md`. This repository's own board is out of scope: `juku-library/` is flat and public.

## The agreed text, verbatim

# How a screen gets designed

Scope: every screen, either stack. Open when: a screen is new or reworked, before code.

His ruling, 2 October 2026: the one order for all visual front-end work. He approves by looking, never by reading a spec.

1. **Style.** The Juku style is the distillation rule and spatial layer below, nothing else. He says how this product differs; adapt it a little, keep the core philosophy. Write the product's version into its `design/` constitution.
2. **Brief.** The CTO briefs the GPT Space visualizer (`@Visualize`) on users, the real task, states, verified figures, fixed rules, its existing screens and tokens, and the distillation rule; never the layout, which it designs. Task clear first, then the most spectacular, beautiful, creative graphics. It never changes a rule or invents a number.
3. **Rounds.** He sends screenshots, phone and key states first; the CTO guides the visualizer. At most three rounds. If still open, he picks between the last two viable pictures. The CTO fixes any wrong figure or unusable screen before showing either.
4. **Save.** In `<product>-library/design/<screen>/`: the agreed screenshots, plainly titled, and a dated builder-only note he never reads (actions, states, rules, data, motion, responsive changes, target phone and network, checks). After release, add phone and desktop screenshots titled "shipped" with date and pull request.
5. **Build.** A builder session builds from the saved screenshots and note into the real product, never a separate artefact; Claude Design only to settle an open layout, motion or responsive question. The builder checks figures against independent worked examples and proves the real journey on phone and desktop, a preview, review. Speed is measured on the preview. The preview is final. Any departure from the agreed look goes to him first as before-and-after pictures.

**Distillation rule.** Distil, never decorate: complex system underneath, the smallest mental model a first-time user needs on top; maximum capability, minimum cognitive load. Distrust the existing structure; design the information architecture around the user's task. Decide what stays, merges, goes, waits for an action, or earns a screen. Fewest layers that stay clear: no crammed screen, no needless steps. Simplify, then disclose progressively; never hide clutter in tabs. When needed, ask the choice that decides the next step. Infer what the system can; mark assumptions, let the user correct them. Rename unclear things; hide internals. Keep all truth, capability, rules, permissions, safety limits. Each screen: where am I, what matters, what can I do, what next, clear in ten seconds? What does not help understand, decide or act goes or moves deeper.

**Spatial layer** (part of Juku style). Use it where it improves the product; never sacrifice usability, clarity or performance for 3D. Reference, inspect live, never copy: https://tarasovvitalii.com/demos/hypersolid/. Light 3D spaces with depth, cinematic movement and travel, more touch-native than the reference: drag to move, pinch to zoom, tap to select or approach, inertia, optional parallax. Strongest in explorable information spaces (the Phena River). Default a light web app; native only if needed. 3D carries space, navigation and transitions; text, figures, forms and payments stay plain HTML (or native) controls. Essential journeys work without 3D: keyboard, screen reader, an alternative to every gesture, reduced motion. Light assets, progressive loading, graceful fallback on weak devices. Speed is a hard limit: usable within two seconds on the mid-range phone and network named in the note, plain interface before any 3D. One product across all devices.

**What stays.** Every screen obeys `design/SCREEN-LAW.md` and the product's constitution. A routine change keeping the agreed layout and behaviour goes straight in. A screenshot never proves the product works. The Architect session and screen spec stay off the default path.
