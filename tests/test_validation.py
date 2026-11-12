
import pandas as pd
import pytest
from src.validation import validate_dataframe


def test_valid_record():

    data = pd.DataFrame([{
        "order_id": "ORD0000001",
        "customer_id": "CUST0001",
        "product_id": "PROD0001",
        "quantity": 2,
        "unit_price": 100.00,
        "total_amount": 200.00,
        "order_status": "completed",
        "order_timestamp": "2026-01-01T10:00:00Z"
    }])

    valid, rejected = validate_dataframe(data)

    assert len(valid) == 1
    assert len(rejected) == 0


def test_missing_customer():

    data = pd.DataFrame([{
        "order_id": "ORD0000002",
        "customer_id": None,
        "product_id": "PROD0001",
        "quantity": 2,
        "unit_price": 100.00,
        "total_amount": 200.00,
        "order_status": "completed",
        "order_timestamp": "2026-01-01T10:00:00Z"
    }])

    valid, rejected = validate_dataframe(data)

    assert len(valid) == 0
    assert len(rejected) == 1


def test_duplicate_order():

    record = {
        "order_id": "ORD0000003",
        "customer_id": "CUST0001",
        "product_id": "PROD0001",
        "quantity": 2,
        "unit_price": 100.00,
        "total_amount": 200.00,
        "order_status": "completed",
        "order_timestamp": "2026-01-01T10:00:00Z"
    }

    data = pd.DataFrame([record, record])

    valid, rejected = validate_dataframe(data)

    assert len(valid) == 1
    assert len(rejected) == 1
    assert "duplicate_order_id" in rejected.iloc[0]["reject_reason"]


def test_invalid_quantity():

    data = pd.DataFrame([{
        "order_id": "ORD0000004",
        "customer_id": "CUST0001",
        "product_id": "PROD0001",
        "quantity": 0,
        "unit_price": 100.00,
        "total_amount": 0,
        "order_status": "completed",
        "order_timestamp": "2026-01-01T10:00:00Z"
    }])

    valid, rejected = validate_dataframe(data)

    assert len(valid) == 0
    assert len(rejected) == 1


def test_empty_dataset():

    columns = [
        "order_id",
        "customer_id",
        "product_id",
        "quantity",
        "unit_price",
        "total_amount",
        "order_status",
        "order_timestamp"
    ]

    data = pd.DataFrame(columns=columns)

    valid, rejected = validate_dataframe(data)

    assert len(valid) == 0
    assert len(rejected) == 0


def test_malformed_unit_price():

    data = pd.DataFrame([{
        "order_id": "ORD0000005",
        "customer_id": "CUST0001",
        "product_id": "PROD0001",
        "quantity": 2,
        "unit_price": "invalid_price",
        "total_amount": 200.00,
        "order_status": "completed",
        "order_timestamp": "2026-01-01T10:00:00Z"
    }])

    valid, rejected = validate_dataframe(data)

    assert len(valid) == 0
    assert len(rejected) == 1


def test_missing_required_column():

    data = pd.DataFrame([{
        "order_id": "ORD0000006",
        "product_id": "PROD0001",
        "quantity": 2,
        "unit_price": 100.00,
        "total_amount": 200.00,
        "order_status": "completed",
        "order_timestamp": "2026-01-01T10:00:00Z"
    }])

    with pytest.raises(ValueError):
        validate_dataframe(data)


def test_invalid_product_reference():

    data = pd.DataFrame([{
        "order_id": "ORD0000007",
        "customer_id": "CUST0001",
        "product_id": "PROD9999",
        "quantity": 2,
        "unit_price": 100.00,
        "total_amount": 200.00,
        "order_status": "completed",
        "order_timestamp": "2026-01-01T10:00:00Z"
    }])

    valid, rejected = validate_dataframe(data)

    assert len(valid) == 0
    assert len(rejected) == 1
