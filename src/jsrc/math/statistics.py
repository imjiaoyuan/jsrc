import math
from jsrc.math.core import mean, var_s, sd as _sd
from jsrc.math.core import parse_columns, col_to_float, write_output


def cmd(args):
    headers, data = parse_columns(args.input, args.sep)
    if not data:
        print("Error: no data")
        return
    vals = col_to_float(data, args.col)
    if len(vals) < 2:
        print("Error: need at least 2 values")
        return
    n = len(vals)
    m = mean(vals)
    med = _median(vals)
    v = var_s(vals)
    s = _sd(vals)
    se = s / math.sqrt(n)
    mn = min(vals)
    mx = max(vals)
    rng = mx - mn
    q1 = _percentile(vals, 25)
    q3 = _percentile(vals, 75)
    iqr = q3 - q1
    cv = (s / m) * 100 if m != 0 else 0
    gm = _geomean(vals)
    hm = _harmean(vals)
    sk = _skewness(vals, m, s, n)
    ku = _kurtosis(vals, m, s, n)
    lines = [
        f"n\t{n}",
        f"min\t{mn}",
        f"max\t{mx}",
        f"range\t{rng}",
        f"mean\t{m}",
        f"median\t{med}",
        f"mode\t{_mode(vals)}",
        f"q1\t{q1}",
        f"q3\t{q3}",
        f"iqr\t{iqr}",
        f"var\t{v}",
        f"sd\t{s}",
        f"se\t{se}",
        f"cv%\t{cv}",
        f"skewness\t{sk}",
        f"kurtosis\t{ku}",
        f"geometric_mean\t{gm}",
        f"harmonic_mean\t{hm}",
    ]
    for p in [1, 5, 10, 25, 50, 75, 90, 95, 99]:
        lines.append(f"p{p}\t{_percentile(vals, p)}")
    write_output(lines, args.output)


def _median(vals):
    s = sorted(vals)
    n = len(s)
    if n % 2 == 1:
        return s[n // 2]
    return (s[n // 2 - 1] + s[n // 2]) / 2


def _mode(vals):
    freq = {}
    for v in vals:
        freq[v] = freq.get(v, 0) + 1
    max_freq = max(freq.values())
    candidates = [k for k, v in freq.items() if v == max_freq]
    return min(candidates) if len(candidates) == 1 else candidates[0]


def _percentile(vals, p):
    s = sorted(vals)
    n = len(s)
    k = (p / 100) * (n - 1)
    f = math.floor(k)
    c = math.ceil(k)
    if f == c:
        return s[f]
    d0 = s[f] * (c - k)
    d1 = s[c] * (k - f)
    return d0 + d1


def _geomean(vals):
    log_sum = sum(math.log(v) for v in vals if v > 0)
    pos = sum(1 for v in vals if v > 0)
    return math.exp(log_sum / pos) if pos > 0 else float("nan")


def _harmean(vals):
    n = len(vals)
    inv_sum = sum(1.0 / v for v in vals if v != 0)
    return n / inv_sum if inv_sum != 0 else float("nan")


def _skewness(vals, m, s, n):
    if s == 0:
        return 0.0
    return (n / ((n - 1) * (n - 2))) * sum(((x - m) / s) ** 3 for x in vals)


def _kurtosis(vals, m, s, n):
    if s == 0:
        return 0.0
    num = sum((x - m) ** 4 for x in vals) / n
    den = (s ** 4)
    k = num / den if den != 0 else 0
    return k - 3.0
