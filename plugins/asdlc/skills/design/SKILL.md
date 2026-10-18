---
name: design
description: Turns an accepted intent.md into a requirements and design spec (spec.md), applying the organization's policy skills (brand, security, compliance, UX) as constraints and flagging conflicts to named policy owners. Use once an intent has been accepted and the user says "write the spec", "design this", "spec out <slug>", "requirements for <slug>", or "start the design pass", or when run headless by the intent-accepted CI job. Do not use to draft or amend intents, write implementation plans, or write code.
argument-hint: "<intent slug or path to intent.md> [--headless]"
---

# Produce a requirements and design spec

The intent to design: $ARGUMENTS

The spec is the second artifact in the lifecycle. It turns an accepted intent
into requirements and a design the engineering team can plan against. Policy is
applied while the spec is written, not discovered in a review weeks later. The
product owner reviews this spec; they do not write it. Anything a reviewer
would have escalated is surfaced up front as a flagged concern with a named
owner.

## Before starting

The argument is a slug or a path to `intent/<slug>/intent.md`. With no slug,
list the accepted intents that have no `spec.md` and ask which one; in
headless mode, stop and say a slug is required.

The run is headless if the arguments include `--headless` or the
AskUserQuestion tool is unavailable. Otherwise it is interactive.

If the project has `asdlc/design-template.md`, use it — the project's
template wins. Otherwise use `${CLAUDE_SKILL_DIR}/TEMPLATE.md`. (The
override's name avoids the word "spec", which the intent gate treats as a
spec file.)

## Gate

Check these in order from the repository root. At the first failure, stop,
write nothing, and say which check failed and what would clear it.

1. `intent/<slug>/intent.md` exists and its frontmatter `status` is
   `accepted`. A draft intent is refused: it is accepted by the commit that
   sets `status: accepted`, and that commit is the product owner's to make.
2. The accepted version is committed and unchanged:
   `git ls-files --error-unmatch intent/<slug>/intent.md` succeeds, and
   `git diff --quiet HEAD -- intent/<slug>/intent.md` exits 0. A staged or
   unstaged change, even to an accepted intent, means the version being
   designed is not the one that was signed off.
3. `intent/<slug>/spec.md` does not exist. If it does, offer to revise it
   (see Revising) rather than starting a second spec for the same intent. In
   headless mode, stop: the CI job never overwrites a spec someone may be
   reviewing.

Record `git log -1 --format=%H -- intent/<slug>/intent.md` as the intent SHA.
It goes in the spec frontmatter and is the start clock for the lead-time
measure.

The plugin's intent gate hook checks the intent against the full accept rule
in `intent/README.md` when `spec.md` is written. If it blocks the write, report
its reasons as given and stop. Do not write the spec another way; the fix
belongs in the intent, made by its owner.

## Load policy

If the project has `asdlc/policies.yaml`, use it — the project's manifest
wins and replaces the default entirely. Otherwise use
`${CLAUDE_SKILL_DIR}/policies.yaml`. Each entry names a domain, the policy
skill that governs it, and the owner its concerns route to.

Invoke every listed skill with the Skill tool and read it in full before
writing anything. Record each one as `name@version`:

- a plugin skill: the plugin's `version` from its `plugin.json`;
- any other skill: the short SHA from
  `git log -1 --format=%h -- <skill folder>/SKILL.md`. If that file is
  uncommitted or modified, record `name@uncommitted` and raise a low concern:
  the rules applied cannot be reproduced later.

If a listed skill is missing or fails to load, record `name@missing` and raise
a high concern for that domain, owned by its listed owner, stating that the
design was not checked against that policy. Do not substitute your own
judgment for the missing policy: write no rules for that domain from general
knowledge, and claim no requirement complies with it. Then continue.

An entry with an empty owner is its own concern, owned by the intent's
originator: concerns in that domain have nobody to go to.

If the manifest names a `risk_classification_skill`, load and record it the
same way and use its classes and criteria. If it is named but missing, raise a
medium concern owned by the intent's originator. If none is named, propose
`standard`, `elevated`, or `high` with a one-line reason, and say no
classification skill was applied.

## Write the spec

Fill every section of the template.

