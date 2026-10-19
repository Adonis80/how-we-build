# HyperSolid

Scope: every screen, either stack. Open when: a screen is new or reworked, before code.

His ruling, 2 October 2026, reworked 19 October 2026 ([#240](https://github.com/Adonis80/how-we-build/issues/240)) so its standards show in the pictures, not only on the page: the one order for all visual front-end work. He approves by looking, never by reading a spec.

## The steps

1. **Style.** Read the product's `design/` constitution: its palette (the *Palette rule* below), its sound, and where the spatial layer earns its place. A product without one gets one first: he says how it differs, and the core stays. List any clash with this page before drawing.
2. **Map.** The CTO's, and it is the distillation. From the person's jobs, never the old screen's arrangement, write four columns: *seen first* (where am I, what matters, the next action), *appears when relevant* (in place, Screen law 9), *a deliberate step deeper*, *goes*. The fewest levels that work. The old screen contributes only verified facts, actual states, permitted actions, correction paths and safety limits; its layout and retired names or controls confer no authority. For each job, map the *spoken sequence* in order: request, questions, material facts read back, confirmation where required, outcome, and correction or refusal; name the equivalent touch path. Record its *data question* (what a chart would answer, or none).
3. **Brief.** In the GPT Space visualizer (`@Visualize`), a fresh chat each round, supplied with the current map, retained decisions and requested changes, using this fixed brief structure in order: user and task; map and full spoken sequence; verified names and figures; states, permissions and correction paths; product palette tokens and meanings; then this authority line, verbatim: *"Use this brief as the only authority for product names, terminology, figures, states and business rules. Do not use earlier chats, remembered layouts or old screenshots as authority. If a required fact is missing, show it as unknown; never invent it. Ordinary interface wording may be proposed, but no new business concept, product name or figure may be introduced."* The CTO owns the map; the visualizer owns the composition and the look within it, the most spectacular, beautiful, creative graphics the task allows; it never changes a rule or invents a number. Pictures are titled `<PRODUCT> R<round> <screen code> <screen name>` (`MYST R2 02 Perfume Lover`); drafts stay in its image library, and only agreed pictures enter a repository (his ruling, 13 October 2026).
4. **The sheet.** Every round delivers one contact sheet, each frame also readable alone on a phone. Row 1: the journey, phone frames in map order. Row 2: the spoken path as chat bubbles, in order, marked *proposed* until the build proves it; switching the assistant on stays his decision (`library/voice-native.md`). Row 3: each data question as a chart storyboard showing the person's interaction, what changes and what becomes clearer, or a frame saying "no chart: <why>", showing either that no complex data is involved or the exact-record task for which a chart adds no understanding. Row 4: motion and sound as a strip, with reduced-motion and non-3D fallback frames where relevant; "none" when no screen-specific motion or cue is justified. A sheet missing a row, mapped job, state, action, correction path or required fallback, or introducing a product name, business concept or factual figure absent from the brief, conflicting with `NAMES.md`, or using a colour with the wrong meaning, goes back to the visualizer, never to him.
5. **Rounds.** He sees complete sheets, phone first. At most three; record the count in the slice's PR. Neither a new chat nor a remap resets it. Then: two viable sheets, he picks; one, he accepts it or not; none, report the failed approach and proposed remap. Further picture rounds require his instruction. Where a screen moves or sounds, he plays a short live rehearsal on his phone before the save.
6. **Save.** In `<product>-library/design/<screen>/`: the agreed sheet and its frames, plainly titled, any rehearsal, and a dated builder-only note he never reads (actions, states, rules, data, motion, responsive changes, target phone and network, checks). After release, phone and desktop screenshots titled "shipped" with date and pull request.
7. **Build.** A builder session builds from the saved sheet and note into the real product, never a separate artefact; Claude Design only for the rehearsal or an open layout, motion or responsive question. It checks figures against independent worked examples and proves the real journey on phone and desktop, on a preview, where speed is measured; the builder compares the preview with the saved sheet, frame by frame, and records the result and any differences; the reviewer checks the build against the note and that journey evidence. The preview is final. Any departure from the agreed look goes to him first as before-and-after pictures.
8. **Close.** One line in the handover: a material improvement or waste found in design or delivery, with evidence or uncertainty and the smallest next action, or none. Record it through `library/ideas-for-later.md`; shared proposals here, product ideas in their roadmap.

**Palette rule.** Dark first, contrast measured, any approved light theme kept. A few accents, each with one meaning within its product; colour is never the only signal or decoration. New navigation and focus treatments must not confuse business meanings; an already approved product use that clashes is recorded, not silently recoloured. The hues are his, chosen by looking; the product's constitution holds its tokens and meanings until he changes them by before-and-after pictures.

## Distillation rule

How the map (step 2) is made. Distil, never decorate: complex system underneath, the smallest mental model a first-time user needs on top; maximum capability, minimum cognitive load. Decide what stays, merges, goes, waits for an action, or earns a screen; no crammed screen, no needless steps. Simplify, then disclose progressively; never hide clutter in tabs. When needed, ask the choice that decides the next step. Infer what the system can; mark assumptions, let the user correct them. Rename unclear things; hide internals. Keep all truth, capability, rules, permissions, safety limits. Each screen: where am I, what matters, what can I do, what next, clear in ten seconds?

## Spatial layer (part of Juku style)

Use it where it improves the product; never sacrifice usability, clarity or performance for 3D. Reference, inspect live, never copy: https://tarasovvitalii.com/demos/hypersolid/. Light 3D spaces with depth, cinematic movement and travel, more touch-native than the reference: drag to move, pinch to zoom, tap to select or approach, inertia, optional parallax. Strongest in explorable information spaces (the Phena River). Default a light web app; native only if needed. 3D carries space, navigation and transitions; text, figures, forms and payments stay plain HTML (or native) controls. Essential journeys work without 3D: keyboard, screen reader, an alternative to every gesture, reduced motion. Light assets, progressive loading, graceful fallback on weak devices. Speed is a hard limit: usable within two seconds on the mid-range phone and network named in the note, plain interface before any 3D. One product across all devices.

**Sound, as standard** (his ruling, 13 October 2026). Every product carries a light, game-grade sound layer, on from the first visit unless its constitution says otherwise: short cues that confirm, travel and reward. Never the only signal; silent while the device is silenced; one mute control, remembered; assets within the speed limit; drawn in the sheet's row 4, heard and approved in the rehearsal.

**Moving charts, as standard** (same ruling): *"the charts must be exciting and interactive but they must be genuinely useful… they present complex data extremely beautifully and efficiently."* Wherever a product holds complex data, design a useful, living, explorable chart as standard, with spatial depth where it helps understanding. Exact record lookup, comparison or reconciliation may require a table or plain figures instead; the sheet must demonstrate that task and why a chart adds no understanding. Necessary exact records remain available alongside any chart. Each one answers a question its user has, faster and more clearly than plain figures would; its movement carries meaning (change, comparison, cause, uncertainty), never decoration; exact figures stay readable as text and to a screen reader. A chart that adds no understanding goes (Screen law 1). Every data question on the map is answered in the sheet's row 3.

## Screen law

How every screen, in every product, earns its look, and so does a prototype or picture of one put to the Chairman. Reviewers judge by this; nobody re-explains it.

Each product adds a constitution of its own holding only what is true there — its money rules, its units, its domain law — and pointing here for the rest. A rule changes only with the Chairman's eyes on a screen that proves the change.

### Comprehension

1. Every visible element helps someone understand, decide or act — or it goes.
2. The task and its primary action are apparent in a breath.
3. Fixed looks fixed; editable looks editable; a lock looks like a lock.
4. The screen never hides operational truth to look simple, and never speaks engine language its users don't use.

### Efficiency

5. Useful density with clear hierarchy beats emptiness; what is used together sits together.
6. Remove duplicated concepts before hiding or rearranging them.
7. Known information is never asked for twice; sensible defaults over questions.
8. Optimise total effort — confidence, speed, error-avoidance — never tap count alone.

### Disclosure

9. Secondary or conditional detail appears only when it becomes relevant; prefer expanding in place so nobody loses their spot.
10. A completed section collapses to a concise, editable summary: what was chosen, and what it changes.
11. A control that stops applying disappears — one quiet line says why, tap for the story. Never a row of disabled ghosts.
12. Explanations, and any instruction or hint the task can do without, live behind the (i), never standing on the working screen: no coaching captions or placeholders.
13. Icons cut reading, never meaning; nothing required ever hides inside an optional-looking control.

### Consistency

14. One name per concept, everywhere — every screen, every document, every message.
15. Reuse an approved pattern before inventing one; equivalent things look and behave equivalently. A new pattern needs a reason.
16. Decoration never compensates for unclear structure.

### State

17. Empty, unknown, estimated, incomplete, confirmed, failed and not-applicable are different states — and look different.
18. Corrections never restart the workflow; destructive acts stand apart from the normal path.

### Devices

19. The phone is a first-class composition, not a squeezed desktop; desktop spends its width on context, not extras. Same concepts, same order, same states on both.

## What stays

Every screen obeys the Screen law above and the product's constitution. A routine change keeping the agreed layout and behaviour goes straight in. A screenshot never proves the product works. The steps above run only for a new or reworked screen: work on an assistant or its actions that changes no screen follows `library/voice-native.md` alone, with no map, brief, sheet or save; if it does change a screen, that screen takes the steps.
