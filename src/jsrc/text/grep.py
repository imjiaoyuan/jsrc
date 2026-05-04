import re

from jsrc.text.core import read_text, write_text


def cmd(args):
    flags = re.IGNORECASE if args.ignore_case else 0
    pattern = re.compile(args.pattern, flags=flags)
    out_lines = []
    for idx, line in enumerate(read_text(args.input).splitlines(), start=1):
        matched = pattern.search(line) is not None
        if args.invert:
            matched = not matched
        if matched:
            if args.line_number:
                out_lines.append(f"{idx}:{line}")
            else:
                out_lines.append(line)
    out = "\n".join(out_lines)
    if out_lines:
        out += "\n"
    write_text(args.output, out)
