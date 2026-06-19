from decimal import Decimal

# Данные из фикстуры
# user = UserOrm(login="test_user")
# wallet = WalletOrm(name="card", balance=Decimal("200.20"), user_id=test_user.id)


def test_success(client, test_user, test_wallet):
    response = client.post(
        "api/v1/operations/income",
        json={"wallet_name": "card", "amount": 100.65, "description": "salary"},
        headers={"Authorization": f"Bearer {test_user.login}"},
    )

    assert response.json()["message"] == "Income added"
    assert response.json()["wallet"] == test_wallet.name
    assert Decimal(str(response.json()["amount"])) == Decimal("100.65")
    assert response.json()["description"] == "salary"
    assert Decimal(str(response.json()["new_balance"])) == Decimal("300.85")
