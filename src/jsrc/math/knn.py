import math
from jsrc.math.core import parse_columns, write_output


def cmd(args):
    train_headers, train_data = parse_columns(args.train)
    test_headers, test_data = parse_columns(args.test)
    if not train_data or not test_data:
        print("Error: empty training or test data")
        return
    feature_cols = [h for h in train_headers if h != args.target_col and _is_numeric_col(train_data, h)]
    if not feature_cols:
        print("Error: no numeric feature columns")
        return
    X_train, y_train = _parse_xy(train_data, feature_cols, args.target_col)
    if len(X_train) < args.k:
        print(f"Warning: training set ({len(X_train)}) smaller than k ({args.k})")
        args.k = max(1, len(X_train))
    X_test, _ = _parse_xy(test_data, feature_cols, args.target_col)
    if not X_test:
        print("Error: no valid test samples")
        return
    predictions = []
    for xt in X_test:
        pred = _predict(X_train, y_train, xt, args.k, args.regression)
        predictions.append(pred)
    output_lines = ["prediction"]
    output_lines.extend(str(p) for p in predictions)
    write_output(output_lines, args.output)


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


def _parse_xy(data, feature_cols, target_col):
    X, y = [], []
    for row in data:
        vec = []
        ok = True
        for f in feature_cols:
            v = row.get(f, "").strip()
            if v == "":
                ok = False
                break
            vec.append(float(v))
        if not ok:
            continue
        t = row.get(target_col, "").strip()
        if t == "":
            continue
        try:
            yt = float(t)
        except ValueError:
            yt = t
        X.append(vec)
        y.append(yt)
    return X, y


def _euclidean(a, b):
    return math.sqrt(sum((x - y) ** 2 for x, y in zip(a, b)))


def _predict(X_train, y_train, x_test, k, regression):
    dists = [(_euclidean(x_test, xt), yt) for xt, yt in zip(X_train, y_train)]
    dists.sort(key=lambda d: d[0])
    neighbors = dists[:k]
    if regression:
        vals = [n[1] for n in neighbors if isinstance(n[1], (int, float))]
        return sum(vals) / len(vals) if vals else 0.0
    else:
        from collections import Counter
        labels = [str(n[1]) for n in neighbors]
        counts = Counter(labels)
        return counts.most_common(1)[0][0]
