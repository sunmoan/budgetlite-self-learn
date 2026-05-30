from __future__ import annotations

from decimal import Decimal

import pytest

from budgetlite.transactions import Transaction, read_transactions_csv


@pytest.fixture
def sample_rows() -> list[dict[str, str]]:
    return [
        {"date": "2026-04-01", "category": "food", "amount": "12.50", "description": "Lunch"},
        {"date": "2026-04-02", "category": "transport", "amount": "4.80", "description": "Train fare"},
        {"date": "2026-04-05", "category": "books", "amount": "38.95", "description": "Testing book"},
        {"date": "2026-05-02", "category": "Food", "amount": "15.25", "description": "Groceries"},
    ]


@pytest.fixture
def sample_transactions(sample_rows: list[dict[str, str]]) -> list[Transaction]:
    from budgetlite.transactions import transactions_from_rows

    return transactions_from_rows(sample_rows)


@pytest.fixture
def csv_file(tmp_path, sample_rows: list[dict[str, str]]):
    path = tmp_path / "transactions.csv"
    lines = ["date,category,amount,description"]
    lines.extend(
        f"{row['date']},{row['category']},{row['amount']},{row['description']}" for row in sample_rows
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path


@pytest.fixture
def budget_file(tmp_path):
    path = tmp_path / "budgets.json"
    path.write_text('{"Food": "40.00", "Transport": "20.00", "Books": "35.00"}', encoding="utf-8")
    return path


@pytest.fixture
def loaded_csv(csv_file):
    return read_transactions_csv(csv_file)


@pytest.fixture
def expected_total() -> Decimal:
    return Decimal("71.50")
