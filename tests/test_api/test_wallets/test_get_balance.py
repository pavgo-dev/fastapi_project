from decimal import Decimal

# Данные из фикстуры
# user = UserOrm(login="test_user")
# wallet = WalletOrm(name="card", balance=Decimal("200.20"), user_id=test_user.id)
# wallet_2 = WalletOrm(name="cash", balance=Decimal("100.50"), user_id=test_user.id)

# user_1 = UserOrm(login="test_user_1")
# wallet_3 = WalletOrm(name="cash", balance=Decimal("5050"), user_id=test_user_1.id)


def test_succes_single_balance_1(client, test_user, test_wallet, test_wallet_2, test_user_1, test_wallet_3):
    response = client.get(
        "api/v1/balance",
        params={"wallet_name": test_wallet.name},
        headers={"Authorization": f"Bearer {test_user.login}"},
    )

    assert response.status_code == 200
    assert response.json()["wallet"] == test_wallet.name
    assert Decimal(str(response.json()["balance"])) == Decimal("200.20")


def test_succes_total_balance_1(client, test_user, test_wallet, test_wallet_2, test_user_1, test_wallet_3):
    response = client.get(
        "api/v1/balance",
        params={},
        headers={"Authorization": f"Bearer {test_user.login}"},
    )

    assert response.status_code == 200
    assert Decimal(str(response.json()["total_balance"])) == Decimal("300.70")


def test_succes_single_balance_2(client, test_user, test_wallet, test_wallet_2, test_user_1, test_wallet_3):
    response = client.get(
        "api/v1/balance",
        params={"wallet_name": test_wallet_3.name},
        headers={"Authorization": f"Bearer {test_user_1.login}"},
    )

    assert response.status_code == 200
    assert response.json()["wallet"] == test_wallet_3.name
    assert Decimal(str(response.json()["balance"])) == Decimal("5050")


def test_succes_total_balance_2(client, test_user, test_wallet, test_wallet_2, test_user_1, test_wallet_3):
    response = client.get(
        "api/v1/balance",
        params={},
        headers={"Authorization": f"Bearer {test_user_1.login}"},
    )

    assert response.status_code == 200
    assert Decimal(str(response.json()["total_balance"])) == Decimal("5050")


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


def test_not_authorized_single(client, test_user, test_wallet, test_wallet_2, test_user_1, test_wallet_3):
    response = client.get("api/v1/balance", params={"wallet_name": "cash"})

    assert response.status_code == 401
