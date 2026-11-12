
import json

from src.reporting import generate_reports
from src.reconciliation import reconcile


def test_report_generation(tmp_path, valid_orders):

    result = reconcile(
        valid_orders,
        valid_orders.copy()
    )

    report = generate_reports(
        output_dir=tmp_path,
        source_rejects=valid_orders.iloc[0:0].copy(),
        target_rejects=valid_orders.iloc[0:0].copy(),
        reconciliation_result=result,
        run_id="TEST_RUN_001",
        source_file="source_orders.csv",
        target_file="target_orders.csv"
    )

    # Check JSON report
    report_file = tmp_path / "reconciliation_report.json"

    assert report_file.exists()

    # Check output CSV files
    assert (tmp_path / "source_rejects.csv").exists()
    assert (tmp_path / "target_rejects.csv").exists()
    assert (tmp_path / "source_only.csv").exists()
    assert (tmp_path / "target_only.csv").exists()
    assert (tmp_path / "field_mismatches.csv").exists()

    # Verify report content
    with open(report_file, encoding="utf-8") as file:
        saved_report = json.load(file)

    assert saved_report["run_id"] == "TEST_RUN_001"
    assert saved_report["final_status"] == "PASS"
