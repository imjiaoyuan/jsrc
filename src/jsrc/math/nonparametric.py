import math
from jsrc.math.core import (
    parse_columns, col_to_float_pair, write_output, mean, normal_cdf,
)


def cmd(args):
    headers, data = parse_columns(args.input, args.sep)
    if not data:
        print("Error: no data")
        return
    x, y = col_to_float_pair(data, args.col[0], args.col[1])
    if args.paired:
        _wilcoxon(x, y, args.output)
    else:
        _mannwhitney(x, y, args.output)


def _mannwhitney(x, y, output):
    n1, n2 = len(x), len(y)
    if n1 < 2 or n2 < 2:
        print("Error: need at least 2 per group")
        return
    all_vals = [(v, 0) for v in x] + [(v, 1) for v in y]
    all_vals.sort(key=lambda t: t[0])
    ranks = [0] * (n1 + n2)
    i = 0
    while i < n1 + n2:
        j = i
        while j < n1 + n2 - 1 and all_vals[j + 1][0] == all_vals[i][0]:
            j += 1
        avg_rank = (i + 1 + j + 1) / 2.0
        for k in range(i, j + 1):
            ranks[k] = avg_rank
        i = j + 1
    r1 = sum(ranks[k] for k in range(n1 + n2) if all_vals[k][1] == 0)
    u1 = r1 - n1 * (n1 + 1) / 2
    u2 = n1 * n2 - u1
    u = min(u1, u2)
    mu = n1 * n2 / 2.0
    tie_counts = {}
    for k in range(n1 + n2):
        v = all_vals[k][0]
        tie_counts[v] = tie_counts.get(v, 0) + 1
    tie_correction = 1.0 - sum(t ** 3 - t for t in tie_counts.values()) / ((n1 + n2) ** 3 - (n1 + n2))
    sigma = math.sqrt(n1 * n2 * (n1 + n2 + 1) / 12.0)
    if sigma == 0:
        z = 0
    else:
        z = (u - mu - 0.5) / sigma if u > mu else (u - mu + 0.5) / sigma
    p = 2.0 * normal_cdf(-abs(z)) if z != 0 else 1.0
    write_output([
        f"test\tmann_whitney_u",
        f"n1\t{n1}",
        f"n2\t{n2}",
        f"u\t{u}",
        f"z\t{z}",
        f"p\t{p}",
    ], output)


def _wilcoxon(x, y, output):
    if len(x) != len(y) or len(x) < 2:
        print("Error: need at least 2 paired observations")
        return
    diffs = [b - a for a, b in zip(x, y)]
    nonzero = [(abs(d), d) for d in diffs if d != 0]
    if len(nonzero) < 2:
        print("Error: not enough non-zero differences")
        return
    n = len(nonzero)
    nonzero.sort(key=lambda t: t[0])
    ranks = [0] * n
    i = 0
    while i < n:
        j = i
        while j < n - 1 and nonzero[j + 1][0] == nonzero[i][0]:
            j += 1
        avg_rank = (i + 1 + j + 1) / 2.0
        for k in range(i, j + 1):
            ranks[k] = avg_rank
        i = j + 1
    w_plus = sum(ranks[k] for k in range(n) if nonzero[k][1] > 0)
    w_minus = sum(ranks[k] for k in range(n) if nonzero[k][1] < 0)
    w = min(w_plus, w_minus)
    mu = n * (n + 1) / 4.0
    sigma = math.sqrt(n * (n + 1) * (2 * n + 1) / 24.0)
    z = (w - mu) / sigma if sigma > 0 else 0
    p = 2.0 * normal_cdf(-abs(z)) if z != 0 else 1.0
    write_output([
        f"test\twilcoxon_signed_rank",
        f"n\t{n}",
        f"w_plus\t{w_plus}",
        f"w_minus\t{w_minus}",
        f"w\t{w}",
        f"z\t{z}",
        f"p\t{p}",
    ], output)
