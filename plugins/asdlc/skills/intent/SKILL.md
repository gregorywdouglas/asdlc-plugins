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

## Amending an intent

Amend in place; never start a second intent for the same change. Record new
statements as dated Evidence entries rather than rewriting what was said
before, and change the other sections to match.

If the intent is `accepted` and the amendment changes Problem, Proposed
outcome, Constraints or Out of scope, set `status` back to `draft` and tell
the user: the change needs re-acceptance, and specs stay blocked until then.
Any other amendment (wording, Evidence, an owner named, a question answered)
leaves the status as it is.

## Interview

Use the AskUserQuestion tool, one round at a time, and let each answer choose
the next round. If it isn't available, ask in plain text, one question at a
time.

Cover the problem and what it costs today (as a number, if anyone has one),
who is affected and how they cope today, what better looks like in observable
terms, what is out of scope, hard constraints and who owns
them, and what would get this rejected. Don't ask about implementation. Skip
the obvious questions and dig into what the user probably hasn't worked
through: conflicting stakeholders, failure and degraded modes, data ownership,
and downstream systems that depend on today's behavior.

Ask who owns or supports each affected process and system while you map who
is affected, not at the end. Owners named early become the owners of the
questions and concerns that come up later.

When probing for constraints, check each kind in turn: security, compliance,
data residency, budget, schedule, organisational standards, and limits of the
platforms already in place. Each constraint you find still needs the
authority that fixed it.

Ask only questions whose answer would change the intent. Do not force
decisions that belong to requirements, architecture or design. When a
question is really a design decision, don't pursue it in the interview:
record it as an open question with `needed by: design` and owner "design
pass", and move on.

When the user answers with mechanism, ask what outcome it serves and record
the outcome. Mechanism is any technology or product name, schema or field,
file, component or orchestration name, or sequence of steps. In a refactor or
migration it usually arrives as the names of what exists today. Keep a
technical choice only if it is genuinely fixed, list it under Constraints with
who fixed it, and tell the user you did this so they can see the pattern in
their own answers.

Ask whether the change touches authentication, data classification or
personal data, or a contract other systems or parties rely on. If it does,
Flagged concerns must name each concern and its owner. If it touches none of
them, write that explicitly under Flagged concerns rather than leaving the
section empty.

When the user can't answer, record an open question with a named owner. Don't
fill the gap with a plausible guess — an honest open question is worth more to
the next stage than a finished-looking document.

Keep facts and assumptions apart. A statement the user hasn't confirmed is
marked unconfirmed where it appears, and if the intent depends on it, it is
also an open question with an owner. Never turn an open question into a fact
because the drafting needs one.

## Stop condition

Keep going until every section of the template could be acted on by someone
who was not in this conversation. If Proposed outcome has grown past about
five bullets, or its bullets need different owners, propose splitting it into
slices before writing. Then, before writing anything, check the
draft against each rule of the accept rule in `intent/README.md` and tell the
user which rules it fails and why, alongside any sections that are still
thin. The intent gate will block a spec on the same rules, so this report is
the user's list of what stands between the draft and acceptance.

## Output

Write `intent/<slug>/intent.md` from the template, with `status: draft`.
The slug is three or four lowercase hyphenated words naming the thing, not
the change type, with no dates or ticket numbers. Confirm the slug with the
user before creating the folder, since later artifacts and branches reuse it.

Leave `title` for last and derive it from the Problem section.

Write these lines in exactly this form, because the intent gate reads them:

- Open question: `- <question> — owner: <name>, needed by: <acceptance | design | date>`
- Flagged concern: `- <concern> — owner: <name>`
- Constraint: `- <constraint> — fixed by <who>, because <reason>`
- Success signal: `- <signal> — sample: <how it is chosen>, run by: <who>`

Every open question has both `owner:` and `needed by:`. `<name>` is a person;
a role is written `<role> (person to be named)` and does not satisfy a
question needed by acceptance, a flagged concern or a constraint. Design
questions may be owned by `design pass`. A constraint whose authority nobody
can name is not yet a constraint: record it as an open question instead.

Follow the template's guidance on content: the Problem gives the cost as a
number or says "cost not yet measured" and adds an open question to measure
it; Out of scope has at least one line, or "Nothing excluded"; How we would
know it worked ends with a **Grounds for rejection** line.

`policy_owners` lists the named owners of the Flagged concerns, or `[]` if
there are none. If this intent is a slice of a broader one, set `parent` to
the broader intent's id, copy its failure signal into How we would know it
worked, and add a constraint that the slice follows the parent's decisions;
where the parent has not decided, the slice records an open question owned by
the parent's owner instead of deciding.

Evidence has two parts. **What the originator said** records this interview:
its date and the user's key answers in their own words. **Other sources**
holds everything else, each with a path, link or `source_ref`, including any
research you did. If the user supplies source material (a ticket, an alert, a
document extract), save it in the intent's folder and cite it by path.

Use the user's own terms for their business, people and documents; don't
rename them into analyst or vendor vocabulary. The exception is technology:
technology terms stay out of Proposed outcome even when they are the user's
words.

Name only systems, teams and documents that the user named or that a cited
source names. Don't infer that a system is affected because similar changes
usually touch one; ask instead.

Write no code and no design. Besides `intent.md`, write only evidence files
the user supplied, in the intent's folder. Do not commit and do not set
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
