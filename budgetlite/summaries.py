from __future__ import annotations

from collections import defaultdict
from decimal import Decimal
from typing import Iterable

from .transactions import Transaction


def total_spent(transactions: Iterable[Transaction]) -> Decimal:
    return sum((transaction.amount for transaction in transactions), Decimal("0.00"))


def spending_by_category(transactions: Iterable[Transaction]) -> dict[str, Decimal]:
    totals: defaultdict[str, Decimal] = defaultdict(lambda: Decimal("0.00"))
    for transaction in transactions:
        totals[transaction.category] += transaction.amount
    return dict(sorted(totals.items()))


def spending_by_month(transactions: Iterable[Transaction]) -> dict[str, Decimal]:
    totals: defaultdict[str, Decimal] = defaultdict(lambda: Decimal("0.00"))
    for transaction in transactions:
        totals[transaction.month] += transaction.amount
    return dict(sorted(totals.items()))


def spending_by_month_and_category(transactions: Iterable[Transaction]) -> dict[str, dict[str, Decimal]]:
    totals: defaultdict[str, defaultdict[str, Decimal]] = defaultdict(lambda: defaultdict(lambda: Decimal("0.00")))
    for transaction in transactions:
        totals[transaction.month][transaction.category] += transaction.amount
    return {month: dict(sorted(categories.items())) for month, categories in sorted(totals.items())}


def largest_transaction(transactions: Iterable[Transaction]) -> Transaction | None:
    transaction_list = list(transactions)
    if not transaction_list:
        return None
    return max(transaction_list, key=lambda transaction: transaction.amount)


def format_money(amount: Decimal) -> str:
    return f"${amount.quantize(Decimal('0.01')):,.2f}"


def render_summary(transactions: Iterable[Transaction]) -> list[str]:
    transaction_list = list(transactions)
    lines = [
        "BudgetLite summary",
        f"Transactions: {len(transaction_list)}",
        f"Total spending: {format_money(total_spent(transaction_list))}",
        "",
        "Spending by category:",
    ]
    for category, amount in spending_by_category(transaction_list).items():
        lines.append(f"- {category}: {format_money(amount)}")

    biggest = largest_transaction(transaction_list)
    if biggest is not None:
        lines.extend(["", f"Largest transaction: {biggest.description} ({format_money(biggest.amount)})"])
    return lines
