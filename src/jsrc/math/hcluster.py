import math
from jsrc.math.core import parse_columns, write_output


def cmd(args):
    headers, data = parse_columns(args.input, args.sep)
    if not data:
        print("Error: no data")
        return
    feature_cols = [h for h in headers if _is_numeric_col(data, h)]
    if len(feature_cols) < 1:
        print("Error: no numeric columns")
        return
    X = []
    labels = []
    for row in data:
        vec = []
        ok = True
        for col in feature_cols:
            v = row.get(col, "").strip()
            if v == "":
                ok = False
                break
            vec.append(float(v))
        if ok:
            X.append(vec)
            labels.append(str(row.get(headers[0], "")))
    if len(X) < 2:
        print("Error: need at least 2 points")
        return
    clusters = _hcluster(X, args.method)
    lines = [f"linkage\t{args.method}", f"n\t{len(X)}"]
    if args.k:
        assignments = _cut_tree(clusters, len(X), args.k)
        for i, (label, cl) in enumerate(zip(labels, assignments)):
            lines.append(f"{label}\tcluster_{cl}")
    else:
        lines.append("")
        for step in clusters:
            lines.append(f"merge\t{step[0]}\t{step[1]}\tdist\t{step[2]:.6g}")
    write_output(lines, args.output)


def _is_numeric_col(data, col):
    count = 0
    for row in data[:50]:
        v = row.get(col, "").strip()
        if v == "":
            continue
        try:
            float(v)
            count += 1
            if count >= 3:
                return True
        except ValueError:
            pass
    return count >= 3


def _euclidean(a, b):
    return math.sqrt(sum((x - y) ** 2 for x, y in zip(a, b)))


def _hcluster(X, method):
    n = len(X)
    dist = [[0.0] * n for _ in range(n)]
    for i in range(n):
        for j in range(i + 1, n):
            d = _euclidean(X[i], X[j])
            dist[i][j] = d
            dist[j][i] = d
    clusters = list(range(n))
    sizes = [1] * n
    merge_history = []
    next_id = n
    active = set(range(n))
    while len(active) > 1:
        min_dist = float("inf")
        pair = None
        for i in active:
            for j in active:
                if i < j and dist[i][j] < min_dist:
                    min_dist = dist[i][j]
                    pair = (i, j)
        if pair is None:
            break
        i, j = pair
        merge_history.append((clusters[i], clusters[j], min_dist))
        new_size = sizes[i] + sizes[j]
        new_cluster_id = next_id
        next_id += 1
        for k in active:
            if k == i or k == j:
                continue
            d_ik = dist[i][k]
            d_jk = dist[j][k]
            d_ij = min_dist
            si, sj, sk = sizes[i], sizes[j], sizes[k]
            if method == "single":
                d_new = min(d_ik, d_jk)
            elif method == "complete":
                d_new = max(d_ik, d_jk)
            else:
                d_new = (si * d_ik + sj * d_jk) / (si + sj)
            dist[i][k] = d_new
            dist[k][i] = d_new
        sizes[i] = new_size
        clusters[i] = new_cluster_id
        active.remove(j)
    return merge_history


def _cut_tree(merge_history, n, k):
    if k >= n:
        return list(range(n))
    sorted_merges = sorted(merge_history, key=lambda x: x[2])
    cuts = n - k
    parent = list(range(n))
    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x
    def union(x, y):
        px, py = find(x), find(y)
        if px != py:
            parent[py] = px
    for m in sorted_merges[:cuts]:
        union(m[0] if m[0] < n else 0, m[1] if m[1] < n else 0)
    cluster_map = {}
    next_cl = 0
    for i in range(n):
        p = find(i)
        if p not in cluster_map:
            cluster_map[p] = next_cl
            next_cl += 1
        yield cluster_map[p]
