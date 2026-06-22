from decimal import Decimal

import pytest

# Данные из фикстуры
# user = UserOrm(login="test_user")
# wallet = WalletOrm(name="card", balance=Decimal("200.20"), user_id=test_user.id)
# wallet_2 = WalletOrm(name="cash", balance=Decimal("100.50"), user_id=test_user.id)

# user_1 = UserOrm(login="test_user_1")
# wallet_3 = WalletOrm(name="cash", balance=Decimal("5050"), user_id=test_user_1.id)


def test_succes(client, test_user, test_wallet, test_wallet_2, test_user_1, test_wallet_3):
    response = client.post(
        "api/v1/wallets",
        json={"name": "my finance", "initial_balance": "0"},
        headers={"Authorization": f"Bearer {test_user.login}"},
    )

    assert response.status_code == 200
    assert response.json()["name"] == "my finance"
    assert Decimal(str(response.json()["balance"])) == Decimal("0")


def test_succes_positive_balance(client, test_user, test_wallet, test_wallet_2, test_user_1, test_wallet_3):
    response = client.post(
        "api/v1/wallets",
        json={"name": "my finance", "initial_balance": "1000.50"},
        headers={"Authorization": f"Bearer {test_user.login}"},
    )

    assert response.status_code == 200
    assert response.json()["name"] == "my finance"
    assert Decimal(str(response.json()["balance"])) == Decimal("1000.50")


def test_succes_wallet_exists_another_user(client, test_user, test_wallet, test_wallet_2, test_user_1, test_wallet_3):
    response = client.post(
        "api/v1/wallets",
        json={"name": test_wallet.name, "initial_balance": "0"},
        headers={"Authorization": f"Bearer {test_user_1.login}"},
    )

    assert response.status_code == 200
    assert response.json()["name"] == test_wallet.name
    assert Decimal(str(response.json()["balance"])) == Decimal("0")


def test_wallet_exists(client, test_user, test_wallet):
    response = client.post(
        "api/v1/wallets",
        json={"name": test_wallet.name, "initial_balance": "0"},
        headers={"Authorization": f"Bearer {test_user.login}"},
    )

    assert response.status_code == 400


@pytest.mark.parametrize(
    ("name", "balance"),
    [
        ("abc" * 50, "0"),  # Сценарий 1: Длинное имя
        ("   ", "200"),  # Сценарий 2: Пустое имя
        ("admin", "0"),  # Сценарий 3: Запрещённое имя
        ("normal name", "-1000"),  # Сценарий 4: Негативный баланс
    ],
    ids=["long_name", "empty_name", "reserved_name", "negative_initial_balance"],
)
def test_validation_errors(client, test_user, name, balance):
    response = client.post(
        "api/v1/wallets",
        json={"name": name, "initial_balance": balance},
        headers={"Authorization": f"Bearer {test_user.login}"},
    )

    assert response.status_code == 422
