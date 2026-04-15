"""Brand-language guardrails for monday.com-facing QBR output."""

import re


_TEXT_REPLACEMENTS: tuple[tuple[re.Pattern[str], str], ...] = (
    (
        re.compile(r"\bJira integration\b", re.IGNORECASE),
        "monday.com integration workflow",
    ),
    (
        re.compile(r"\bJira sync\b", re.IGNORECASE),
        "monday.com workflow sync",
    ),
    (
        re.compile(r"\bJira roadmap\b", re.IGNORECASE),
        "integration roadmap",
    ),
    (
        re.compile(r"\bJira\b", re.IGNORECASE),
        "development workflow",
    ),
)


def normalize_monday_facing_language(text: str) -> str:
    """Keep generated language centered on monday.com rather than external vendors."""

    normalized = text
    for pattern, replacement in _TEXT_REPLACEMENTS:
        normalized = pattern.sub(replacement, normalized)
    return normalized
