---
id:                 # kebab-case, matches the folder name under intent/
title:              # one line, plain language
originator:         # who wants this
created:            # ISO 8601, e.g. 2026-09-15
status: draft       # draft | accepted | rejected | superseded
source: idea        # idea | ticket | incident | scan-finding
source_ref:         # ticket ID, alert ID, PR/commit SHA, or omit
policy_owners: []   # names of people who must resolve a Flagged concern
supersedes:         # id of the intent this replaces, or omit
parent:             # id of the broader intent this is a slice of, or omit
---

# <Title>

<!-- Aim for one page. A long intent is usually several intents: if Proposed
outcome needs more than about five bullets, or its bullets need different
owners, split it into slices that name this one as `parent`. -->

## Problem

What cannot be done today, who pays for it, and how much. Give the cost as a
number (time, money, errors, delay), or write "cost not yet measured" and add
an open question to measure it. Written from the originator's position, not
the system's. No proposed solution in this section. A short paragraph.

## Affected users and systems

Who is affected and how they work around it now. Who owns or supports each
affected process and system. Systems that produce or consume the current
behavior, including any that have not been consulted and would notice a
change.

## Proposed outcome

What is true once this is done, stated so it can be checked without reading the
implementation. Mechanism-free: no technology or product names, schemas, file
layouts, component names, or step sequences. If a technology is genuinely
fixed, it belongs under Constraints with its reason, not here.

- <outcome>

## Out of scope

What this explicitly does not cover, so the Design pass does not widen it. At
least one line; if nothing is excluded, write "Nothing excluded" so the choice
is visible.

- <exclusion>

## Constraints

One per line, each with the named person or body whose authority makes it
binding. A constraint whose authority is not known is an open question, not a
constraint.

- <constraint> — fixed by <owner / policy / contract>, because <reason>

## How we would know it worked

Observable signals. What changes in behavior, in a metric, or in someone's day.
This is what the Test stage will be asked to prove, so vagueness here is
expensive later. For each signal, say how the sample is chosen and who runs
the check.

- <signal> — sample: <how it is chosen>, run by: <who>
- **Grounds for rejection:** <the result that would mean this failed>

## Flagged concerns

Points a security, compliance, data, or UX owner would escalate. Each named to a
person. Empty only when the change touches none of them — say so explicitly,
for example "Not applicable: touches no authentication, data classification,
personal data or published contract."

- <concern> — owner: <name>

## Open questions

Unresolved decisions. Each with an owner and when it is needed. Do not guess an
answer into this file.

- <question> — owner: <name>, needed by: <acceptance | design | date>

## Evidence

Where this came from, kept apart by who said it, so nobody mistakes research
for the originator's view.

### What the originator said

Interview notes or the originator's own words, with dates.

### Other sources

Tickets, documents, alert payloads, scan findings, prior intents and research,
each with a path, link or `source_ref`. Material the originator supplied sits
in this intent's folder and is cited by path.
