from jsrc.math.core import (
    parse_columns, write_output, chi2_pvalue, chi2_cdf,
)


def cmd(args):
    if args.observed and args.col:
        print("Error: specify either --observed/--expected or --col, not both")
        return
    if args.observed:
        _goodness_of_fit(args.observed, args.expected, args.output)
    elif args.col:
        _independence(args.input, args.sep, args.col[0], args.col[1], args.output)
    else:
        print("Error: specify --observed or --col")


def _goodness_of_fit(observed, expected, output):
    n = len(observed)
    if expected:
        if len(expected) != n:
            print(f"Error: observed ({n}) and expected ({len(expected)}) length differ")
            return
    else:
        total = sum(observed)
        expected = [total / n] * n
    total_obs = sum(observed)
    total_exp = sum(expected)
    if total_exp > 0 and abs(total_exp - total_obs) > 1e-9:
        scale = total_obs / total_exp
        expected = [e * scale for e in expected]
    chi2 = sum((o - e) ** 2 / e for o, e in zip(observed, expected) if e > 0)
    df = n - 1
    p = chi2_pvalue(chi2, df)
    write_output([
        f"test\tgoodness_of_fit",
        f"chi2\t{chi2}",
        f"df\t{df}",
        f"p\t{p}",
    ], output)


def _independence(filepath, sep, col1, col2, output):
    headers, data = parse_columns(filepath, sep)
    if not data:
        print("Error: no data")
        return
    if col1.isdigit():
        c1 = int(col1)
        col1 = list(data[0].keys())[c1] if data else col1
    if col2.isdigit():
        c2 = int(col2)
        col2 = list(data[0].keys())[c2] if data else col2
    table = {}
    row_levels = set()
    col_levels = set()
    for row in data:
        r = row.get(col1, "").strip()
        c = row.get(col2, "").strip()
        if r == "" or c == "":
            continue
        table[(r, c)] = table.get((r, c), 0) + 1
        row_levels.add(r)
        col_levels.add(c)
    row_levels = sorted(row_levels)
    col_levels = sorted(col_levels)
    if len(row_levels) < 2 or len(col_levels) < 2:
        print("Error: need at least 2 levels in each dimension")
        return
    row_sums = {r: sum(table.get((r, c), 0) for c in col_levels) for r in row_levels}
    col_sums = {c: sum(table.get((r, c), 0) for r in row_levels) for c in col_levels}
    total = sum(row_sums.values())
    if total == 0:
        print("Error: empty table")
        return
    chi2 = 0.0
    for r in row_levels:
        for c in col_levels:
            observed = table.get((r, c), 0)
            expected = row_sums[r] * col_sums[c] / total
            if expected > 0:
                chi2 += (observed - expected) ** 2 / expected
    df = (len(row_levels) - 1) * (len(col_levels) - 1)
    p = chi2_pvalue(chi2, df)
    write_output([
        f"test\tindependence",
        f"rows\t{len(row_levels)}",
        f"cols\t{len(col_levels)}",
        f"chi2\t{chi2}",
        f"df\t{df}",
        f"p\t{p}",
    ], output)
