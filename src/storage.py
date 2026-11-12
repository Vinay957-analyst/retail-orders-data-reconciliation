
import sqlite3
from pathlib import Path
from datetime import datetime, timezone

import pandas as pd


# Business columns in target table
TARGET_COLUMNS = [
    "order_id",
    "customer_id",
    "product_id",
    "quantity",
    "unit_price",
    "total_amount",
    "order_status",
    "order_timestamp"
]


def create_database(db_path):

    db_path = Path(db_path)
    db_path.parent.mkdir(parents=True, exist_ok=True)

    with sqlite3.connect(db_path) as conn:

        # Target business table
        conn.execute("""
            CREATE TABLE IF NOT EXISTS target_orders (
                order_id TEXT PRIMARY KEY,
                customer_id TEXT NOT NULL,
                product_id TEXT NOT NULL,
                quantity INTEGER NOT NULL,
                unit_price REAL NOT NULL,
                total_amount REAL NOT NULL,
                order_status TEXT NOT NULL,
                order_timestamp TEXT NOT NULL,
                run_id TEXT NOT NULL,
                source_file TEXT NOT NULL,
                loaded_at TEXT NOT NULL
            )
        """)

        # Pipeline execution history
        conn.execute("""
            CREATE TABLE IF NOT EXISTS pipeline_runs (
                run_id TEXT PRIMARY KEY,
                started_at TEXT NOT NULL,
                ended_at TEXT,
                status TEXT NOT NULL,
                source_input_count INTEGER DEFAULT 0,
                target_input_count INTEGER DEFAULT 0,
                source_valid_count INTEGER DEFAULT 0,
                target_valid_count INTEGER DEFAULT 0,
                source_reject_count INTEGER DEFAULT 0,
                target_reject_count INTEGER DEFAULT 0,
                failure_reason TEXT
            )
        """)

    print("Database and tables created successfully!")


def publish_target_snapshot(
    valid_target,
    db_path,
    run_id,
    source_file
):

    db_path = Path(db_path)

    create_database(db_path)

    data = valid_target[TARGET_COLUMNS].copy()

    # Add operational metadata
    data["run_id"] = run_id
    data["source_file"] = str(source_file)

    data["loaded_at"] = datetime.now(
        timezone.utc
    ).isoformat()

    # Replace snapshot inside a transaction
    with sqlite3.connect(db_path) as conn:

        conn.execute("BEGIN")

        conn.execute("DELETE FROM target_orders")

        data.to_sql(
            "target_orders",
            conn,
            if_exists="append",
            index=False
        )

        conn.commit()

    print(f"Published {len(data)} records to target database.")


def read_target_snapshot(db_path):

    with sqlite3.connect(db_path) as conn:

        target = pd.read_sql_query(
            """
            SELECT
                order_id,
                customer_id,
                product_id,
                quantity,
                unit_price,
                total_amount,
                order_status,
                order_timestamp
            FROM target_orders
            ORDER BY order_id
            """,
            conn
        )

    return target


def record_pipeline_run(db_path, metrics):

    with sqlite3.connect(db_path) as conn:

        conn.execute("""
            INSERT OR REPLACE INTO pipeline_runs (
                run_id,
                started_at,
                ended_at,
                status,
                source_input_count,
                target_input_count,
                source_valid_count,
                target_valid_count,
                source_reject_count,
                target_reject_count,
                failure_reason
            )
            VALUES (
                :run_id,
                :started_at,
                :ended_at,
                :status,
                :source_input_count,
                :target_input_count,
                :source_valid_count,
                :target_valid_count,
                :source_reject_count,
                :target_reject_count,
                :failure_reason
            )
        """, metrics)

    print("Pipeline execution history recorded.")
