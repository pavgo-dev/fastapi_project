# AAA
# Arrange(подготовить)
# ACT(выполнить действие)
# Assert(Проверить результат)

from decimal import Decimal

import pytest

# Данные из фикстуры
# user = UserOrm(login="test_user")
# wallet = WalletOrm(name="card", balance=Decimal("200.20"), user_id=test_user.id, currency="RUB")

# user_1 = UserOrm(login="test_user_1")
# wallet_3 = WalletOrm(name="cash", balance=Decimal("5050"), user_id=test_user_1.id, currency="RUB")


def test_success(client, test_user, test_wallet):

    # Arrange  ОПРЕДЕЛИЛ в tests/test_api/test_operations/conftest.py

    # user = UserOrm(login="test_user")
    # db_session.add(user)
    # db_session.flush()
    # wallet = WalletOrm(name="card", balance=Decimal("200.20"), user_id=test_user.id)
    # db_session.add(wallet)
    # db_session.flush()

    # ACT
    response = client.post(
        "api/v1/operations/expense",
        json={"wallet_name": "card", "amount": "50.10", "description": "Food"},
        headers={"Authorization": f"Bearer {test_user.login}"},
    )

    # Assert
    assert response.status_code == 200
    assert response.json()["message"] == "Expense added"
    assert response.json()["wallet"] == test_wallet.name
    assert Decimal(str(response.json()["amount"])) == Decimal("50.10")
    assert response.json()["description"] == "Food"
    assert Decimal(str(response.json()["new_balance"])) == Decimal("150.10")
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
        "api/v1/operations/expense",
        json={"wallet_name": wallet_name, "amount": amount, "description": "Food"},
        headers={"Authorization": f"Bearer {test_user.login}"},
    )

    assert response.status_code == 422


def test_wallet_not_exists(client, test_user):
    response = client.post(
        "api/v1/operations/expense",
        json={"wallet_name": "card", "amount": "100", "description": "Food"},
        headers={"Authorization": f"Bearer {test_user.login}"},
    )

    assert response.status_code == 404


def test_wallet_wrong_name(client, test_user, test_wallet):
    response = client.post(
        "api/v1/operations/expense",
        json={"wallet_name": "cash", "amount": "100", "description": "Salary"},
        headers={"Authorization": f"Bearer {test_user.login}"},
    )

    assert response.status_code == 404


def test_not_authorized(client):
    response = client.post(
        "api/v1/operations/expense",
        json={"wallet_name": "card", "amount": "100", "description": "Food"},
    )

    assert response.status_code == 401


def test_insufficient_funds(db_session, client, test_user, test_wallet):
    response = client.post(
        "api/v1/operations/expense",
        json={"wallet_name": "card", "amount": "1000", "description": "Food"},
        headers={"Authorization": f"Bearer {test_user.login}"},
    )

    assert response.status_code == 400

    db_session.expire(test_wallet)
    assert test_wallet.balance == Decimal("200.20")


def test_expense_from_foreign_wallet(client, test_user, test_wallet_3):
    response = client.post(
        "api/v1/operations/expense",
        json={"wallet_name": test_wallet_3.name, "amount": "10.00", "description": "Steal"},
        headers={"Authorization": f"Bearer {test_user.login}"},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == f"Wallet '{test_wallet_3.name}' not found"


def test_expense_exact_zero_balance(client, test_user, test_wallet):
    response = client.post(
        "api/v1/operations/expense",
        json={"wallet_name": test_wallet.name, "amount": "200.20", "description": "All in"},
        headers={"Authorization": f"Bearer {test_user.login}"},
    )

    assert response.status_code == 200
    assert Decimal(str(response.json()["new_balance"])) == Decimal("0.0000")
