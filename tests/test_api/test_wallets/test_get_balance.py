from decimal import Decimal

# Данные из фикстуры
# user = UserOrm(login="test_user")
# wallet = WalletOrm(name="card", balance=Decimal("200.20"), user_id=test_user.id, currency="RUB")
# wallet_2 = WalletOrm(name="cash", balance=Decimal("100.50"), user_id=test_user.id, currency="USD")

# user_1 = UserOrm(login="test_user_1")
# wallet_3 = WalletOrm(name="cash", balance=Decimal("5050"), user_id=test_user_1.id, currency="RUB"))


def test_succes(client, test_user, test_wallet, test_wallet_2, test_user_1, test_wallet_3):
    response = client.get(
        "api/v1/balance",
        params={"wallet_name": test_wallet.name},
        headers={"Authorization": f"Bearer {test_user.login}"},
    )

    assert response.status_code == 200
    assert response.json()["wallet_name"] == test_wallet.name
    assert Decimal(str(response.json()["balance"])) == Decimal("200.20")
    assert response.json()["currency"] == "RUB"


def test_succes_1(client, test_user, test_wallet, test_wallet_2, test_user_1, test_wallet_3):
    response = client.get(
        "api/v1/balance",
        params={"wallet_name": test_wallet_3.name},
        headers={"Authorization": f"Bearer {test_user_1.login}"},
    )

    assert response.status_code == 200
    assert response.json()["wallet_name"] == test_wallet_3.name
    assert Decimal(str(response.json()["balance"])) == Decimal("5050")
    assert response.json()["currency"] == "RUB"


def test_wrong_wallet_name(client, test_user, test_wallet, test_wallet_2, test_user_1, test_wallet_3):
    response = client.get(
        "api/v1/balance",
        params={"wallet_name": "wrong_name"},
        headers={"Authorization": f"Bearer {test_user.login}"},
    )

    assert response.status_code == 404


def test_not_authorized_total(client, test_user, test_wallet, test_wallet_2, test_user_1, test_wallet_3):
    response = client.get("api/v1/balance", params={})

    assert response.status_code == 401
    assert response.json() == {"detail": "Not authenticated"}


def test_not_authorized_single(client, test_user, test_wallet, test_wallet_2, test_user_1, test_wallet_3):
    response = client.get("api/v1/balance", params={"wallet_name": "cash"})

    assert response.status_code == 401
    assert response.json() == {"detail": "Not authenticated"}
