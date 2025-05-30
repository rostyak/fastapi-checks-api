import pytest


def test_register_user(client):
    response = client.post("/register", json={
        "name": "Test User",
        "username": "testuser",
        "password": "securepass"
    })
    data = response.json()

    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert response.status_code == 200


def test_login_user(client):
    response = client.post("/login", json={
        "username": "testuser",
        "password": "securepass"
    })
    data = response.json()

    assert response.status_code == 200
    assert "access_token" in data
    assert data["token_type"] == "bearer"


@pytest.fixture
def auth_headers(client):
    client.post("/register", json={
        "name": "Check Creator",
        "username": "creator",
        "password": "pass123"
    })
    token_res = client.post("/login", json={
        "username": "creator",
        "password": "pass123"
    })
    access_token = token_res.json()["access_token"]

    return {"Authorization": f"Bearer {access_token}"}


def test_create_receipt(client, auth_headers):
    response = client.post("/receipts", json={
        "products": [
            {"name": "Apple", "price": 2.5, "quantity": 3},
            {"name": "Banana", "price": 1.0, "quantity": 5}
        ],
        "payment": {"type": "cash", "amount": 20.0}
    }, headers=auth_headers)
    data = response.json()

    assert response.status_code == 200
    assert data["total"] == 2.5 * 3 + 1.0 * 5
    assert data["rest"] == 20.0 - data["total"]
    assert data["products"][0]["name"] == "Apple"


def test_get_receipts(client, auth_headers):
    # Create multiple receipts
    for i in range(3):
        client.post("/receipts", json={
            "products": [{"name": f"Item{i}", "price": 1.0, "quantity": i+1}],
            "payment": {"type": "cashless", "amount": 10.0}
        }, headers=auth_headers)

    # Test pagination
    response = client.get("/receipts?limit=2&offset=1", headers=auth_headers)

    assert response.status_code == 200
    assert len(response.json()) == 2

    # Test filter
    response = client.get(
        "/receipts?payment_type=cashless", headers=auth_headers
    )

    assert response.status_code == 200
    assert all(r["payment"]["type"] == "cashless" for r in response.json())


def test_view_single_receipt(client, auth_headers):
    create_res = client.post("/receipts", json={
        "products": [
            {"name": "ViewItem", "price": 5.0, "quantity": 2}
        ],
        "payment": {"type": "cash", "amount": 20.0}
    }, headers=auth_headers)

    receipt_id = create_res.json()["id"]
    get_res = client.get(f"/receipts/{receipt_id}", headers=auth_headers)

    assert get_res.status_code == 200
    assert get_res.json()["id"] == receipt_id


def test_view_public_receipt(client, auth_headers, db):
    create_res = client.post("/receipts", json={
        "products": [
            {"name": "PublicItem", "price": 4.0, "quantity": 2}
        ],
        "payment": {"type": "cashless", "amount": 20.0}
    }, headers=auth_headers)

    receipt_id = create_res.json()["id"]

    from app.models import Receipt

    receipt = db.query(Receipt).filter(Receipt.id == receipt_id).first()
    public_token = receipt.public_token

    response = client.get(f"/public/receipt/{public_token}")

    assert response.status_code == 200
    assert "Дякуємо за покупку" in response.text


def test_invalid_receipt_creation(client, auth_headers):
    # Insufficient payment
    response = client.post("/receipts", json={
        "products": [
            {"name": "CheapItem", "price": 10.0, "quantity": 1}
        ],
        "payment": {"type": "cash", "amount": 5.0}
    }, headers=auth_headers)

    assert response.status_code == 400
    assert "Insufficient payment" in response.json()["detail"]


def test_invalid_receipt_access(client, auth_headers):
    response = client.get("/receipts/99999", headers=auth_headers)

    assert response.status_code == 404
    assert "Receipt not found" in response.json()["detail"]
