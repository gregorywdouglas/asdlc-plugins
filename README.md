# asdlc-plugins

Claude Code plugins for the Spec-Driven / AI-native SDLC.

## Install

The repo is private, so git needs credentials first. In a terminal, outside
Claude Code:

```bash
gh auth setup-git
```

Then in a Claude Code session, one command at a time (pasting several at once
runs them together as one malformed argument):

```shell
/plugin marketplace add https://github.com/gregorywdouglas/asdlc-plugins.git
/plugin install asdlc@asdlc-plugins
```

Use the full HTTPS URL. The `owner/repo` shorthand tries SSH first and fails
without an SSH key.

The intent gate also needs a working Python 3; see [Intent gate](#intent-gate).

Then, in a repo the change belongs to:
`/asdlc:intent domains need to publish to DNI Hub without a new integration
each time`. Plain `/intent` also works while no other command claims that
name, because the skill sets `name: intent`.

## Update

Run these in a Claude Code session after each release, one at a time:

```shell
/plugin marketplace update asdlc-plugins
/reload-plugins
```

`/plugin` then shows the installed version.

## Enable it automatically in a project

Commit this to the project's `.claude/settings.json`, and the marketplace
registers itself once the folder is trusted:

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

Each person still needs git credentials for the private repo.

Delete any project-level copy of the same skill from `.claude/skills/` so
there is only one version in play.

The skill copies its accept rule into a project's `intent/README.md` only on
first use. After the rule changes, copy `plugins/asdlc/skills/intent/README.md`
over the project's copy and commit it; sessions read the project's copy.

## Plugins

| Plugin  | Contents |
| ------- | -------- |
| `asdlc` | `/asdlc:intent` (draft an `intent.md`), `/asdlc:design` (write the `spec.md` for an accepted intent) and the intent gate hook |

Later lifecycle skills (plan, review) go in the same plugin under
`plugins/asdlc/skills/`, so one install carries the whole chain.

## Design pass

`/asdlc:design <slug>` is Stage 02. It runs only when
`intent/<slug>/intent.md` is `accepted`, committed and unchanged from HEAD,
and no `spec.md` exists yet. It loads every policy skill named in the
project's `asdlc/policies.yaml` (or the plugin's default manifest), and writes
`intent/<slug>/spec.md` at `status: draft`.

Conflicts with policy go to the top of the spec as flagged concerns, each with
a named owner from the manifest. A missing policy skill is flagged, never
improvised. The skill does not commit: the product owner's commit that sets
the spec's `status: accepted` is the sign-off, and starts Stage 3.

A project overrides the spec template with `asdlc/design-template.md`. The
name avoids the word "spec" because the intent gate treats any such file as a
spec.

## Design pass in CI

`.github/workflows/design-pass.yml` is a reusable workflow that runs the
design pass when an intent is accepted, with nobody to answer questions. For
each intent a push to the default branch moves to `accepted` (and that has no
`spec.md` yet), it:

1. runs `/asdlc:design <slug> --headless` with the plugin from this repo;
2. checks that the run wrote only `intent/<slug>/spec.md`, at `status: draft`,
   and changed nothing else (`ci/design-pass/check-output.sh`), and fails
   otherwise;
3. commits the spec to a new `design/<slug>` branch and opens a pull request
   whose body is the skill's closing report;
4. keeps the full session transcript and the exact command as the
   `design-transcript-<slug>` artifact for 90 days, whether the pass
   succeeded or not.

The spec records the intent SHA, the design skill's version, the command
that ran it, and every policy skill's version. The CI commit adds the plugin
commit and a link to the run, so each spec can be traced to what produced it.

A wording fix to an already accepted intent does not start a second pass; an
intent amended back to `draft` and accepted again does, if it still has no
spec (`ci/design-pass/detect.sh`). Several intents accepted in one push each
get their own job, branch and pull request. The product owner works the
concerns on that pull request and accepts the spec by committing
`status: accepted` on the branch.

**Caller.** Commit this to the project as `.github/workflows/asdlc-design.yml`:

```yaml
name: Design pass
on:
  push:
    branches: [main]
    paths: ["intent/*/intent.md"]
  workflow_dispatch:
    inputs:
      slug:
        description: Intent slug to design
        required: true
jobs:
  design:
    uses: gregorywdouglas/asdlc-plugins/.github/workflows/design-pass.yml@main
    permissions:
      contents: write
      pull-requests: write
    with:
      slug: ${{ inputs.slug || '' }}
    secrets:
      ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
      ASDLC_PLUGINS_TOKEN: ${{ secrets.ASDLC_PLUGINS_TOKEN }}
```

The manual trigger runs one intent by slug, for a pass that failed or was
skipped. Optional inputs: `asdlc_ref` (default `main`; keep it the same as
the `@ref` above), `claude_code_version` (default `2.1.302`) and
`max_budget_usd` (default `5`, per intent).

**Setup, once per project:**

- Secret `ANTHROPIC_API_KEY`.
- Secret `ASDLC_PLUGINS_TOKEN`: a fine-grained token with read-only Contents
  access to `gregorywdouglas/asdlc-plugins`. This repo is private, and the
  job clones it for the plugin and the scripts.
- In the project: Settings > Actions > General > Workflow permissions,
  turn on "Allow GitHub Actions to create and approve pull requests".
- In this repo, once: Settings > Actions > General > Access, choose
  "Accessible from repositories owned by the user", so private projects can
  call the workflow.

