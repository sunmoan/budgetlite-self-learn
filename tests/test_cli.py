from __future__ import annotations

import pytest

from budgetlite.cli import build_report, load_budget_file, main
from budgetlite.transactions import TransactionError


def test_build_report_without_budget(csv_file):
    report = build_report(csv_file)
    assert "BudgetLite summary" in report
    assert "Total spending: $71.50" in report
    assert "Budget comparison" not in report


def test_build_report_with_budget(csv_file, budget_file):
    report = build_report(csv_file, budget_file)
    assert "Budget comparison:" in report
    assert "- Books: over by $3.95" in report
    assert "- Food: $12.25 left" in report


def test_load_budget_file_returns_json_object(budget_file):
    assert load_budget_file(budget_file)["Food"] == "40.00"


def test_load_budget_file_rejects_missing_file(tmp_path):
    with pytest.raises(TransactionError, match="could not be read"):
        load_budget_file(tmp_path / "missing.json")


def test_load_budget_file_rejects_invalid_json(tmp_path):
    path = tmp_path / "bad.json"
    path.write_text("{not valid", encoding="utf-8")
    with pytest.raises(TransactionError, match="not valid JSON"):
        load_budget_file(path)


def test_load_budget_file_rejects_non_object_json(tmp_path):
    path = tmp_path / "list.json"
    path.write_text("[1, 2, 3]", encoding="utf-8")
    with pytest.raises(TransactionError, match="JSON object"):
        load_budget_file(path)


def test_main_prints_report_and_returns_zero(csv_file, budget_file, capsys):
    code = main([str(csv_file), "--budget", str(budget_file)])
    captured = capsys.readouterr()
    assert code == 0
    assert "BudgetLite summary" in captured.out
    assert "Books: over by $3.95" in captured.out
    assert captured.err == ""


def test_main_prints_error_and_returns_two(tmp_path, capsys):
    code = main([str(tmp_path / "missing.csv")])
    captured = capsys.readouterr()
    assert code == 2
    assert "BudgetLite error:" in captured.err
    assert "not found" in captured.err
    assert captured.out == ""
