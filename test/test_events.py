def test_post_events(client, auth_headers):
    response = client.post("/events", json={
        "vendor_id": "V001",
        "order_id": "ORD123",
        "items": [
            {"sku": "SKU1", "qty": 2, "unit_price": 100},
            {"sku": "SKU2", "qty": 1, "unit_price": 50}
        ],
        "timestamp": "2025-07-29T14:00:00Z"
    }, headers=auth_headers)

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "queued"
    assert data["order_id"] == "ORD123"