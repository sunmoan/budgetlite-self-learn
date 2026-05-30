from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Sequence

from .budgets import compare_category_budgets
from .summaries import render_summary, spending_by_category
from .transactions import TransactionError, read_transactions_csv


def load_budget_file(path: str | Path) -> dict[str, object]:
    try:
        with Path(path).open(encoding="utf-8") as handle:
            payload = json.load(handle)
    except OSError as exc:
        raise TransactionError(f"budget file could not be read: {path}") from exc
    except json.JSONDecodeError as exc:
        raise TransactionError(f"budget file is not valid JSON: {path}") from exc

    if not isinstance(payload, dict):
        raise TransactionError("budget file must contain a JSON object")
    return payload


def build_report(csv_path: str | Path, budget_path: str | Path | None = None) -> str:
    transactions = read_transactions_csv(csv_path)
    lines = render_summary(transactions)

    if budget_path is not None:
        lines.extend(["", "Budget comparison:"])
        budgets = load_budget_file(budget_path)
        for result in compare_category_budgets(spending_by_category(transactions), budgets):
            lines.append(f"- {result.render()}")

    return "\n".join(lines)


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Summarise CSV spending and compare it with budgets.")
    parser.add_argument("csv_path", help="CSV file with date, category, amount, description columns")
    parser.add_argument("--budget", help="Optional JSON file mapping categories to budget limits")
    args = parser.parse_args(argv)

    try:
        print(build_report(args.csv_path, args.budget))
    except TransactionError as exc:
        print(f"BudgetLite error: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
