import math
from jsrc.math.core import (
    parse_columns, col_to_float_grouped, write_output, f_pvalue, f_cdf,
)


def cmd(args):
    headers, data = parse_columns(args.input, args.sep)
    if not data:
        print("Error: no data")
        return
    groups = col_to_float_grouped(data, args.group_col, args.value_col)
    if len(groups) < 2:
        print("Error: need at least 2 groups")
        return
    _oneway(groups, args.output)


def _oneway(groups, output):
    k = len(groups)
    group_stats = []
    total_n = 0
    grand_sum = 0.0
    for name, vals in sorted(groups.items()):
        n = len(vals)
        if n < 2:
            print(f"Warning: group '{name}' has < 2 values, skipping")
            continue
        m = sum(vals) / n
        ss = sum((v - m) ** 2 for v in vals)
        group_stats.append((name, n, m, ss))
        total_n += n
        grand_sum += sum(vals)
    if len(group_stats) < 2:
        print("Error: need at least 2 groups with >= 2 values each")
        return
    grand_mean = grand_sum / total_n
    ssb = sum(n * (m - grand_mean) ** 2 for _, n, m, _ in group_stats)
    ssw = sum(ss for _, _, _, ss in group_stats)
    dfb = k - 1
    dfw = total_n - k
    msb = ssb / dfb if dfb > 0 else 0
    msw = ssw / dfw if dfw > 0 else 0
    f_val = msb / msw if msw > 0 else 0
    p_val = f_pvalue(f_val, dfb, dfw)
    eta2 = ssb / (ssb + ssw) if (ssb + ssw) > 0 else 0
    write_output([
        f"source\tss\tdf\tms\tf\tp",
        f"between\t{ssb}\t{dfb}\t{msb}\t{f_val}\t{p_val}",
        f"within\t{ssw}\t{dfw}\t{msw}",
        f"total\t{ssb + ssw}\t{total_n - 1}",
        f"eta_sq\t{eta2}",
        f"k\t{k}",
        f"n\t{total_n}",
    ], output)
