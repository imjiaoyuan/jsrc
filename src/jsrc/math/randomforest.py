import math
import random
from collections import Counter
from jsrc.math.core import parse_columns, write_output, mean
from jsrc.math.decisiontree import _build_tree, _predict_one, _parse_xy as _dt_parse, _is_numeric_col


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
    X, y = _dt_parse(train_data, feature_cols, args.target_col)
    if not X:
        print("Error: no valid training samples")
        return
    regression = args.regression
    n_features = len(feature_cols)
    n_samples = len(X)
    sqrt_nf = max(1, int(math.sqrt(n_features)))
    forest = []
    for t in range(args.n_trees):
        indices = [random.randint(0, n_samples - 1) for _ in range(n_samples)]
        X_boot = [X[i] for i in indices]
        y_boot = [y[i] for i in indices]
        n_sub = max(1, n_features // 3 if regression else sqrt_nf)
        feat_subset = sorted(random.sample(range(n_features), n_sub))
        X_sub = [[xi[f] for f in feat_subset] for xi in X_boot]
        tree = _build_tree(X_sub, y_boot, args.max_depth, 2, regression)
        forest.append((tree, feat_subset))
    X_test, _ = _dt_parse(test_data, feature_cols, args.target_col)
    if not X_test:
        print("Error: no valid test samples")
        return
    output_lines = ["prediction"]
    for xt in X_test:
        preds = []
        for tree, feat_subset in forest:
            xt_sub = [xt[f] for f in feat_subset]
            pred = _predict_one(tree, xt_sub)
            preds.append(pred)
        if regression:
            output_lines.append(str(mean(preds)))
        else:
            output_lines.append(Counter(preds).most_common(1)[0][0])
    write_output(output_lines, args.output)
