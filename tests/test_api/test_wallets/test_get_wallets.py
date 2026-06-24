from decimal import Decimal

# Данные из фикстуры
# user = UserOrm(login="test_user")
# wallet = WalletOrm(name="card", balance=Decimal("200.20"), user_id=test_user.id, currency="RUB")
# wallet_2 = WalletOrm(name="cash", balance=Decimal("100.50"), user_id=test_user.id, currency="USD")

# user_1 = UserOrm(login="test_user_1")
# wallet_3 = WalletOrm(name="cash", balance=Decimal("5050"), user_id=test_user_1.id, currency="RUB"))


def test_succes(client, test_user, test_wallet, test_wallet_2, test_user_1, test_wallet_3):
    response = client.get(
        "api/v1/wallets",
        params={},
        headers={"Authorization": f"Bearer {test_user.login}"},
    )

    assert response.status_code == 200
    data = response.json()
    wallets = data["wallets"]

    assert len(wallets) == 2

    assert wallets[0]["id"] == str(test_wallet.id)
    assert wallets[0]["name"] == test_wallet.name
    assert wallets[0]["user_id"] == str(test_wallet.user_id)
    assert Decimal(str(wallets[0]["balance"])) == Decimal("200.20")
    assert wallets[0]["currency"] == "RUB"

    assert wallets[1]["id"] == str(test_wallet_2.id)
    assert wallets[1]["name"] == test_wallet_2.name
    assert wallets[1]["user_id"] == str(test_wallet_2.user_id)
    assert Decimal(str(wallets[1]["balance"])) == Decimal("100.50")
    assert wallets[1]["currency"] == "USD"


def test_get_wallets_unauthorized(client):
    response = client.get("api/v1/wallets")

    assert response.status_code == 401
    assert response.json() == {"detail": "Not authenticated"}


def test_get_wallets_empty(client, test_user_1):
    # test_user_1 создан в фикстурах, но у него нет кошельков в базе данных
    response = client.get(
        "api/v1/wallets",
        headers={"Authorization": f"Bearer {test_user_1.login}"},
    )

    assert response.status_code == 200
    data = response.json()
    # Ключ "wallets" должен быть, но список обязан быть пустым
    assert "wallets" in data
    assert data["wallets"] == []


def test_get_wallets_isolation(client, test_user_1, test_wallet):
    # test_wallet принадлежит test_user
    # Запрос от лица test_user_1
    response = client.get(
        "api/v1/wallets",
        headers={"Authorization": f"Bearer {test_user_1.login}"},
    )

    assert response.status_code == 200
    wallets = response.json()["wallets"]

    for wallet in wallets:
        assert wallet["id"] != str(test_wallet.id)


## AI Generated Test
def test_get_wallets_data_types(client, test_user, test_wallet):
    response = client.get(
        "api/v1/wallets",
        headers={"Authorization": f"Bearer {test_user.login}"},
    )

    wallet_data = response.json()["wallets"][0]

    import re

    uuid_regex = r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$"
    assert re.match(uuid_regex, wallet_data["id"])
    assert re.match(uuid_regex, wallet_data["user_id"])

    # Проверяем баланс: в JSON он приходит как строка или число.
    # Убеждаемся, что строка "200.20" парсится в точный Decimal без float-искажений (типа 200.199999)
    assert isinstance(wallet_data["balance"], (str, int, float))
    assert Decimal(str(wallet_data["balance"])) == test_wallet.balance
