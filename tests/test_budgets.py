from __future__ import annotations

from decimal import Decimal

import pytest

from budgetlite.budgets import compare_budget, compare_category_budgets, parse_budget_limit
from budgetlite.transactions import TransactionError


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("100", Decimal("100.00")),
        ("$1,000.50", Decimal("1000.50")),
        (Decimal("12.30"), Decimal("12.30")),
    ],
)
def test_parse_budget_limit_accepts_valid_values(raw, expected):
    assert parse_budget_limit(raw) == expected


@pytest.mark.parametrize("raw", ["", "x", "-1.00", None])
def test_parse_budget_limit_rejects_invalid_values(raw):
    with pytest.raises(TransactionError):
        parse_budget_limit(raw)


def test_compare_budget_under_limit():
    result = compare_budget("Food", Decimal("25.00"), Decimal("40.00"))
    assert result.status == "under"
    assert result.remaining == Decimal("15.00")
    assert not result.is_over_budget
    assert result.render() == "Food: $15.00 left ($25.00 spent, $40.00 limit)"


def test_compare_budget_exactly_at_limit_is_not_over_budget():
    result = compare_budget("Books", Decimal("35.00"), Decimal("35.00"))
    assert result.status == "at_limit"
    assert result.remaining == Decimal("0.00")
    assert not result.is_over_budget
    assert result.render() == "Books: exactly at budget ($35.00)"


def test_compare_budget_over_limit():
    result = compare_budget("Books", Decimal("38.95"), Decimal("35.00"))
    assert result.status == "over"
    assert result.remaining == Decimal("-3.95")
    assert result.is_over_budget
    assert result.render() == "Books: over by $3.95 ($38.95 spent, $35.00 limit)"


def test_compare_category_budgets_returns_sorted_results():
    results = compare_category_budgets(
        {"Food": Decimal("27.75"), "Books": Decimal("38.95")},
        {"Food": "40.00", "Books": "35.00"},
    )
    assert [result.category for result in results] == ["Books", "Food"]
    assert [result.status for result in results] == ["over", "under"]


def test_compare_category_budgets_includes_budget_with_no_spending():
    results = compare_category_budgets({"Food": Decimal("10.00")}, {"Food": "40.00", "Transport": "20.00"})
    transport = next(result for result in results if result.category == "Transport")
    assert transport.spent == Decimal("0.00")
    assert transport.remaining == Decimal("20.00")


def test_compare_category_budgets_includes_spending_with_no_budget():
    results = compare_category_budgets({"Other": Decimal("10.00")}, {})
    assert results[0].category == "Other"
    assert results[0].status == "over"
