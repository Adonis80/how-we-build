# HyperSolid

Scope: every product's map and screens, either stack. Open when: a product's map or a screen is new or reworked, before code.

The one standard for how every screen in every product looks, and the one order for visual front-end work. **It alone owns the look** and is the only front-end guide (`HOW-WE-BUILD.md`, *Which rule wins*; R-2026-10-08ca), drawn in its kit, `library/juku-style.md` with `library/juku-style.css` (R-2026-11-05ca); any other looks line in a product page is deleted when found. **He approves by looking, never by reading a spec**: a look or motion rule here is adopted or changed only on his approval of what it shows — a picture; for motion, a rehearsal played on his phone (a written draft may come before it, never in force until he approves). His approval covers the behaviour shown, never a restriction carried in a prose summary (R-2026-11-04ca, decision 0024).

## The steps

**Once a product's look is agreed, no picture rounds** (R-2026-11-05cb). A product's look is agreed once its constitution holds his dated picture approval of it (on Hemz, the formula screen of 4 November 2026), the kit giving the shared rest. Its new and reworked screens then skip the picture round, steps 3 to 5 and step 6's save of a design. They are built at step 7 from the map's records for the jobs being built, in the kit's classes and values and that look, to a working preview, phone and desktop, on the product's test address, which he approves by tapping through it before it merges (`CHARTER.md` §12: never a material user-facing change before he has accepted it). Where a screen moves or sounds, that preview is the rehearsal he plays on his phone. What a note would carry goes in the slice's pull request; step 6's shipped screenshots are still taken after release. The desktop composition and the screen's own size, which every screen has, are built the same way, from the kit's existing classes and values.

Steps 3 to 6 still run whole where the look is not yet agreed: a product with no such approval; a new part, or a size, colour, gap or timing the kit does not have (`library/juku-style.md`, *What the kit does not draw yet* and *Never*), which stays his by picture; or when he asks for pictures.

1. **Inputs.** From the product's constitution take its tokens and their meanings, its units, its money and domain law, and its dated picture-approved exceptions; everything else comes from this page and its kit. A product without a constitution gets one first, its values and any exceptions from him by picture; a clash between the two is listed before drawing and settled by this page.

   **Its North Star** (R-2026-10-28ca): before its next new or reworked screen, its constitution's Tokens set its colours (values, themes and meanings), haptics and sound palette, each value his by picture or rehearsal. Its type, spacing and density, depth and light and motion are the kit's, shared by every product, save an exception he approves by picture (R-2026-11-04cb, R-2026-11-05ca). A type, spacing, depth or motion value a constitution already holds by an earlier dated approval, and the kit differs from, is listed as a clash and put to him as before-and-after pictures, never silently changed.

   **A rework of a live product** (R-2026-10-24ca) starts from the live screens: where he approved their look, that approval is recorded, dated, in the constitution, and they are the starting picture. Its map carries a parity list: every live capability and control kept, moved (where, which tap), changed (why) or proposed for removal (his decision).

