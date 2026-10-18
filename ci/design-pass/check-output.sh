#!/bin/sh
# Checks what a headless design pass left in the working tree, before the job
# commits anything. Run from the project root.
#
#   check-output.sh <slug>
#
# Passes only when the run wrote exactly intent/<slug>/spec.md, as a new file
# at `status: draft`, and changed nothing else. No spec means the skill's gate
# or the intent gate hook refused; any other change breaks the skill's hard
# stops. Either way the job fails and nothing is pushed.
set -eu

slug="${1:?usage: check-output.sh <slug>}"
want="?? intent/$slug/spec.md"
changes=$(git status --porcelain --untracked-files=all)

if [ -z "$changes" ]; then
  echo "No spec was written. The design pass refused or stopped; its report above says why." >&2
  exit 1
fi

if [ "$changes" != "$want" ]; then
  echo "The design pass changed files it must not touch. Expected only intent/$slug/spec.md:" >&2
  printf '%s\n' "$changes" | grep -vxF "$want" >&2 || true
  exit 1
fi

status=$(tr -d '\r' < "intent/$slug/spec.md" | awk '
  NR == 1 && $0 != "---" { exit }
  NR > 1 && $0 == "---"  { exit }
  /^status:/ { sub(/^status:[ \t]*/, ""); sub(/[ \t#].*$/, ""); print; exit }')
if [ "$status" != draft ]; then
  echo "intent/$slug/spec.md has status '${status:-missing}', not 'draft'. Only the product owner's commit accepts a spec." >&2
  exit 1
fi

echo "ok: intent/$slug/spec.md written as draft, nothing else changed"
