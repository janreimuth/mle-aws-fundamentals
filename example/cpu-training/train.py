"""Fit a synthetic linear model without external dependencies."""

import json
from pathlib import Path
from statistics import linear_regression, mean


def main() -> None:
    train_x = [x for x in range(-50, 50) if x % 5 != 0]
    test_x = list(range(-50, 50, 5))
    train_y = [2 * x + 1 for x in train_x]
    slope, intercept = linear_regression(train_x, train_y)

    model = {"slope": slope, "intercept": intercept}
    errors = [abs((2 * x + 1) - (slope * x + intercept)) for x in test_x]
    metrics = {
        "train_examples": len(train_x),
        "test_examples": len(test_x),
        "mean_absolute_error": mean(errors),
    }

    for name, data in [("model", model), ("metrics", metrics)]:
        Path(f"{name}.json").write_text(json.dumps(data) + "\n", encoding="utf-8")
    print(json.dumps({"event": "cpu_training_complete", **metrics}))


if __name__ == "__main__":
    main()
