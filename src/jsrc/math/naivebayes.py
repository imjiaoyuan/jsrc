import math
from collections import Counter
from jsrc.math.core import parse_columns, write_output, normal_pdf, mean, var_s


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
    X_train, y_train = _parse_xy(train_data, feature_cols, args.target_col)
    if not X_train:
        print("Error: no valid training samples")
        return
    classes, class_priors, means_dict, vars_dict = _fit(X_train, y_train, feature_cols)
    X_test, _ = _parse_xy(test_data, feature_cols, args.target_col)
    if not X_test:
        print("Error: no valid test samples")
        return
    output_lines = ["prediction"]
    for xt in X_test:
        pred = _predict(xt, classes, class_priors, means_dict, vars_dict, feature_cols)
        output_lines.append(pred)
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
        X.append(vec)
        y.append(t)
    return X, y


def _fit(X, y, feature_cols):
    n = len(X)
    n_features = len(feature_cols)
    classes = sorted(set(y))
    counts = Counter(y)
    class_priors = {c: counts[c] / n for c in classes}
    means_dict = {c: [0.0] * n_features for c in classes}
    vars_dict = {c: [0.0] * n_features for c in classes}
    for c in classes:
        members = [X[i] for i in range(n) if y[i] == c]
        if len(members) < 1:
            continue
        for f in range(n_features):
            vals = [m[f] for m in members]
            means_dict[c][f] = mean(vals)
            v = var_s(vals) if len(vals) > 1 else 1e-6
            vars_dict[c][f] = max(v, 1e-6)
    return classes, class_priors, means_dict, vars_dict


def _predict(xt, classes, class_priors, means_dict, vars_dict, feature_cols):
    best_class = None
    best_log_prob = -float("inf")
    for c in classes:
        log_prob = math.log(class_priors[c])
        for f in range(len(feature_cols)):
            mu = means_dict[c][f]
            sigma = math.sqrt(vars_dict[c][f])
            log_prob += math.log(normal_pdf((xt[f] - mu) / sigma) / sigma)
        if log_prob > best_log_prob:
            best_log_prob = log_prob
            best_class = c
    return best_class
