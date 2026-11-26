"""The Printer Finally Answers — entry writer.

Writes the printer's single-line comeback to entry.txt inside the output
directory named by MAKEFUN_OUTPUT_DIR (default /output), then reads it back
and verifies it byte-for-byte before reporting success.

Standard library only, no network, deterministic.
"""

import os
import sys

ENTRY_LINE = "I didn't jam. I stopped on page 47 of 48 because the last page was a 12 MB screenshot of an email. I have standards. You, clearly, do not."

MIN_CHARS = 1
MAX_CHARS = 240


def validate(line):
    """Check the entry line against the competition gate.

    Returns a list of problems; an empty list means the line is valid.
    """
    problems = []
    if not isinstance(line, str) or not line:
        problems.append("entry line is empty")
        return problems
    try:
        line.encode("utf-8")
    except UnicodeEncodeError:
        problems.append("entry line is not valid UTF-8 text")
    if not line.strip():
        problems.append("entry line is only whitespace")
    if line != line.strip():
        problems.append("entry line has leading or trailing whitespace")
    if any(ord(ch) < 32 or ord(ch) == 127 for ch in line):
        problems.append("entry line contains control characters")
    if len(line) < MIN_CHARS or len(line) > MAX_CHARS:
        problems.append(
            f"entry line has {len(line)} characters, must be {MIN_CHARS}-{MAX_CHARS}"
        )
    if "\n" in line or "\r" in line:
        problems.append("entry line must be a single line with no line breaks")
    return problems


def write_entry(line, output_dir):
    """Write the line to entry.txt in output_dir; return the file path."""
    os.makedirs(output_dir, exist_ok=True)
    path = os.path.join(output_dir, "entry.txt")
    with open(path, "w", encoding="utf-8", newline="") as f:
        f.write(line)
    return path


def check_bytes_match(line, raw):
    """Fail unless the raw bytes equal the entry line encoded as UTF-8."""
    if raw != line.encode("utf-8"):
        print(
            "INVALID: byte check failed — written bytes do not match the entry line",
            file=sys.stderr,
        )
        sys.exit(1)


def check_text_shape(line, text):
    """Fail unless the decoded text has the right length and is one clean line."""
    if len(text) != len(line):
        print(
            "INVALID: character-count check failed — decoded text length does not match",
            file=sys.stderr,
        )
        sys.exit(1)
    if not text.strip() or "\n" in text or "\r" in text:
        print(
            "INVALID: single-line check failed — written entry is not a single non-blank line",
            file=sys.stderr,
        )
        sys.exit(1)


def verify_entry(line, path):
    """Read the file back; fail unless bytes and character count match."""
    with open(path, "rb") as f:
        raw = f.read()
    check_bytes_match(line, raw)
    text = raw.decode("utf-8")
    check_text_shape(line, text)
    return text


def main():
    problems = validate(ENTRY_LINE)
    if problems:
        for problem in problems:
            print(f"INVALID: {problem}", file=sys.stderr)
        sys.exit(1)
    output_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    path = write_entry(ENTRY_LINE, output_dir)
    text = verify_entry(ENTRY_LINE, path)
    byte_count = len(text.encode("utf-8"))
    print(
        f"OK: entry {text!r} ({len(text)} characters, {byte_count} bytes) verified in {path}"
    )


if __name__ == "__main__":
    main()
