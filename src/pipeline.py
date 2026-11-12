
import argparse
import logging
import time
import uuid

from pathlib import Path
from datetime import datetime, timezone

import pandas as pd

from src.validation import validate_dataframe
from src.storage import (
    create_database,
    publish_target_snapshot,
    read_target_snapshot,
    record_pipeline_run
)
from src.reconciliation import reconcile
from src.reporting import generate_reports


def get_timestamp():
    return datetime.now(timezone.utc).isoformat()


def read_input_file(file_path):

    file_path = Path(file_path)

    if not file_path.exists():
        raise FileNotFoundError(
            f"Input file not found: {file_path}"
        )

    return pd.read_csv(
        file_path,
        dtype={
            "order_id": "string",
            "customer_id": "string",
            "product_id": "string",
            "order_status": "string",
            "order_timestamp": "string"
        }
    )


def run_pipeline(
    source_path,
    target_path,
    db_path,
    output_dir
):

    run_id = str(uuid.uuid4())

    started_at = get_timestamp()

    start_time = time.perf_counter()

    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Configure logging
    logging.basicConfig(
        filename=output_dir / "run.log",
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
        force=True
    )

    logging.info("Pipeline started: %s", run_id)

    metrics = {
        "run_id": run_id,
        "started_at": started_at,
        "ended_at": None,
        "status": "FAILED",
        "source_input_count": 0,
        "target_input_count": 0,
        "source_valid_count": 0,
        "target_valid_count": 0,
        "source_reject_count": 0,
        "target_reject_count": 0,
        "failure_reason": None
    }

    try:

        # Step 1: Read source and target
        print("\nSTEP 1: Reading input datasets")

        source_raw = read_input_file(source_path)
        target_raw = read_input_file(target_path)

        metrics["source_input_count"] = len(source_raw)
        metrics["target_input_count"] = len(target_raw)

        # Step 2: Validate source
        print("\nSTEP 2: Validating source dataset")

        source_valid, source_rejects = (
            validate_dataframe(source_raw)
        )

        # Step 3: Validate target
        print("\nSTEP 3: Validating target dataset")

        target_valid, target_rejects = (
            validate_dataframe(target_raw)
        )

        metrics["source_valid_count"] = len(source_valid)
        metrics["target_valid_count"] = len(target_valid)

        metrics["source_reject_count"] = len(source_rejects)
        metrics["target_reject_count"] = len(target_rejects)

        # Step 4: Publish target snapshot
        print("\nSTEP 4: Publishing target dataset")

        create_database(db_path)

        publish_target_snapshot(
            target_valid,
            db_path,
            run_id,
            str(target_path)
        )

        # Step 5: Read published target
        print("\nSTEP 5: Reading target database")

        published_target = read_target_snapshot(db_path)

        # Step 6: Reconciliation
        print("\nSTEP 6: Reconciling source and target")

        result = reconcile(
            source_valid,
            published_target
        )

        # Step 7: Generate reports
        print("\nSTEP 7: Generating reports")

        generate_reports(
            output_dir=output_dir,
            source_rejects=source_rejects,
            target_rejects=target_rejects,
            reconciliation_result=result,
            run_id=run_id,
            source_file=source_path,
            target_file=target_path
        )

        # Step 8: Record metrics
        metrics["status"] = result["summary"]["status"]
        metrics["ended_at"] = get_timestamp()

        record_pipeline_run(
            db_path,
            metrics
        )

        elapsed = round(
            time.perf_counter() - start_time,
            3
        )

        print("\n========== PIPELINE SUMMARY ==========")

        print("Run ID:", run_id)
        print("Source input:", metrics["source_input_count"])
        print("Target input:", metrics["target_input_count"])

        print("Source valid:", metrics["source_valid_count"])
        print("Target valid:", metrics["target_valid_count"])

        print("Source rejects:", metrics["source_reject_count"])
        print("Target rejects:", metrics["target_reject_count"])

        print("Reconciliation status:", metrics["status"])
        print("Execution time:", elapsed, "seconds")

        print("\nPipeline execution completed.")

        logging.info(
            "Pipeline completed: %s, status=%s, duration=%s",
            run_id,
            metrics["status"],
            elapsed
        )

        if metrics["status"] == "PASS":
            return 0

        return 2

    except Exception as error:

        metrics["ended_at"] = get_timestamp()
        metrics["failure_reason"] = str(error)

        logging.exception(
            "Pipeline failed: %s",
            run_id
        )

        try:
            create_database(db_path)

            record_pipeline_run(
                db_path,
                metrics
            )

        except Exception:
            logging.exception("Could not save failure metrics")

        print("\nPIPELINE FAILED")
        print("Reason:", error)

        return 1


def main():

    parser = argparse.ArgumentParser(
        description="Retail Orders Data Reconciliation Pipeline"
    )

    parser.add_argument(
        "--source",
        default="data/generated/source_orders.csv"
    )

    parser.add_argument(
        "--target",
        default="data/generated/target_orders.csv"
    )

    parser.add_argument(
        "--db",
        default="outputs/reconciliation.db"
    )

    parser.add_argument(
        "--out",
        default="outputs"
    )

    args = parser.parse_args()

    exit_code = run_pipeline(
        args.source,
        args.target,
        args.db,
        args.out
    )

    raise SystemExit(exit_code)


if __name__ == "__main__":
    main()
