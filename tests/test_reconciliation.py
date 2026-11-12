
from src.validation import validate_dataframe
from src.reconciliation import reconcile


def test_identical_datasets(valid_orders):

    valid, rejects = validate_dataframe(valid_orders)

    result = reconcile(valid, valid.copy())

    assert result["summary"]["status"] == "PASS"

    assert result["summary"]["checks"]["row_count_match"]

    assert result["summary"]["checks"]["business_keys_match"]

    assert result["summary"]["checks"]["field_values_match"]


def test_missing_and_extra_records(valid_orders):

    source, _ = validate_dataframe(valid_orders)

    target = source.iloc[:1].copy()

    result = reconcile(source, target)

    assert result["summary"]["status"] == "FAIL"

    assert result["summary"]["source_only_count"] == 1


def test_field_level_mismatch(valid_orders):

    source, _ = validate_dataframe(valid_orders)

    target = source.copy()

    target.loc[0, "customer_id"] = "CUST0003"

    result = reconcile(source, target)

    assert result["summary"]["status"] == "FAIL"

    assert result["summary"]["field_mismatch_record_count"] == 1


def test_aggregate_mismatch(valid_orders):

    source, _ = validate_dataframe(valid_orders)

    target = source.copy()

    target.loc[0, "quantity"] = 3

    target.loc[0, "total_amount"] = 300.00

    result = reconcile(source, target)

    assert result["summary"]["status"] == "FAIL"

    assert not result["summary"]["aggregates"]["quantity"]["match"]


def test_empty_datasets():

    import pandas as pd

    columns = [
        "order_id", "customer_id", "product_id",
        "quantity", "unit_price", "total_amount",
        "order_status", "order_timestamp"
    ]

    empty = pd.DataFrame(columns=columns)

    result = reconcile(empty, empty.copy())

    assert result["summary"]["status"] == "PASS"
