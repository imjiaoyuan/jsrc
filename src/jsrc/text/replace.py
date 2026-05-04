import re

from jsrc.text.core import read_text, write_text


def cmd(args):
    flags = re.IGNORECASE if args.ignore_case else 0
    pattern = re.compile(args.pattern, flags=flags)
    count = args.count if args.count >= 0 else 0
    out_lines = []
    for line in read_text(args.input).splitlines():
        out_lines.append(pattern.sub(args.repl, line, count=count))
    out = "\n".join(out_lines)
    if out_lines:
        out += "\n"
    write_text(args.output, out)
