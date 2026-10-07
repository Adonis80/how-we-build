# Model roles: one source of truth. Consensus, 3 October 2026

**Outcome:** AGREED in round 3 (Claude CTO and Astra, GPT-6.1 Sol High). Design only: nothing is implemented, no pull request opened. The rulebook is frozen until 10 October 2026.
**Chairman's idea:** one place on GitHub that decides the model for every role, each role clearly defined, so a new model can be re-sorted into the right roles using benchmark and test evidence, and no mismatch can exist.

## What is true today (read live, 3 Oct 2026)
- `model-registry/registry.json` in how-we-build is already "the one place a model is named" (decision 0008, issue #103). It has 10 build and review roles. Every model fact carries a date and a source. `check.sh` refuses model ids elsewhere in the repo.
- Missing: the conversation roles (lead, consultant, debate pair, step-up pair, Max break, designer). Their model names live in the Claude Advisor and Astra Project instructions, outside GitHub. That is where mismatches come from.
- Not built (the registry page says so): weekly model check, re-read only what changed.
- Astra's finding: today's resolver accepts only two route kinds (claude-code, openai-compatible) and demands a credential. Chat roles cannot be added by rows alone: a synthetic chat route fails, and reusing a code route passes with the wrong meaning.

## The nine points (Stage 1)
1. **Roles.** The registry gains the conversation roles with one-line duties kept inside the existing consultant and design remits. Pair records reference role assignments and do not repeat model names.
2. **Routes.** Model identity and access routes are separate (app, picker label, effort, availability, who selects). A valid UI route resolves without a credential; the API caller refuses it with an explicit unsupported-route error; an invalid UI route fails validation. A picker label is never claimed as an exact backend version.
3. **Declared pairs, no strength tiers.** A pair is an approved pairing for a stated class of question, each side separately qualified, no known material capability gap, evidence and uncertainty recorded, opposite stacks kept. Declaration is not proof of equal strength, and the Chairman's "never a stronger model against a weaker one" rule is honoured by declaration plus qualification, not claimed as proved. An unavailable member means another approved pair or a handoff, never a silent swap. The Max break is its own role, qualified for adversarial review, in a different session.
4. **Status per assignment.** "Assigned" until that assignment's own model, route and effort have route evidence and role qualification; then "operational". Debate competence never qualifies the designer or breaker. Unproved roles stay assigned and existing approved arrangements are preserved.
5. **Thin Projects.** Project text drops model names but keeps scope, duties and links to the working rules. It carries the registry URL, the role, and the cold-start contract: resolve the role from main at session start and keep that commit for the bounded task; re-resolve at handover or before a consequential action; if GitHub is unreachable, do not choose from memory, restore access or hand off.
6. **Three observations.** Instruction text matched, picker matched, identity known or unknown, recorded on first use of each conversation role and after any selection, effort or fallback change (not on unchanged turns). A visible mismatch is corrected or handed off. A model's own statement is not evidence. No central drift service.
7. **First proof (an acceptance test, not a certificate).** One normal round using both sides of the declared round-one pair through the intended Projects, registry commit and three observations recorded for each side, plus a deliberate selection mismatch and its correction or handoff. It proves that pair's path only. Step-up pair, breaker and designer each need their own evidence.
8. **Promotion.** A new release triggers evaluation, never an automatic swap. Candidate and incumbent run the same tasks, tools and effort; cost, time, missed defects and false alarms are compared; a small held-out set is kept. A candidate never approves its own promotion; the incumbent stays for rollback. The CTO may merge a qualified switch within existing money and permission limits. Public benchmarks shortlist; our own role tests decide. Scorecards and the weekly proposer are Stage 2.
9. **Process.** No rulebook pull request before 10 October without an observed product failure or a named Chairman exemption. After that, one reviewed change with an unused decision number (0012 is taken by the shared-ideas decision), citing the consultant and design rules it touches and restoring no retired remit. Stage 1 needs enough existing or newly run qualification evidence to activate its assignments; what is unproved stays assigned.

## What changed whose mind
- **Claude changed:** dropped the global strength tier (a number cannot show who is a better reviewer or designer); accepted routes-versus-identity after Astra reproduced the resolver failure; accepted per-assignment operational status after round 2 (one good debate round must not certify several roles); widened the three-observation check to first use of each role and any change.
- **Astra changed:** accepted extending the one registry; accepted declared pairs once they carried scope, evidence and uncertainty and made no equality claim.
- **Claude held:** one registry, not two; thin Projects with no model names; benchmarks propose, our own role tests decide; the Chairman's pair rule survives in declared form.

## Strongest objection left
Picker agreement cannot prove an app's exact backend identity. Recording "unknown" honestly contains the limit; the registry cannot remove it.

## Not checked
- Astra read the README live in round 3; core rules and registry were read in round 2 (later refreshes timed out). Nobody inspected either app's Project text or picker, ran candidate benchmarks, or ran the resolver change.
- No existing qualification evidence has been catalogued for the conversation roles, so how much exists today is unknown.
- Max break not run: nothing here is irreversible and no money moves. Run it before any rulebook change that touches the reviewer gate.

## Also settled this session
- The earlier "refresh Astra's instructions with the consultant block" ask in the Juku Marketing pack was wrong (project doc ideas-for-later-decision-0011 explains why). The pack's "yes refresh Astra" question is withdrawn.
- Mismatch seen today: the Claude Advisor Project names Opus 5.5 for round one, while this session ran on Sonnet 5.5. Under this design the Project would name the role only and the session would record what actually ran.

## Next (not started)
After 10 October or a named exemption: one rulebook change implementing points 1 to 9, with a new decision number, read as a risky change. A code session does the resolver test first.
