from decimal import Decimal


def test_transfer_success_with_exchange(client, test_user, test_wallet, test_wallet_2):
    # test_wallet RUB balance 200.20 transfer 100 RUB
    # test_wallet_2 USD balance 100.50
    # Курс RUB to USD = 0.0105 /// 100 * 0.0105 = 1.0500 USD
    response = client.post(
        "api/v1/operations/transfer",
        json={
            "from_wallet_id": str(test_wallet.id),
            "to_wallet_id": str(test_wallet_2.id),
            "amount": "100.00",
            "description": "Exchange test",
        },
        headers={"Authorization": f"Bearer {test_user.login}"},
    )

    assert response.status_code == 200
    data = response.json()

    # Проверка списания
    assert data["from_wallet_name"] == "card"
    assert Decimal(str(data["from_wallet_new_balance"])).quantize(Decimal("0.01")) == Decimal("100.20")
    assert data["debiting_currency"] == "RUB"

    # Проверка зачисления
    assert data["to_wallet_name"] == "cash"
    assert Decimal(str(data["replenishment_amount"])).quantize(Decimal("0.01")) == Decimal("1.05")
    assert data["replenishment_currency"] == "USD"
    assert Decimal(str(data["to_wallet_new_balance"])).quantize(Decimal("0.01")) == Decimal("101.55")
    assert data["type"] == "transfer"


def test_transfer_insufficient_funds(client, test_user, test_wallet, test_wallet_2):
    response = client.post(
        "api/v1/operations/transfer",
        json={"from_wallet_id": str(test_wallet.id), "to_wallet_id": str(test_wallet_2.id), "amount": "500.00"},
        headers={"Authorization": f"Bearer {test_user.login}"},
    )
    assert response.status_code == 400
    assert "Not enough balance" in response.json()["detail"]


def test_transfer_to_same_wallet_error(client, test_user, test_wallet):
    response = client.post(
        "api/v1/operations/transfer",
        json={"from_wallet_id": str(test_wallet.id), "to_wallet_id": str(test_wallet.id), "amount": "10.00"},
        headers={"Authorization": f"Bearer {test_user.login}"},
    )
    assert response.status_code == 422
    assert "Can not transfer to the same wallet" in response.text


def test_transfer_foreign_wallet_access_denied(client, test_user, test_wallet, test_wallet_3):
    response = client.post(
        "api/v1/operations/transfer",
        json={"from_wallet_id": str(test_wallet.id), "to_wallet_id": str(test_wallet_3.id), "amount": "10.00"},
        headers={"Authorization": f"Bearer {test_user.login}"},
    )
    assert response.status_code == 404
    assert "Wallet for transfer was not found" in response.json()["detail"]
