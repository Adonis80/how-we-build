# HyperSolid: the Juku style

Scope: every product's screens, either stack. Open when: a screen is designed, built or reviewed, or a design brief is written.

HyperSolid's look, drawn: `library/hypersolid.md` owns how a screen looks, and this page and its stylesheet, `library/juku-style.css`, are that look (the kit). The one look for every screen in every product: his ask of 4 November 2026 that the formula screen's look be saved and *"easily replicated across the entire Juku OS ecosystem"* (`Hemz-OS` `evidence/2026-11-04-chairman-design-words.md`), and his ruling of 5 November that the look be codified, every element, as a light instruction any designer can match ([#363](https://github.com/Adonis80/how-we-build/issues/363#issuecomment-6657017181)).

**Approved by him, 5 November 2026, 12:05: *"Kit matches"*** ([#363](https://github.com/Adonis80/how-we-build/issues/363#issuecomment-6657545568)), after comparing the blind test, a screen built from the kit alone (https://claude.ai/artifact/CaHkEXiUmtVXKunxRmCnjm), with the approved formula screen (https://claude.ai/artifact/85YmnKiJdRTG3saj96mJKh); transition, colours, type sizes and spacing confirmed identical by machine. Taken from the formula screen he approved by picture on 4 November 2026 (`Hemz-OS` `hemz-library/design/price-calculator/2026-11-04-R2-Main.dc.html` and `-Along-the-hem.dc.html`). The draft, the blind test's source and the inventory mapping every element of those screens to a kit class stand at commit `385b54b` (branch `juku-style-kit-draft`). His approval covers what those screens show (decision 0024): where these words and the screens differ, the screens win, and the difference is corrected here.

Every value is in `library/juku-style.css`. If a value is not in that file, the screen does not use it, save a product's colours and a new part he approves by picture (below).

**Colours are each product's own** (`library/hypersolid.md`, *Palette rule*: the hues are his, the constitution's tokens are the values). The colour values in the stylesheet, and the meanings this page names (gold, turquoise, green, red), are Hemz's, from its constitution. Another product sets its own in its constitution's *Tokens*, mapped onto the kit's colour tokens (`--j-ground`, the inks, `--j-gold`, `--j-turq`, `--j-green`, `--j-red`, the lines), and reads each colour named here as its own colour for that meaning; one meaning a colour still holds everywhere. Type, spacing, lines, corners, depth and motion are shared: a product departs from them only by an exception he approved by picture, dated in its constitution (`HOW-WE-BUILD.md`, *Which rule wins*).

**What the kit does not draw yet.** It was lifted from one phone screen, so it holds the parts that screen shows. The desktop composition (`library/hypersolid.md`, Screen law 19 and step 4's desktop frame), charts and data spaces (*Moving charts and data spaces*), tabs and overlays (Spatial layer 2), and the gaps its blind test hit (a typed figure or text, confirm before a stop, a row of choices, read-only for staff, text inside the (i) sheet, full-screen safe-area gutters) are drawn by HyperSolid's steps 3 to 6 as before, in the kit's values wherever they apply. A new part or value is his by picture, and is added here in the slice that builds it, so the kit grows and is never worked round. The equation is for a level that adds something up; any other level keeps the kit's rows, type, spacing and lines, without operators.

**Not covered by his approval** (decision 0024: it covers what the screens show). The stylesheet's values marked as not drawn in those screens (`--j-r-surface`, `--j-t`) and its light and midnight themes are not used until he approves them by picture; the midnight theme also gives done and measured one colour (`--j-green` and `--j-turq` both `#5FD3C4`), a clash to settle then.

## (a) The feel

Words and figures sit straight on a near-black ground, like a private-bank statement: no cards and no boxes, and only one faint line on the whole screen, above the total. Colour shows up only where it means something: gold for money and for the actions you take, turquoise for what was measured, green for done, red for a stop. Everything else is warm off-white in three shades. Tapping a part makes it the whole screen. The level you came from drops back, blurred and dimmed, so you always know where you are, and the working sits low on the screen within thumb reach.

## (b) The parts

| Element | What it looks like | Class |
|---|---|---|
| Ground | `#08090a`, ink `#FFFDF7`, sans 13.5px / 1.45, tabular figures | `.j-page` `.j-screen` |
| Top bar | 64px tall, 14px sides, 9px gaps; solid ground fading to clear below 62% | `.j-bar` |
| Back | gold 13.5px / 500, ‹ icon 18px, names the parent level, at least 44px tall | `.j-back` |
| Brand (top level only) | 9.5px / 600 capitals, .2em, `#BFB9A9` | `.j-brand` |
| Bar rule | 1px line `rgba(255,255,255,.055)` filling the gap | `.j-bar-rule` |
| (i) button | 44×44, 1px `rgba(255,255,255,.10)` border, 2px corners, icon 17px | `.j-icon-btn` |
| Done | bordered control, green text, green border at 45% | `.j-btn .j-done` |
| Explainer (behind the (i)) | `#131417` sheet under the bar, 12.5px / 1.55 `#E0DCCE`, shadow `0 30px 50px -20px rgba(0,0,0,.95)` | `.j-info` |
| Level | padding 76px top, 14px sides, 26px bottom; scrolls without a scrollbar | `.j-level` |
| Deeper level veil | ground at 66% fading to 38% | `.j-level.is-deep` |
| Level one behind | opacity .36, blur 7px, saturate .85, scale .92, up 16px | `.is-behind-1` |
| Level two behind | opacity .18, blur 12px, saturate .7, scale .85, up 30px | `.is-behind-2` |
| Level leaving | scale 1.06, blur 3px, fades to 0 | `.is-off` |
| Crumb | 9.5px capitals, .16em, `#BFB9A9`, "THE FORMULA · MINUTES" | `.j-crumb` |
| Level title | 27px / 600, −.02em, line 1, sentence case | `.j-title` |
| Lead | 12.5px `#E0DCCE`, line 1.55: the level's sum in words | `.j-lead` |
| Equation block | a column pushed to the foot of the screen | `.j-eqn .j-foot` |
| Part row | at least 68px, 10px top and bottom, 10px gaps; flashes `rgba(255,255,255,.055)` when pressed | `.j-row` |
| Step row | at least 52px; name 13.5px, figure 16px | `.j-row .j-step` |
| Operator | × + ≥ = in a 22px column, 20px / 450 `#BFB9A9`; left empty on the first row | `.j-op` |
| Rule number | 10px / 500, .14em, `#BFB9A9`, 12px column, top-aligned | `.j-n` |
| Part name | 16px / 500, line 1.3, ink | `.j-name` |
| Name aside | "· Outer" in `#BFB9A9` | `.j-name-aside` |
| Subline | 10.5px `#BFB9A9`, 3px above | `.j-sub` |
| Row figure | 20px / 450, right, coloured by meaning; unit 12.5px; note under it 10.5px | `.j-val` `.j-val-unit` `.j-val-note` |
| Opens marker | › 15px `#9C9686`, 10px column | `.j-chev` |
| Band heading | 10px / 500 capitals, .14em, `#BFB9A9`, row 40px | `.j-band-row` `.j-band` |
| The hairline | 1px `rgba(255,255,255,.055)` above a total | `.j-sum` |
| Hero money | serif 42px, gold, −.01em, row 92px (96px on an opened level) | `.j-money` `.is-hero` |
| Total | 30px / 500, gold or turquoise; unit 12.5px / 450 | `.j-big` `.j-big-unit` |
| Total label | 9.5px capitals, .12em, `#E0DCCE`, "BEFORE VAT" | `.j-total-label` |
| Opened-level line | at least 76px, 14px top and bottom; figure 30px / 500, label 12.5px pushed right | `.j-line` `.j-fig` `.j-line-label` |
| Confirmation | green tick 16px and a 13.5px ink sentence, indented 32px | `.j-ok` |
| Add | gold 11.5px / 500 text with a + icon, no fill, indented 32px | `.j-add` `.j-add-row` |
| Choice / pick | `#0e0f11` fill, 1px border, 2px corners, 11.5px `#E0DCCE`; full-width pick is 52px tall at 13.5px | `.j-btn` `.j-pick` |
| Selected choice | gold text, gold border at 50%, fill `rgba(255,176,31,.2)` | `.j-btn.is-on` |
| Drill-in motion | 420ms `cubic-bezier(.22,1,.36,1)` on size, fade and blur; arriving rows rise 12px over .5s, 45ms apart | `.j-level` `.j-in` |

## (c) Always / Never

**Always**
- Put content straight on the ground.
- Draw a hairline above each total and nowhere else in the content. The top bar's rule is the only other line.
- On a level that adds something up, lay rows out as one equation, left to right: operator, name, figure, ›. Keep the operator column there even when it is empty, so the names line up.
- Push the equation to the bottom of the level (`.j-foot`), so the screen's whole height is used. The title gets the space above it, and the thumb reaches the rows.
- Keep sections clearly apart, each under its band heading (`.j-band-row`), never by a line or a box.
- Colour every figure by what it means: gold for money, turquoise for anything measured (its unit too), ink for plain percentages.
- Use tabular figures. Put a unit straight after its figure, smaller (12.5px), in the same colour. A space goes before %, as in "+25 %".
- Write crumbs, bands, the brand and total labels in widely spaced capitals. Only the level title is in sentence case.
- Make every tap target at least 44px tall: rows 68px, steps 52px, picks 52px.
- Keep 14px gutters on both sides and 76px clear under the bar.
- Use gold text for back, add and selected. Back names the level it goes back to.
- Make a tapped part the whole view, with at most two levels showing behind it, blurred. With reduced motion, the screen just changes, with no movement.
- Put the › only on rows that open.
- Give each level one job: its title, a line saying what it adds up to, and its parts. Any part with detail of its own opens as its own level by the drill-in, so detail is never crammed underneath. If a level would need more than one phone screen of rows, split it into deeper levels instead of shrinking the spacing.
- Use only the kit's spacing values (gutters, row heights, gaps, the 76px under the bar). Spacing is never tightened to fit more in.

**Never**
- Never put content in boxes, cards, panels, borders or row dividers. The only filled things are controls and the (i) sheet.
- Never use a flat gold button or a gold background behind words. Gold is for text, and the only gold fill is the translucent one under a selected choice.
- Never use a colour without its meaning. Turquoise is never money, and gold is never a measurement.
- Never put the serif on anything except the hero money.
- Never put explanations on the screen. They go behind the (i).
- Never add shadows, glows or gradients to content. The only ones are the bar fade, the deep-level veil and the sheet's shadow.
- Never round corners past 2px on controls (3px for surfaces, `--j-r-surface`).
- Never introduce a size, colour, gap or timing that is not in `library/juku-style.css`, save the product's own colours from its constitution and a new part he approved by picture, added here (*What the kit does not draw yet*).

## (d) How a new screen is made from this

1. **Load the kit.** Load `library/juku-style.css` read from this repository at a pinned rulebook commit by the product's build, never a copy kept or edited in the product (`library/carries-sessions.md`, *Its pages*: "read from this repository, never copied down"); the product's own stylesheet sets the kit's colour tokens from its constitution where they differ. Put `.j-page` on the body and `.j-screen` on the root, and set `data-theme` on `<html>` only to switch to light or midnight.
2. **Build the frame.** `.j-stage` holds one `.j-level` per level, with `.is-deep` on every level below the top one. `.j-bar` sits after the stage and contains back or brand, then `.j-bar-rule`, the (i) and Done. `.j-info` is optional and opens from the (i).
3. **Map the content from the product's map.** Each level gets `.j-head` (crumb, title, lead) and then a `.j-eqn.j-foot` of `.j-row`s in the map's order. Each row's operator comes from the maths, and each figure is coloured by its meaning. Every subtotal and total is a `.j-sum`.
4. **Use only `.j-` classes.** Write no inline styles and no new values. If something has no class here, it is a design question: send it back to the designer and don't invent a fix (*What the kit does not draw yet*).
5. **Wire the drill-in.** Tapping a row sets the levels to `.is-on`, `.is-behind-1` or `.is-behind-2` (`.is-off` for anything else) and puts `.is-forward` on the screen. Back drops the class from the screen and sets the leaving level to `.is-off`. Mark each arriving row `.j-in` with `--i`. Make the levels behind `inert`.

## (e) Self-check: answer yes to all eleven

1. Is every piece of content sitting on the ground, with no boxes, cards, borders or row dividers?
2. Is there exactly one hairline per total, directly above it, and no other line in the content?
3. Does each money figure appear in gold, each measured figure and its unit in turquoise, and nothing else in either colour?
4. Is the serif used only for the hero money?
5. On a level that adds up, do the operators sit in one 22px column, with the names lined up even where there is no operator?
6. Do the working rows sit at the bottom of the screen, within thumb reach, with every target at least 44px?
7. Are the crumbs, bands and total labels in spaced capitals, and only the title in sentence case?
8. Are back, add and selected shown as gold text, with no flat gold button anywhere?
9. Does tapping a part make it the whole view, with the parent blurred behind and Back naming the parent, and does it simply switch with no movement when reduced motion is on?
10. Is every size, colour, gap and timing on the screen one of the values in `library/juku-style.css` (colours, the product's own), with no inline styles?
11. Does each level do one job and fit one phone screen, with any further detail opening as a deeper level rather than crammed in or squeezed tighter?
