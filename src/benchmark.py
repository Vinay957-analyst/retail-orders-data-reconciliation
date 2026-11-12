
import time
from pathlib import Path

from src.data_generator import generate_datasets
from src.validation import validate_dataframe
from src.reconciliation import reconcile


def run_benchmark(row_counts=(1000, 10000, 100000)):

    results = []

    for row_count in row_counts:

        print(f"\nBenchmarking {row_count:,} records")

        source, target = generate_datasets(
            rows=row_count,
            seed=42
        )

        start_time = time.perf_counter()

        source_valid, source_rejects = validate_dataframe(source)
        target_valid, target_rejects = validate_dataframe(target)

        validation_time = time.perf_counter() - start_time

        start_time = time.perf_counter()

        reconciliation_result = reconcile(
            source_valid,
            target_valid
        )

        reconciliation_time = time.perf_counter() - start_time

        results.append({
            "records": row_count,
            "source_valid": len(source_valid),
            "target_valid": len(target_valid),
            "source_rejects": len(source_rejects),
            "target_rejects": len(target_rejects),
            "validation_seconds": round(validation_time, 3),
            "reconciliation_seconds": round(reconciliation_time, 3),
            "status": reconciliation_result["summary"]["status"]
        })

        print("Validation time:", round(validation_time, 3), "seconds")
        print("Reconciliation time:", round(reconciliation_time, 3), "seconds")
        print("Status:", reconciliation_result["summary"]["status"])

    output_dir = Path("outputs")
    output_dir.mkdir(exist_ok=True)

    import pandas as pd

    report = pd.DataFrame(results)
    report.to_csv(output_dir / "benchmark_results.csv", index=False)

    print("\nBenchmark completed.")
    print(report.to_string(index=False))
    print("\nSaved: outputs/benchmark_results.csv")


if __name__ == "__main__":
    run_benchmark()
