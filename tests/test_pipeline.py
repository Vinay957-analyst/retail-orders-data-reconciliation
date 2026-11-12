
import sqlite3
import src.pipeline as pipeline_module

from src.pipeline import run_pipeline


def test_pipeline_handles_missing_source_file(tmp_path):

    db_path = tmp_path / "test.db"
    output_dir = tmp_path / "outputs"

    missing_source = tmp_path / "missing_source.csv"
    target_file = tmp_path / "target.csv"

    exit_code = run_pipeline(
        source_path=missing_source,
        target_path=target_file,
        db_path=db_path,
        output_dir=output_dir
    )

    assert exit_code == 1

    connection = sqlite3.connect(db_path)

    run = connection.execute(
        """
        SELECT status, failure_reason
        FROM pipeline_runs
        """
    ).fetchone()

    connection.close()

    assert run is not None
    assert run[0] == "FAILED"
    assert "Input file not found" in run[1]


def test_pipeline_handles_empty_csv_file(tmp_path):

    db_path = tmp_path / "empty_test.db"
    output_dir = tmp_path / "outputs"

    empty_source = tmp_path / "empty_source.csv"
    target_file = tmp_path / "target.csv"

    # Create an empty CSV file
    empty_source.write_text("", encoding="utf-8")

    exit_code = run_pipeline(
        source_path=empty_source,
        target_path=target_file,
        db_path=db_path,
        output_dir=output_dir
    )

    assert exit_code == 1

    connection = sqlite3.connect(db_path)

    run = connection.execute(
        """
        SELECT status, failure_reason
        FROM pipeline_runs
        """
    ).fetchone()

    connection.close()

    assert run is not None
    assert run[0] == "FAILED"
    assert run[1] is not None


def test_pipeline_handles_malformed_csv(tmp_path):

    db_path = tmp_path / "malformed_test.db"
    output_dir = tmp_path / "outputs"

    malformed_source = tmp_path / "malformed_source.csv"
    target_file = tmp_path / "target.csv"

    malformed_source.write_text(
        'order_id,customer_id,quantity\n'
        '"ORD0001,"CUST0001,2\n',
        encoding="utf-8"
    )

    exit_code = run_pipeline(
        source_path=malformed_source,
        target_path=target_file,
        db_path=db_path,
        output_dir=output_dir
    )

    assert exit_code == 1

    connection = sqlite3.connect(db_path)

    run = connection.execute(
        """
        SELECT status, failure_reason
        FROM pipeline_runs
        """
    ).fetchone()

    connection.close()

    assert run is not None
    assert run[0] == "FAILED"
    assert run[1] is not None

def test_pipeline_handles_schema_change(tmp_path):

    db_path = tmp_path / "schema_test.db"
    output_dir = tmp_path / "outputs"

    source_file = tmp_path / "source.csv"
    target_file = tmp_path / "target.csv"

    # customer_id column is intentionally missing
    source_file.write_text(
        "order_id,product_id,quantity,unit_price,total_amount,order_status,order_timestamp\n"
        "ORD0000001,PROD0001,2,100,200,completed,2026-01-01T10:00:00Z\n",
        encoding="utf-8"
    )

    target_file.write_text(
        "order_id,customer_id,product_id,quantity,unit_price,total_amount,order_status,order_timestamp\n"
        "ORD0000001,CUST0001,PROD0001,2,100,200,completed,2026-01-01T10:00:00Z\n",
        encoding="utf-8"
    )

    exit_code = run_pipeline(
        source_path=source_file,
        target_path=target_file,
        db_path=db_path,
        output_dir=output_dir
    )

    assert exit_code == 1

    connection = sqlite3.connect(db_path)

    run = connection.execute(
        "SELECT status, failure_reason FROM pipeline_runs"
    ).fetchone()

    connection.close()

    assert run is not None
    assert run[0] == "FAILED"
    assert "customer_id" in run[1]

