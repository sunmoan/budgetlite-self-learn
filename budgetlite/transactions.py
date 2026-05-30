from __future__ import annotations

import csv
import re
from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from pathlib import Path
from typing import Iterable, Mapping


REQUIRED_FIELDS = ("date", "category", "amount", "description")
MONEY_QUANT = Decimal("0.01")


class TransactionError(ValueError):
    """Raised when transaction input is missing or invalid."""


@dataclass(frozen=True)
class Transaction:
    date: date
    category: str
    amount: Decimal
    description: str

    @property
    def month(self) -> str:
        return self.date.strftime("%Y-%m")


def parse_amount(value: object) -> Decimal:
    if value is None:
        raise TransactionError("amount is missing")

    raw = str(value).strip().replace("$", "").replace(",", "")
    if not raw:
        raise TransactionError("amount is blank")

    try:
        amount = Decimal(raw)
    except InvalidOperation as exc:
        raise TransactionError(f"invalid amount: {value!r}") from exc

    if amount < 0:
        raise TransactionError("amount cannot be negative")

    return amount.quantize(MONEY_QUANT, rounding=ROUND_HALF_UP)


def parse_date(value: object) -> date:
    if value is None:
        raise TransactionError("date is missing")

    raw = str(value).strip()
    if not raw:
        raise TransactionError("date is blank")

    try:
        return datetime.strptime(raw, "%Y-%m-%d").date()
    except ValueError as exc:
        raise TransactionError(f"invalid date: {value!r}; expected YYYY-MM-DD") from exc


def normalize_category(value: object) -> str:
    if value is None:
        raise TransactionError("category is missing")

    raw = re.sub(r"\s+", " ", str(value).strip())
    if not raw:
        raise TransactionError("category is blank")

    return raw.title()


def normalize_description(value: object) -> str:
    if value is None:
        raise TransactionError("description is missing")

    raw = re.sub(r"\s+", " ", str(value).strip())
    if not raw:
        raise TransactionError("description is blank")

    return raw


def parse_transaction_row(
    row: Mapping[str, object],
    *,
    row_number: int | None = None,
) -> Transaction:
    missing = [field for field in REQUIRED_FIELDS if field not in row]
    if missing:
        raise _with_row(row_number, f"missing required field(s): {', '.join(missing)}")

    try:
        return Transaction(
            date=parse_date(row["date"]),
            category=normalize_category(row["category"]),
            amount=parse_amount(row["amount"]),
            description=normalize_description(row["description"]),
        )
    except TransactionError as exc:
        raise _with_row(row_number, str(exc)) from exc


def read_transactions_csv(path: str | Path) -> list[Transaction]:
    csv_path = Path(path)
    if not csv_path.exists():
        raise TransactionError(f"CSV file not found: {csv_path}")
    if not csv_path.is_file():
        raise TransactionError(f"CSV path is not a file: {csv_path}")

    with csv_path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        _validate_headers(reader.fieldnames)
        return [parse_transaction_row(row, row_number=index) for index, row in enumerate(reader, start=2)]


def transactions_from_rows(rows: Iterable[Mapping[str, object]]) -> list[Transaction]:
    return [parse_transaction_row(row, row_number=index) for index, row in enumerate(rows, start=1)]


def _validate_headers(fieldnames: list[str] | None) -> None:
    if fieldnames is None:
        raise TransactionError("CSV file is empty")

    missing = [field for field in REQUIRED_FIELDS if field not in fieldnames]
    if missing:
        raise TransactionError(f"CSV missing required column(s): {', '.join(missing)}")


def _with_row(row_number: int | None, message: str) -> TransactionError:
    if row_number is None:
        return TransactionError(message)
    return TransactionError(f"row {row_number}: {message}")
