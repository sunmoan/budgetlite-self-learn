from __future__ import annotations

from decimal import Decimal

from budgetlite.summaries import (
    format_money,
    largest_transaction,
    render_summary,
    spending_by_category,
    spending_by_month,
    spending_by_month_and_category,
    total_spent,
)


def test_total_spent_uses_decimal(sample_transactions, expected_total):
    assert total_spent(sample_transactions) == expected_total


def test_total_spent_handles_empty_list():
    assert total_spent([]) == Decimal("0.00")


def test_spending_by_category_groups_and_sorts(sample_transactions):
    assert spending_by_category(sample_transactions) == {
        "Books": Decimal("38.95"),
        "Food": Decimal("27.75"),
        "Transport": Decimal("4.80"),
    }


def test_spending_by_month_groups_by_year_month(sample_transactions):
    assert spending_by_month(sample_transactions) == {
        "2026-04": Decimal("56.25"),
        "2026-05": Decimal("15.25"),
    }


def test_spending_by_month_and_category_builds_nested_totals(sample_transactions):
    assert spending_by_month_and_category(sample_transactions) == {
        "2026-04": {"Books": Decimal("38.95"), "Food": Decimal("12.50"), "Transport": Decimal("4.80")},
        "2026-05": {"Food": Decimal("15.25")},
    }


def test_largest_transaction_returns_highest_amount(sample_transactions):
    assert largest_transaction(sample_transactions).description == "Testing book"


def test_largest_transaction_returns_none_for_empty_collection():
    assert largest_transaction([]) is None


def test_format_money_adds_currency_and_thousands_separator():
    assert format_money(Decimal("1234.5")) == "$1,234.50"


def test_render_summary_contains_key_lines(sample_transactions):
    output = "\n".join(render_summary(sample_transactions))
    assert "BudgetLite summary" in output
    assert "Transactions: 4" in output
    assert "Total spending: $71.50" in output
    assert "- Food: $27.75" in output
    assert "Largest transaction: Testing book ($38.95)" in output


def test_render_summary_for_empty_collection_has_no_largest_line():
    output = "\n".join(render_summary([]))
    assert "Transactions: 0" in output
    assert "Largest transaction" not in output
