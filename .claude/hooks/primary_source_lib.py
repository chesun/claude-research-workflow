"""
Shared logic for the primary-source-first enforcement hooks.

Two hooks use this:

- primary-source-check.py (PreToolUse on Edit|Write): blocks edits to
  load-bearing files that cite papers lacking reading-notes evidence.
- primary-source-audit.py (Stop): scans assistant text in the session
  transcript and blocks the turn-end if citations in prose lack notes
  evidence.

Both rely on the same citation-detection, notes-existence, and
session-read-verification logic, which lives here.

Project-agnostic. The surname allowlist is loaded at import time from
`.claude/state/primary_source_surnames.txt` (one lowercase surname per
line). If the file is missing or empty, the allowlist is skipped and
every Author-Year match is accepted. See `.claude/rules/primary-source-first.md`.
"""

from __future__ import annotations

import json
import os
import re
from pathlib import Path
from typing import Iterable


# File paths where primary-source enforcement applies. Template-generic —
# scoped to in-repo load-bearing artifacts. Overleaf paper .tex files live
# outside the repo and are not reachable by the PreToolUse hook.
ENFORCEABLE_PATTERNS = [
    r"decisions/.*\.md$",
    r"experiments/designs/decisions/.*\.md$",
    r"experiments/designs/.*\.md$",
    r"theory/.*\.(tex|md)$",
    r"quality_reports/advisor_meeting_[^/]+/.*\.(tex|md)$",
    r"quality_reports/session_logs/.*\.md$",
    r"quality_reports/plans/.*\.md$",
    r"quality_reports/reviews/.*\.md$",
    r"quality_reports/[^/]+_analysis\.md$",
]


def _load_surname_allowlist() -> set[str]:
    """Load lowercase surnames from the project-local allowlist file.

    Looks up `.claude/state/primary_source_surnames.txt` under
    CLAUDE_PROJECT_DIR if set, otherwise relative to this library file.
    Returns an empty set if the file is missing or empty — the caller
    treats empty as "skip filtering" (accept all Author-Year matches).
    """
    project_dir = os.environ.get("CLAUDE_PROJECT_DIR", "")
    if project_dir:
        path = Path(project_dir) / ".claude" / "state" / "primary_source_surnames.txt"
    else:
        path = Path(__file__).resolve().parent.parent / "state" / "primary_source_surnames.txt"
    if not path.is_file():
        return set()
    try:
        text = path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return set()
    surnames: set[str] = set()
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        surnames.add(line.lower())
    return surnames


KNOWN_SURNAMES = _load_surname_allowlist()

# Author-Year regex. Matches:
#   Chakraborty and Kendall (2025)
#   Chakraborty & Kendall 2025
#   Danz, Vesterlund, and Wilson (2024)
#   Karni (2009)
#   Brown et al. (2025)
AUTHOR_YEAR = re.compile(
    r"""
    \b
    (?P<first>[A-Z][A-Za-z\-']+)
    (?:\s*(?:,|and|&)\s*(?P<second>[A-Z][A-Za-z\-']+))?
    (?:\s*(?:,\s*and|&)\s*(?P<third>[A-Z][A-Za-z\-']+))?
    (?:\s+et\s+al\.?)?
    \s*\(?(?P<year>(?:19|20)\d{2})[a-z]?\)?
    """,
    re.VERBOSE,
)

# Escape hatch: <!-- primary-source-ok: stem1, stem2 -->
# Use non-greedy `.+?` with the explicit `-->` terminator so stems containing
# hyphens (e.g., `chetty-friedman-rockoff_2014`) are not truncated. The earlier
# `[^-]+` pattern stopped at the first hyphen, silently dropping any stems
# listed after a hyphen-containing one.
ESCAPE_HATCH = re.compile(
    r"<!--\s*primary-source-ok:\s*(?P<stems>.+?)\s*-->",
    re.IGNORECASE | re.DOTALL,
)

# Sentence-boundary detector. A capitalized first word right after a sentence
# terminator is almost never a surname citation; it's just the next sentence.
SENTENCE_BOUNDARY = re.compile(r"(?:[.?!:;]\s+|\n\s*\n)\s*$")

