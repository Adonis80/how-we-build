# HyperSolid

Scope: every screen, either stack. Open when: a screen is new or reworked, before code.

The one standard for how every screen in every product looks, and the one order for visual front-end work. He approves by looking, never by reading a spec. **It alone owns the look** (`HOW-WE-BUILD.md`, *Which rule wins*): a product's `design/CONSTITUTION.md` supplies only its tokens, units, money and domain law, and the exceptions he approved by picture, each dated; any other looks line in a product page is void and is deleted when found.

## The steps

1. **Inputs.** From the product's constitution take its tokens and their meanings, its units, its money and domain law, and its dated picture-approved exceptions; everything else comes from this page. A product without a constitution gets one first, its values and any exceptions from him by picture; a clash between the two is listed before drawing and settled by this page. **A rework of a live product** (his ruling, 24 October 2026) starts from the live screens: where he approved their look, that approval is recorded, dated, in the constitution, and they are the starting picture; its map carries a parity list, every live capability and control kept, moved (where, which tap), changed (why) or proposed for removal (his decision).
2. **Map.** The CTO's, and it is the distillation: a list of what exists is an inventory, not a map, and goes back (his finding on Hemz's round 1, 20 October 2026). From the person's jobs, never the old screen's arrangement, write four columns: *seen first* (where am I, what matters, the next action), *appears when relevant* (in place, Screen law 9), *a deliberate step deeper*, *goes*. The fewest levels that work. The old screen contributes only verified facts, actual states, permitted actions, correction paths and safety limits; its layout and retired names confer no authority, its controls only through the parity list. For each job, map the *spoken sequence* in order: request, questions, material facts read back, confirmation where required, outcome, and correction or refusal; name the equivalent touch path. Record its *data question* (what a chart would answer, or none).
3. **Brief.** The Space visualizer (`@Visualize`) designs, Claude Design as fallback, and either gets the map, never the paint (his rulings, 26 October 2026, #266): one screen per fresh chat, phone first, carrying only who uses it and the one job; this screen's four columns, condensed, as intent, never a layout; the real names and figures, as text; the behaviour that changes what is seen or allowed (the primary action, what is not permitted, the few states that visibly change availability or meaning, the confirmation, correction or refusal); any live screens as the starting picture; the product's colour and type tokens and their meanings; then, verbatim: *"This is a professional operational workspace; clarity and confidence matter more than decoration. Choose the visual composition yourself. Use only this brief's names, figures and rules, never earlier chats; ordinary wording may be proposed, but show a missing fact as unknown and never invent a name, concept or figure."* The parity list and state matrix stay with the CTO; the rest of the map and the spoken path wait for step 4; layout, components and adjectives never go. Reasoning rises only for complex screens. The designer owns composition and look within the product's approved look; leaving an approved live look is his option, never a new baseline. **Switch to Claude Design**, with the same map, when an invented name or figure or a dropped mapped job returns after one correction, a generic or cartoony result survives one targeted correction against the live reference, or he asks for it. Designs are titled `<PRODUCT> R<round> <screen code> <screen name>`; drafts stay in the tool; only agreed designs enter a repository.
4. **What comes back.** First one phone-first screen. Once the CTO accepts its look, the same chat adds what this job needs, every frame readable alone on a phone and every obligation met before the save: journey frames in map order; the spoken path in order, marked *proposed* until the build proves it, switching the assistant on staying his decision (`library/voice-native.md`); each data question as a chart showing the interaction and what becomes clearer, or "no chart: <why>"; motion and sound with reduced-motion and non-3D fallbacks where relevant, or "none". A design missing a mapped job, state, action, correction path or required fallback, introducing a name, concept or figure absent from the brief, conflicting with `NAMES.md`, or using a colour with the wrong meaning goes back to the designer, never to him.
5. **Rounds.** He sees complete designs, phone first. At most three; record the count in the slice's PR, and in a draft PR's handover the brief sent, the round and the last two designs. Neither a new chat, a remap nor a switch of tool resets it. Then: two viable designs, he picks; one, he accepts it or not; none, report the failed approach and proposed remap. Further picture rounds require his instruction. Where a screen moves or sounds, he plays a short live rehearsal on his phone before the save.
6. **Save.** The session fetches the agreed design from the tool itself, never by his hands, into `<product>-library/design/<screen>/`: the agreed design and its frames, plainly titled, any rehearsal, and a dated builder-only note he never reads (actions, states, rules, data, motion, responsive changes, target phone and network, checks). After release, phone and desktop screenshots titled "shipped" with date and pull request.
7. **Build.** A builder session builds from the saved design and note into the real product, never a separate artefact; Claude Design also for the rehearsal or an open layout, motion or responsive question. Every word and figure on screen is real, accessible text, checked against its data and `NAMES.md`. It checks figures against independent worked examples and proves the real journey on phone and desktop, on a preview, where speed is measured; the builder compares the preview with the saved design, frame by frame, and a rework with its parity list, trying each new or changed action through its visible result, undo and saved state where claimed; it records the result and any differences, and what does not work says so; the reviewer checks the build against the note and that journey evidence. The preview is final. A picture judges composition; a whole product is put to him only as a working build, phone and desktop. Any departure from the agreed look goes to him first as before-and-after pictures.
8. **Close.** One line in the handover: a material improvement or waste found in design or delivery, with evidence or uncertainty and the smallest next action, or none. Record it through `library/ideas-for-later.md`; shared proposals here, product ideas in their roadmap.

**Palette rule.** Dark first, contrast measured, any approved light theme kept. A few accents, each with one meaning within its product; colour is never the only signal or decoration. New navigation and focus treatments must not confuse business meanings; an approved use that clashes is put to him as before-and-after pictures, never silently recoloured. The hues are his, chosen by looking: the constitution's tokens are the values, this page is how they are used.

## Distillation rule

How the map (step 2) is made. Distil, never decorate: complex system underneath, the smallest mental model a first-time user needs on top; maximum capability, minimum cognitive load. Decide what stays, merges, goes, waits for an action, or earns a screen; no crammed screen, no needless steps. Simplify, then disclose progressively; never hide clutter in tabs. When needed, ask the choice that decides the next step. Infer what the system can; mark assumptions, let the user correct them. Rename unclear things; hide internals. Keep all truth, capability, rules, permissions, safety limits. Each screen: where am I, what matters, what can I do, what next, clear in ten seconds?

## Spatial layer (part of Juku style)

Use it where it improves the product; never sacrifice usability, clarity or performance for 3D. Reference, inspect live, never copy: https://tarasovvitalii.com/demos/hypersolid/. Light 3D spaces with depth, cinematic movement and travel, more touch-native than the reference: drag to move, pinch to zoom, tap to select or approach, inertia, optional parallax. Strongest in explorable information spaces (the Phena River). Default a light web app; native only if needed. 3D carries space, navigation and transitions; text, figures, forms and payments stay plain HTML (or native) controls. Essential journeys work without 3D: keyboard, screen reader, an alternative to every gesture, reduced motion. Light assets, progressive loading, graceful fallback on weak devices. Speed is a hard limit: usable within two seconds on the mid-range phone and network named in the note, plain interface before any 3D. One product across all devices.

**Sound, as standard.** Every product carries a light, game-grade sound layer, on from the first visit unless he approved otherwise by picture or rehearsal: short cues that confirm, travel and reward. Never the only signal; silent while the device is silenced; one mute control, remembered; assets within the speed limit; drawn in the design, heard and approved in the rehearsal.

**Moving charts, as standard.** Wherever a product holds complex data, design a useful, living, explorable chart as standard, with spatial depth where it helps understanding. Necessary exact records remain available alongside any chart. Each one answers a question its user has, faster and more clearly than plain figures would; its movement carries meaning (change, comparison, cause, uncertainty), never decoration; exact figures stay readable as text and to a screen reader. A chart that adds no understanding goes (Screen law 1).

## Screen law

How every screen, in every product, earns its look, and so does a prototype or picture of one put to the Chairman. Reviewers judge by this; nobody re-explains it.

A rule here changes only with the Chairman's eyes on a screen that proves the change.

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

Every screen obeys this page, within the product's tokens and domain law. A routine change keeping the agreed layout and behaviour goes straight in. A screenshot never proves the product works. The steps above run only for a new or reworked screen: work on an assistant or its actions that changes no screen follows `library/voice-native.md` alone, with no map, brief, design or save; if it does change a screen, that screen takes the steps.
