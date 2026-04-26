import math
from jsrc.math.core import parse_columns, col_to_float_pair, write_output, t_pvalue, mean


def cmd(args):
    headers, data = parse_columns(args.input, args.sep)
    if not data:
        print("Error: no data")
        return
    x, y = col_to_float_pair(data, args.col[0], args.col[1])
    if len(x) < 3:
        print("Error: need at least 3 valid pairs")
        return
    lines = [f"n\t{len(x)}"]
    if args.method in ("pearson", "both"):
        r, p = _pearson(x, y)
        lines.append(f"pearson_r\t{r}")
        lines.append(f"pearson_p\t{p}")
    if args.method in ("spearman", "both"):
        r, p = _spearman(x, y)
        lines.append(f"spearman_r\t{r}")
        lines.append(f"spearman_p\t{p}")
    if args.method in ("both",):
        cv = _covariance(x, y)
        lines.append(f"covariance\t{cv}")
    write_output(lines, args.output)


def _covariance(x, y):
    mx = mean(x)
    my = mean(y)
    return sum((a - mx) * (b - my) for a, b in zip(x, y)) / (len(x) - 1)


def _pearson(x, y):
    n = len(x)
    mx = mean(x)
    my = mean(y)
    num = sum((a - mx) * (b - my) for a, b in zip(x, y))
    den = math.sqrt(sum((a - mx) ** 2 for a in x) * sum((b - my) ** 2 for b in y))
    if den == 0:
        return 0.0, 1.0
    r = num / den
    if abs(r) >= 1.0:
        return r, 0.0
    t = r * math.sqrt((n - 2) / (1 - r * r))
    p = t_pvalue(t, n - 2, two_sided=True)
    return r, p


def _spearman(x, y):
    n = len(x)
    x_rank = _rank(x)
    y_rank = _rank(y)
    mx = mean(x_rank)
    my = mean(y_rank)
    num = sum((a - mx) * (b - my) for a, b in zip(x_rank, y_rank))
    den = math.sqrt(sum((a - mx) ** 2 for a in x_rank) * sum((b - my) ** 2 for b in y_rank))
    if den == 0:
        return 0.0, 1.0
    rho = num / den
    if abs(rho) >= 1.0:
        return rho, 0.0
    t = rho * math.sqrt((n - 2) / (1 - rho * rho))
    p = t_pvalue(t, n - 2, two_sided=True)
    return rho, p


def _rank(vals):
    s = sorted(enumerate(vals), key=lambda x: x[1])
    ranks = [0] * len(vals)
    i = 0
    while i < len(s):
        j = i
        while j < len(s) - 1 and s[j + 1][1] == s[i][1]:
            j += 1
        avg_rank = (i + 1 + j + 1) / 2.0
        for k in range(i, j + 1):
            ranks[s[k][0]] = avg_rank
        i = j + 1
    return ranks
