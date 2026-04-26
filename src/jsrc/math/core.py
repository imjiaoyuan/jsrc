import csv
import math

_LOG_2PI = math.log(2 * math.pi)
_SQRT2 = math.sqrt(2)


def _log_gamma(x):
    return math.lgamma(x)


def _log_beta(a, b):
    return math.lgamma(a) + math.lgamma(b) - math.lgamma(a + b)


def _regularized_incomplete_beta(a, b, x):
    if x < 0 or x > 1:
        return 0.0
    if x == 0 or x == 1:
        return float(x)
    lbeta = _log_beta(a, b)
    front = math.exp(a * math.log(x) + b * math.log1p(-x) - lbeta) / a
    qab = a + b
    qap = a + 1.0
    qam = a - 1.0
    c = 1.0
    d = 1.0 - qab * x / qap
    if abs(d) < 1e-30:
        d = 1e-30
    d = 1.0 / d
    h = d
    eps = 3e-12
    max_iter = 300
    for m in range(1, max_iter + 1):
        m2 = 2 * m
        aa = m * (b - m) * x / ((qam + m2) * (a + m2))
        d = 1.0 + aa * d
        if abs(d) < 1e-30:
            d = 1e-30
        c = 1.0 + aa / c
        if abs(c) < 1e-30:
            c = 1e-30
        d = 1.0 / d
        delta = d * c
        h *= delta
        aa = -(a + m) * (qab + m) * x / ((a + m2) * (qap + m2))
        d = 1.0 + aa * d
        if abs(d) < 1e-30:
            d = 1e-30
        c = 1.0 + aa / c
        if abs(c) < 1e-30:
            c = 1e-30
        d = 1.0 / d
        delta = d * c
        h *= delta
        if abs(delta - 1.0) < eps:
            break
    return front * h


def _regularized_incomplete_gamma(s, x):
    if x < 0:
        return 0.0
    if x == 0 or x < 1e-30:
        return 0.0
    if s <= 0:
        return 1.0
    g = math.lgamma(s)
    result = 1.0 / s
    term = 1.0 / s
    for k in range(1, 500):
        term *= x / (s + k)
        result += term
        if abs(term) < 1e-14:
            break
    result = math.exp(s * math.log(x) - x - g) * result
    return max(0.0, min(1.0, result))


def normal_cdf(z):
    return 0.5 * (1.0 + math.erf(z / _SQRT2))


def normal_pdf(z):
    return math.exp(-0.5 * z * z) / math.sqrt(2 * math.pi)


def t_cdf(t, df):
    if df <= 0:
        return float("nan")
    if t >= 0:
        return 1.0 - 0.5 * _regularized_incomplete_beta(df / 2, 0.5, df / (df + t * t))
    else:
        return 0.5 * _regularized_incomplete_beta(df / 2, 0.5, df / (df + t * t))


def t_pvalue(t, df, two_sided=True):
    p = t_cdf(-abs(t), df)
    return 2.0 * p if two_sided else p


def f_cdf(f, df1, df2):
    if f <= 0:
        return 0.0
    if df2 <= 0 or df1 <= 0:
        return float("nan")
    x = df1 * f / (df1 * f + df2)
    return _regularized_incomplete_beta(df1 / 2, df2 / 2, x)


def f_pvalue(f, df1, df2):
    return 1.0 - f_cdf(f, df1, df2)


def chi2_cdf(x, df):
    if x <= 0:
        return 0.0
    return _regularized_incomplete_gamma(df / 2, x / 2)


def chi2_pvalue(x, df):
    return 1.0 - chi2_cdf(x, df)


def normal_quantile(p):
    if p <= 0:
        return -float("inf")
    if p >= 1:
        return float("inf")
    if p == 0.5:
        return 0.0
    a = (-2 * math.log(p if p < 0.5 else 1 - p)) ** 0.5
    num = (((2.3212128 * a + 4.85014136) * a - 2.29796479) * a - 2.78718933)
    den = ((1.6370678 * a + 3.54388947) * a + 1.0)
    q = a - num / den
    return -q if p < 0.5 else q


def betai(a, b, x):
    return _regularized_incomplete_beta(a, b, x)


def gammainc(s, x):
    return _regularized_incomplete_gamma(s, x)


def parse_columns(filepath, sep=None):
    with open(filepath, "r", encoding="utf-8") as f:
        reader = csv.reader(f, delimiter=sep or "\t")
        rows = list(reader)
    if not rows:
        return [], []
    headers = rows[0]
    data = []
    for row in rows[1:]:
        if not row or all(c.strip() == "" for c in row):
            continue
        if len(row) < len(headers):
            row = row + [""] * (len(headers) - len(row))
        data.append(dict(zip(headers, row)))
    return headers, data


def col_to_float(data, col):
    if isinstance(col, int) or col.isdigit():
        idx = int(col)
        col_name = list(data[0].keys())[idx] if data else col
    else:
        col_name = col
    vals = []
    for row in data:
        v = row.get(col_name, "").strip()
        if v == "":
            continue
        try:
            vals.append(float(v))
        except ValueError:
            continue
    return vals


def col_to_float_pair(data, col1, col2):
    if isinstance(col1, int) or col1.isdigit():
        idx1 = int(col1)
        c1 = list(data[0].keys())[idx1] if data else col1
    else:
        c1 = col1
    if isinstance(col2, int) or col2.isdigit():
        idx2 = int(col2)
        c2 = list(data[0].keys())[idx2] if data else col2
    else:
        c2 = col2
    x_vals, y_vals = [], []
    for row in data:
        v1 = row.get(c1, "").strip()
        v2 = row.get(c2, "").strip()
        if v1 == "" or v2 == "":
            continue
        try:
            x_vals.append(float(v1))
            y_vals.append(float(v2))
        except ValueError:
            continue
    return x_vals, y_vals


def col_to_float_grouped(data, col_group, col_value):
    if isinstance(col_group, int) or col_group.isdigit():
        gi = int(col_group)
        cg = list(data[0].keys())[gi] if data else col_group
    else:
        cg = col_group
    if isinstance(col_value, int) or col_value.isdigit():
        vi = int(col_value)
        cv = list(data[0].keys())[vi] if data else col_value
    else:
        cv = col_value
    groups = {}
    for row in data:
        g = row.get(cg, "").strip()
        v = row.get(cv, "").strip()
        if g == "" or v == "":
            continue
        try:
            groups.setdefault(g, []).append(float(v))
        except ValueError:
            continue
    return groups


def write_output(data_lines, output_path=None):
    text = "\n".join(data_lines)
    if output_path:
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(text + "\n")
    else:
        print(text)


def write_table(headers, rows, output_path=None):
    lines = ["\t".join(headers)]
    for row in rows:
        lines.append("\t".join(str(v) for v in row))
    write_output(lines, output_path)


def mean(vals):
    return sum(vals) / len(vals)


def var_s(vals):
    m = mean(vals)
    return sum((x - m) ** 2 for x in vals) / (len(vals) - 1)


def sd(vals):
    return math.sqrt(var_s(vals))
