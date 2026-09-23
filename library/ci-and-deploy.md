# CI and deploy

Scope: every product. Open when: a product's checks, workflows or deploy change.

**Build minutes are finite and shared.** On the free plan, every private repository under this account draws on one pool of 2,000 Actions minutes a month; this public rulebook draws nothing. The Actions budget is $5 a month with stop-at-limit on (his ruling); the ceiling is not the answer, spending less is. A job refused a machine fails in seconds with no step run, which reads like a broken workflow and is not.

**A product's checks do each piece of work once:**
- one full run per commit, not one for the push and another for the pull request;
- a posted review re-checks the review, not the suite;
- a newer push cancels the older run on a branch, never on `main`;
- a words-only change runs the word checks, not browsers and a deploy it cannot affect;
- a browser's setup is cached, not reinstalled.

Every test that runs today still runs on every commit that can reach `main`. Quality is the constraint; minutes are what gets trimmed.

**The deploy.** CI deploys with the deploy key held as a repository secret, so no session ever holds it. CI builds the app, deploys a preview and smoke-tests that exact deployment. A merge to `main` promotes the same deployment, never a rebuild and never "whatever is newest", then smokes the live addresses. If they are red, it promotes the previous production deployment straight back and fails loudly. The previous deployment is recorded before anything moves. The host's own Git integration stays off, because it would put every push into production untested.

Four traps cost Hemz OS real runs:
- The deploy tool treats GitHub-flavoured environment variables and a `github.com` remote as an integration deploy, which a private repo on the free plan refuses with no visible error. Put both out of its sight for the deploy call.
- A team-scoped key works; a project-scoped one authenticates and then dies with a misleading missing-project message.
- Promoting a preview-built deployment mints a production copy rather than repointing production. So the check passes on the smoked id **or** on a deployment whose original is the smoked id.
- The edge serves the new build a little after the control plane calls it live. Ask again for a couple of minutes before calling it red.
