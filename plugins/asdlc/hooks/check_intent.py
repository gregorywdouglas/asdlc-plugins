#!/usr/bin/env python3
"""Intent gate for the asdlc plugin.

Runs as a Claude Code PreToolUse hook. When a session is about to write or edit
a spec.md, it finds the paired intent (intent/<slug>/intent.md, where <slug> is
the spec's folder name) and checks it against the accept rule in
intent/README.md. If the intent fails, the write is blocked (exit code 2) and
the reasons are returned to the session, with the route to approval.

Checks:
  1. A paired intent exists.
  2. status is `accepted` in the committed version, not just the working copy.
  3. Frontmatter carries every template field; policy_owners is not TBD.
  4. Every open question has an owner; questions needed by acceptance have a
     named person, not a role placeholder or "design pass".
  5. Every constraint names who fixed it.
  6. Proposed outcome names no technology from the term list.
  7. Flagged concerns is populated, or explicitly marked not applicable, and
     each concern has an owner.

Whether success signals are checkable is a judgement, not a pattern, so it is
left to the human sign-off.

Term list: the defaults below, plus one term per line from intent/tech-terms.txt
in the project if that file exists. Lines starting with "-" remove a default.
"""

import json
import os
import re
import subprocess
import sys

DEFAULT_TERMS = [
    # Microsoft / Azure
    "Azure", "APIM", "API Management", "Logic Apps", "Logic App", "Service Bus",
    "Event Grid", "Event Hubs", "Azure Functions", "Cosmos DB", "Blob Storage",
    "Data Factory", "ADF", "Entra", "Active Directory", "SharePoint",
    "OneDrive", "Power Automate", "Power Apps", "Dynamics", "BizTalk",
    "Key Vault", "AKS", "Bicep", "ARM template",
    # Other platforms and infrastructure
    "AWS", "S3", "Lambda", "GCP", "Kubernetes", "Docker", "Terraform", "Kafka",
    "RabbitMQ", "Redis", "PostgreSQL", "Postgres", "MySQL", "SQL Server",
    "MongoDB", "Elasticsearch", "Snowflake", "Databricks",
    # Protocols and formats
    "REST", "GraphQL", "gRPC", "SOAP", "JSON", "XML", "CSV", "OAuth", "SAML",
    "webhook", "OpenTelemetry", "CloudEvents",
    # Enterprise applications
    "Guidewire", "PolicyCenter", "BillingCenter", "ClaimCenter",
    "ContactManager", "Salesforce", "SAP", "ServiceNow", "Maximo", "Workday",
    "SmartComm",
]

REQUIRED_FIELDS = [
    "id", "title", "originator", "created", "status", "source",
    "source_ref", "policy_owners", "supersedes",
]

PLACEHOLDER_OWNERS = re.compile(
    r"^(|unassigned.*|unknown.*|owner unknown.*|tbd.*|tba.*|none|n/?a|\?+|<name>)$",
    re.IGNORECASE,
)

WRITE_TOOLS = {"Write", "Edit", "MultiEdit"}
SHELL_TOOLS = {"Bash", "PowerShell"}
# A spec is any Markdown file whose name contains "spec" as a word part:
# spec.md, SPEC.md, provisional-spec.md, spec-draft.md, spec_v2.md, specs.md,
# specification.md. Not inspect.md, respect.md or aspects.md.
SPEC_FILE = re.compile(r"(?:^|[-_. ])spec(?:s|ification)?(?:[-_. ][^/\\]*)?\.md$", re.IGNORECASE)


def is_spec(path):
    return bool(SPEC_FILE.search(re.split(r"[\\/]", path)[-1]))


def main():
    try:
        # Read bytes and decode as UTF-8: Windows consoles default to a code page.
        event = json.loads(sys.stdin.buffer.read().decode("utf-8", errors="replace"))
    except ValueError:
        return 0  # Not a hook payload we understand.

    cwd = event.get("cwd") or os.getcwd()
    specs = spec_paths(event, cwd)
    if not specs:
        return 0

    # From here on a spec write is in play, so any failure blocks (fails closed).
    try:
        report = []
        for spec in specs:
            problems, intent_rel = check_spec(spec)
            if problems:
                report.append((spec, intent_rel, problems))
        if not report:
            return 0
        message = render(report, cwd)
    except Exception as exc:  # noqa: BLE001
        message = (
            "Blocked by the asdlc intent gate: the paired intent could not be checked "
            f"({type(exc).__name__}: {exc}). A spec is never written unchecked. Tell the "
            "user this is blocking; do not write the spec another way.\n"
        )

    emit(message)
    return 2


def emit(text):
    # Encode explicitly so a Windows code page cannot crash the gate open.
    try:
        sys.stderr.buffer.write(text.encode("utf-8"))
        sys.stderr.buffer.flush()
    except (AttributeError, OSError):
        sys.stderr.write(text.encode("ascii", "replace").decode("ascii"))


