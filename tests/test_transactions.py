from __future__ import annotations

from datetime import date
from decimal import Decimal

import pytest

from budgetlite.transactions import (
    TransactionError,
    normalize_category,
    normalize_description,
    parse_amount,
    parse_date,
    parse_transaction_row,
    read_transactions_csv,
    transactions_from_rows,
)


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("12", Decimal("12.00")),
        ("12.5", Decimal("12.50")),
        ("$1,234.567", Decimal("1234.57")),
        (" 0.005 ", Decimal("0.01")),
    ],
)
def test_parse_amount_accepts_valid_money(raw, expected):
    assert parse_amount(raw) == expected


@pytest.mark.parametrize("raw", ["", "   ", "abc", "-0.01", None])
def test_parse_amount_rejects_invalid_money(raw):
    with pytest.raises(TransactionError):
        parse_amount(raw)


def test_parse_date_accepts_iso_date():
    assert parse_date("2026-05-30") == date(2026, 5, 30)


@pytest.mark.parametrize("raw", ["30-05-2026", "2026/05/30", "2026-02-30", "", None])
def test_parse_date_rejects_invalid_date(raw):
    with pytest.raises(TransactionError):
        parse_date(raw)


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("food", "Food"),
        ("  public   transport ", "Public Transport"),
        ("BOOKS", "Books"),
    ],
)
def test_normalize_category_collapses_space_and_title_cases(raw, expected):
    assert normalize_category(raw) == expected


@pytest.mark.parametrize("raw", ["", "   ", None])
def test_normalize_category_rejects_blank(raw):
    with pytest.raises(TransactionError):
        normalize_category(raw)


def test_normalize_description_collapses_internal_space():
    assert normalize_description("  lunch   near   campus ") == "lunch near campus"


@pytest.mark.parametrize("raw", ["", None])
def test_normalize_description_rejects_blank(raw):
    with pytest.raises(TransactionError):
        normalize_description(raw)


def test_parse_transaction_row_returns_transaction():
    transaction = parse_transaction_row(
        {"date": "2026-04-01", "category": "food", "amount": "12.50", "description": "Lunch"},
    )
    assert transaction.date == date(2026, 4, 1)
    assert transaction.category == "Food"
    assert transaction.amount == Decimal("12.50")
    assert transaction.description == "Lunch"
    assert transaction.month == "2026-04"


def test_parse_transaction_row_reports_missing_fields_with_row_number():
    with pytest.raises(TransactionError, match="row 4: missing required field"):
        parse_transaction_row({"date": "2026-04-01", "amount": "2.00"}, row_number=4)


def test_parse_transaction_row_reports_missing_fields_without_row_number():
    with pytest.raises(TransactionError, match="missing required field"):
        parse_transaction_row({"date": "2026-04-01", "amount": "2.00"})


def test_parse_transaction_row_wraps_validation_error_with_row_number():
    with pytest.raises(TransactionError, match="row 7: invalid date"):
        parse_transaction_row(
            {"date": "01/04/2026", "category": "food", "amount": "2.00", "description": "Lunch"},
            row_number=7,
        )


def test_transactions_from_rows_parses_iterable(sample_rows):
    transactions = transactions_from_rows(sample_rows)
    assert len(transactions) == 4
    assert transactions[0].category == "Food"


def test_read_transactions_csv_loads_valid_file(csv_file):
    transactions = read_transactions_csv(csv_file)
    assert [transaction.description for transaction in transactions] == [
        "Lunch",
        "Train fare",
        "Testing book",
        "Groceries",
    ]


def test_read_transactions_csv_rejects_missing_file(tmp_path):
    with pytest.raises(TransactionError, match="not found"):
        read_transactions_csv(tmp_path / "missing.csv")


def test_read_transactions_csv_rejects_directory(tmp_path):
    with pytest.raises(TransactionError, match="not a file"):
        read_transactions_csv(tmp_path)


def test_read_transactions_csv_rejects_empty_file(tmp_path):
    path = tmp_path / "empty.csv"
    path.write_text("", encoding="utf-8")
    with pytest.raises(TransactionError, match="empty"):
        read_transactions_csv(path)


def test_read_transactions_csv_rejects_missing_required_header(tmp_path):
    path = tmp_path / "bad.csv"
    path.write_text("date,category,amount\n2026-04-01,Food,1.00\n", encoding="utf-8")
    with pytest.raises(TransactionError, match="description"):
        read_transactions_csv(path)


def test_read_transactions_csv_reports_bad_row_number(tmp_path):
    path = tmp_path / "bad_row.csv"
    path.write_text(
        "date,category,amount,description\n2026-04-01,Food,1.00,Lunch\nbad,Food,2.00,Dinner\n",
        encoding="utf-8",
    )
    with pytest.raises(TransactionError, match="row 3"):
        read_transactions_csv(path)
