
# Retail Orders Data Reconciliation Pipeline

## 1. Project Overview

The Retail Orders Data Reconciliation Pipeline is a Python-based data engineering project designed to validate, process, publish, and reconcile retail order datasets.

It compares source and target datasets using:
- Record counts
- Business key comparison
- Aggregate validation
- Field-level comparison

The pipeline generates machine-readable JSON and CSV reports to identify missing records, extra records, rejected records, and data mismatches.

## 2. Technology Stack

- Python 3.13
- Pandas
- NumPy
- SQLite
- Pytest

## 3. Project Structure

```text
Yottaflex/
│
├── data/
│   └── generated/
│       ├── source_orders.csv
│       └── target_orders.csv
│
├── outputs/
│   ├── reconciliation.db
│   ├── reconciliation_report.json
│   ├── source_rejects.csv
│   ├── target_rejects.csv
│   ├── source_only.csv
│   ├── target_only.csv
│   ├── field_mismatches.csv
│   └── benchmark_results.csv
│
├── src/
│   ├── data_generator.py
│   ├── validation.py
│   ├── storage.py
│   ├── reconciliation.py
│   ├── reporting.py
│   ├── pipeline.py
│   └── benchmark.py
│
├── tests/
│   ├── conftest.py
│   ├── test_validation.py
│   ├── test_storage.py
│   ├── test_reconciliation.py
│   ├── test_reporting.py
│   └── test_pipeline.py
│
├── DATA_DICTIONARY.md
├── README.md
└── requirements.txt
```

## 4. Installation

Clone or download the project.

Create and activate a virtual environment:

```bash
python -m venv .venv
```

Windows activation:

```bash
.venv\Scripts\activate
```

Install dependencies:

```bash
python -m pip install -r requirements.txt
```

## 5. Generate Sample Data

```bash
python -m src.data_generator
```

The generator creates reproducible source and target datasets with intentional data-quality issues and reconciliation mismatches.

## 6. Run the Pipeline

```bash
python -m src.pipeline
```

The pipeline performs:

1. Reads source and target datasets.
2. Validates required fields and business rules.
3. Separates valid and rejected records.
4. Publishes target records to SQLite.
5. Reads the published target snapshot.
6. Performs reconciliation.
7. Generates JSON and CSV reports.
8. Records pipeline execution metrics.

## 7. Reconciliation Rules

Business key: `order_id`

The pipeline checks:

- Source and target record counts.
- Source-only and target-only records.
- Quantity and total amount aggregates.
- Field-level differences for common business keys.

A reconciliation result is PASS only when all configured checks match.

## 8. Data Quality Rules

- Required fields must not be null or empty.
- Order IDs must be unique.
- Customer and product references must be valid.
- Quantity must be an integer between 1 and 1000.
- Unit price must be non-negative.
- Total amount must equal quantity multiplied by unit price.
- Order status must be valid.
- Order timestamps must be parseable.

Invalid records are isolated into reject reports with reasons.

## 9. Generated Reports

| Report | Purpose |
|---|---|
| reconciliation_report.json | Machine-readable reconciliation summary |
| source_rejects.csv | Invalid source records |
| target_rejects.csv | Invalid target records |
| source_only.csv | Records missing from target |
| target_only.csv | Extra records in target |
| field_mismatches.csv | Field-level differences |
| benchmark_results.csv | Performance measurements |

## 10. Automated Testing

Run all tests:

```bash
python -m pytest -v
```

The project includes tests for:

- Valid and invalid records
- Missing required fields
- Duplicate business keys
- Empty datasets
- Malformed input
- Invalid reference IDs
- Reconciliation mismatches
- Database publishing
- Idempotent snapshots
- Pipeline failure handling and retry

## 11. Performance Benchmark

Benchmark command:

```bash
python -m src.benchmark
```

Measured results:

| Records | Validation | Reconciliation |
|---:|---:|---:|
| 1,000 | 0.257 sec | 0.319 sec |
| 10,000 | 0.442 sec | 1.453 sec |
| 100,000 | 3.898 sec | 14.898 sec |

These are observed local benchmark results. Actual performance depends on the machine and runtime environment.

## 12. Idempotency

Target publishing uses snapshot replacement rather than appending duplicate records.

Repeated pipeline runs replace the target snapshot while preserving execution history.

## 13. Limitations and Future Improvements

- Optimize reconciliation for larger datasets.
- Add transaction-level failure recovery tests.
- Add schema versioning and configurable validation rules.
- Introduce incremental reconciliation for large-scale data.
- Add structured monitoring and alerting.

## 14. Author

Retail Orders Data Reconciliation Pipeline

Developed as a practical data engineering challenge project.