Pull requests opened with the job's own token don't trigger other workflows.
If the project runs checks on pull requests, push an empty commit to the
branch, or switch the job to a GitHub App token.

**What the session can do.** The design pass runs with this allowlist:

```bash
claude -p "/asdlc:design <slug> --headless" \
  --permission-mode acceptEdits \
  --allowedTools "Read,Write,Glob,Grep,Skill,Bash(git ls-files:*),Bash(git diff:*),Bash(git log:*),Bash(git status:*)"
```

The allowlist is deliberately narrow: single `git ls-files`, `git diff`,
`git log` and `git status` commands, and no `cd`, `echo` or chaining.
`git status` is how the skill checks whether a policy skill's `SKILL.md` has
uncommitted changes. The skill runs each git check on its own for this
reason. Don't widen the list to fix a refused compound command; Claude Code
refuses commands with shell variables such as `$?` regardless, and an
unattended job should run as little as it can.

Only the Anthropic key reaches that step. The checkout keeps no credentials
and no GitHub token is set, so the session cannot push; the job commits and
opens the pull request itself, after the output check. The intent gate hook
ships with the plugin and runs in CI too.

In headless mode the skill asks nothing: every gap becomes a flagged concern
or a carried-forward question.

## Intent gate

The plugin ships a `PreToolUse` hook on the `Write`, `Edit`, `MultiEdit`,
`Bash` and `PowerShell` tools. It acts when a session writes or edits a spec
file, directly or through a shell command. A spec file is any Markdown file
with "spec" as a word part of its name: `spec.md`, `provisional-spec.md`,
`spec-draft.md`, `specification.md` and so on, but not `inspect.md`.

The spec's folder name is taken as the slug. The write is blocked unless
`intent/<slug>/intent.md` exists and passes these checks:

- status is `accepted` in the last commit, not only in the working copy;
- every template frontmatter field is present, and `policy_owners` is not TBD;
- every open question is written `— owner: <name>, needed by: <stage>`, and
  those needed by acceptance name a person rather than a role or "design
  pass";
- every constraint names the person or body that fixed it (`— fixed by <who>,
  because <reason>`), not a role awaiting a name or "not named";
- a `parent`, if set, names an intent that exists;
- Proposed outcome names no technology from the term list;
- Flagged concerns is populated, each with a named owner rather than a role
  awaiting a name, or marked not applicable.

Whether the success signals are checkable, and whether someone outside the
drafting conversation could act on the intent, are left to the human
sign-off.

A block lists every failure and tells the session to fix the intent rather
than the spec, and not to write the spec another way.

The gate only applies inside a project that has an `intent/` folder, so a
user-level install does not block spec files in repos that have not adopted
the lifecycle.

The term list is in `plugins/asdlc/hooks/check_intent.py`. A project extends
it with `intent/tech-terms.txt`, one term per line; a line starting with `-`
removes a default term.

**Requirements.** The hook runs through `sh`, which on Windows is Git Bash. It
needs a working Python 3, found as `python3`, `python` or the Windows `py -3`
launcher. On Windows, turn off the Microsoft Store aliases for `python.exe`
and `python3.exe` (Settings > Apps > Advanced app settings > App execution
aliases), or they shadow a real install, then restart VS Code so Claude Code
sees the new PATH.

**Fails closed.** If no working Python is found, or the check hits an error
while a spec write is in play, the write is blocked rather than let through
unchecked. If `sh` itself cannot run, Claude Code reports a hook error and the
write proceeds, so keep Git Bash installed on Windows.

## Develop

Test against a local checkout before pushing:

```shell
/plugin marketplace add ./asdlc-plugins
/plugin install asdlc@asdlc-plugins
```

Validate before every push. This checks the manifests, duplicate names and
source paths:

```bash
claude plugin validate .
```

`plugin.json` declares a `version`, and installs stay on it until it changes.
Bump it on every release, or installs keep the cached copy: patch for fixes
and wording, minor for new skills or gates. Then push to `main` and run the
[update](#update) commands.

Skills are namespaced by plugin, so a skill added here never silently
replaces a bundled command or a project skill of the same name.

## Handoff

`docs/HANDOFF.md` is the current state of the plugin: versions, the gate, the
first run and its corrections, next steps and troubleshooting. Update it with
each release.

## Repo layout

```
.claude-plugin/marketplace.json     catalog: which plugins live here
.github/workflows/design-pass.yml   reusable CI workflow for the headless design pass
ci/design-pass/detect.sh            which intents a push accepted
ci/design-pass/check-output.sh      the run wrote only a draft spec.md
docs/HANDOFF.md                     current state and next steps
plugins/asdlc/
  .claude-plugin/plugin.json        plugin manifest, including version
  hooks/hooks.json                  the intent gate's hook registration
  hooks/run_gate.sh                 finds a working Python 3; fails closed
  hooks/check_intent.py             the accept-rule checks and term list
  skills/intent/SKILL.md            the interview, its rules and Corrections
  skills/intent/TEMPLATE.md         the intent.md skeleton
  skills/intent/README.md           accept rule, copied into a project's intent/
  skills/design/SKILL.md            the design pass, its gate and Corrections
  skills/design/TEMPLATE.md         the spec.md skeleton
  skills/design/policies.yaml       default policy manifest
```

Skills reference their own resources with `${CLAUDE_SKILL_DIR}`, and hooks
with `${CLAUDE_PLUGIN_ROOT}`. Installed plugins are copied to a cache, so
never reference files outside the plugin directory with `../`.
