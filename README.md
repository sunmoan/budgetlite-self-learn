# BudgetLite

BudgetLite is a small command line expense analysis tool rebuilt as evidence for the INFO1111 Self-Learn Advanced assignment. It reads CSV transactions, validates the data, summarises spending, and compares category totals against JSON budget limits.

## Skills Demonstrated

- `pytest` unit testing
- fixtures and parameterised tests
- exception testing with `pytest.raises`
- temporary files for CSV/JSON inputs
- coverage measurement with `pytest-cov`
- a GitHub Actions workflow for continuous integration
- a fault-injection check proving that the tests catch a realistic boundary bug

## Run Locally

```bash
python -m pip install -r requirements.txt
python -m pytest
python -m pytest --cov=budgetlite --cov-report=term-missing
python -m budgetlite.cli data/sample_transactions.csv --budget data/sample_budgets.json
```

## CSV Format

The transaction CSV requires these columns:

- `date` in `YYYY-MM-DD` format
- `category`
- `amount`
- `description`

Money is parsed with `Decimal`, not floating point arithmetic.
