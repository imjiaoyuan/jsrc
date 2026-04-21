from jsrc.text.core import read_text, write_text


def _parse_fields(spec: str) -> list[int]:
    out = []
    for x in spec.split(","):
        x = x.strip()
        if not x:
            continue
        v = int(x)
        if v < 1:
            raise ValueError("Field indices must be >= 1")
        out.append(v - 1)
    if not out:
        raise ValueError("No valid fields provided")
    return out


def cmd(args):
    fields = _parse_fields(args.fields)
    in_delim = args.delimiter
    out_delim = args.out_delimiter if args.out_delimiter is not None else in_delim
    out_lines = []
    for line in read_text(args.input).splitlines():
        parts = line.split(in_delim)
        picked = [parts[i] if i < len(parts) else "" for i in fields]
        out_lines.append(out_delim.join(picked))
    out = "\n".join(out_lines)
    if out_lines:
        out += "\n"
    write_text(args.output, out)
