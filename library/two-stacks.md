# The two stacks

Scope: every product, in either stack. Open when: choosing the lead or its effort, handing work between stacks, a job that needs hands.

Each stack's own working is in library/stack-anthropic.md and library/stack-openai.md.

One lead owns a slice at a time. The pull request is the handover, and a replacement lead rebuilds what it needs from GitHub, never from a chat. At a clean checkpoint, *build* in the other stack transfers ownership — and only then: ownership moves when the pull request's latest entry is the outgoing lead's checkpoint. Otherwise the incoming lead leaves that pull request alone and takes the next item. Nothing is built to manage this: no switch file, no lock service, no registry, no orchestrator.

**A brief to a code session** names passages and the commit, carries patches on the branch rather than inline, and forecasts the files expected (a forecast, not a limit); a mandatory entry document is still read as its rule says. Its shape (decision 0015): a bootstrap, hard rules, tasks each with goal, files, change, acceptance and stop, and a definition of done; a report to the Chairman ends with a receipt: what was read, in KB, and the cost.

**Whichever stack leads, his part is only a tap no hand may make.** The hands may not sign in for him, type a password or a secret into a web page, get past an are-you-human check, pay, or approve a sign-in key on his account by themselves. A session takes such a job to that one tap and hands him the tap alone — the link, what he will see, the words to reply — never the job, and never a choice of how. Learned 17 September 2026, when a Hemz OS session handed him a credential to add, with a choice attached, that a Cowork session then made and sealed itself, leaving him one tap: *Authorize*.

**The effort ladder** (his ruling, 28 September 2026, quoted whole on [#124](https://github.com/Adonis80/how-we-build/pull/124)).
- **Medium** for small, clear fixes.
- **High** is the default for product slices, and the lead runs there.
- **Max** only for knotty work with several interlocking business rules, or a failure diagnosed as a reasoning limit. The lead stays at high and hands that one bounded piece to the product's max subagent, at the model and effort of the registry's `max-subagent` role (library/max-subagent.md), briefed fully, since it starts with no context. The lead keeps the pull request and the tests. **xhigh** is a middle step where it fits.
- **Never step up just because a check failed.** Diagnose first: a broken setup, missing product truth, a dependency, an oversized slice. Fix the cause or shrink the slice, and step back down once the hard part is done.

**The Chairman's ruling, 11 September 2026.** While a Claude model is the strongest available to him, it leads, and the OpenAI path stays configured to build; who reviews is the registry's (*The independent reviewer*). The rules are written by role, so the swap costs nothing the day that changes.
