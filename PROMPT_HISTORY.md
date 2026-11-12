
# AI Usage and Prompt History

## 1. AI Tool Used

- Tool: ChatGPT
- Model: GPT-6
- Purpose: Technical guidance, implementation assistance, debugging, testing, and documentation.

## 2. Project Context

Project: Retail Orders Data Reconciliation Pipeline

The project was developed as part of the YottaFlex AI recruitment challenge.

ChatGPT was used as an AI assistance tool during development. The candidate reviewed the generated code, executed it locally, tested functionality, and verified outputs.

## 3. Prompt History

The following records summarize the prompts and requests used during the development process. They are organized by development stage. They are not claimed to be verbatim exports of every original conversation message.

### Stage 1 – Project Setup
- Guide me step by step to build the data reconciliation pipeline.
- Explain the project structure and required files.
- Provide complete Python code for each file when needed.

### Stage 2 – Data Generation and Validation
- Help create source and target retail order datasets.
- Implement validation for required fields, data types, duplicate keys, and business rules.
- Add tests for valid records, missing customers, duplicate orders, and invalid quantities.

### Stage 3 – Storage and Reconciliation
- Implement SQLite database creation and target snapshot publishing.
- Make target publishing idempotent.
- Compare source and target datasets using business keys.
- Identify missing records, extra records, aggregate differences, and field-level mismatches.

### Stage 4 – Reporting and Pipeline
- Generate machine-readable JSON and CSV reconciliation reports.
- Build a pipeline to read, validate, publish, reconcile, and report.
- Handle missing files and pipeline execution failures.
- Record pipeline execution history.

### Stage 5 – Testing and Debugging
- Add tests for empty datasets and malformed values.
- Test missing required columns and invalid product references.
- Debug failing pytest tests.
- Test duplicate records and pipeline retry behavior.
- Verify database record counts after repeated runs.

### Stage 6 – Performance
- Create a benchmark for 1,000, 10,000, and 100,000 records.
- Measure validation and reconciliation execution times.
- Fix the Pandas dtype warning in the data generator.

### Stage 7 – Documentation
- Prepare README.md with installation and execution instructions.
- Document architecture, design decisions, and trade-offs.
- Prepare AI usage and prompt history documentation.

## 4. How AI Assisted the Development

ChatGPT provided:
- Step-by-step implementation guidance.
- Python code examples and debugging suggestions.
- Pytest test-case examples.
- SQLite and reconciliation design guidance.
- Documentation drafts.
- Performance benchmarking guidance.

## 5. Candidate's Work and Verification

The candidate:
- Created and organized the project files in VS Code.
- Executed the Python pipeline locally on Windows.
- Ran automated tests using pytest.
- Investigated test failures and corrected mismatched test expectations.
- Inspected generated CSV and JSON reports.
- Verified missing and extra records and field-level mismatches.
- Ran the pipeline twice and checked database record counts and unique order IDs.
- Executed the 100,000-record benchmark.
- Reviewed and saved project documentation.

## 6. AI Usage Limitations and Disclosure

This document is a structured development-stage record based on the available ChatGPT conversation history.

It is not a verbatim export of every individual prompt. Earlier conversation messages may not all be available in this record.

AI responses and code suggestions were used as implementation assistance. The candidate is responsible for reviewing, understanding, validating, and explaining the submitted implementation.

No claim is made that all code was independently authored without AI assistance.

## 7. Validation Evidence

The project was tested locally using:

```bash
python -m pytest -v
```

The benchmark was executed using:

```bash
python -m src.benchmark
```

Observed benchmark results are documented in README.md and benchmark_results.csv.
