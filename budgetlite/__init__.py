"""BudgetLite: small CSV expense analysis tool used for pytest/CI evidence."""

from .budgets import BudgetResult, compare_budget, compare_category_budgets
from .summaries import (
    format_money,
    spending_by_category,
    spending_by_month,
    spending_by_month_and_category,
    total_spent,
)
from .transactions import Transaction, TransactionError, read_transactions_csv

__all__ = [
    "BudgetResult",
    "Transaction",
    "TransactionError",
    "compare_budget",
    "compare_category_budgets",
    "format_money",
    "read_transactions_csv",
    "spending_by_category",
    "spending_by_month",
    "spending_by_month_and_category",
    "total_spent",
]

__version__ = "1.0.0"
