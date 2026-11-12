
import json
import pandas as pd


BUSINESS_KEY = "order_id"

COMPARE_COLUMNS = [
    "customer_id",
    "product_id",
    "quantity",
    "unit_price",
    "total_amount",
    "order_status",
    "order_timestamp"
]

AGGREGATE_COLUMNS = [
    "quantity",
    "total_amount"
]


def reconcile(source, target):

    # Step 1: Check duplicate business keys
    if source[BUSINESS_KEY].duplicated().any():
        raise ValueError("Duplicate order_id found in source data")

    if target[BUSINESS_KEY].duplicated().any():
        raise ValueError("Duplicate order_id found in target data")

    # Step 2: Compare row counts
    source_count = len(source)
    target_count = len(target)

    row_count_match = source_count == target_count

    # Step 3: Compare business keys
    source_keys = set(source[BUSINESS_KEY])
    target_keys = set(target[BUSINESS_KEY])

    source_only_keys = sorted(source_keys - target_keys)
    target_only_keys = sorted(target_keys - source_keys)

    common_keys = sorted(source_keys & target_keys)

    source_only = source[
        source[BUSINESS_KEY].isin(source_only_keys)
    ].copy()

    target_only = target[
        target[BUSINESS_KEY].isin(target_only_keys)
    ].copy()

    # Step 4: Compare matching records
    merged = source.merge(
        target,
        on=BUSINESS_KEY,
        how="inner",
        suffixes=("_source", "_target")
    )

    mismatch_records = []

    for _, row in merged.iterrows():

        differences = {}

        for column in COMPARE_COLUMNS:

            source_value = row[f"{column}_source"]
            target_value = row[f"{column}_target"]

            # Numeric comparison with tolerance
            if column in ["unit_price", "total_amount"]:

                is_equal = (
                    abs(float(source_value) - float(target_value))
                    <= 0.01
                )

            elif column == "quantity":

                is_equal = int(source_value) == int(target_value)

            else:

                is_equal = str(source_value) == str(target_value)

            if not is_equal:

                differences[column] = {
                    "source": source_value,
                    "target": target_value
                }

        if differences:

            mismatch_records.append({
                "order_id": row[BUSINESS_KEY],
                "mismatch_fields": ",".join(differences.keys()),
                "differences_json": json.dumps(
                    differences,
                    default=str
                )
            })

    field_mismatches = pd.DataFrame(
        mismatch_records,
        columns=[
            "order_id",
            "mismatch_fields",
            "differences_json"
        ]
    )

    # Step 5: Compare business aggregates
    aggregates = {}

    for column in AGGREGATE_COLUMNS:

        source_sum = float(source[column].sum())
        target_sum = float(target[column].sum())

        difference = source_sum - target_sum

        aggregates[column] = {
            "source_sum": round(source_sum, 2),
            "target_sum": round(target_sum, 2),
            "difference": round(difference, 2),
            "match": abs(difference) <= 0.01
        }

    # Step 6: Prepare reconciliation checks
    checks = {

        "row_count_match": row_count_match,

        "business_keys_match": (
            len(source_only_keys) == 0
            and len(target_only_keys) == 0
        ),

        "aggregates_match": all(
            item["match"]
            for item in aggregates.values()
        ),

        "field_values_match": field_mismatches.empty
    }

    # Step 7: Final reconciliation status
    status = (
        "PASS"
        if all(checks.values())
        else "FAIL"
    )

    # Step 8: Prepare summary
    summary = {

        "source_row_count": source_count,

        "target_row_count": target_count,

        "common_key_count": len(common_keys),

        "source_only_count": len(source_only_keys),

        "target_only_count": len(target_only_keys),

        "field_mismatch_record_count": len(field_mismatches),

        "aggregates": aggregates,

        "checks": checks,

        "status": status
    }

    return {

        "summary": summary,

        "source_only": source_only,

        "target_only": target_only,

        "field_mismatches": field_mismatches
    }
