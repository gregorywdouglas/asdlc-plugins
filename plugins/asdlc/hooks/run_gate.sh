#!/bin/sh
# Launcher for the asdlc intent gate.
#
# Finds a working Python 3 (python3, python, or the Windows "py -3" launcher)
# and runs check_intent.py with the hook payload. Each candidate is actually
# executed, because on Windows "python3" and "python" often exist only as
# Microsoft Store placeholders that print an error and exit.
#
# Fails closed: if no Python 3 works and the tool call looks like a spec write,
# the write is blocked rather than let through unchecked.

payload=$(cat)
here="${CLAUDE_PLUGIN_ROOT:-$(dirname "$0")/..}/hooks"

for py in python3 python "py -3"; do
  # $py is deliberately unquoted so "py -3" splits into command and flag.
  if $py -c "import sys; sys.exit(0 if sys.version_info[0] == 3 else 1)" >/dev/null 2>&1; then
    printf '%s' "$payload" | $py "$here/check_intent.py"
    exit $?
  fi
done

case "$payload" in
  *spec.md*)
    cat >&2 <<'EOF'
Blocked by the asdlc intent gate: no working Python 3 was found, so the paired
intent could not be checked, and a spec is never written unchecked.

Fix: install Python 3 (python.org, or "winget install Python.Python.3.12"). On
Windows, also turn off the Microsoft Store aliases for python.exe and
python3.exe under Settings > Apps > Advanced app settings > App execution
aliases. Then retry. Tell the user this is blocking; do not write the spec
another way.
EOF
    exit 2
    ;;
esac
exit 0
