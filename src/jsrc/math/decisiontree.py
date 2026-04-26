import math
from collections import Counter
from jsrc.math.core import parse_columns, write_output, mean, var_s


def cmd(args):
    train_headers, train_data = parse_columns(args.train)
    test_headers, test_data = parse_columns(args.test)
    if not train_data:
        print("Error: empty training data")
        return
    feature_cols = [h for h in train_headers if h != args.target_col and _is_numeric_col(train_data, h)]
    if not feature_cols:
        print("Error: no numeric feature columns")
        return
    X, y = _parse_xy(train_data, feature_cols, args.target_col)
    if not X:
        print("Error: no valid training samples")
        return
    tree = _build_tree(X, y, args.max_depth, args.min_samples, args.regression)
    if args.print_tree:
        _print_tree(tree, feature_cols)
    X_test, _ = _parse_xy(test_data, feature_cols, args.target_col)
    if not X_test:
        print("Error: no valid test samples")
        return
    output_lines = ["prediction"]
    for xt in X_test:
        pred = _predict_one(tree, xt)
        output_lines.append(str(pred))
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


def _build_tree(X, y, max_depth, min_samples, regression):
    n = len(X)
    n_features = len(X[0])
    if n <= min_samples or max_depth == 0 or _is_pure(y):
        return _make_leaf(y, regression)
    best_feat, best_thresh = _find_split(X, y, regression, n_features)
    if best_feat is None:
        return _make_leaf(y, regression)
    left_X, left_y, right_X, right_y = _split(X, y, best_feat, best_thresh)
    if not left_y or not right_y:
        return _make_leaf(y, regression)
    return {
        "feat": best_feat,
        "thresh": best_thresh,
        "left": _build_tree(left_X, left_y, max_depth - 1, min_samples, regression),
        "right": _build_tree(right_X, right_y, max_depth - 1, min_samples, regression),
    }


def _is_pure(y):
    if not y:
        return True
    if isinstance(y[0], (int, float)):
        return len(set(y)) == 1
    return len(set(y)) == 1


def _make_leaf(y, regression):
    if regression:
        return {"value": mean(y) if y else 0}
    else:
        return {"value": Counter(y).most_common(1)[0][0]}


def _find_split(X, y, regression, n_features):
    best_gain = -float("inf")
    best_feat = None
    best_thresh = None
    current_imp = _impurity(y, regression)
    for f in range(n_features):
        vals = sorted(set(X[i][f] for i in range(len(X))))
        for i in range(len(vals) - 1):
            thresh = (vals[i] + vals[i + 1]) / 2
            left_y, right_y = [], []
            for j in range(len(X)):
                if X[j][f] <= thresh:
                    left_y.append(y[j])
                else:
                    right_y.append(y[j])
            if not left_y or not right_y:
                continue
            gain = current_imp - _weighted_impurity(left_y, right_y, regression)
            if gain > best_gain:
                best_gain = gain
                best_feat = f
                best_thresh = thresh
    if best_gain < 0:
        return None, None
    return best_feat, best_thresh


def _impurity(y, regression):
    if not y:
        return 0
    if regression:
        if len(y) < 2:
            return 0
        return var_s(y) * (len(y) - 1) / len(y)
    else:
        n = len(y)
        counts = Counter(y)
        return 1.0 - sum((c / n) ** 2 for c in counts.values())


def _weighted_impurity(left_y, right_y, regression):
    n = len(left_y) + len(right_y)
    return (len(left_y) / n) * _impurity(left_y, regression) + (len(right_y) / n) * _impurity(right_y, regression)


def _split(X, y, feat, thresh):
    left_X, left_y, right_X, right_y = [], [], [], []
    for i in range(len(X)):
        if X[i][feat] <= thresh:
            left_X.append(X[i])
            left_y.append(y[i])
        else:
            right_X.append(X[i])
            right_y.append(y[i])
    return left_X, left_y, right_X, right_y


def _predict_one(tree, x):
    if "value" in tree:
        return tree["value"]
    if x[tree["feat"]] <= tree["thresh"]:
        return _predict_one(tree["left"], x)
    else:
        return _predict_one(tree["right"], x)


def _print_tree(tree, feature_cols, depth=0):
    prefix = "  " * depth
    if "value" in tree:
        print(f"{prefix}-> {tree['value']}")
    else:
        feat_name = feature_cols[tree["feat"]] if tree["feat"] < len(feature_cols) else f"feat{tree['feat']}"
        print(f"{prefix}{feat_name} <= {tree['thresh']:.4g}:")
        _print_tree(tree["left"], feature_cols, depth + 1)
        print(f"{prefix}{feat_name} > {tree['thresh']:.4g}:")
        _print_tree(tree["right"], feature_cols, depth + 1)