# Words that are *never* surnames. Applied independent of the project allowlist
# so the hook is reasonable on day one (when the allowlist is empty). Keep this
# list conservative — only words with effectively zero chance of being a real
# surname in academic prose.
NEVER_SURNAMES = frozenset({
    # Articles, demonstratives, copulae
    "the", "a", "an", "this", "these", "those", "that",
    # Prepositions
    "in", "on", "at", "from", "for", "to", "by", "with", "of",
    # Pronouns
    "we", "our", "us", "i", "you", "your", "he", "she", "they", "their", "it", "its",
    # Quantifiers
    "all", "some", "most", "both", "each", "every", "any", "no", "none",
    # Adverbs / discourse markers
    "only", "also", "even", "still", "yet", "however", "moreover",
    "additionally", "furthermore", "thus", "therefore", "hence",
    "meanwhile", "instead", "rather", "indeed",
    # Adjectives commonly capitalized at sentence start
    "available", "important", "notable", "key", "main", "primary",
    "significant", "relevant", "specific", "general",
    # Question / subordinator words
    "when", "where", "why", "how", "what", "which", "who", "whose",
    "if", "unless", "until", "while", "since", "because", "although",
    "despite", "given", "based", "using", "according", "see",
    "though", "before", "after",
    # Seasons
    "spring", "summer", "fall", "autumn", "winter",
    # Days of the week
    "monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday",
    # Months
    "january", "february", "march", "april", "may", "june",
    "july", "august", "september", "october", "november", "december",
    # Document-structure words
    "table", "figure", "panel", "column", "row", "section", "appendix",
    "chapter", "footnote", "equation", "model", "specification",
    "step", "stage", "phase", "round", "wave", "cohort", "year", "yr",
    "note", "notes",
    # Role-words used as placeholders in citation-style examples
    # ("Author and Author (year)", "Coauthor (year)", etc.)
    "author", "authors", "coauthor", "coauthors", "co-author", "co-authors",
    "editor", "editors", "name", "names", "surname", "surnames",
})


def _is_sentence_start(text: str, pos: int) -> bool:
    """True if `pos` is at start-of-document or right after a sentence terminator."""
    if pos == 0:
        return True
    return bool(SENTENCE_BOUNDARY.search(text[:pos]))


def _split_hyphenated_surname(token: str) -> list[str]:
    """If token has 3+ hyphen-separated capitalized name-like parts, split it.

    Used to handle method-name compounds like `Chetty-Friedman-Rockoff` that
    appear as a single hyphenated token but represent multiple surnames. A
    properly-named reading-notes file uses underscores, so the split lets the
    extractor build the right stem.

    Returns a single-element list (the original token) if the heuristic
    doesn't apply.
    """
    parts = token.split("-")
    if len(parts) < 3:
        return [token]
    if all(p[:1].isupper() and p[1:].isalpha() and len(p) >= 2 for p in parts):
        return parts
    return [token]

# Markdown section-header / citation-metadata line patterns for matching
# compiled reading-notes files.
HEADER_LINE = re.compile(r"^\s*#{1,6}\s+")
CITATION_LINE = re.compile(r"^\s*\*\*Citation", re.IGNORECASE)


def is_enforceable(rel_path: str) -> bool:
    """True if the file path is load-bearing for primary-source enforcement."""
    return any(re.search(p, rel_path) for p in ENFORCEABLE_PATTERNS)


