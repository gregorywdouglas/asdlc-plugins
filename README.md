# asdlc-plugins

Claude Code plugins for the Spec-Driven / AI-native SDLC.

## Install

```shell
/plugin marketplace add gregorywdouglas/asdlc-plugins
/plugin install asdlc@asdlc-plugins
```

Then, in any repo: `/asdlc:intent domains need to publish to DNI Hub without
a new integration each time`. Plain `/intent` also works while no other
command claims that name.

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

Delete any project-level copy of the same skill from `.claude/skills/` so
there is only one version in play.

## Plugins

| Plugin  | Contents                                 |
| ------- | ---------------------------------------- |
| `asdlc` | `/asdlc:intent` — draft an `intent.md`; intent gate hook |

Later lifecycle skills (spec, plan, review) go in the same plugin under
`plugins/asdlc/skills/`, so one install carries the whole chain.

## Develop

Test against a local checkout before pushing:

```shell
/plugin marketplace add ./asdlc-plugins
/plugin install asdlc@asdlc-plugins
```

Validate before every push — this checks the manifests, duplicate names, and
source paths:

```bash
claude plugin validate .
```

`plugin.json` declares a `version`. Bump it on every release, or installs
keep the cached copy: patch for wording, minor for new skills or gates.

Skills are namespaced by plugin, so a skill added here never silently
replaces a bundled command or a project skill of the same name.

## Intent gate

The plugin ships a `PreToolUse` hook that runs whenever a session writes or
edits a spec file, including through a shell or PowerShell command. A spec file
is any Markdown file with "spec" as a word part of its name: `spec.md`,
`provisional-spec.md`, `spec-draft.md`, `specification.md` and so on, but not
`inspect.md`. The spec's folder name is taken as the slug, and the paired
`intent/<slug>/intent.md` must pass the accept rule or the write is blocked:

- status is `accepted` in the last commit, not only in the working copy;
- every template frontmatter field is present, and `policy_owners` is not TBD;
- every open question has an owner, and those needed by acceptance name a
  person rather than a role or "design pass";
- every constraint says who fixed it;
- Proposed outcome names no technology from the term list;
- Flagged concerns is populated, with owners, or marked not applicable.

Whether success signals are checkable is left to the human sign-off.

The gate only applies inside a project that has an `intent/` folder, so a
user-level install does not block spec files in repos that have not adopted
the lifecycle.

The term list is in `hooks/check_intent.py`. A project extends it with
`intent/tech-terms.txt`, one term per line; a line starting with `-` removes a
default term.

The hook needs a working Python 3, found as `python3`, `python` or the Windows
`py -3` launcher. On Windows, turn off the Microsoft Store aliases for
`python.exe` and `python3.exe` (Settings > Apps > Advanced app settings > App
execution aliases), or they shadow a real install. If no working Python is
found, spec writes are blocked rather than let through unchecked.

## Handoff

`docs/HANDOFF.md` is the current state of the plugin: versions, the gate, the
first run and its corrections, next steps and troubleshooting. Update it with
each release.

## Repo layout

```
.claude-plugin/marketplace.json     catalog: which plugins live here
plugins/<plugin>/
  .claude-plugin/plugin.json        plugin manifest
  skills/<skill>/SKILL.md           the skill
  skills/<skill>/*.md               resources the skill reads
  hooks/hooks.json                  deterministic gates
  hooks/*.py                        the scripts the gates run
```

Skills reference their own resources with `${CLAUDE_SKILL_DIR}`. Installed
plugins are copied to a cache, so never reference files outside the plugin
directory with `../`.
