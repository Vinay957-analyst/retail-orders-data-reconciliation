
import pandas as pd
import pytest


@pytest.fixture
def valid_orders():

    return pd.DataFrame([
        {
            "order_id": "ORD0000001",
            "customer_id": "CUST0001",
            "product_id": "PROD0001",
            "quantity": 2,
            "unit_price": 100.00,
            "total_amount": 200.00,
            "order_status": "completed",
            "order_timestamp": "2026-01-01T10:00:00Z"
        },
        {
            "order_id": "ORD0000002",
            "customer_id": "CUST0002",
            "product_id": "PROD0002",
            "quantity": 1,
            "unit_price": 150.00,
            "total_amount": 150.00,
            "order_status": "pending",
            "order_timestamp": "2026-01-01T11:00:00Z"
        }
    ])
