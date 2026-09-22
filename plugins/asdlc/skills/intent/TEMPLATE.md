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
---

# <Title>

## Problem

What cannot be done today, and what that costs. Written from the originator's
position, not the system's. No proposed solution in this section.

## Affected users and systems

Who is affected and how they work around it now. Systems that produce or consume
the current behavior, including any that have not been consulted and would notice
a change.

## Proposed outcome

What is true once this is done, stated so it can be checked without reading the
implementation. Mechanism-free: no technology names, schemas, file layouts, or
step sequences. If a technology is genuinely fixed, it belongs under Constraints
with its reason, not here.

## Out of scope

What this explicitly does not cover, so the Design pass does not widen it.

## Constraints

One per line, each with the owner or source of authority that makes it binding.

- <constraint> — fixed by <owner / policy / contract>, because <reason>

## How we would know it worked

Observable signals. What changes in behavior, in a metric, or in someone's day.
This is what the Test stage will be asked to prove, so vagueness here is
expensive later.

## Flagged concerns

Points a security, compliance, data, or UX owner would escalate. Each named to a
policy owner. Empty only when the change touches none of them — say so
explicitly rather than leaving the section blank.

- <concern> — owner: <name>

## Open questions

Unresolved decisions. Each with an owner, and a by-when where one exists. Do not
guess an answer into this file.

- <question> — owner: <name>, needed by: <date or stage>

## Evidence

Where this came from. Conversation notes, ticket text, alert payload, scan
finding, or prior intent. Enough for someone who was not in the room to see what
was actually said.
