# Data Dictionary – Retail Orders Reconciliation System

## 1. Project Overview

This project compares retail order records between a source dataset and a target analytical database to identify data quality issues and reconciliation differences.

## 2. Entity: Orders

**Grain:** One record represents one retail order.

**Primary Business Key:** `order_id`

| Column | Data Type | Nullable | Description |
|---|---|---|---|
| order_id | VARCHAR | No | Unique order identifier |
| customer_id | VARCHAR | No | Customer reference ID |
| product_id | VARCHAR | No | Product reference ID |
| quantity | INTEGER | No | Number of products ordered |
| unit_price | DECIMAL(10,2) | No | Price per unit |
| total_amount | DECIMAL(12,2) | No | Quantity multiplied by unit price |
| order_status | VARCHAR | No | Order processing status |
| order_timestamp | TIMESTAMP | No | Order creation timestamp |

## 3. Reference Entities

### Customers
- Primary key: customer_id
- Relationship: One customer can have multiple orders.

### Products
- Primary key: product_id
- Relationship: One product can appear in multiple orders.

## 4. Business Rules

1. Order ID must be unique.
2. Customer ID must exist in the customer reference dataset.
3. Product ID must exist in the product reference dataset.
4. Quantity must be between 1 and 1000.
5. Unit price must be greater than or equal to zero.
6. Total amount must equal quantity multiplied by unit price.
7. Valid statuses: pending, completed, cancelled, returned.
8. Order timestamp must be a valid ISO-8601 timestamp.
9. Invalid records must be moved to quarantine with rejection reasons.
10. Duplicate business keys must not be loaded into the target.

## 5. Reconciliation Rules

- Compare source and target row counts.
- Compare business keys.
- Identify source-only and target-only records.
- Compare quantity and total amount aggregates.
- Perform field-level comparisons for matching business keys.
- Report all mismatches separately.

## 6. Operational Metadata

The pipeline will maintain:

- run_id
- source_file
- started_at
- ended_at
- run_status
- input_count
- valid_count
- rejected_count
- failure_reason

## 7. Assumptions

- Synthetic datasets are used for reproducibility.
- order_id is the stable business key.
- One order represents one record.
- Source and target follow the same business schema.
- Decimal comparisons allow a tolerance of 0.01.
- Target publishing uses an idempotent snapshot approach for this assessment.
