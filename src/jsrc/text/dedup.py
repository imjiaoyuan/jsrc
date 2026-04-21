from collections import OrderedDict

from jsrc.text.core import read_text, write_text


def cmd(args):
    text = read_text(args.input)
    lines = text.splitlines()
    counts = OrderedDict()
    for line in lines:
        counts[line] = counts.get(line, 0) + 1
    if args.count:
        out_lines = [f"{v}\t{k}" for k, v in counts.items()]
    else:
        out_lines = list(counts.keys())
    out = "\n".join(out_lines)
    if out_lines:
        out += "\n"
    write_text(args.output, out)
