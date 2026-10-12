# /asdlc:intent — Handoff

Oct 11, 2026 · @Gregory · plugin version 0.2.3

## What the skill is

`/asdlc:intent` interviews you and drafts an `intent.md` — the first artifact in the AI-native SDLC, written before any spec, design or code exists.

An intent records three things: what is wanted, why, and under which constraints. It is deliberately not a spec. Once implementation detail enters the document, the design pass inherits assumptions nobody consciously chose, and the first place anyone can argue with them is a finished diff.

The skill exists mainly to guard one failure mode: mechanism-leak. Describing a change naturally produces technology names, file layouts and step sequences. The skill catches those during the interview, asks what outcome the mechanism serves, and records the outcome instead — keeping a technical choice only where it is genuinely fixed, under Constraints, with the authority that fixed it.

The skill itself is advisory. Since 0.2.0 it is backed by a deterministic gate: a hook that refuses to let a spec be written until the paired intent passes the accept rule.

## Where it lives

A private Claude Code plugin marketplace at `gregorywdouglas/asdlc-plugins`. One repo, one plugin (`asdlc`), one skill and one gate so far.

```
asdlc-plugins/
├── .claude-plugin/marketplace.json      name: asdlc-plugins
├── README.md
└── plugins/asdlc/
    ├── .claude-plugin/plugin.json       name: asdlc, version: 0.2.3
    ├── hooks/
    │   ├── hooks.json                   PreToolUse gate on spec writes
    │   ├── run_gate.sh                  finds a working Python 3, fails closed
    │   └── check_intent.py              the accept-rule checks
    └── skills/intent/
        ├── SKILL.md                     the interview, its rules, Corrections
        ├── TEMPLATE.md                  the intent.md skeleton
        └── README.md                    copied into a project's intent/ on first use
```

| File | What it carries | Edit it when |
| --- | --- | --- |
| `SKILL.md` | Trigger description, interview rules, stop condition, output rules, Corrections | A draft needed a fix you don't want to make again |
| `TEMPLATE.md` | Frontmatter and the nine sections of an `intent.md` | A section is missing or earning nothing |
| `README.md` (skill) | The accept/reject rule for the intent home | The gate conditions change |
| `check_intent.py` | The checks the gate runs, and the default technology term list | The accept rule or the term list changes |

The skill prefers a project's own `intent/TEMPLATE.md` and falls back to the one it ships with. Resources are referenced with `${CLAUDE_SKILL_DIR}` and `${CLAUDE_PLUGIN_ROOT}`; installed plugins are copied to a cache, so a `../` path would not survive.

## Versioning and release

`plugin.json` declares a `version`. Claude Code caches installs by version, so **a push alone is no longer a release**: bump the version on every release or installs keep the cached copy. Patch for fixes and wording, minor for a new skill or gate.

| Version | What it added |
| --- | --- |
| 0.1.0 | Nine Corrections from the first real run; accept rule 1 scoped to `needed by: acceptance` |
| 0.2.0 | The intent gate |
| 0.2.1 | Gate fails closed when Python is missing; Windows fixes (Store aliases, `py -3`, encoding, backslash paths) |
| 0.2.2 | Gate matches every spec-named file, not only `spec.md`; skips repos with no `intent/` folder |
| 0.2.3 | Gate also covers the PowerShell tool, which is on by default on Windows |

Release routine: validate with `claude plugin validate .`, bump the version, push to `main`. Then, in each Claude Code session, one at a time:

```shell
/plugin marketplace update asdlc-plugins
/reload-plugins
```

`/plugin` should then show `asdlc` at the new version.

## Install

In a Claude Code session, one command at a time — pasting several at once concatenates them into a single malformed argument.

```shell
/plugin marketplace add https://github.com/gregorywdouglas/asdlc-plugins.git
/plugin marketplace list
/plugin install asdlc@asdlc-plugins
```

The explicit HTTPS URL avoids SSH, which the shorthand form tries first. The repo is private, so git needs credentials: `gh auth setup-git` in a terminal, outside Claude Code.

**The gate needs a working Python 3**, found as `python3`, `python` or the Windows `py -3` launcher. On Windows, install it (`winget install Python.Python.3.12`), turn off the Microsoft Store aliases for `python.exe` and `python3.exe` under Settings → Apps → Advanced app settings → App execution aliases, and restart VS Code so Claude Code sees the new PATH. Without Python the gate blocks every spec write.

To enable it automatically in a project, commit this to that repo's `.claude/settings.json`:

```json
{
  "extraKnownMarketplaces": {
    "asdlc-plugins": {
      "source": { "source": "github", "repo": "gregorywdouglas/asdlc-plugins" }
    }
  },
  "enabledPlugins": { "asdlc@asdlc-plugins": true }
}
```