2. **Map.** The CTO's, and it is the distillation (*Distillation rule*); an inventory is not a map, and goes back (R-2026-10-20ca). **One per product with screens, whole** (charter §13; the case is [#306](https://github.com/Adonis80/how-we-build/pull/306), *The case for part 5*). How many screens and levels it has is not predetermined, and it starts from the full complexity of the product (`juku-library/Juku_Complexity_Distillation_Prompt.md#Prompt`): before its next new or reworked screen design, the map covers the product's current agreed scope, its live items read from the code and reconciled with `PRODUCT.md` and the running product, each in one canonical record (several entry points allowed), so it is also step 1's parity list; then each slice updates the jobs it touches. Its home is `MAP.md` beside `PRODUCT.md`, read when a slice touches a mapped job, never a rule page.

   **Per job**, from the person's jobs, never the old screen's arrangement: role where permissions or journeys differ; frequency rank; where the person is; level (*seen first*, *appears when relevant* in place, *a deliberate step deeper*, *goes*) and screen; touch path and *spoken sequence* (request, questions, material facts read back, confirmation where required, outcome, correction or refusal); *data question* (what a chart would answer, or none; why no motion or sound where none helps); a link to its journey test's acceptance criteria, evidence pending until built (loop step 4), unfinished without one; one vocabulary, agreeing with `NAMES.md`; and a hand-drawn Mermaid screen tree.

   **The fewest levels that work.** Frequency is weighed with context, consequence and total effort, never a fixed depth; a touch path is always kept, voice perhaps a fast route. Each control, link and word earns its place by the fastest correct action; money and figures exact. Where a simpler structure would work better than the proposed one, the map says so and designs it (`juku-library/Juku_Complexity_Distillation_Prompt.md#AI Responsibility`). A screen fits the map or revises it, never sits beside it. Moving a frequent job is batched and his to approve by looking, since how a product looks is his (`HOW-WE-BUILD.md`, *Who decides*): by tapping through the working preview where the look is agreed, by picture where steps 3 to 6 run (above).

   **Judged by coverage and total effort** (Screen law 8) against the live product or last map, same person, starting point and finished outcome: a capability lost without his approval fails; an added step needs a reason and evidence that confidence, speed or error-avoidance pays for it, or the map is revised. Ranks and step counts are predictions until built and used; measured use revises them. The old screen contributes only verified facts, actual states, permitted actions, correction paths and safety limits; its layout and retired names confer no authority, its controls only through the parity list.

3. **Brief.** The Space visualizer (`@Visualize`) designs, Claude Design as fallback; either gets the goal, never the plan (R-2026-10-26ca). One screen per fresh chat, phone first, beside any live screen it reworks. The brief fills, within their budgets, the slots `product-reads/brief-check.py` holds (who, the one job, what matters most, the real names and figures, the rules that change what is seen or allowed, the tokens and their meanings, quoted as the constitution words them, and the kit named in Look) and ends on its closing line, verbatim. The kit itself, `library/juku-style.md` and `library/juku-style.css`, goes with it as an attachment, the look the designer works in, its words never copied into the brief (R-2026-11-05cc); the goal is still the brief's, the composition still the designer's. Layout, position, components, adjectives, states, frames and the spoken path never go; his own words may, quoted. Nothing reaches a designer before the script passes it, and a brief also passes a fresh reader given this step, never the map. Reasoning rises only for complex screens.

   The designer owns composition within the kit and the product's approved look, then the most spectacular design the task allows (R-2026-10-02ca); leaving an approved live look is his option, never a new baseline. **A correction** is one sentence through the script: back to the live picture, or the missing fact or job, never paint. **Switch to Claude Design**, same brief, when an invented name or figure or a dropped job returns after one correction, a generic or cartoony result survives one, or he asks. Designs are titled `<PRODUCT> R<round> <screen code> <screen name>`; drafts stay in the tool; only agreed designs enter a repository.

4. **What comes back.** First one phone-first screen. Once the CTO accepts its look, the same chat adds what this job needs, asked through the script in map order, each frame readable alone on a phone, every obligation met before the save: the journey; the opening moment at desktop width; the spoken path, marked *proposed* until the build proves it, switching the assistant on staying his decision (`library/voice-native.md`); each data question as a chart showing the interaction and what becomes clearer, or "no chart: <why>"; motion and sound with reduced-motion and non-3D fallbacks where relevant, or "none" with the map's reason. A design missing a mapped job, state, action, correction path or required fallback, inventing a name, concept or figure, conflicting with `NAMES.md`, or misusing a colour's meaning goes back to the designer, never to him.