def extract_citations(text: str) -> list[tuple[str, str]]:
    """Return list of (stem, display) tuples for citations in text.

    Applies four filters in order:

    1. **NEVER_SURNAMES blocklist** — words that are never surnames
       (function words, seasons, months, table/figure/etc.). Drops the
       match regardless of allowlist state.
    2. **Hyphenated-name decomposition** — if the captured `first` group
       is a 3+ part hyphenated capitalized token (e.g.,
       "Chetty-Friedman-Rockoff"), split it and treat each part as a
       surname. Builds an underscore-joined stem matching reading-notes
       filename conventions. Runs before the sentence-start check so
       that sentence-start hyphenated compounds can be tested against
       the allowlist using the decomposed head.
    3. **Sentence-start filter** — a capitalized first word right after a
       sentence terminator is dropped unless the project allowlist
       explicitly contains the (possibly-decomposed) head. Sentence-
       start function-word + year is almost never a citation.
    4. **Allowlist filter** — if KNOWN_SURNAMES is non-empty, the leading
       surname must appear in it. If empty (default for new projects),
       all matches that pass filters 1–3 are accepted.
    """
    citations: list[tuple[str, str]] = []
    seen: set[str] = set()
    allowlist_active = bool(KNOWN_SURNAMES)

    for match in AUTHOR_YEAR.finditer(text):
        first = match.group("first") or ""
        second = match.group("second") or ""
        third = match.group("third") or ""
        year = match.group("year") or ""

        # Filter 1: hard-coded blocklist — independent of allowlist
        if first.lower() in NEVER_SURNAMES:
            continue

        # Filter 2: hyphenated-name decomposition (handles method compounds)
        # Runs BEFORE the sentence-start check so that sentence-start hyphenated
        # compounds like "Chetty-Friedman-Rockoff (2014)" can be tested against
        # the allowlist using the decomposed head, not the full hyphenated form.
        first_parts = _split_hyphenated_surname(first)

        # Filter 3: sentence-start positions require explicit allowlist match
        # on the head of the (possibly-decomposed) compound.
        if _is_sentence_start(text, match.start()):
            head = first_parts[0].lower()
            if not (allowlist_active and head in KNOWN_SURNAMES):
                continue

        # Filter 4: allowlist + surname collection
        if len(first_parts) > 1:
            # Decomposed compound; treat each part as a surname slot
            all_parts = first_parts + [p for p in [second, third] if p]
            if allowlist_active:
                if first_parts[0].lower() not in KNOWN_SURNAMES:
                    continue
                surnames = [p for p in all_parts if p.lower() in KNOWN_SURNAMES]
            else:
                surnames = all_parts
        else:
            # Standard allowlist filter
            if allowlist_active:
                if first.lower() not in KNOWN_SURNAMES:
                    continue
                surnames = [s for s in [first, second, third] if s and s.lower() in KNOWN_SURNAMES]
            else:
                surnames = [s for s in [first, second, third] if s]

        if not surnames:
            continue

        stem = "_".join(s.lower() for s in surnames) + "_" + year
        # Use comma+and form so the display string round-trips through this
        # same extractor: a space-joined "Chetty Friedman Rockoff (2014)"
        # would be re-parsed as "Rockoff (2014)" alone (the regex doesn't
        # recognize space as a multi-author separator). Comma+and is what
        # the regex's `,/and/&` separator alternation actually accepts.
        if len(surnames) == 1:
            display = f"{surnames[0]} ({year})"
        elif len(surnames) == 2:
            display = f"{surnames[0]} and {surnames[1]} ({year})"
        else:
            display = ", ".join(surnames[:-1]) + f", and {surnames[-1]} ({year})"

        if stem not in seen:
            seen.add(stem)
            citations.append((stem, display))
    return citations


def extract_escaped_stems(text: str) -> set[str]:
    """Return lower-cased citation stems named in escape-hatch comments."""
    escaped: set[str] = set()
    for match in ESCAPE_HATCH.finditer(text):
        raw = match.group("stems")
        for stem in (s.strip().lower() for s in raw.split(",")):
            if stem:
                escaped.add(stem)
    return escaped


def matching_notes_files(stem: str, reading_notes_dir: Path) -> list[Path]:
    """Return all reading-notes files that match the citation stem.

    Match conditions:
    1. Filename starts with the citation stem (case-insensitive) — a
       dedicated per-paper file like `chakraborty_kendall_2025.md`.
    2. A citation-metadata line in the file references all of the stem's
       surnames and the year. Recognized citation-metadata forms:
       - Markdown: lines starting with `**Citation:**` or `**Citation:** ...`
       - YAML frontmatter: lines starting with `citation:` in the top block

    Section-header matching alone (e.g., `## 9. Chakraborty & Kendall 2025`)
    is NOT accepted, because documents like the reading-notes README or
    conceptual memos may mention the paper in a header without being notes
    about it. The `**Citation:**` line is the stronger signal of "this is
    reading notes for this paper."
    """
    if not reading_notes_dir.is_dir():
        return []

    stem_lower = stem.lower()
    parts = stem_lower.split("_")
    if len(parts) < 2:
        return []
    year = parts[-1]
    surnames = parts[:-1]

    surname_pattern = r"\b" + r"\b.*\b".join(re.escape(s) for s in surnames) + r"\b"
    citation_match_pattern = re.compile(
        surname_pattern + r".*" + re.escape(year),
        re.IGNORECASE,
    )

    matches: list[Path] = []
    for f in reading_notes_dir.glob("*.md"):
        if f.name.lower().startswith(stem_lower):
            matches.append(f)
            continue
        try:
            text = f.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        for line in text.splitlines():
            if not CITATION_LINE.match(line):
                continue
            if citation_match_pattern.search(line):
                matches.append(f)
                break
    return matches


