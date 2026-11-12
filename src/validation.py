
import pandas as pd

# Expected source and target schema
REQUIRED_COLUMNS = [
    "order_id",
    "customer_id",
    "product_id",
    "quantity",
    "unit_price",
    "total_amount",
    "order_status",
    "order_timestamp"
]

# Allowed order statuses
VALID_STATUSES = [
    "pending",
    "completed",
    "cancelled",
    "returned"
]

# Reference IDs for our synthetic dataset
VALID_CUSTOMERS = {
    f"CUST{i:04d}" for i in range(1, 501)
}

VALID_PRODUCTS = {
    f"PROD{i:04d}" for i in range(1, 201)
}


def validate_dataframe(df):

    # Step 1: Schema validation
    missing_columns = set(REQUIRED_COLUMNS) - set(df.columns)
    unexpected_columns = set(df.columns) - set(REQUIRED_COLUMNS)

    if missing_columns or unexpected_columns:
        raise ValueError(
            f"Schema mismatch. "
            f"Missing columns: {sorted(missing_columns)}. "
            f"Unexpected columns: {sorted(unexpected_columns)}"
        )

    # Step 2: Work on a copy
    data = df[REQUIRED_COLUMNS].copy()

    # Store rejection reasons for each record
    reasons = pd.Series("", index=data.index, dtype="object")

    def add_reason(mask, message):

        mask = mask.fillna(False)

        reasons.loc[mask] = reasons.loc[mask].apply(
            lambda old: f"{old}; {message}" if old else message
        )

    # Step 3: Required string field validation
    string_columns = [
        "order_id",
        "customer_id",
        "product_id",
        "order_status",
        "order_timestamp"
    ]

    for column in string_columns:

        data[column] = data[column].astype("string").str.strip()

        missing = (
            data[column].isna()
            | data[column].eq("")
        )

        add_reason(
            missing,
            f"missing_required_{column}"
        )

    # Step 4: Numeric data type validation
    numeric_columns = [
        "quantity",
        "unit_price",
        "total_amount"
    ]

    for column in numeric_columns:

        data[column] = pd.to_numeric(
            data[column],
            errors="coerce"
        )

        add_reason(
            data[column].isna(),
            f"invalid_or_missing_{column}"
        )

    # Step 5: Customer reference validation
    add_reason(
        ~data["customer_id"].isin(VALID_CUSTOMERS),
        "invalid_customer_reference"
    )

    # Step 6: Product reference validation
    add_reason(
        ~data["product_id"].isin(VALID_PRODUCTS),
        "invalid_product_reference"
    )

    # Step 7: Order status validation
    add_reason(
        ~data["order_status"].isin(VALID_STATUSES),
        "invalid_order_status"
    )

    # Step 8: Quantity validation
    add_reason(
        data["quantity"].notna()
        & (
            (data["quantity"] < 1)
            | (data["quantity"] > 1000)
            | (data["quantity"] % 1 != 0)
        ),
        "quantity_out_of_range_or_not_integer"
    )

    # Step 9: Unit price validation
    add_reason(
        data["unit_price"].notna()
        & (data["unit_price"] < 0),
        "negative_unit_price"
    )

    # Step 10: Timestamp validation
    parsed_timestamp = pd.to_datetime(
        data["order_timestamp"],
        errors="coerce",
        utc=True
    )

    add_reason(
        parsed_timestamp.isna(),
        "invalid_order_timestamp"
    )

    # Step 11: Derived amount validation
    expected_amount = (
        data["quantity"] * data["unit_price"]
    ).round(2)

    amount_mismatch = (
        data["total_amount"].notna()
        & expected_amount.notna()
        & (
            (data["total_amount"] - expected_amount).abs()
            > 0.01
        )
    )

    add_reason(
        amount_mismatch,
        "total_amount_calculation_mismatch"
    )

    # Step 12: Duplicate business key validation
    duplicate_mask = (
        data["order_id"].notna()
        & data["order_id"].duplicated(keep="first")
    )

    add_reason(
        duplicate_mask,
        "duplicate_order_id"
    )

    # Step 13: Separate valid and rejected records
    rejected_mask = reasons != ""

    rejected_records = data.loc[
        rejected_mask
    ].copy()

    rejected_records["reject_reason"] = (
        reasons.loc[rejected_mask]
    )

    valid_records = data.loc[
        ~rejected_mask
    ].copy()

    # Step 14: Standardize valid records
    valid_records["quantity"] = (
        valid_records["quantity"].astype("int64")
    )

    valid_records["unit_price"] = (
        valid_records["unit_price"].astype("float64").round(2)
    )

    valid_records["total_amount"] = (
        valid_records["total_amount"].astype("float64").round(2)
    )

    valid_records["order_timestamp"] = (
        pd.to_datetime(
            valid_records["order_timestamp"],
            utc=True
        )
        .map(lambda x: x.isoformat().replace("+00:00", "Z"))
    )

    # Step 15: Return both datasets
    return (
        valid_records.reset_index(drop=True),
        rejected_records.reset_index(drop=True)
    )
