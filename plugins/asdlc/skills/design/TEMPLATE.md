---
title:                   # from the intent, one line
slug:                    # matches the intent's folder name and id
status: draft            # draft | accepted (set only by the product owner's commit)
intent_sha:              # commit that last changed the accepted intent.md
design_skill:            # asdlc:design@<plugin version> that wrote this spec
design_command:          # the invocation exactly as run, e.g. "/asdlc:design <slug> --headless"
policy_skills: []        # name@version for every policy and risk skill applied; name@missing if absent
risk_class_proposed:     # standard | elevated | high, or the classification skill's classes
flagged_concerns: 0      # number of rows in Flagged concerns
---

# <Title>

## Flagged concerns

Ordered by severity: blocker | high | medium | low. Each owner is a name from
the policy manifest (both owners when two policies conflict), or the intent's
originator for concerns about the intent.

| # | Severity | Domain | Rule (skill § section) | Conflict | Proposed resolution | Owner |
|---|----------|--------|------------------------|----------|---------------------|-------|

## Summary

What is being built, in two or three sentences, and which intent outcome it
serves.

## Requirements

### Functional

| ID | Requirement | Intent source | Acceptance check |
|----|-------------|---------------|------------------|

### Non-functional

| ID | Requirement | Intent source / policy rule | Acceptance check |
|----|-------------|-----------------------------|------------------|

### Success signals

Carried from the intent's How we would know it worked, with the requirements
each one proves.

| Signal | Sample | Run by | Proves |
|--------|--------|--------|--------|

**Grounds for rejection:** <carried unchanged from the intent>.

## Constraints

Every constraint from the intent, unchanged, and how the design honours it.

| Constraint (from intent) | Fixed by | How the design honours it |
|--------------------------|----------|---------------------------|

## Design

### Approach

### Components and interfaces

### Data (ownership, classification, retention)

### Failure and degraded modes

### UX (screens, states, content — front-end work only)

For each screen: its purpose, the states it can be in (empty, loading, error,
partial, no permission), and its content (labels, messages, copy rules from
policy). No mockups. With no user-facing surface, say so here.

## Policy application

How each policy skill shaped the design, with rule citations. Name any policy
that could not be applied and the concern that records it.

## Risk class

Proposed class, the criteria that put it there, and the classification skill
used, if any. The product owner decides.

## Intent questions

Every open question from the intent, none dropped.

| Question (from intent) | Answered / carried forward | Answer and its source, or owner and needed-by |
|------------------------|----------------------------|-----------------------------------------------|

## Out of scope

Carried from the intent, plus anything this design explicitly excludes.
