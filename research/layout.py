"""Split a CompanyIQ Markdown report into sections and describe its snapshot.

The report itself stays one Markdown string (that is what the PDF is built
from). This module only works out how to show it on screen.
"""

import re
from dataclasses import dataclass, field

HEADING_RE = re.compile(r"^(#{1,6})\s+(.+?)\s*#*\s*$")
BOLD_LINE_RE = re.compile(r"^\*\*(.+?)\*\*\s*:?\s*$")
NUMBERED_RE = re.compile(r"^\s*(\d+|[IVX]+)[.)]\s+")
SMALL_WORDS = {"and", "or", "of", "the", "to", "in", "for", "a", "an", "on"}


@dataclass
class Section:
    title: str
    body: str


@dataclass
class ReportParts:
    intro: str
    sections: list[Section] = field(default_factory=list)


def _clean_title(raw: str) -> str:
    title = raw.strip().strip("*_").strip().rstrip(":").strip()
    title = NUMBERED_RE.sub("", title)

    letters = [ch for ch in title if ch.isalpha()]
    if letters and all(ch.isupper() for ch in letters):
        words = title.lower().split()
        title = " ".join(
            word if i and word in SMALL_WORDS else word.capitalize()
            for i, word in enumerate(words)
        )

    return title


def _find_headings(lines: list[str]) -> list[tuple[int, int, str]]:
    """Return (line index, level, text) for headings outside code blocks.

    Lines that are only bold text count as level 7, so they are used only
    when the report has no real Markdown headings.
    """

    found = []
    in_code = False

    for index, line in enumerate(lines):
        if line.lstrip().startswith("```"):
            in_code = not in_code
            continue
        if in_code:
            continue

        match = HEADING_RE.match(line)
        if match:
            found.append((index, len(match.group(1)), match.group(2)))
            continue

        match = BOLD_LINE_RE.match(line.strip())
        if match and NUMBERED_RE.match(match.group(1)):
            found.append((index, 7, match.group(1)))

    return found


def _pick_section_level(headings: list[tuple[int, int, str]]) -> int | None:
    if not headings:
        return None

    real = [h for h in headings if h[1] <= 6] or headings

    # Prefer the level the numbered sections (1. COMPANY OVERVIEW ...) use.
    numbered = [h[1] for h in real if NUMBERED_RE.match(h[2].strip("*_ "))]
    if len(numbered) >= 2:
        return max(set(numbered), key=numbered.count)

    # Otherwise the highest level that appears more than once
    # (a lone top heading is usually just the report title).
    for level in sorted({h[1] for h in real}):
        if sum(1 for h in real if h[1] == level) >= 2:
            return level

    return None


def split_report(report: str) -> ReportParts:
    """Split the report at its main section headings."""

    lines = report.splitlines()
    headings = _find_headings(lines)
    level = _pick_section_level(headings)

    if level is None:
        return ReportParts(intro=report.strip())

    starts = [(i, text) for i, lvl, text in headings if lvl == level]
    intro_lines = lines[: starts[0][0]]

    # Drop a lone title heading at the top; the app shows its own title.
    intro_lines = [
        line for line in intro_lines
        if not (HEADING_RE.match(line) and len(HEADING_RE.match(line).group(1)) < level)
    ]

    sections = []
    for n, (start, text) in enumerate(starts):
        end = starts[n + 1][0] if n + 1 < len(starts) else len(lines)
        body = "\n".join(lines[start + 1:end]).strip()
        sections.append(Section(title=_clean_title(text), body=body))

    return ReportParts(intro="\n".join(intro_lines).strip(), sections=sections)


SNAPSHOT_FACTS = [
    ("industry", "Industry"),
    ("founded", "Founded"),
    ("headquarters", "Headquarters"),
    ("revenue_model", "Makes money from"),
]


def snapshot_to_markdown(snapshot: dict | None) -> str:
    """Write the snapshot as Markdown so the PDF can include it too."""

    if not snapshot:
        return ""

    parts = ["## At a Glance", ""]

    if snapshot.get("summary"):
        parts += [snapshot["summary"], ""]

    facts = [
        f"- **{label}:** {snapshot[key]}"
        for key, label in SNAPSHOT_FACTS
        if snapshot.get(key)
    ]
    parts += facts + [""]

    steps = snapshot.get("process_steps") or []
    if steps:
        parts.append("**Business process:** " + " → ".join(
            step.get("step", "") for step in steps if step.get("step")
        ))
        parts.append("")

    return "\n".join(parts).strip()
