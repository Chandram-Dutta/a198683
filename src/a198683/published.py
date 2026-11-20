"""Jon E. Schoenfield's published tables for n = 1..11 (an OEIS "a-file", 2017).

For every bracketing with n <= 11 the tables record whether its value is new or which
earlier bracketing it equals. The file is not redistributed here; it is downloaded from
the OEIS on first use into data/, which is not kept in git.
"""

import pathlib
import urllib.request

URL = "https://oeis.org/A198683/a198683.txt"
REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
PATH = REPO_ROOT / "data" / "a198683.txt"


def _lines() -> list:
    if not PATH.exists():
        PATH.parent.mkdir(exist_ok=True)
        request = urllib.request.Request(URL, headers={"User-Agent": "a198683-verification"})
        PATH.write_bytes(urllib.request.urlopen(request, timeout=60).read())
    return PATH.read_text().splitlines()


def tables() -> dict:
    """{n: [(bracketing text, index of the lowest-indexed bracketing with the same value)]}."""
    result, n, count_end = {}, None, None
    for line in _lines():
        if line.startswith("n = "):
            n = int(line[4:].rstrip(":"))
            result[n] = []
        elif line.startswith("Index Expression"):
            count_end = line.index("Count") + len("Count")
        elif n is not None and line[:5].strip().isdigit():
            index, text, number = line.split()
            # A number in the Count column marks a new value; in the Match column, a repeat.
            is_new = len(line.rstrip()) <= count_end
            result[n].append((text, int(index) if is_new else int(number)))
    return result


def section(n: int) -> list:
    """The lines of the published table for one n, exactly as published."""
    lines = _lines()
    start = lines.index(f"n = {n}:")
    end = next(i for i in range(start, len(lines)) if lines[i].startswith(f"A198683({n}) = ")) + 2
    return lines[start:end]
