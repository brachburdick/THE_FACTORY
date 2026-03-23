# Case 001: Slugify Title

## Brief

Implement `slugify_title(title: str) -> str` in `slugify.py`.

The function should turn a human-readable title into a URL-safe slug.

## Acceptance Criteria

- lowercase all letters
- keep letters and digits
- treat spaces, underscores, and hyphens as separators
- collapse repeated separators into a single hyphen
- remove punctuation and other non-alphanumeric characters
- strip leading and trailing separators
- return an empty string for empty or whitespace-only input

## Verifier

Run:

```bash
python3 -m unittest -v
```