- Trace every requirement to the intent section it serves. A requirement with
  no source in the intent is scope creep: drop it, or flag it if a policy rule
  demands it.
- Derive acceptance checks from How we would know it worked, keeping each
  signal's sample and who runs it, and carry the Grounds for rejection line
  unchanged.
- Treat the intent's Constraints as fixed and its Out of scope as binding. List
  each constraint with how the design honours it. Where a policy rule and an
  intent constraint cannot both hold, do not choose between them: flag it,
  cite both, and route it to the policy owner.
- Answer each open question from the intent, or carry it forward with its
  original owner. Answer only from the intent, a policy rule, or the user in
  interactive mode, and say which; never guess an answer in. Every question in
  the intent appears in the spec. A question owned by "design pass" is this
  skill's to answer; if it can't, carry it forward to the intent's originator,
  marked "reassigned from design pass".
- A carried-forward question keeps a dated needed-by. Any other needed-by
  becomes `spec acceptance`, because the design stage it was waiting for is
  this one, and it has run.
- Carry every flagged concern from the intent into the spec's table with its
  owner. The proposed resolution may give this design's answer, but only the
  owner closes it.
- If the intent names a `parent`, read the parent intent, and its spec if one
  exists. The parent's decisions bind this spec; where the parent has not
  decided, carry the question forward to the parent's owner rather than
  deciding it here.
- Apply each policy skill as a constraint on the design, and cite the rule as
  `skill § section` wherever it shaped a decision.
- For front-end work, write the UX section as screens, states (empty,
  loading, error, partial, no permission), and content, so the product owner
  can mock it in Claude Design straight from the spec. Do not produce mockups.
  With no user-facing surface, say so in that section.
- Propose a risk class. The product owner decides; anything above standard
  goes to a technical lead.

If the intent itself is wrong (contradictory, infeasible, or missing something
the design depends on), that is a flagged concern in domain `intent`, owned by
the originator. Do not edit `intent.md`. The originator amends and recommits
it, so the correction stays visible in the intent's history; a material
amendment returns the intent to `draft` for re-acceptance.

## Flagged concerns

These are the points an analyst would have escalated. Each row states its
severity, domain, the rule that triggered it (`skill § section`, or the intent
section), why the design can't satisfy both, a proposed resolution, and the
named owner from the manifest — or the intent's originator for concerns about
the intent. Never TBD.

Severity is `blocker` (the spec cannot be accepted until it is resolved),
`high`, `medium`, or `low`. Order by severity. Concerns go at the top of the
spec because the product owner works them first.

Prefer flagging over guessing. A spec that looks finished but hid a conflict
costs more than one with five honest concerns.

## Modes

**Interactive** (default): use AskUserQuestion only for ambiguities in the
intent itself, one round at a time. Policy conflicts are never resolved in
conversation; they are flagged for the policy owner. When an answer settles
an ambiguity, use it in the spec, cite "clarified in design session", and
raise a low concern for the originator to amend the intent to match.

**Headless** (`--headless`, or AskUserQuestion is unavailable): ask nothing.
Every ambiguity becomes a flagged concern or a carried-forward question. Write
the spec and stop; the CI job opens the pull request.

## Revising

When the user accepts the offer to revise an existing spec, re-run gate checks
1 and 2, reload every policy skill, and update `spec.md` in place with a fresh
intent SHA and policy versions, and `status: draft`. Keep every concern and
carried-forward question from the previous version unless the spec records
its owner's resolution or the intent now answers it.

## Output

Write `intent/<slug>/spec.md` with `status: draft` and the frontmatter filled
in: title, slug, intent SHA, every policy skill with its version, the proposed
risk class, and the number of flagged concerns.

Write no plan, no code, and no other files. Do not edit `intent.md`. Do not
commit and do not set status to accepted. Acceptance is the product owner's
decision, recorded by their commit, and that commit is what starts plan mode
in Stage 3.

Finish by telling the user how many concerns were flagged by severity, who
owns them, which intent questions were carried forward and to whom, and which
policy skills were missing. In headless mode, make this the last output so the
CI job can use it as the pull request body.

## Corrections

Recurring fixes the product owner has had to make to specs from this skill.
Add one line per correction as they come up; each line is worth more than any
guidance above it, because it came from a real spec.

- (none yet)