Delete any project-level copy of the same skill from `.claude/skills/` so only one version is in play.

**Existing projects keep their old `intent/README.md`.** The skill copies it in only on first use, so after an accept-rule change, copy the plugin's `skills/intent/README.md` over the project's copy by hand and commit it. A session reads the project copy, not the plugin's.

## How to use it

Run it from the repo the change belongs to, with the problem — not the solution — as the argument:

```shell
/asdlc:intent domains need to publish to DNI Hub without a new integration each time
```

What it does, in order:

1. Reads the template — the project's `intent/TEMPLATE.md` if present, otherwise its own.
2. Asks before creating `intent/`, and copies the accept rule in with it.
3. Checks for an existing intent covering the same problem, and offers to amend rather than duplicate.
4. Interviews one round at a time, letting each answer choose the next.
5. Reports which sections are still thin.
6. Writes `intent/<slug>/intent.md` at `status: draft` and stops.

What it will not do: write code, propose a design, create any other file, commit, or set status to `accepted`. Acceptance is your decision, recorded by your commit.

It also fires on description alone — "I have an idea for…" — without the slash command. Add `disable-model-invocation: true` to the frontmatter to make it command-only; consider this before enabling it in client repos.

## The artifact it produces

One folder per change under `intent/`, named with the slug: three or four lowercase hyphenated words naming the thing, not the change type, with no dates or ticket numbers. The same slug is reused by the spec, the plan and the branch.

Frontmatter carries `id`, `title`, `originator`, `created`, `status`, `source`, `source_ref`, `policy_owners` and `supersedes`. Every field is written; an explicit empty value is used where one does not apply, never `TBD`.

| Section | Holds | Common failure |
| --- | --- | --- |
| Problem | What cannot be done today, and its cost | Written from the system's position; session research presented as the originator's rationale |
| Affected users and systems | Who is affected, how they cope now, what else notices | Downstream consumers left out |
| Proposed outcome | What is true when done, checkable without the implementation | Mechanism-leak lands here first; too many independent outcomes in one intent |
| Out of scope | What this does not cover | Left empty, so the design pass widens |
| Constraints | One per line, each with the owner that makes it binding | Listed without an owner; contradictory constraints carried forward |
| How we would know it worked | Observable signals the test stage will prove | No way to select the sample or say who runs it |
| Flagged concerns | Points a policy owner would escalate, each named | Owner recorded as a role or "unassigned" |
| Open questions | Unresolved decisions, each with an owner | Filled with a guess, or left unowned |
| Evidence | What was actually said, and where it came from | Summarised away; sources cited with no location |

Status moves `draft` → `accepted` | `rejected` | `superseded`, and rejected intents stay in the tree.

**Accept rule.** An intent may be accepted only when: every open question marked `needed by: acceptance` has a named person as owner (questions marked `needed by: design` may be owned by "design pass"); Proposed outcome names no technology; Flagged concerns is populated or explicitly not applicable; the success signals are checkable; and someone outside the drafting conversation could act on it. The commit that flips status to `accepted` is the sign-off.

## The intent gate

A `PreToolUse` hook runs on every Write, Edit, MultiEdit, Bash and PowerShell call. When the target is a spec file — any Markdown file with "spec" as a word part of its name (`spec.md`, `provisional-spec.md`, `spec-draft.md`, `specification.md`; not `inspect.md`) — it takes the spec's folder name as the slug and checks `intent/<slug>/intent.md`. It blocks the write unless:

- status is `accepted` **in the last commit**, not only in the working copy;
- every template frontmatter field is present and `policy_owners` is not TBD;
- every open question has an owner, and those needed by acceptance name a person rather than a role or "design pass";
- every constraint says who fixed it;
- Proposed outcome names no technology from the term list;
- Flagged concerns is populated with owners, or marked not applicable.

Whether success signals are checkable, and whether a stranger could act on the intent, stay with the human sign-off.

The block lists every failure and tells the session to fix the intent rather than the spec and not to work around the gate. It fails closed: no working Python, or an internal error during a spec write, blocks the write. It runs through `sh` (Git Bash on Windows); if `sh` cannot run at all, Claude Code treats that as a non-blocking hook error, so keep Git Bash installed. It does nothing in a repo with no `intent/` folder, so a user-level install leaves other repos alone.

The default term list is in `check_intent.py` (Azure integration services, common platforms, protocols, Guidewire and other enterprise applications). A project adds terms in `intent/tech-terms.txt`, one per line; a line starting with `-` removes a default.

## Current state

