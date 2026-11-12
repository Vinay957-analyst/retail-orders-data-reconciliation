
import sqlite3

from src.storage import (
    create_database,
    publish_target_snapshot,
    read_target_snapshot
)


def test_database_creation(tmp_path):

    db_path = tmp_path / "test.db"

    create_database(db_path)

    with sqlite3.connect(db_path) as conn:

        tables = conn.execute("""
            SELECT name
            FROM sqlite_master
            WHERE type='table'
        """).fetchall()

    table_names = [table[0] for table in tables]

    assert "target_orders" in table_names
    assert "pipeline_runs" in table_names


def test_target_publishing(tmp_path, valid_orders):

    db_path = tmp_path / "test.db"

    publish_target_snapshot(
        valid_orders,
        db_path,
        "RUN001",
        "source_orders.csv"
    )

    target = read_target_snapshot(db_path)

    assert len(target) == 2


def test_idempotent_snapshot(tmp_path, valid_orders):

    db_path = tmp_path / "test.db"

    publish_target_snapshot(
        valid_orders,
        db_path,
        "RUN001",
        "source_orders.csv"
    )

    publish_target_snapshot(
        valid_orders,
        db_path,
        "RUN002",
        "source_orders.csv"
    )

    target = read_target_snapshot(db_path)

    assert len(target) == 2
    assert target["order_id"].is_unique
