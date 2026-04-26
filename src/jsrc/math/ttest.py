from jsrc.math.core import (
    parse_columns, col_to_float, col_to_float_pair, write_output, mean, var_s,
    t_pvalue, t_cdf,
)
import math


def cmd(args):
    headers, data = parse_columns(args.input, args.sep)
    if not data:
        print("Error: no data")
        return
    cols = args.col
    if len(cols) == 1:
        _one_sample(data, cols[0], args.mu, args.output)
    elif len(cols) == 2:
        if args.paired:
            _paired(data, cols[0], cols[1], args.output)
        else:
            _independent(data, cols[0], cols[1], args.equal_var, args.output)
    else:
        print("Error: specify 1 or 2 columns")


def _one_sample(data, col, mu, output):
    vals = col_to_float(data, col)
    n = len(vals)
    if n < 2:
        print("Error: need at least 2 values")
        return
    m = mean(vals)
    s = var_s(vals)
    se = (s / n) ** 0.5
    t = (m - mu) / se if se > 0 else 0
    df = n - 1
    p = t_pvalue(t, df, two_sided=True)
    t_crit = _t_inv_95(df)
    ci_lo = m - t_crit * se
    ci_hi = m + t_crit * se
    write_output([
        f"test\tone_sample",
        f"n\t{n}",
        f"mean\t{m}",
        f"mu\t{mu}",
        f"t\t{t}",
        f"df\t{df}",
        f"p\t{p}",
        f"ci_95_lo\t{ci_lo}",
        f"ci_95_hi\t{ci_hi}",
    ], output)


def _independent(data, col1, col2, equal_var, output):
    x, y = col_to_float_pair(data, col1, col2)
    n1, n2 = len(x), len(y)
    if n1 < 2 or n2 < 2:
        print("Error: need at least 2 values per group")
        return
    m1, m2 = mean(x), mean(y)
    v1, v2 = var_s(x), var_s(y)
    if equal_var:
        sp2 = ((n1 - 1) * v1 + (n2 - 1) * v2) / (n1 + n2 - 2)
        se = math.sqrt(sp2 * (1 / n1 + 1 / n2))
        df = n1 + n2 - 2
    else:
        se = math.sqrt(v1 / n1 + v2 / n2)
        num = (v1 / n1 + v2 / n2) ** 2
        den = (v1 / n1) ** 2 / (n1 - 1) + (v2 / n2) ** 2 / (n2 - 1)
        df = num / den if den > 0 else 0
    t = (m1 - m2) / se if se > 0 else 0
    p = t_pvalue(t, df, two_sided=True)
    write_output([
        f"test\t{'welch' if not equal_var else 'independent'}",
        f"n1\t{n1}",
        f"mean1\t{m1}",
        f"var1\t{v1}",
        f"n2\t{n2}",
        f"mean2\t{m2}",
        f"var2\t{v2}",
        f"t\t{t}",
        f"df\t{df}",
        f"p\t{p}",
    ], output)


def _paired(data, col1, col2, output):
    x, y = col_to_float_pair(data, col1, col2)
    if len(x) < 2:
        print("Error: need at least 2 pairs")
        return
    diffs = [a - b for a, b in zip(x, y)]
    n = len(diffs)
    m = mean(diffs)
    s = math.sqrt(var_s(diffs)) if len(diffs) > 1 else 0
    se = s / math.sqrt(n) if n > 0 else 0
    t = m / se if se > 0 else 0
    df = n - 1
    p = t_pvalue(t, df, two_sided=True)
    write_output([
        f"test\tpaired",
        f"n\t{n}",
        f"mean_diff\t{m}",
        f"sd_diff\t{s}",
        f"t\t{t}",
        f"df\t{df}",
        f"p\t{p}",
    ], output)


def _t_inv_95(df):
    if df <= 0:
        return 1.96
    if df > 200:
        return 1.96
    z = 1.96
    a = (z ** 3 + z) / 4
    b = (5 * z ** 5 + 16 * z ** 3 + 3 * z) / 96
    return z + a / df + b / (df ** 2)
