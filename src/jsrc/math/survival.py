import math
from jsrc.math.core import parse_columns, col_to_float, write_output, chi2_pvalue


def cmd(args):
    headers, data = parse_columns(args.input, args.sep)
    if not data:
        print("Error: no data")
        return
    time = col_to_float(data, args.time_col)
    event = col_to_float(data, args.event_col)
    if len(time) < 2:
        print("Error: need at least 2 observations")
        return
    if args.group_col:
        groups = {}
        for row in data:
            g = row.get(args.group_col, "").strip()
            t = row.get(args.time_col, "").strip()
            e = row.get(args.event_col, "").strip()
            if t == "" or e == "" or g == "":
                continue
            try:
                groups.setdefault(g, []).append((float(t), float(e)))
            except ValueError:
                continue
        _logrank(groups, args.output)
    else:
        pairs = sorted(zip(time, event), key=lambda x: x[0])
        _kaplan_meier(pairs, args.output)


def _kaplan_meier(pairs, output):
    n_total = len(pairs)
    at_risk = n_total
    lines = ["time\tn_at_risk\tn_event\tsurvival"]
    surv = 1.0
    i = 0
    while i < n_total:
        t = pairs[i][0]
        n_events = 0
        j = i
        while j < n_total and pairs[j][0] == t:
            if pairs[j][1] >= 0.5:
                n_events += 1
            j += 1
        if n_events > 0 and at_risk > 0:
            surv *= (at_risk - n_events) / at_risk
        lines.append(f"{t}\t{at_risk}\t{n_events}\t{surv:.6g}")
        at_risk -= (j - i)
        i = j
    write_output(lines, output)


def _logrank(groups, output):
    if len(groups) < 2:
        print("Error: need at least 2 groups for Log-rank test")
        return
    all_times = set()
    for g, pairs in groups.items():
        pairs.sort(key=lambda x: x[0])
        for t, e in pairs:
            all_times.add(t)
    all_times = sorted(all_times)
    o_minus_e_sum = 0.0
    var_sum = 0.0
    group_names = sorted(groups.keys())
    for t in all_times:
        n_risk = {}
        n_events = {}
        total_risk = 0
        total_events = 0
        for g in group_names:
            n_risk[g] = sum(1 for pt in groups[g] if pt[0] >= t)
            n_events[g] = sum(1 for pt in groups[g] if pt[0] == t and pt[1] >= 0.5)
            total_risk += n_risk[g]
            total_events += n_events[g]
        if total_risk <= 1 or total_events == 0:
            continue
        g0 = group_names[0]
        if n_risk[g0] > 0:
            expected = n_risk[g0] * total_events / total_risk
            o_minus_e = n_events[g0] - expected
            o_minus_e_sum += o_minus_e
            var = (total_risk - total_events) * total_events * n_risk[g0] * (total_risk - n_risk[g0])
            var /= (total_risk ** 2 * (total_risk - 1)) if total_risk > 1 else 1
            var_sum += var
    chi2 = o_minus_e_sum ** 2 / var_sum if var_sum > 0 else 0
    df = len(groups) - 1
    p = chi2_pvalue(chi2, df)
    write_output([
        f"test\tlog_rank",
        f"groups\t{len(groups)}",
        f"chi2\t{chi2}",
        f"df\t{df}",
        f"p\t{p}",
    ], output)
