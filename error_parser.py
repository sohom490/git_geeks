"""error_parser.py - pulls the key facts out of a pasted Python traceback."""
import re

ERROR_SUFFIXES = ("Error", "Exception", "Warning", "Exit", "Interrupt", "Iteration")

FILE_RE = re.compile(r'File "(?P<file>[^"]+)", line (?P<line>\d+)(?:, in (?P<func>.+))?')
TYPE_RE = re.compile(r"^(?P<type>[A-Za-z_][\w.]*)(?::\s*(?P<msg>.*))?$")


def _looks_like_error_type(name: str) -> bool:
    return name.split(".")[-1].endswith(ERROR_SUFFIXES)


def parse_error(text: str) -> dict:
    """Return error_type, message, file, line, function and code_line (any may be None)."""
    result = {
        "error_type": None,
        "message": "",
        "file": None,
        "line": None,
        "function": None,
        "code_line": None,
    }
    lines = [l.rstrip() for l in text.strip().splitlines() if l.strip()]
    if not lines:
        return result

    # 1. Find the error line (search from the bottom up)
    error_idx = None
    for i in range(len(lines) - 1, -1, -1):
        m = TYPE_RE.match(lines[i].strip())
        if m and _looks_like_error_type(m.group("type")):
            result["error_type"] = m.group("type").split(".")[-1]
            result["message"] = (m.group("msg") or "").strip()
            error_idx = i
            break

    # 2. Find the last 'File "...", line N' reference (where the crash happened)
    last_file_idx = None
    for i, line in enumerate(lines):
        fm = FILE_RE.search(line)
        if fm:
            result["file"] = fm.group("file")
            result["line"] = fm.group("line")
            result["function"] = fm.group("func")
            last_file_idx = i

    # 3. The code line usually sits right under the file reference
    if last_file_idx is not None and last_file_idx + 1 < len(lines):
        nxt = lines[last_file_idx + 1].strip()
        if (
            last_file_idx + 1 != error_idx
            and not FILE_RE.search(nxt)
            and not nxt.startswith(("^", "~"))
        ):
            result["code_line"] = nxt

    return result