def notes_exist_for(stem: str, reading_notes_dir: Path) -> bool:
    """True if at least one reading-notes file matches the citation stem."""
    return bool(matching_notes_files(stem, reading_notes_dir))


def paper_pdf_exists_for(stem: str, papers_dir: Path) -> bool:
    """True if a PDF matching the citation stem is in the papers dir.

    Matches by tokenizing filenames on non-alphanumeric characters. A
    filename matches if all of the stem's surnames and the year appear
    as distinct tokens. This is robust to filename conventions that use
    underscores (which would defeat \\b word boundaries because `_` is a
    word character in regex).
    """
    if not papers_dir.is_dir():
        return False

    stem_lower = stem.lower()
    parts = stem_lower.split("_")
    if len(parts) < 2:
        return False
    year = parts[-1]
    surnames = set(parts[:-1])

    for f in papers_dir.glob("*.pdf"):
        tokens = set(re.split(r"[^a-z0-9]+", f.name.lower()))
        tokens.discard("")
        if year in tokens and surnames.issubset(tokens):
            return True
    return False


# ---------------------------------------------------------------------------
# Session-transcript inspection
# ---------------------------------------------------------------------------


def iter_transcript_events(transcript_path: Path) -> Iterable[dict]:
    """Yield each JSONL event from the session transcript (fail-safe)."""
    if not transcript_path.is_file():
        return
    try:
        with transcript_path.open(encoding="utf-8", errors="ignore") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    yield json.loads(line)
                except json.JSONDecodeError:
                    continue
    except OSError:
        return


TOUCH_TOOLS = {"Read", "Write", "Edit"}


def notes_touched_in_session(transcript_path: Path) -> set[str]:
    """Return the set of absolute file paths touched (Read/Write/Edit) this session.

    Writing or editing a file counts as having consulted it — the author
    knows its contents at least as well as a reader does. Only Read is
    required for passive consultation.
    """
    touched: set[str] = set()
    for event in iter_transcript_events(transcript_path):
        msg = event.get("message", {}) or {}
        content = msg.get("content", [])
        if not isinstance(content, list):
            continue
        for block in content:
            if not isinstance(block, dict):
                continue
            if block.get("type") != "tool_use":
                continue
            if block.get("name") not in TOUCH_TOOLS:
                continue
            file_path = (block.get("input", {}) or {}).get("file_path", "") or ""
            if file_path:
                try:
                    touched.add(str(Path(file_path).resolve()))
                except (ValueError, OSError):
                    continue
    return touched


def notes_read_in_session(
    stem: str,
    reading_notes_dir: Path,
    transcript_path: Path,
) -> bool:
    """True iff a reading-notes file matching the citation was touched this session.

    "Touched" = Read, Write, or Edit on the notes file. Writing a notes file
    is equivalent to having read it (author knows the content).
    """
    if not transcript_path.is_file():
        return False
    matches = matching_notes_files(stem, reading_notes_dir)
    if not matches:
        return False
    touched = notes_touched_in_session(transcript_path)
    return any(str(f.resolve()) in touched for f in matches)


def extract_assistant_text(transcript_path: Path) -> str:
    """Concatenate all assistant-message text in the session transcript."""
    texts: list[str] = []
    for event in iter_transcript_events(transcript_path):
        if event.get("type") != "assistant":
            continue
        msg = event.get("message", {}) or {}
        content = msg.get("content", [])
        if isinstance(content, list):
            for block in content:
                if isinstance(block, dict) and block.get("type") == "text":
                    texts.append(block.get("text", "") or "")
        elif isinstance(content, str):
            texts.append(content)
    return "\n".join(texts)


def extract_tool_use_inputs(transcript_path: Path) -> str:
    """Concatenate the string-valued fields of all tool_use inputs in the transcript.

    Escape-hatch comments placed inside a file edit (Edit's new_string,
    Write's content) appear in the transcript as part of a tool_use block,
    not an assistant text block. Scanning here makes them visible to the
    audit hook, so a user who scoped the escape hatch to the edit does not
    also have to repeat it in prose.
    """
    texts: list[str] = []
    for event in iter_transcript_events(transcript_path):
        if event.get("type") != "assistant":
            continue
        msg = event.get("message", {}) or {}
        content = msg.get("content", [])
        if not isinstance(content, list):
            continue
        for block in content:
            if not isinstance(block, dict):
                continue
            if block.get("type") != "tool_use":
                continue
            tool_input = block.get("input", {}) or {}
            if not isinstance(tool_input, dict):
                continue
            for value in tool_input.values():
                if isinstance(value, str):
                    texts.append(value)
    return "\n".join(texts)


