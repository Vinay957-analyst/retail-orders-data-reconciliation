
import json
from pathlib import Path
from datetime import datetime, timezone

import pandas as pd


def generate_reports(
    output_dir,
    source_rejects,
    target_rejects,
    reconciliation_result,
    run_id,
    source_file,
    target_file
):

    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    summary = reconciliation_result["summary"]

    # 1. Save source rejected records
    source_rejects.to_csv(
        output_dir / "source_rejects.csv",
        index=False
    )

    # 2. Save target rejected records
    target_rejects.to_csv(
        output_dir / "target_rejects.csv",
        index=False
    )

    # 3. Save source-only records
    reconciliation_result["source_only"].to_csv(
        output_dir / "source_only.csv",
        index=False
    )

    # 4. Save target-only records
    reconciliation_result["target_only"].to_csv(
        output_dir / "target_only.csv",
        index=False
    )

    # 5. Save field-level mismatches
    reconciliation_result["field_mismatches"].to_csv(
        output_dir / "field_mismatches.csv",
        index=False
    )

    # 6. Prepare machine-readable JSON report
    report = {

        "project_name": "Retail Orders Data Reconciliation",

        "run_id": run_id,

        "generated_at": datetime.now(
            timezone.utc
        ).isoformat(),

        "input_files": {
            "source_file": str(source_file),
            "target_file": str(target_file)
        },

        "data_quality": {
            "source_rejected_count": len(source_rejects),
            "target_rejected_count": len(target_rejects)
        },

        "reconciliation": summary,

        "output_files": {
            "source_rejects": "source_rejects.csv",
            "target_rejects": "target_rejects.csv",
            "source_only": "source_only.csv",
            "target_only": "target_only.csv",
            "field_mismatches": "field_mismatches.csv"
        },

        "final_status": summary["status"]
    }

    # 7. Write JSON report
    report_path = (
        output_dir / "reconciliation_report.json"
    )

    with open(report_path, "w", encoding="utf-8") as file:

        json.dump(
            report,
            file,
            indent=4,
            default=str
        )

    print("\nREPORT GENERATION COMPLETED")

    print("Source rejects:", len(source_rejects))
    print("Target rejects:", len(target_rejects))

    print(
        "Field mismatches:",
        len(reconciliation_result["field_mismatches"])
    )

    print("Final status:", summary["status"])

    print("Report saved:", report_path)

    return report