def test_pipeline_handles_duplicate_records(tmp_path):

    db_path = tmp_path / "duplicate_test.db"
    output_dir = tmp_path / "outputs"

    source_file = tmp_path / "source.csv"
    target_file = tmp_path / "target.csv"

    header = (
        "order_id,customer_id,product_id,quantity,unit_price,"
        "total_amount,order_status,order_timestamp\n"
    )

    record = (
        "ORD0000001,CUST0001,PROD0001,2,100,200,"
        "completed,2026-01-01T10:00:00Z\n"
    )

    source_file.write_text(
        header + record + record,
        encoding="utf-8"
    )

    target_file.write_text(
        header + record,
        encoding="utf-8"
    )

    exit_code = run_pipeline(
        source_path=source_file,
        target_path=target_file,
        db_path=db_path,
        output_dir=output_dir
    )

    # Reconciliation may fail, but pipeline should complete.
    assert exit_code == 0

    import pandas as pd

    rejects = pd.read_csv(output_dir / "source_rejects.csv")

    assert len(rejects) == 1
    assert "duplicate_order_id" in rejects.iloc[0]["reject_reason"]


def test_pipeline_handles_invalid_product_reference(tmp_path):

    db_path = tmp_path / "invalid_reference.db"
    output_dir = tmp_path / "outputs"

    source_file = tmp_path / "source.csv"
    target_file = tmp_path / "target.csv"

    header = (
        "order_id,customer_id,product_id,quantity,unit_price,"
        "total_amount,order_status,order_timestamp\n"
    )

    valid_record = (
        "ORD0000001,CUST0001,PROD0001,2,100,200,"
        "completed,2026-01-01T10:00:00Z\n"
    )

    invalid_record = (
        "ORD0000002,CUST0001,PROD9999,2,100,200,"
        "completed,2026-01-01T10:00:00Z\n"
    )

    source_file.write_text(
        header + valid_record + invalid_record,
        encoding="utf-8"
    )

    target_file.write_text(
        header + valid_record,
        encoding="utf-8"
    )

    exit_code = run_pipeline(
        source_path=source_file,
        target_path=target_file,
        db_path=db_path,
        output_dir=output_dir
    )

    assert exit_code == 0

    import pandas as pd

    rejects = pd.read_csv(output_dir / "source_rejects.csv")

    assert len(rejects) == 1
    assert "invalid_product_reference" in rejects.iloc[0]["reject_reason"]


def test_pipeline_retry_after_publish_failure(tmp_path, monkeypatch):

    db_path = tmp_path / "retry_test.db"
    output_dir = tmp_path / "outputs"

    source_file = tmp_path / "source.csv"
    target_file = tmp_path / "target.csv"

    header = (
        "order_id,customer_id,product_id,quantity,unit_price,"
        "total_amount,order_status,order_timestamp\n"
    )

    record = (
        "ORD0000001,CUST0001,PROD0001,2,100,200,"
        "completed,2026-01-01T10:00:00Z\n"
    )

    source_file.write_text(header + record, encoding="utf-8")
    target_file.write_text(header + record, encoding="utf-8")

    # Save the original publishing function
    original_publish = pipeline_module.publish_target_snapshot

    # Simulate a publishing failure
    def fail_publish(*args, **kwargs):
        raise RuntimeError("Simulated publishing failure")

    monkeypatch.setattr(
        pipeline_module,
        "publish_target_snapshot",
        fail_publish
    )

    first_exit_code = run_pipeline(
        source_file,
        target_file,
        db_path,
        output_dir
    )

    assert first_exit_code == 1

    # Restore normal publishing for retry
    monkeypatch.setattr(
        pipeline_module,
        "publish_target_snapshot",
        original_publish
    )

    second_exit_code = run_pipeline(
        source_file,
        target_file,
        db_path,
        output_dir
    )

    assert second_exit_code == 0

    connection = sqlite3.connect(db_path)

    runs = connection.execute(
        "SELECT status FROM pipeline_runs ORDER BY rowid"
    ).fetchall()

    target_count = connection.execute(
        "SELECT COUNT(*) FROM target_orders"
    ).fetchone()[0]

    connection.close()

    assert len(runs) == 2
    assert runs[0][0] == "FAILED"
    assert runs[1][0] == "PASS"
    assert target_count == 1