def spec_paths(event, cwd):
    tool = event.get("tool_name", "")
    params = event.get("tool_input") or {}
    paths = []
    if tool in WRITE_TOOLS:
        p = params.get("file_path") or ""
        if is_spec(p):
            paths.append(p)
    elif tool in SHELL_TOOLS:
        cmd = params.get("command") or ""
        if re.search(r"spec", cmd, re.IGNORECASE) and re.search(r"(>|\btee\b|\bcp\b|\bmv\b|\bsed\s+-i|\bperl\s+-[pi]|Out-File|Set-Content|Add-Content|New-Item|Copy-Item|Move-Item)", cmd):
            for m in re.finditer(r"""([^\s'"<>|;&]+\.md)\b""", cmd, re.IGNORECASE):
                if is_spec(m.group(1)):
                    paths.append(m.group(1))
    return [p if os.path.isabs(p) else os.path.normpath(os.path.join(cwd, p)) for p in paths]


def check_spec(spec_path):
    spec_path = spec_path.replace("\\", "/") if os.sep == "/" else spec_path
    slug = os.path.basename(os.path.dirname(spec_path))
    root = find_root(os.path.dirname(spec_path))
    if root is None:
        # No intent/ folder above the file: this project has not adopted the
        # lifecycle, so the gate does not apply (the plugin may be installed for
        # every repo on the machine).
        return [], None

    intent_rel = f"intent/{slug}/intent.md"
    intent_path = os.path.join(root, "intent", slug, "intent.md")
    if not os.path.isfile(intent_path):
        return ([
            f"No intent exists for '{slug}'. The spec's folder name is the slug, "
            f"and {intent_rel} must exist and be accepted before a spec is written. "
            f"Run /asdlc:intent first, or move the spec under the right slug."
        ], intent_rel)

    with open(intent_path, encoding="utf-8") as f:
        text = f.read()
    return check_intent(text, root, intent_rel), intent_rel


def find_root(start):
    d = os.path.abspath(start)
    while True:
        if os.path.isdir(os.path.join(d, "intent")):
            return d
        parent = os.path.dirname(d)
        if parent == d:
            return None
        d = parent


def check_intent(text, root, intent_rel):
    problems = []
    fm, body = split_frontmatter(text)
    sections = split_sections(body)

    # Status, in the working copy and in the last commit.
    status = fm.get("status", "").strip()
    if status != "accepted":
        problems.append(
            f"status is '{status or 'missing'}', not 'accepted'. No spec may be "
            f"written from a {status or 'missing'} intent."
        )
    else:
        committed = committed_status(root, intent_rel)
        if committed is not None and committed != "accepted":
            problems.append(
                "status is 'accepted' in the working copy but not in the last "
                "commit. Acceptance is the commit that flips status, so commit "
                "it first. The commit is the sign-off."
            )

    # Frontmatter completeness.
    missing = [k for k in REQUIRED_FIELDS if k not in fm]
    if missing:
        problems.append(
            "Frontmatter is missing: " + ", ".join(missing) +
            ". Write every template field; use an explicit empty value where one does not apply."
        )
    po = fm.get("policy_owners", "")
    if re.search(r"\b(tbd|tba|unknown|unassigned)\b", po, re.IGNORECASE):
        problems.append(f"policy_owners is '{po.strip()}'. Name the people, or use [] if none.")

    # Open questions.
    oq = sections.get("open questions")
    if oq is not None:
        for q in bullets(oq):
            owner, needed = owner_of(q), needed_by(q)
            label = first_words(q)
            if owner is None:
                problems.append(f"Open question has no owner: \"{label}\"")
            elif is_placeholder(owner):
                problems.append(f"Open question owner is '{owner}': \"{label}\"")
            elif needed.startswith("acceptance"):
                if owner.lower() == "design pass":
                    problems.append(
                        f"Open question is needed by acceptance but owned by the design pass: \"{label}\""
                    )
                elif "to be named" in owner.lower():
                    problems.append(
                        f"Open question needed by acceptance has a role, not a person ('{owner}'): \"{label}\""
                    )

    # Constraints.
    cons = sections.get("constraints")
    if cons is not None:
        for c in bullets(cons):
            label = first_words(c)
            m = re.search(r"fixed by\s+(.+?)(?:,|\bbecause\b|$)", c, re.IGNORECASE)
            if not m:
                problems.append(f"Constraint does not say who fixed it: \"{label}\"")
            elif is_placeholder(clean(m.group(1))):
                problems.append(f"Constraint owner is '{clean(m.group(1))}': \"{label}\"")

    # Proposed outcome.
    outcome = sections.get("proposed outcome")
    if outcome is None:
        problems.append("Proposed outcome section is missing.")
    else:
        found = tech_terms_in(outcome, root)
        if found:
            problems.append(
                "Proposed outcome names technology: " + ", ".join(found) +
                ". Name affected systems under Affected users and systems, and anything "
                "genuinely fixed under Constraints with who fixed it."
            )

    # Flagged concerns.
    fc = sections.get("flagged concerns")
    fc_text = strip_guidance(fc or "")
    if not fc_text:
        problems.append(
            "Flagged concerns is empty. Populate it, or state explicitly that it does not apply."
        )
    elif not re.search(r"not applicable|\bn/a\b|none apply|does not (touch|apply)", fc_text, re.IGNORECASE):
        for c in bullets(fc):
            owner = owner_of(c)
            if owner is None or is_placeholder(owner):
                problems.append(
                    f"Flagged concern has no named owner ('{owner or 'none'}'): \"{first_words(c)}\""
                )

    return problems


