import math
import random
from jsrc.math.core import parse_columns, write_output


def cmd(args):
    headers, data = parse_columns(args.input, args.sep)
    if not data:
        print("Error: no data")
        return
    feature_cols = [h for h in headers if _is_numeric_col(data, h)]
    if len(feature_cols) < 1:
        print("Error: no numeric columns found")
        return
    X = []
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
    if len(X) < args.k:
        print(f"Error: fewer points ({len(X)}) than clusters ({args.k})")
        return
    clusters, centroids, inertia = _kmeans(X, args.k, args.max_iter)
    lines = [f"k\t{args.k}", f"n\t{len(X)}", f"features\t{len(feature_cols)}",
             f"inertia\t{inertia}", f"iterations\t{args.max_iter}", ""]
    lines.append("cluster\t" + "\t".join(feature_cols))
    for i, (cl, vec) in enumerate(zip(clusters, X)):
        lines.append(f"{cl}\t" + "\t".join(f"{v:.6g}" for v in vec))
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


def _kmeans(X, k, max_iter=100):
    n = len(X)
    dim = len(X[0])
    centroids = [X[random.randint(0, n - 1)]]
    for _ in range(1, k):
        dists = [min(_euclidean(x, c) ** 2 for c in centroids) for x in X]
        total = sum(dists)
        if total == 0:
            centroids.append(X[random.randint(0, n - 1)])
        else:
            r = random.random() * total
            cum = 0
            for i, d in enumerate(dists):
                cum += d
                if cum >= r:
                    centroids.append(X[i])
                    break
    clusters = [0] * n
    for _ in range(max_iter):
        changed = False
        for i, x in enumerate(X):
            best = min(range(k), key=lambda j: _euclidean(x, centroids[j]))
            if clusters[i] != best:
                changed = True
                clusters[i] = best
        if not changed:
            break
        new_centroids = []
        for j in range(k):
            members = [X[i] for i in range(n) if clusters[i] == j]
            if members:
                new_centroids.append([sum(vals) / len(members) for vals in zip(*members)])
            else:
                new_centroids.append(centroids[j][:])
        centroids = new_centroids
    inertia = sum(_euclidean(X[i], centroids[clusters[i]]) ** 2 for i in range(n))
    return clusters, centroids, inertia


def _euclidean(a, b):
    return math.sqrt(sum((x - y) ** 2 for x, y in zip(a, b)))
