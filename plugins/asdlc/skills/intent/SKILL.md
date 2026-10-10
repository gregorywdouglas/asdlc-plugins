---
name: intent
description: Drafts an intent.md — what is wanted, why, and under which constraints — by interviewing the user, before any spec or design exists. Use whenever the user has a new idea, feature, integration, refactor, or backlog item and wants to capture it, says "write an intent", "new intent", "capture this idea", or starts describing a change that has no accepted intent yet, even if they don't use the word intent. Do not use for writing specs, plans, or code.
argument-hint: "[the problem, in a sentence]"
---

# Draft an intent

The problem to capture: $ARGUMENTS

An intent is the first artifact in the lifecycle. It records the problem, the
outcome, and the constraints in the originator's own terms, so the design pass
can act on it later. It is deliberately not a spec: once implementation creeps
in, the design pass inherits assumptions nobody chose.

## Before starting

If the project has `intent/TEMPLATE.md`, use it — the project's template wins.
Otherwise use `${CLAUDE_SKILL_DIR}/TEMPLATE.md`.

If the project has no `intent/` folder, ask before creating it. When the user
agrees, create `intent/` and copy `${CLAUDE_SKILL_DIR}/README.md` into it so
the accept rule travels with the artifacts.

Check `intent/` for an existing folder covering the same problem. If one
exists, offer to amend it rather than starting a second intent for the same
change.

## Interview

Use the AskUserQuestion tool, one round at a time, and let each answer choose
the next round.

Cover the problem, who is affected and how they cope today, what better looks
like in observable terms, what is out of scope, hard constraints and who owns
them, and what would get this rejected. Don't ask about implementation. Skip
the obvious questions and dig into what the user probably hasn't worked
through: conflicting stakeholders, failure and degraded modes, data ownership,
and downstream systems that depend on today's behavior.

When the user answers with a technology or a design, ask what outcome it
serves and record the outcome. Keep a technical choice only if it is genuinely
fixed, list it under Constraints with who fixed it, and tell the user you did
this so they can see the pattern in their own answers.

When the user can't answer, record an open question with a named owner. Don't
fill the gap with a plausible guess — an honest open question is worth more to
the next stage than a finished-looking document.

## Stop condition

Keep going until every section of the template could be acted on by someone
who was not in this conversation. Then tell the user which sections are still
thin and why, before writing anything.

## Output

Write `intent/<slug>/intent.md` from the template, with `status: draft`.
The slug is three or four lowercase hyphenated words naming the thing, not
the change type, with no dates or ticket numbers. Confirm the slug with the
user before creating the folder, since later artifacts and branches reuse it.

Leave `title` for last and derive it from the Problem section.

Write no code, no design, and no other files. Do not commit and do not set
status to accepted — acceptance is the user's decision, recorded by their
commit.

## Corrections

Recurring fixes the user has had to make to drafts from this skill. Add one
line per correction as they come up; each line is worth more than any
guidance above it, because it came from a real draft.

- 2026-10-10 · cross-domain-documents · Unowned items accumulated (30+)
  without challenge. When an answer leaves a question, concern or constraint
  unowned, ask immediately who it would be sent to. A role is a placeholder:
  record it as "role → person to be named by <date>" and list it in the
  thin-sections report.
- 2026-10-10 · cross-domain-documents · Proposed outcome reached 18 bullets
  across independent concerns. If outcomes need different policy owners or
  could be accepted separately, propose a split into sibling intents before
  writing.
- 2026-10-10 · cross-domain-documents · Session research (regulations, case
  law) entered as rationale. The Problem section records only what the
  originator said. Research goes in Evidence, labelled "research, not
  originator statement", or becomes a question to the relevant owner.
- 2026-10-10 · cross-domain-documents · Proposed outcome named Guidewire and
  SharePoint. Name affected systems in Affected users and systems; the outcome
  refers to "the systems and channels people use today".
- 2026-10-10 · cross-domain-documents · Contradictory constraints (SharePoint
  "interim" vs "backing repository") were carried forward. Stop and resolve, or
  demote the constraint to an open question, before continuing.
- 2026-10-10 · cross-domain-documents · Evidence cited a document with no
  recorded location. Every source needs a path, link or source_ref; otherwise
  record it as unverifiable.
- 2026-10-10 · cross-domain-documents · A success signal was not checkable
  ("zero decisions made from a superseded version"). For each signal, ask how
  a sample would be selected and who runs it.
- 2026-10-10 · cross-domain-documents · The draft was amended across three
  weeks without stopping. If more than half of the open questions are
  unowned, the next step is an ownership pass, not more drafting; say so and
  stop.
- 2026-10-10 · cross-domain-documents · Frontmatter omitted `source_ref` and
  `supersedes`, and set `policy_owners: [TBD]`. Write every template field;
  use an explicit empty value, never TBD.
