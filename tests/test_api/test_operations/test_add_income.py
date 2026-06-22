from decimal import Decimal

import pytest

# Данные из фикстуры
# user = UserOrm(login="test_user")
# wallet = WalletOrm(name="card", balance=Decimal("200.20"), user_id=test_user.id, currency="RUB")


def test_success(client, test_user, test_wallet):
    response = client.post(
        "api/v1/operations/income",
        json={"wallet_name": "card", "amount": "100.65", "description": "salary"},
        headers={"Authorization": f"Bearer {test_user.login}"},
    )

    assert response.status_code == 200
    assert response.json()["message"] == "Income added"
    assert response.json()["wallet"] == test_wallet.name
    assert Decimal(str(response.json()["amount"])) == Decimal("100.65")
    assert response.json()["description"] == "salary"
    assert Decimal(str(response.json()["new_balance"])) == Decimal("300.85")
    assert response.json()["currency"] == "RUB"


@pytest.mark.parametrize(
    ("wallet_name", "amount"),
    [
        ("card", "-100"),  # Сценарий 1: Отрицательная сумма
        ("card", "0"),  # Сценарий 2: Нулевая сумма
        ("   ", "100"),  # Сценарий 3: Пробелы вместо имени кошелька
    ],
    ids=["negative_amount", "zero_amount", "empty_wallet_name"],
)

# ПАРАМЕТРИЗИРОВАННЫЙ ТЕСТ ДЛЯ ПРОВЕРКИ ВСЕХ ОШИБОК ВАЛИДАЦИИ КОШЕЛЬКА (422)
def test_validation_errors(client, test_user, test_wallet, wallet_name, amount):
    response = client.post(
        "api/v1/operations/income",
        json={"wallet_name": wallet_name, "amount": amount, "description": "Salary"},
        headers={"Authorization": f"Bearer {test_user.login}"},
    )

    assert response.status_code == 422


def test_wallet_not_exists(client, test_user):
    response = client.post(
        "api/v1/operations/income",
        json={"wallet_name": "card", "amount": "100", "description": "Salary"},
        headers={"Authorization": f"Bearer {test_user.login}"},
    )

    assert response.status_code == 404


def test_wallet_wrong_name(client, test_user, test_wallet):
    response = client.post(
        "api/v1/operations/income",
        json={"wallet_name": "cash", "amount": "100", "description": "Salary"},
        headers={"Authorization": f"Bearer {test_user.login}"},
    )

    assert response.status_code == 404


def test_not_authorized(client):
    response = client.post(
        "api/v1/operations/income",
        json={"wallet_name": "card", "amount": "100", "description": "Salary"},
    )

    assert response.status_code == 401
