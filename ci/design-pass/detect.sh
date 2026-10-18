#!/bin/sh
# Finds the intents the design pass should run on, and prints them as a JSON
# array of slugs. Run from the project root.
#
#   detect.sh <before-sha> <after-sha>   push mode: intents this push accepted
#   detect.sh --slug <slug>              manual mode: one intent, at HEAD
#
# Push mode picks an intent when its status is `accepted` at <after-sha> but
# was not at <before-sha> (or the file did not exist), and it has no spec.md
# yet. Anything else is skipped with a note on stderr, so a wording fix to an
# accepted intent never starts a second design pass.
#
# Manual mode fails, with the reason, unless the intent is accepted and has no
# spec.md. The skill's own gate still runs; this only saves a wasted job.
set -eu

# The frontmatter `status` of <path> at <rev>, or nothing if absent.
status_at() {
  git show "$1:$2" 2>/dev/null | tr -d '\r' | awk '
    NR == 1 && $0 != "---" { exit }
    NR > 1 && $0 == "---"  { exit }
    /^status:/ { sub(/^status:[ \t]*/, ""); sub(/[ \t#].*$/, ""); print; exit }'
}

valid_slug() {
  printf '%s' "$1" | grep -Eq '^[a-z0-9][a-z0-9-]*$'
}

has_spec() {
  git cat-file -e "$1:intent/$2/spec.md" 2>/dev/null
}

if [ "${1:-}" = "--slug" ]; then
  slug="${2:-}"
  valid_slug "$slug" || { echo "Not a valid intent slug: '$slug'." >&2; exit 1; }
  status=$(status_at HEAD "intent/$slug/intent.md")
  if [ -z "$status" ]; then
    echo "intent/$slug/intent.md does not exist at HEAD, or has no status." >&2; exit 1
  fi
  if [ "$status" != accepted ]; then
    echo "intent/$slug/intent.md is '$status', not 'accepted'." >&2; exit 1
  fi
  if has_spec HEAD "$slug"; then
    echo "intent/$slug/spec.md already exists. Revise it interactively instead." >&2; exit 1
  fi
  printf '["%s"]\n' "$slug"
  exit 0
fi

before="${1:?usage: detect.sh <before-sha> <after-sha> | --slug <slug>}"
after="${2:?usage: detect.sh <before-sha> <after-sha> | --slug <slug>}"

# A new branch, or a force push past history we don't have: compare against
# the empty tree, so every intent at <after-sha> is considered.
if ! git cat-file -e "$before^{commit}" 2>/dev/null; then
  before=$(git hash-object -t tree /dev/null)
fi

out=""
for path in $(git diff --name-only "$before" "$after" -- 'intent/*/intent.md'); do
  slug=$(basename "$(dirname "$path")")
  # Git's pathspec `*` also matches `/`, so drop anything nested deeper.
  if [ "$path" != "intent/$slug/intent.md" ]; then
    echo "skip $path: not directly under intent/" >&2; continue
  fi
  if ! valid_slug "$slug"; then
    echo "skip $path: '$slug' is not a valid slug" >&2; continue
  fi
  now=$(status_at "$after" "$path")
  was=$(status_at "$before" "$path")
  if [ "$now" != accepted ]; then
    echo "skip $slug: status is '${now:-missing}'" >&2; continue
  fi
  if [ "$was" = accepted ]; then
    echo "skip $slug: already accepted before this push" >&2; continue
  fi
  if has_spec "$after" "$slug"; then
    echo "skip $slug: spec.md already exists" >&2; continue
  fi
  echo "design $slug: accepted in this push" >&2
  out="$out${out:+,}\"$slug\""
done
printf '[%s]\n' "$out"
