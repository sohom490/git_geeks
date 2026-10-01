"""matcher.py - matches a parsed error against rules.json."""
import json
import re
import sys
from pathlib import Path
from urllib.parse import quote_plus

from error_parser import parse_error

RULES_PATH = Path(__file__).with_name("rules.json")


def load_rules() -> list:
    with open(RULES_PATH, encoding="utf-8") as f:
        return json.load(f)


def fill(text: str, values: dict) -> str:
    """Replace <placeholders> in a rule's text with values found in the error."""
    for key, val in values.items():
        text = text.replace(f"<{key}>", str(val) if val is not None else "")
    return text


def _build(rule: dict, parsed: dict, groups: dict) -> dict:
    values = {
        "type": parsed["error_type"],
        "message": parsed["message"],
        "file": parsed["file"],
        "line": parsed["line"],
        **groups,
    }
    return {
        "matched": True,
        "parsed": parsed,
        "summary": fill(rule["summary"], values),
        "causes": [fill(c, values) for c in rule["causes"]],
        "fix": fill(rule["fix"], values),
        "example": fill(rule.get("example", ""), values),
    }


def _fallback(parsed: dict) -> dict:
    if parsed["error_type"]:
        query = f"python {parsed['error_type']} {parsed['message']}"
        reason = "No rule exists for this error yet."
    else:
        query = "python error"
        reason = "Could not find an error line. Paste the full traceback, including the last line."
    return {
        "matched": False,
        "parsed": parsed,
        "reason": reason,
        "search_url": "https://www.google.com/search?q=" + quote_plus(query),
    }


def analyze(raw_text: str) -> dict:
    parsed = parse_error(raw_text)
    if not parsed["error_type"]:
        return _fallback(parsed)

    candidates = [r for r in load_rules() if r["error_type"] == parsed["error_type"]]

    # Pass 1: specific rules (with a pattern)
    for rule in candidates:
        if rule.get("pattern"):
            m = re.search(rule["pattern"], parsed["message"])
            if m:
                return _build(rule, parsed, m.groupdict())

    # Pass 2: general rules for the error type (no pattern)
    for rule in candidates:
        if not rule.get("pattern"):
            return _build(rule, parsed, {})

    return _fallback(parsed)


if __name__ == "__main__":
    # Quick command-line test:  python matcher.py < error.txt
    result = analyze(sys.stdin.read())
    print(json.dumps(result, indent=2))
