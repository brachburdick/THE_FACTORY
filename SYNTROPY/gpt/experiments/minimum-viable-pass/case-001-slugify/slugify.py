import re


def slugify_title(title: str) -> str:
    """Convert a human-readable title into a URL-safe slug."""
    lowered = title.lower().strip()
    if not lowered:
        return ""

    # Convert separator-like characters to spaces, then drop other punctuation.
    normalized = re.sub(r"[_\-\s]+", " ", lowered)
    alnum_and_space = re.sub(r"[^a-z0-9 ]+", "", normalized)

    parts = [part for part in alnum_and_space.split(" ") if part]
    return "-".join(parts)
