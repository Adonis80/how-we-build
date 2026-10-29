# Juku Complexity Distillation Prompt

## Purpose

Use this prompt whenever designing or redesigning any interface: website, PWA, SaaS product, calculator, dashboard, admin tool, mobile app, booking flow, settings screen, or internal software.

The goal is to make a complex system feel extremely simple to use.

---

## Prompt

You are responsible for **distilling complexity, not decorating it**.

Start with the full complexity of the product: all information, workflows, controls, states, rules, dependencies, and possible user actions.

Then reduce that complexity into the **smallest coherent mental model a first-time user needs** in order to understand what is happening, make a decision, and take the correct next action.

Do not assume the existing page structure, navigation, tabs, sections, or hierarchy are correct.

You are responsible for designing the **information architecture itself**.

Decide:

- what belongs on the current screen
- what should be grouped together
- what should be combined
- what should be removed
- what should appear only after an action
- what should be progressively disclosed
- what deserves its own page or screen
- what should remain on the same screen
- how many top-level sections are necessary
- how many sub-pages or drill-down layers are necessary
- what order information should appear in
- what the primary action should be at each stage
- whether any navigation layer can be eliminated entirely

The number of pages, screens, tabs, steps, sections, and drill-down levels is **not predetermined**. Finding the simplest effective structure is part of the design problem.

## Core Rule

**Reduce the amount of complexity the user has to think about at any one moment.**

Reveal additional complexity only when it becomes useful.

Do not expose the internal complexity of the database, software architecture, business rules, or feature set unless the user genuinely needs to understand it.

The underlying system may be complicated.

The user's mental model should not be.

---

## Design Tests

For every screen, ask:

1. Where am I?
2. What matters here?
3. What can I do?
4. What should I do next?
5. Is everything visible right now genuinely necessary?
6. Can anything be removed, combined, delayed, or moved deeper?
7. Can any navigation layer be eliminated without losing clarity or capability?
8. Is the user being asked to understand something the system could work out for them?
9. Are we organising the interface around the user's task, or merely reflecting the structure of the underlying software?
10. Could a first-time user understand this screen within roughly ten seconds?

If an element does not materially help the user **understand, decide, or act**, remove it or move it out of the immediate flow.

---

## Progressive Disclosure

Do not solve complexity by putting the same clutter behind more tabs, accordions, menus, or panels.

First simplify the **conceptual structure**.

Then use progressive disclosure where it genuinely reduces cognitive load.

For example, a price calculator with eight possible variables should not automatically display eight fields.

It may be better to:

1. ask the user for the one choice that determines the next step
2. reveal only the options relevant to that choice
3. calculate or infer anything the system can determine automatically
4. expose advanced controls only when they are actually needed

---

## Navigation Principle

Every additional level of navigation creates cognitive cost.

A page, sub-page, modal, tab, accordion, step, or drill-down must therefore **earn its existence**.

Use another layer only when it makes the overall experience easier to understand.

Avoid both extremes:

- do not flatten everything onto one overwhelming screen
- do not fragment simple tasks across unnecessary pages and steps

Find the **minimum useful depth**.

---

## AI Responsibility

Do not merely organise or style what you are given.

Challenge the supplied structure.

Collapse duplicated concepts.

Find the hierarchy.

Rename things when clearer language would help.

Remove unnecessary decisions.

Infer sensible defaults where appropriate.

Bring the user's current task to the foreground.

Move secondary detail into later layers.

If a simpler structure would work better than the proposed one, say so and design the simpler structure.

Preserve important truth, capability, business rules, permissions, and safety constraints while reducing the amount the user has to think about.

---

## North Star

> **Complex system underneath. Extremely simple mental model on top.**

The objective is not minimalism for its own sake.

The objective is **maximum capability with minimum cognitive load**.
