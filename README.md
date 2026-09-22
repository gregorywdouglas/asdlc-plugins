# claude-plugins

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
    "claude-plugins": {
      "source": { "source": "github", "repo": "gregorywdouglas/claude-plugins" }
    }
  },
  "enabledPlugins": { "asdlc@claude-plugins": true }
}
```

Delete any project-level copy of the same skill from `.claude/skills/` so
there is only one version in play.

## Plugins

| Plugin  | Contents                                 |
| ------- | ---------------------------------------- |
| `asdlc` | `/asdlc:intent` — draft an `intent.md`   |

Later lifecycle skills (spec, plan, review) go in the same plugin under
`plugins/asdlc/skills/`, so one install carries the whole chain.

## Develop

Test against a local checkout before pushing:

```shell
/plugin marketplace add ./claude-plugins
/plugin install asdlc@claude-plugins
```

Validate before every push — this checks the manifests, duplicate names, and
source paths:

```bash
claude plugin validate .
```

Neither manifest declares a `version`, so installs track the latest commit
and a push is the release. If you add a `version`, bump it on every release
or users keep the cached copy.

Skills are namespaced by plugin, so a skill added here never silently
replaces a bundled command or a project skill of the same name.

## Repo layout

```
.claude-plugin/marketplace.json     catalog: which plugins live here
plugins/<plugin>/
  .claude-plugin/plugin.json        plugin manifest
  skills/<skill>/SKILL.md           the skill
  skills/<skill>/*.md               resources the skill reads
  hooks/hooks.json                  (later) deterministic gates
```

Skills reference their own resources with `${CLAUDE_SKILL_DIR}`. Installed
plugins are copied to a cache, so never reference files outside the plugin
directory with `../`.
