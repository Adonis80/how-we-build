# HyperSolid

Scope: every screen and every product's assistant, either stack. Open when: a screen is new or reworked, before code, or work touches a product's assistant or its actions.

His ruling, 2 October 2026: the one order for all visual front-end work. He approves by looking, never by reading a spec.

1. **Style.** The Juku style is the distillation rule and spatial layer below, nothing else. He says how this product differs; adapt it a little, keep the core philosophy. Write the product's version into its `design/` constitution.
2. **Brief.** The CTO briefs the GPT Space visualizer (`@Visualize`) on users, the real task, states, verified figures, fixed rules, its existing screens and tokens, and the distillation rule; never the layout, which it designs. Task clear first, then the most spectacular, beautiful, creative graphics. It never changes a rule or invents a number.
3. **Rounds.** He sends screenshots, phone and key states first; the CTO guides the visualizer. At most three rounds. If still open, he picks between the last two viable pictures. The CTO fixes any wrong figure or unusable screen before showing either.
4. **Save.** In `<product>-library/design/<screen>/`: the agreed screenshots, plainly titled, and a dated builder-only note he never reads (actions, states, rules, data, motion, responsive changes, target phone and network, checks). After release, add phone and desktop screenshots titled "shipped" with date and pull request.
5. **Build.** A builder session builds from the saved screenshots and note into the real product, never a separate artefact; Claude Design only to settle an open layout, motion or responsive question. The builder checks figures against independent worked examples and proves the real journey on phone and desktop, a preview, review. Speed is measured on the preview. The preview is final. Any departure from the agreed look goes to him first as before-and-after pictures.

## Voice Native (every Juku product, Juku OS included)

His ruling, 12 October 2026. Juku OS has nothing to declare under it until it has an assistant. Every product can be operated and configured through natural two-way conversation with its assistant, typed or spoken, in the speaker's language. Conversation enhances the screen and never replaces or weakens it: everything stays fully usable by touch, keyboard and mouse, and a workflow declared voice-capable never secretly needs the screen.

1. **One state, one implementation.** The assistant reaches only actions the screens already perform, through the same routes, validation and permission checks, under the product's server-verified authority; a selected person is kept distinct from authenticated identity. The model proposes; ordinary code decides, computes and saves. Conversation adds no second implementation of a business rule. Adding voice does not require rebuilding existing screens. Each product lists its conversational actions beside the existing handlers they call.
2. **A yes approves one proposal.** Reads need no confirmation. Reversible draft edits may proceed with an accurate outcome and correction path; product rules may require stricter confirmation. Consequential actions require read-back of the material facts and a clear yes, spoken or tapped on the same card. Code holds the proposal: the action, validated inputs, record version, person and account (in Hemz OS, the shop). A correction, cancellation or change to those facts voids it. Ordinary code checks authority and the relevant state version as part of the write, refusing a changed proposal, and durably deduplicates its execution: a repeated yes or a retry returns the first result, and an unknown outcome is checked before any new attempt. A yes never grants what the person may not do. Saved and sent are separate outcomes.
3. **One conversation, in time order.** One thread per person per product, kept with the product's data under its existing retention, access and clearing rules (`RICH-DATA.md`). Speech becomes text; the text is the record. The screen shows the same thread, and typing is the same path as speaking. Summaries are disposable context, never proof. Help and builder requests keep existing masking; any raw contact data sent to a model is limited to the action that needs it, under permitted provider processing, and never enters help retrieval or later unrelated context.
4. **Current state wins.** The assistant reads current state when it needs it, including after its own actions. A screen change to a pending proposal voids it, and the assistant says so.
5. **A truthful next step, never an invented figure.** When unsure: one question, the nearest relevant thing with where it came from, an honest "not available yet", or, on the person's yes, a note to the builders. Figures come from validated user inputs, authorised records or deterministic calculations, never model invention.
6. **Bounded.** Code caps model calls, actions, input/output and time per turn, enforces the approved spending allowance before paid calls, and stops with an accurate, resumable outcome. Every attempt's usage and cost are recorded; unknown cost is reported as unknown.
7. **Proven per workflow.** Free CI tests with typed transcripts and a stubbed model prove the verified read result or saved outcome, covering missing data, correction, refusal, interruption and resumption; writes also cover stale and repeated confirmation and lost response where applicable. A real-model spoken preview journey in working noise proves the declared workflow without screen navigation once authenticated and listening is enabled. Each product declares coverage and the languages and devices demonstrated, never more. Required security and physical steps remain.

## Distillation rule

Distil, never decorate: complex system underneath, the smallest mental model a first-time user needs on top; maximum capability, minimum cognitive load. Distrust the existing structure; design the information architecture around the user's task. Decide what stays, merges, goes, waits for an action, or earns a screen. Fewest layers that stay clear: no crammed screen, no needless steps. Simplify, then disclose progressively; never hide clutter in tabs. When needed, ask the choice that decides the next step. Infer what the system can; mark assumptions, let the user correct them. Rename unclear things; hide internals. Keep all truth, capability, rules, permissions, safety limits. Each screen: where am I, what matters, what can I do, what next, clear in ten seconds? What does not help understand, decide or act goes or moves deeper.

## Spatial layer (part of Juku style)

Use it where it improves the product; never sacrifice usability, clarity or performance for 3D. Reference, inspect live, never copy: https://tarasovvitalii.com/demos/hypersolid/. Light 3D spaces with depth, cinematic movement and travel, more touch-native than the reference: drag to move, pinch to zoom, tap to select or approach, inertia, optional parallax. Strongest in explorable information spaces (the Phena River). Default a light web app; native only if needed. 3D carries space, navigation and transitions; text, figures, forms and payments stay plain HTML (or native) controls. Essential journeys work without 3D: keyboard, screen reader, an alternative to every gesture, reduced motion. Light assets, progressive loading, graceful fallback on weak devices. Speed is a hard limit: usable within two seconds on the mid-range phone and network named in the note, plain interface before any 3D. One product across all devices.

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

Every screen obeys the Screen law above and the product's constitution. A routine change keeping the agreed layout and behaviour goes straight in. A screenshot never proves the product works.
