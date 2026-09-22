# Intent home

Every change to this repository starts here. An intent captures what is wanted,
why, and under which constraints — never how to build it. The accepted intent is
the input to the requirements and design pass; the spec is not written until an
intent has been accepted.

## Layout

```
intent/
  TEMPLATE.md              the section skeleton and frontmatter — copy, don't edit
  README.md                this file
  <slug>/
    intent.md              the artifact
```

One folder per change, named with the same kebab-case slug as the `id` in
frontmatter. The folder exists so that evidence (an alert payload, a pasted
ticket, a screenshot) can sit beside the intent rather than being summarized
away.

## Lifecycle

`status` in frontmatter moves in one direction:

| status | meaning |
|---|---|
| `draft` | being written or corrected; no spec may be generated |
| `accepted` | reviewed and signed off; the Design pass may run |
| `rejected` | closed without a spec; kept for the record, never deleted |
| `superseded` | replaced by another intent, named in that intent's `supersedes` |

Rejected and superseded intents stay in the tree. The value of the intent home
is the record of what was asked for, including what was turned down.

## Accept / reject rule

This repo has one person acting as originator, product owner, and technical
lead, so acceptance is a self-review. It is a real gate anyway, and it is held by
the hook rather than by good intentions.

An intent may move to `accepted` only when all of the following hold:

1. Every open question has a named owner. An unowned question is a decision
   nobody is making.
2. **Proposed outcome** names no technology, schema, file, or step. Anything
   technical that is genuinely fixed appears under **Constraints** with the
   authority that fixed it.
3. **Flagged concerns** is either populated or explicitly marked as not
   applicable. It may not be silently empty when the change touches
   authentication, data classification, or a published contract.
4. **How we would know it worked** is checkable without reading the
   implementation.
5. The intent is understandable by someone who was not in the drafting
   conversation.

Acceptance is recorded by the commit that flips `status` to `accepted`. That
commit is the sign-off; git holds the author and the timestamp.

## Correcting an accepted intent

If the Design or Build stage shows the intent was wrong, amend the intent and
commit the change — do not fix it only in the spec. Intent commits dated after
the first `spec.md` commit for the same change are the signal being tracked
here, and hiding them in the spec destroys the signal.

## Writing one

Run `/asdlc:intent <the problem in a sentence>` in Claude Code. The skill
interviews you, drafts the file, and stops — you review and commit.

Correct the draft before committing. The correction pass is the point: what
you have to fix by hand belongs in the skill's Corrections section, so the
next draft doesn't need the same fix.
