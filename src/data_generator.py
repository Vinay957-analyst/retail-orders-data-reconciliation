
import argparse
from pathlib import Path

import numpy as np
import pandas as pd


def generate_datasets(rows=1000, seed=42):

    if rows < 20:
        raise ValueError("Minimum 20 records required.")

    rng = np.random.default_rng(seed)

    # Generate normal order records
    order_numbers = np.arange(1, rows + 1)
    quantities = rng.integers(1, 8, size=rows)
    prices = np.round(rng.uniform(10, 500, size=rows), 2)

    source = pd.DataFrame({
        "order_id": [
            f"ORD{i:07d}" for i in order_numbers
        ],
        "customer_id": [
            f"CUST{i:04d}"
            for i in rng.integers(1, 501, size=rows)
        ],
        "product_id": [
            f"PROD{i:04d}"
            for i in rng.integers(1, 201, size=rows)
        ],
        "quantity": quantities,
        "unit_price": prices,
        "total_amount": np.round(quantities * prices, 2),
        "order_status": rng.choice(
            ["pending", "completed", "cancelled", "returned"],
            size=rows
        ),
        "order_timestamp": pd.date_range(
            "2026-01-01T00:00:00Z",
            periods=rows,
            freq="min"
        ).strftime("%Y-%m-%dT%H:%M:%SZ")
    })

    # Source data quality problems
    source.loc[1, "order_id"] = source.loc[0, "order_id"]
    source.loc[2, "customer_id"] = None
    source.loc[3, "product_id"] = "PROD9999"
    source.loc[4, "quantity"] = 0
    source["unit_price"] = source["unit_price"].astype("object")
    source.loc[5, "unit_price"] = "invalid_price"
    source.loc[6, "total_amount"] = 99999.99

    # Create target from the valid source population
    target = pd.concat(
        [source.iloc[[0]], source.iloc[7:]],
        ignore_index=True
    )

    # Remove one order from target
    target = target[
        target["order_id"] != "ORD0000008"
    ].copy()

    # Add an extra target order
    extra = source.iloc[[7]].copy()
    extra.loc[:, "order_id"] = "ORD_EXTRA_0001"

    target = pd.concat([target, extra], ignore_index=True)

    # Change one shared order's quantity and amount
    target.loc[1, "quantity"] = int(target.loc[1, "quantity"]) + 1
    target.loc[1, "total_amount"] = round(
        int(target.loc[1, "quantity"])
        * float(target.loc[1, "unit_price"]),
        2
    )

    # Invalid customer reference in target
    bad = target.iloc[[-1]].copy()
    bad.loc[:, "order_id"] = "ORD_TARGET_BAD_REF"
    bad.loc[:, "customer_id"] = "CUST9999"

    target = pd.concat([target, bad], ignore_index=True)

    return source, target


def main():

    parser = argparse.ArgumentParser()
    parser.add_argument("--rows", type=int, default=1000)
    parser.add_argument("--seed", type=int, default=42)

    args = parser.parse_args()

    source, target = generate_datasets(
        rows=args.rows,
        seed=args.seed
    )

    output_dir = Path("data/generated")
    output_dir.mkdir(parents=True, exist_ok=True)

    source.to_csv(
        output_dir / "source_orders.csv",
        index=False
    )

    target.to_csv(
        output_dir / "target_orders.csv",
        index=False
    )

    print("\nDATA GENERATION COMPLETED")
    print("Source records:", len(source))
    print("Target records:", len(target))
    print("\nGenerated files:")
    print("data/generated/source_orders.csv")
    print("data/generated/target_orders.csv")


if __name__ == "__main__":
    main()
