
# System Design – Retail Orders Data Reconciliation Pipeline

## 1. Architecture Overview

The project follows a modular batch-processing architecture.

The pipeline separates data generation, validation, storage, reconciliation, and reporting into independent modules.

### High-Level Workflow

```text
Source CSV                 Target CSV
    |                          |
    v                          v
 Read Input                Read Input
    |                          |
    v                          v
 Source Validation        Target Validation
    |                          |
    v                          v
 Valid + Rejected         Valid + Rejected
    |                          |
    |                     SQLite Publishing
    |                          |
    |                     Read Target Snapshot
    |                          |
    +------------+-------------+
                 |
                 v
           Reconciliation
                 |
                 v
          Report Generation
                 |
                 v
       JSON + CSV + Run History
```

## 2. Module Responsibilities

| Module | Responsibility |
|---|---|
| data_generator.py | Generates reproducible source and target datasets |
| validation.py | Validates schema, references, and business rules |
| storage.py | Creates SQLite tables and publishes target snapshots |
| reconciliation.py | Compares records, keys, fields, and aggregates |
| reporting.py | Generates machine-readable JSON and CSV reports |
| pipeline.py | Orchestrates the complete workflow |
| benchmark.py | Measures validation and reconciliation performance |

## 3. Data Model and Grain

The dataset represents retail orders.

**Grain:** One row represents one order.

**Business key:** `order_id`

Important relationships:
- Each order references a customer through `customer_id`.
- Each order references a product through `product_id`.
- `total_amount` is calculated as quantity multiplied by unit price.

The detailed schema and business rules are documented in `DATA_DICTIONARY.md`.

## 4. Validation Strategy

Validation is performed before publishing or reconciliation.

The validation module checks:

1. Required schema and columns.
2. Null and empty required values.
3. Duplicate order IDs.
4. Valid customer and product references.
5. Numeric data types and quantity boundaries.
6. Valid order status.
7. Timestamp parsing.
8. Total amount calculation.

Invalid records are separated from valid records.

Each rejected record includes a rejection reason to support investigation.

## 5. Reconciliation Strategy

The pipeline compares source and published target datasets using `order_id`.

The following checks are performed:

### Record Count

Compares the number of valid source and target records.

### Business Key Comparison

Identifies:
- Source-only records.
- Target-only records.
- Common records.

### Aggregate Comparison

Compares:
- Total quantity.
- Total order amount.

### Field-Level Comparison

Compares individual fields for common business keys.

Numeric comparisons use configured tolerances where appropriate.

The final status is PASS only when all configured reconciliation checks pass.

## 6. Storage Design

SQLite is used as the target storage layer.

Two main tables are maintained:

- `target_orders`: Contains the published target snapshot and operational metadata.
- `pipeline_runs`: Stores execution history and pipeline metrics.

The target publishing process replaces the existing snapshot inside a database transaction.

This prevents duplicate records during repeated snapshot publishing.

## 7. Idempotency

The pipeline uses snapshot replacement instead of appending records to the target table.

When the same input is processed again:

- Existing target snapshot is replaced.
- Duplicate order IDs are not accumulated.
- A separate pipeline execution record is created.

This behavior was verified by running the pipeline twice and checking record counts and unique business keys.

## 8. Error Handling and Recovery

The pipeline catches execution exceptions and records:

- Run ID.
- Start and end timestamps.
- Execution status.
- Failure reason.
- Input and validation counts.

The pipeline returns:
- Exit code 0 for reconciliation PASS.
- Exit code 2 for completed reconciliation FAIL.
- Exit code 1 for pipeline execution failure.

A simulated publishing failure followed by a retry is covered by an automated test.

## 9. Reporting and Traceability

Each pipeline execution generates:

- Reconciliation JSON report.
- Source reject CSV.
- Target reject CSV.
- Source-only CSV.
- Target-only CSV.
- Field mismatch CSV.
- Execution log.

Operational metadata includes run ID, source file, timestamps, record counts, and execution status.

## 10. Performance and Scalability

The project was benchmarked with 1,000, 10,000, and 100,000 records.

Observed results:

| Records | Validation | Reconciliation |
|---:|---:|---:|
| 1,000 | 0.257 sec | 0.319 sec |
| 10,000 | 0.442 sec | 1.453 sec |
| 100,000 | 3.898 sec | 14.898 sec |

Reconciliation is the main performance optimization opportunity.

Potential improvements include:
- Reducing repeated DataFrame operations.
- Using more efficient join and comparison strategies.
- Processing large datasets in controlled batches.
- Using database-side aggregation where appropriate.

## 11. Design Trade-offs

### SQLite Instead of a Distributed Database

SQLite provides a simple local database with transactional support and minimal infrastructure requirements.

For this challenge, it keeps the implementation easy to run and test.

For production workloads with concurrent writers and distributed processing, a server-based database may be more appropriate.

### Batch Processing Instead of Streaming

Batch processing keeps the architecture straightforward and supports repeatable reconciliation runs.

For real-time requirements, an event-driven or streaming architecture could be considered.

### Rejecting Invalid Records

Invalid records are isolated instead of silently correcting or publishing them.

This preserves data quality and provides traceability.

### Snapshot Publishing

Snapshot replacement simplifies idempotent publishing for the current full-dataset workflow.

For very large incremental datasets, partitioned or incremental publishing may be more efficient.

## 12. Future Enhancements

- Schema versioning.
- Configurable validation rules.
- Incremental reconciliation.
- Transaction-level failure injection and recovery testing.
- Parallel processing for large datasets.
- Monitoring and alerting.
- Cloud-based storage and orchestration.
