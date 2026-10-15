# The build board: the proposals card

Scope: the build board's proposals card. Open when: changing the proposals card, or checking it against what he approved.

**Approved (his ruling, 15 October 2026, [#222](https://github.com/Adonis80/how-we-build/issues/222#issuecomment-6192725037): Option D).** One card above the product timelines, on the board's live read, so it adds no deploy. Built in `board/build.py` (`proposals_card`), held by its selftest. The picture below is the real card rendered from that day's open proposals at phone width (390 px); it shows this repository's issues only, since a product's ideas are private and this repository is public. It is accepted when he approves it by looking.

![The proposals card at phone width](board-proposals-card.png)

**The screen spec.**
- Pure HTML and CSS: no image, no chart library, no script for looks; under 10 KB with its styles (the selftest holds it with ten rows).
- Dark and high contrast, in cyan, yellow and teal alone (his ruling): near-black surfaces, white text, light-grey waiting times.
- Top: "Proposals" and the open count, then a stage bar sized by count: Being built (cyan), Waiting for debate (yellow), Agreed (teal), each labelled with its count.
- A yellow "Debate due - N ideas waiting" banner when decision 0020's trigger is met (3 proposals waiting, or one waiting 7 days); the rule only behind its tap.
- A numbered spine down the left; the P1 node and card glow cyan. Each row: the title, a stage pill and the time waited; a tap opens its one plain sentence.
- Busy: the top 6, the rest under "Show N more". Empty: a grey bar and "Nothing waiting".

**What it reads.** This repository's open issues labelled `proposal`, ranked by their `Priority:` line (P1 to P4; none sorts last), then oldest, and each product's `proposed` roadmap items after them. An issue an open pull request here says it builds, closes, fixes, resolves or implements (`#N`) is being built, one it only cites is not; one whose body has a `Decision: agreed` line is agreed; the rest wait for debate, as do the products' ideas. Its sentence is the issue's `Plain:` line, else its priority's reason; a product idea's is its `plain`. Priority and age rank it, not a dependency. It reads the first 100 open proposals.
