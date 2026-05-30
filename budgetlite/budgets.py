from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from typing import Mapping

from .summaries import format_money
from .transactions import TransactionError


@dataclass(frozen=True)
class BudgetResult:
    category: str
    spent: Decimal
    limit: Decimal
    remaining: Decimal
    status: str

    @property
    def is_over_budget(self) -> bool:
        return self.status == "over"

    def render(self) -> str:
        if self.status == "over":
            return (
                f"{self.category}: over by {format_money(abs(self.remaining))} "
                f"({format_money(self.spent)} spent, {format_money(self.limit)} limit)"
            )
        if self.status == "at_limit":
            return f"{self.category}: exactly at budget ({format_money(self.limit)})"
        return (
            f"{self.category}: {format_money(self.remaining)} left "
            f"({format_money(self.spent)} spent, {format_money(self.limit)} limit)"
        )


def parse_budget_limit(value: object) -> Decimal:
    if value is None:
        raise TransactionError("budget limit is missing")
    raw = str(value).strip().replace("$", "").replace(",", "")
    if not raw:
        raise TransactionError("budget limit is blank")
    try:
        limit = Decimal(raw).quantize(Decimal("0.01"))
    except InvalidOperation as exc:
        raise TransactionError(f"invalid budget limit: {value!r}") from exc
    if limit < 0:
        raise TransactionError("budget limit cannot be negative")
    return limit


def compare_budget(category: str, spent: Decimal, limit: Decimal) -> BudgetResult:
    normalized_limit = parse_budget_limit(limit)
    normalized_spent = parse_budget_limit(spent)
    remaining = normalized_limit - normalized_spent

    if normalized_spent > normalized_limit:
        status = "over"
    elif normalized_spent == normalized_limit:
        status = "at_limit"
    else:
        status = "under"

    return BudgetResult(
        category=category,
        spent=normalized_spent,
        limit=normalized_limit,
        remaining=remaining,
        status=status,
    )


def compare_category_budgets(
    category_totals: Mapping[str, Decimal],
    budget_limits: Mapping[str, object],
) -> list[BudgetResult]:
    results = []
    for category in sorted(set(category_totals) | set(budget_limits)):
        spent = category_totals.get(category, Decimal("0.00"))
        limit = budget_limits.get(category, Decimal("0.00"))
        results.append(compare_budget(category, spent, parse_budget_limit(limit)))
    return results