# ---------------------------------------------------------------------------
# Block-message construction
# ---------------------------------------------------------------------------


def describe_missing_status(
    stem: str,
    reading_notes_dir: Path,
    papers_dir: Path,
    transcript_path: Path | None,
) -> str | None:
    """Return a one-line status string for a missing citation, or None if OK.

    Three possible statuses:
    - "MISSING_NOTES_NO_PDF": paper not in repo at all.
    - "MISSING_NOTES_PDF_EXISTS": PDF is present but no notes written.
    - "NOTES_NOT_READ_IN_SESSION": notes exist but weren't opened this session.
    - None: the citation is satisfied.
    """
    if not notes_exist_for(stem, reading_notes_dir):
        if paper_pdf_exists_for(stem, papers_dir):
            return "MISSING_NOTES_PDF_EXISTS"
        return "MISSING_NOTES_NO_PDF"
    if transcript_path is not None:
        if not notes_read_in_session(stem, reading_notes_dir, transcript_path):
            return "NOTES_NOT_READ_IN_SESSION"
    return None


def build_block_message(
    context_description: str,
    missing: list[tuple[str, str, str]],
    rule_path: str = ".claude/rules/primary-source-first.md",
) -> str:
    """Build the human-readable block message from a list of missing citations.

    `missing` is a list of (stem, display, status) tuples where status is
    one of the strings returned by describe_missing_status.
    """
    lines = [
        "PRIMARY-SOURCE-FIRST: blocking.",
        "",
        context_description,
        "",
    ]

    by_status: dict[str, list[tuple[str, str]]] = {}
    for stem, display, status in missing:
        by_status.setdefault(status, []).append((stem, display))

    if by_status.get("MISSING_NOTES_PDF_EXISTS"):
        lines.extend(
            [
                "The following papers have PDFs in master_supporting_docs/literature/papers/",
                "but no corresponding reading-notes file in master_supporting_docs/literature/reading_notes/:",
                "",
            ]
        )
        for stem, display in by_status["MISSING_NOTES_PDF_EXISTS"]:
            lines.append(f"  - {display}  (expected notes stem: {stem})")
        lines.extend(
            [
                "",
                "Fix: read each PDF (use the pdf-learnings skill for long papers),",
                "then produce a reading-notes file following the template in",
                "master_supporting_docs/literature/reading_notes/README.md",
                "",
            ]
        )

    if by_status.get("MISSING_NOTES_NO_PDF"):
        lines.extend(
            [
                "The following papers are cited but have neither a PDF in",
                "master_supporting_docs/literature/papers/ nor a reading-notes file:",
                "",
            ]
        )
        for stem, display in by_status["MISSING_NOTES_NO_PDF"]:
            lines.append(f"  - {display}  (expected stem: {stem})")
        lines.extend(
            [
                "",
                "Fix: add the PDF to master_supporting_docs/literature/papers/ (name it",
                "with the surname(s) and year so the hook can find it, e.g.",
                "Smith_Jones_2024_something.pdf), then read it and produce a",
                "reading-notes file. A citation you cannot ground in a primary source",
                "does not belong in a load-bearing project artifact.",
                "",
            ]
        )

    if by_status.get("NOTES_NOT_READ_IN_SESSION"):
        lines.extend(
            [
                "The following papers have reading-notes files that exist but were",
                "NOT opened with the Read tool in this session:",
                "",
            ]
        )
        for stem, display in by_status["NOTES_NOT_READ_IN_SESSION"]:
            lines.append(f"  - {display}  (stem: {stem})")
        lines.extend(
            [
                "",
                "Fix: open the corresponding reading-notes file in",
                "master_supporting_docs/literature/reading_notes/ with the Read tool",
                "before making this claim. Cached context from prior sessions or",
                "derivative docs is not a substitute — the session-scoped Read is the",
                "mechanism by which this hook verifies you actually consulted the notes.",
                "",
            ]
        )

    lines.extend(
        [
            "Escape hatch (only when editing around an existing citation without",
            "making a new framing claim about it): add a comment to the delta or",
            "to a recent message:",
            "    <!-- primary-source-ok: stem1, stem2 -->",
            "",
            f"Rule: {rule_path}",
        ]
    )

    return "\n".join(lines)
