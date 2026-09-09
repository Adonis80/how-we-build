# Spec — <screen or journey name>

```yaml
id: <area.screen>
status: draft | in-review | approved | implemented | deprecated
source_commit: <sha>
brief: design/briefs/<file>  # an input, deleted when this spec lands and gone from history under squash-merge: what it fixed is carried below in Contract, Acceptance and Decisions, never by a path
prototype_ref: <canvas link, when it exists>
```

**Contract.** Who uses it; what they must understand; the decision they make; the action they complete; what is true when they leave.

**Hierarchy.** Five lists: act now / act confidently / supporting context / on demand / not on this screen.

**Layout.** An indented tree of the composition — relationships, not decoration. Separate phone and desktop trees only where placement differs.

**States.** Every state that changes understanding or action, each in one line: what shows, what it says. Unknown, zero, blank, estimated and not-applicable are never interchangeable.

**Responsive behaviour.** What stays simultaneously visible on desktop; what becomes sequential, sticky, or a sheet on the phone; what is never hidden.

**Access.** Focus order and return; names for non-text controls; touch targets; contrast; nothing carried by colour alone.

**Acceptance.** Measurable outcomes a machine or a first-time user can verify.

**Decisions.** Only the consequential ones: what, why, what would reopen it.

Mark a section "n/a" rather than omitting it silently.
