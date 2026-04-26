import math
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
    X_test, _ = _dt_parse(test_data, feature_cols, args.target_col)
    if not X_test:
        print("Error: no valid test samples")
        return
    n = len(X)
    base_pred = mean(y)
    residuals = [yi - base_pred for yi in y]
    trees = []
    lr = args.lr
    for _ in range(args.n_trees):
        tree = _build_tree(X, residuals, args.max_depth, 5, regression=True)
        trees.append(tree)
        for i in range(n):
            residuals[i] -= lr * _predict_one(tree, X[i])
    output_lines = ["prediction"]
    for xt in X_test:
        pred = base_pred
        for tree in trees:
            pred += lr * _predict_one(tree, xt)
        output_lines.append(str(pred))
    write_output(output_lines, args.output)