5. **Rounds.** He sees complete designs, phone first. At most three; record the count in the slice's PR, and in a draft PR's handover the brief sent, the round and the last two designs. Neither a new chat, a remap nor a switch of tool resets it. Then: two viable designs, he picks; one, he accepts it or not; none, report the failed approach and proposed remap. Further picture rounds require his instruction. Where a screen moves or sounds, he plays a short live rehearsal on his phone before the save.

6. **Save.** The session fetches the agreed design from the tool itself, never by his hands, into `<product>-library/design/<screen>/`: the agreed design and its frames, plainly titled, any rehearsal, and a dated builder-only note he never reads (actions, states, rules, data, motion, responsive changes, target phone and network, checks). After release, phone and desktop screenshots titled "shipped" with date and pull request.

7. **Build.** A builder session builds from the saved design and note, or, with no picture round (above), from the map, into the real product, in the kit's classes and values (`library/juku-style.md`, *How a new screen is made from this*), and what the kit does not draw yet by steps 3 to 6 in its values (same page), never a separate artefact; Claude Design also for the rehearsal or an open layout, motion or responsive question. Every word and figure on screen is real, accessible text, checked against its data and `NAMES.md`. It checks figures against independent worked examples and proves the real journey on phone and desktop, on a preview, where speed is measured.

   The builder compares the preview with the saved design, frame by frame, where one was saved, and a rework with its parity list, trying each new or changed action through its visible result, undo and saved state where claimed; it records the result and any differences, and what does not work says so. The reviewer checks the build against the note (with no picture round, the map's records and the pull request), that journey evidence and the kit's self-check. The preview is final. A picture judges composition; a whole product is put to him only as a working build, phone and desktop. Any departure from the agreed look goes to him first as before-and-after pictures.

8. **Close.** One line in the handover: a material improvement or waste found in design or delivery, with evidence or uncertainty and the smallest next action, or none. Record it through `library/ideas-for-later.md`; shared proposals here, product ideas in their roadmap.

**Every handoff sized for its reader** (R-2026-10-28cb): the goal and only what its job needs, the rest in files it can open; a builder starts fresh from the saved design, its note and the kit, or, with no picture round, from the map's records for the jobs it builds and the kit; never the whole map or this page pasted. What must hold every time is held by a check, not memory.

**Palette rule.** Dark first, contrast measured, any approved light theme kept. A few accents, each with one meaning within its product, save a sharing he approved by picture (Hemz's gold, money and actions, on the formula screen he approved on 4 November 2026; `library/juku-style.md`); colour is never the only signal or decoration. New navigation and focus treatments must not confuse business meanings; an approved use that clashes is put to him as before-and-after pictures, never silently recoloured. The hues are his, chosen by looking: the constitution's tokens are the values, this page and its kit are how they are used.

## Distillation rule

How the map (step 2) is made (his paper, `juku-library/Juku_Complexity_Distillation_Prompt.md`). Distil, never decorate: complex system underneath, the smallest mental model a first-time user needs on top; maximum capability, minimum cognitive load. Decide what stays, merges, goes, waits for an action, or earns a screen; no crammed screen, no needless steps. Simplify, then disclose progressively; never hide clutter in tabs. When needed, ask the choice that decides the next step. Infer what the system can; mark assumptions, let the user correct them. Rename unclear things; hide internals. Keep all truth, capability, rules, permissions, safety limits. Each screen: where am I, what matters, what can I do, what next, clear in ten seconds?

## Spatial layer

**Calm Depth** (R-2026-10-29ca, R-2026-10-02cb). Products feel like light, interactive 3D spaces, more like a light game or a cinematic space than a conventional website; Three.js, WebGL or WebGPU where they help, never needlessly heavy rendering. Spectacle in motion belongs to charts (*Moving charts and data spaces*, below); navigation takes depth by layers alone.

1. **In navigation, depth by layers, never a moving world.** **The drill-in** (R-2026-11-04cc, on Hemz's formula screen; reference build `Hemz-OS` `hemz-library/design/price-calculator/2026-11-04-R2-note.md`): a tapped part with contents of its own becomes the whole view, and each level above recedes behind it, faded and blurred, so the way back stays in sight. An overlay rises over its still, dimmed parent; the map decides what earns a level. No camera travel in application navigation; data spaces are below. The reference, https://tarasovvitalii.com/demos/hypersolid/: inspect live, never copy; in navigation borrow its depth and light, never its travel.

2. **Navigation motion short and directional.** Tabs slide a short way sideways and an overlay rises, about a quarter of a second. The drill-in's values are those of the build he approved by looking (R-2026-11-04cb), kept in the kit (`library/juku-style.css`, `.j-level`): levels deeper than two behind gone, no bounce; back reverses it, its button naming where it returns. Reduced motion: the change only.

3. **Touch answers back.** Where supported, light haptics acknowledge activation, with distinct confirmation and stop cues as the platform permits; visual feedback always remains, sound follows the rule below, rehearsed on the target phone.

4. **Density is rhythm, decluttered** (R-2026-11-04cc): content on the ground, never fenced in boxes or borders, as the kit draws it; its one home is `library/juku-style.md`, *Always / Never*.

5. **Light and fast.** A light web app; native only if needed. Text, figures, forms and payments stay plain HTML (or native) controls. Essential journeys work without 3D or motion: keyboard, screen reader, an alternative to every gesture, reduced motion. Light assets, progressive loading, graceful fallback on weak devices. Usable within two seconds on the mid-range phone and network named in the note (with no picture round, in the pull request), plain interface before any chart's 3D. One product across all devices.

**Sound, as standard.** Every product carries a light, game-grade sound layer, on from the first visit unless he approved otherwise by picture or rehearsal: short cues that confirm, travel and reward. Never the only signal; silent while the device is silenced; one mute control, remembered; assets within the speed limit; drawn in the design, heard and approved in the rehearsal (once the look is agreed, built in the working preview and heard there: the steps' opening).

**Moving charts and data spaces, as standard.** Wherever a product holds complex data, design a useful, living, explorable chart, in 3D and motion graphics where they help understanding, its exact records and figures still available as text and to a screen reader. Each answers a question its user has, faster and more clearly than plain figures; its movement carries meaning (change, comparison, cause, uncertainty), never decoration. A chart that adds no understanding goes (Screen law 1).

In charts and data spaces, where it helps (R-2026-11-03ca, on his tap of the tappable chart demo on his phone; R-2026-10-02cb, `juku-library/Juking_Style_3D_UI.md#Added Juku Style spatial layer` and `#Phena River`): one finger drags to pan, rotate or travel; a pinch zooms; a tap selects an object or moves toward it; momentum where useful; optional, subtle device-motion parallax; hierarchy shown partly by physical depth, scale and position. The Phena River carries this layer strongly, from the broad landscape and its major patterns, through clusters and themes and single experiences, down to individual people, claims, transcripts, audio and evidence. Always the most perceived depth and spatial sophistication for the least rendering cost.

## Screen law

How every screen, in every product, earns its look, and so does a prototype or picture of one put to the Chairman. Reviewers judge by this; nobody re-explains it.

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

9. Secondary or conditional detail appears only when it becomes relevant: a short reveal expands in place; a part with contents of its own opens by the drill-in (Spatial layer 1), so nobody loses their spot.
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

A routine change keeping the agreed layout and behaviour goes straight in. The steps above run only for a new or reworked screen; a new or reworked map runs step 2 alone. Assistant-only work follows `library/voice-native.md` without a brief, design or save; a changed screen takes the steps. Updating a mapped job's entry while no screen changes is not a rework: the slice edits the entry, with no brief, design or save. A job added to a screen, moved to another level or screen, or given a new touch path there changes a screen and takes the steps, a frequent job's move also batched and his to approve by looking (step 2): tapping through the preview where the look is agreed, else by picture.