- **First real run done and corrected.** `cross-domain-documents` (Ascot document management) was drafted on 2026-09-23 and amended through 2026-10-07. Its review produced the nine Corrections now in `SKILL.md`: unowned items not challenged, an 18-bullet outcome never split, research entering as rationale, technology in the outcome, contradictory constraints carried forward, untraceable evidence, uncheckable signals, drafting that never stopped, and incomplete frontmatter.
- **Gate live on Windows.** Verified in VS Code on 2026-10-11: it blocked `intent/cross-domain-documents/spec.md` first for missing Python (fail-closed), then, with Python installed, for the intent's actual gaps across seven categories. The session stopped rather than writing the spec another way.
- **`cross-domain-documents` is being narrowed (option 2).** Design-level questions move to `needed by: design` / owner "design pass", technology comes out of the outcome, ownerless constraints become open questions, and the SharePoint interim-versus-backing contradiction is resolved or demoted. What remains is a short list of acceptance-blocking items needing named people (Srini, Brian, the PwC lead, a Legal and Compliance contact). A sibling intent for the Guidewire IM/COP Agency Bill first slice, answering to the parent, is the planned route to a first spec.
- **Single-person sign-off.** Originator, product owner and tech lead are the same person. The gate is the only control not dependent on that person's discipline.
- **Only the Plan stage exists.** Spec, plan and review skills are not written.
- **The github plugin's MCP server is failing.** Not needed for intent work; blocks the PR review stage later.

## Next steps

- [ ] Finish the ownership pass on `cross-domain-documents`; get the named people to agree; commit `status: accepted`.
- [ ] Draft the Guidewire IM/COP Agency Bill sibling intent with a parent link and the parent's "another silo" failure signal. Add a `parent` field to `TEMPLATE.md` and teach the gate about it (0.2.4).
- [ ] Second real run on a refactor or migration item (e.g. the WMX BizTalk orchestrations feeding Maximo). Check whether 0.1.0's Corrections hold when mechanism arrives as file and component names. Add what fails to Corrections.
- [ ] Copy the current `skills/intent/README.md` into every project that already has an `intent/` folder.
- [ ] Decide on `disable-model-invocation: true` before enabling the plugin in a client repo.
- [ ] Write the spec skill.

If a draft needs almost no correction, the interview is too easy. Harden the questions rather than declaring it done.

Measures, all readable from git log on `intent/`: time from first conversation to a committed `intent.md`; the share of intents accepted rather than closed; and `intent.md` commits dated after the first spec commit for the same change — the mechanism-leak proxy. A fix made only in the spec destroys that last signal.

## Troubleshooting

| Symptom | Cause | Fix |
| --- | --- | --- |
| `Marketplace name impersonates an official Anthropic/Claude marketplace` | Marketplace named `claude-plugins` | Rename to `asdlc-plugins` in `marketplace.json` and README references |
| `git@github.com: Permission denied (publickey)` | Shorthand `owner/repo` resolves to SSH | Use the full `https://….git` URL; run `gh auth setup-git` |
| Clone path ends in `--plugin-marketplace-list--plugin-install-asdlc` | Three slash commands pasted at once | Remove the broken marketplace entry; enter one command at a time |
| Marketplace add fails against a repo that exists | Add ran before the repo was pushed | Confirm with `git ls-remote`, then retry |
| Plugin enabled but shows a red dot | A bundled MCP server failed to start | `/mcp` for the status; usually auth or a missing runtime |
| `PreToolUse:Write hook error … Python was not found` and the spec is written anyway | 0.2.0 on Windows: `python3` is a Store alias; the crash was non-blocking | Update to 0.2.1 or later; install Python and turn off the Store aliases |
| Gate blocks with "no working Python 3 was found" | 0.2.1+ failing closed | Install Python 3, turn off the Store aliases, restart VS Code |
| Gate test does nothing | Session opened in the wrong repo (e.g. `asdlc-plugins` instead of the project) | Open Claude Code in the repo that has `intent/<slug>/intent.md` |
| Session applies the old accept rule | Project still has the old `intent/README.md` | Copy the plugin's `skills/intent/README.md` into the project and commit |
| Old behaviour after a push | Version not bumped, or no marketplace update | Bump `version`; run `/plugin marketplace update asdlc-plugins` and `/reload-plugins` |
| Gate blocks although status says accepted | Acceptance not committed | Commit the status change; the commit is the sign-off |

Two checks worth keeping. `git ls-files | grep claude-plugin` confirms both manifests were committed — they sit in dot-directories and a stray gitignore rule silently drops them. And `/plugin marketplace list` between the add and the install tells you which of the two actually failed.