def split_frontmatter(text):
    m = re.match(r"^---\s*\n(.*?)\n---\s*\n(.*)$", text, re.DOTALL)
    if not m:
        return {}, text
    fm = {}
    for line in m.group(1).splitlines():
        km = re.match(r"^([A-Za-z_]+):\s*(.*?)\s*(#.*)?$", line)
        if km:
            fm[km.group(1)] = km.group(2)
    return fm, m.group(2)


def split_sections(body):
    sections, current, buf = {}, None, []
    for line in body.splitlines():
        h = re.match(r"^##\s+(.+?)\s*$", line)
        if h:
            if current is not None:
                sections[current] = "\n".join(buf)
            current, buf = h.group(1).strip().lower(), []
        elif current is not None:
            buf.append(line)
    if current is not None:
        sections[current] = "\n".join(buf)
    return sections


def bullets(section):
    items, cur = [], None
    for line in section.splitlines():
        if re.match(r"^[-*]\s+", line):
            if cur is not None:
                items.append(cur)
            cur = re.sub(r"^[-*]\s+", "", line)
        elif cur is not None and line.strip() and line.startswith((" ", "\t")):
            cur += " " + line.strip()
        elif cur is not None and not line.strip():
            continue
        elif cur is not None:
            items.append(cur)
            cur = None
    if cur is not None:
        items.append(cur)
    # Drop template placeholders such as "<question> — owner: <name>".
    return [i for i in items if not i.startswith("<")]


def clean(s):
    return re.sub(r"[*_`]", "", s).strip().rstrip(".").strip()


def owner_of(item):
    m = re.search(r"owner:\s*(.+?)(?:,\s*needed by:|$)", clean(item), re.IGNORECASE)
    if not m:
        return None
    owner = m.group(1).strip()
    owner = re.sub(r"\s*\((?!person to be named).*?\)\s*$", "", owner).strip()
    return owner


def needed_by(item):
    m = re.search(r"needed by:\s*(.+)$", clean(item), re.IGNORECASE)
    return m.group(1).strip().lower() if m else ""


def is_placeholder(owner):
    return bool(PLACEHOLDER_OWNERS.match(owner.strip()))


def first_words(item, n=12):
    words = clean(item).split()
    return " ".join(words[:n]) + (" …" if len(words) > n else "")


def strip_guidance(section):
    """Remove empty lines and template guidance paragraphs, keep bullets and real text."""
    lines = [l for l in section.splitlines() if l.strip()]
    text = "\n".join(lines)
    if text.startswith("Points a security, compliance"):
        text = "\n".join(l for l in lines if l.lstrip().startswith(("-", "*")))
    return text.strip()


def tech_terms_in(section, root):
    terms = list(DEFAULT_TERMS)
    extra = os.path.join(root, "intent", "tech-terms.txt")
    if os.path.isfile(extra):
        with open(extra, encoding="utf-8") as f:
            for line in f:
                t = line.strip()
                if not t or t.startswith("#"):
                    continue
                if t.startswith("-"):
                    terms = [x for x in terms if x.lower() != t[1:].strip().lower()]
                else:
                    terms.append(t)
    found = []
    for t in terms:
        # Acronyms match case-sensitively so "rest" or "sap" in prose do not trip.
        flags = 0 if t.isupper() else re.IGNORECASE
        if re.search(r"(?<![\w-])" + re.escape(t) + r"(?![\w-])", section, flags):
            found.append(t)
    return sorted(set(found), key=str.lower)


def committed_status(root, intent_rel):
    try:
        out = subprocess.run(
            ["git", "-C", root, "show", f"HEAD:{intent_rel}"],
            capture_output=True, text=True, timeout=10,
        )
    except (OSError, subprocess.SubprocessError):
        return None  # No git available: fall back to the working copy.
    if out.returncode != 0:
        # Not a repo, or the intent was never committed.
        inside = subprocess.run(
            ["git", "-C", root, "rev-parse", "--is-inside-work-tree"],
            capture_output=True, text=True,
        )
        return "uncommitted" if inside.returncode == 0 else None
    fm, _ = split_frontmatter(out.stdout)
    return fm.get("status", "").strip()


def render(report, cwd):
    out = ["Blocked by the asdlc intent gate: a spec can only be written from an accepted intent.", ""]
    for spec, intent_rel, problems in report:
        out.append(f"Spec: {os.path.relpath(spec, cwd)}")
        out.append(f"Intent: {intent_rel}")
        for p in problems:
            out.append(f"  - {p}")
        out.append("")
    out += [
        "Route to approval: fix these in the intent, not in the spec, then commit the",
        "change that sets status: accepted. That commit is the sign-off. Do not work",
        "around this gate by writing the spec another way; tell the user what is",
        "blocking and which owners need to answer.",
    ]
    return "\n".join(out) + "\n"


if __name__ == "__main__":
    sys.exit(main())
