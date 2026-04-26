import math
from jsrc.math.core import (
    parse_columns, col_to_float_pair, write_output, mean,
    t_pvalue, f_pvalue, t_cdf,
)


def cmd(args):
    headers, data = parse_columns(args.input, args.sep)
    if not data:
        print("Error: no data")
        return
    x, y = col_to_float_pair(data, args.col[0], args.col[1])
    if len(x) < 3:
        print("Error: need at least 3 points")
        return
    degree = max(1, args.degree)
    if degree == 1:
        _simple_linear(x, y, args.output)
    else:
        _polynomial(x, y, degree, args.output)


def _simple_linear(x, y, output):
    n = len(x)
    mx = mean(x)
    my = mean(y)
    num = sum((a - mx) * (b - my) for a, b in zip(x, y))
    den = sum((a - mx) ** 2 for a in x)
    den2 = sum((b - my) ** 2 for b in y)
    if den == 0:
        print("Error: constant X")
        return
    slope = num / den
    intercept = my - slope * mx
    residuals = [b - (intercept + slope * a) for a, b in zip(x, y)]
    ss_res = sum(r ** 2 for r in residuals)
    ss_tot = den2
    r2 = 1.0 - ss_res / ss_tot if ss_tot != 0 else 0.0
    adj_r2 = 1.0 - (ss_res / (n - 2)) / (ss_tot / (n - 1)) if ss_tot != 0 else 0.0
    se_reg = math.sqrt(ss_res / (n - 2))
    se_slope = se_reg / math.sqrt(den) if den > 0 else 0
    se_intercept = se_reg * math.sqrt(1.0 / n + mx * mx / den) if den > 0 else 0
    if se_slope > 0:
        t_slope = slope / se_slope
        p_slope = t_pvalue(t_slope, n - 2)
    else:
        t_slope = float("inf") if slope != 0 else 0
        p_slope = 0.0 if slope != 0 else 1.0
    if se_intercept > 0:
        t_intercept = intercept / se_intercept
        p_intercept = t_pvalue(t_intercept, n - 2)
    else:
        t_intercept = float("inf") if intercept != 0 else 0
        p_intercept = 0.0 if intercept != 0 else 1.0
    ss_reg = ss_tot - ss_res
    if ss_res > 0 and n > 2:
        f_stat = (ss_reg / 1) / (ss_res / (n - 2))
        p_f = f_pvalue(f_stat, 1, n - 2)
    else:
        f_stat = float("inf") if ss_reg > 0 else 0
        p_f = 0.0 if ss_reg > 0 else 1.0
    write_output([
        f"n\t{n}",
        f"slope\t{slope}",
        f"intercept\t{intercept}",
        f"r2\t{r2}",
        f"adj_r2\t{adj_r2}",
        f"se_slope\t{se_slope}",
        f"se_intercept\t{se_intercept}",
        f"t_slope\t{t_slope}",
        f"p_slope\t{p_slope}",
        f"t_intercept\t{t_intercept}",
        f"p_intercept\t{p_intercept}",
        f"f\t{f_stat}",
        f"p_f\t{p_f}",
        f"df1\t1",
        f"df2\t{n - 2}",
        f"se_regression\t{se_reg}",
    ], output)


def _polynomial(x, y, degree, output):
    n = len(x)
    m = []
    for xi in x:
        row = [1.0]
        for d in range(1, degree + 1):
            row.append(xi ** d)
        m.append(row)
    p = degree + 1
    if n <= p:
        print(f"Error: need more points than parameters ({n} <= {p})")
        return
    xtx = [[sum(m[k][i] * m[k][j] for k in range(n)) for j in range(p)] for i in range(p)]
    xty = [sum(m[k][i] * y[k] for k in range(n)) for i in range(p)]
    beta = _cholesky_solve(xtx, xty, p)
    if beta is None:
        print("Error: singular matrix")
        return
    residuals = [b - sum(beta[i] * m[k][i] for i in range(p)) for k, b in enumerate(y)]
    ss_res = sum(r ** 2 for r in residuals)
    my = mean(y)
    ss_tot = sum((b - my) ** 2 for b in y)
    r2 = 1.0 - ss_res / ss_tot if ss_tot != 0 else 0.0
    adj_r2 = 1.0 - (ss_res / (n - p)) / (ss_tot / (n - 1)) if ss_tot != 0 else 0.0
    se_reg = math.sqrt(ss_res / (n - p))
    cov = _cholesky_inverse(xtx, p)
    lines = [
        f"n\t{n}",
        f"degree\t{degree}",
        f"r2\t{r2}",
        f"adj_r2\t{adj_r2}",
        f"se_regression\t{se_reg}",
        f"f_stat\t{(ss_tot - ss_res) / p / se_reg ** 2 if se_reg > 0 else 0}",
        f"p_f\t{f_pvalue((ss_tot - ss_res) / p / se_reg ** 2 if se_reg > 0 else 0, p, n - p)}",
        f"df1\t{p}",
        f"df2\t{n - p}",
    ]
    for i in range(p):
        se = math.sqrt(cov[i][i]) * se_reg if cov else 0
        t = beta[i] / se if se > 0 else 0
        pv = t_pvalue(t, n - p)
        lines.append(f"coeff_{i}\t{beta[i]}\tse_{i}\t{se}\tt_{i}\t{t}\tp_{i}\t{pv}")
    write_output(lines, output)


def _cholesky_solve(a, b, n):
    L = [[0.0] * n for _ in range(n)]
    for i in range(n):
        for j in range(i + 1):
            s = sum(L[i][k] * L[j][k] for k in range(j))
            if i == j:
                d = a[i][i] - s
                if d <= 1e-12:
                    return None
                L[i][j] = math.sqrt(d)
            else:
                L[i][j] = (a[i][j] - s) / L[j][j]
    y = [0.0] * n
    for i in range(n):
        y[i] = (b[i] - sum(L[i][k] * y[k] for k in range(i))) / L[i][i]
    x = [0.0] * n
    for i in range(n - 1, -1, -1):
        x[i] = (y[i] - sum(L[k][i] * x[k] for k in range(i + 1, n))) / L[i][i]
    return x


def _cholesky_inverse(a, n):
    L = [[0.0] * n for _ in range(n)]
    for i in range(n):
        for j in range(i + 1):
            s = sum(L[i][k] * L[j][k] for k in range(j))
            if i == j:
                d = a[i][i] - s
                if d <= 1e-12:
                    return None
                L[i][j] = math.sqrt(d)
            else:
                L[i][j] = (a[i][j] - s) / L[j][j]
    Linv = [[0.0] * n for _ in range(n)]
    for i in range(n):
        Linv[i][i] = 1.0 / L[i][i]
        for j in range(i - 1, -1, -1):
            s = sum(L[i][k] * Linv[k][j] for k in range(j, i))
            Linv[i][j] = -s / L[i][i]
    inv = [[0.0] * n for _ in range(n)]
    for i in range(n):
        for j in range(n):
            inv[i][j] = sum(Linv[k][i] * Linv[k][j] for k in range(max(i, j), n))
    return inv
