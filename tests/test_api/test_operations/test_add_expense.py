# AAA
# Arrange(подготовить)
# ACT(выполнить действие)
# Assert(Проверить результат)

from decimal import Decimal

import pytest

from app.enum import CurrencyEnum
from app.repository import wallets as wallets_repository

# Данные из фикстуры
# user = UserOrm(login="test_user")
# wallet = WalletOrm(name="card", balance=Decimal("200.20"), user_id=test_user.id, currency="RUB")

# user_1 = UserOrm(login="test_user_1")
# wallet_3 = WalletOrm(name="cash", balance=Decimal("5050"), user_id=test_user_1.id, currency="RUB")


def test_success(client, test_user, test_wallet):

    # Arrange  ОПРЕДЕЛИЛ в tests/test_api/test_operations/conftest.py

    # ACT
    response = client.post(
        "api/v1/operations/expense",
        json={"wallet_name": "card", "amount": "50.10", "description": "Food", "category": "Grocery"},
        headers={"Authorization": f"Bearer {test_user.login}"},
    )

    # Assert
    assert response.status_code == 200

    data = response.json()
    assert "id" in data
    assert "created_at" in data
    assert data["type"] == "expense"
    assert data["category"] == "Grocery"

    assert data["wallet_name"] == test_wallet.name
    assert Decimal(str(data["amount"])) == Decimal("50.10")
    assert data["description"] == "Food"
    assert Decimal(str(data["new_balance"])) == Decimal("150.10")
    assert data["currency"] == "RUB"


@pytest.mark.parametrize(
    ("wallet_name", "amount"),
    [
        ("card", "-100"),  # Отрицательная сумма
        ("card", "0"),  # Нулевая сумма
        ("   ", "100"),  # Пробелы вместо имени кошелька
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


def test_expense_from_foreign_wallet(client, db_session, test_user):
    from app.models import UserOrm

    foreign_user = UserOrm(login="victim_user")
    db_session.add(foreign_user)
    db_session.flush()

    wallets_repository.create_wallet(
        session=db_session,
        wallet_name="cash",
        user_id=foreign_user.id,
        currency=CurrencyEnum.RUB,
        amount=Decimal("500.00"),
    )
    db_session.flush()

    response = client.post(
        "api/v1/operations/expense",
        json={"wallet_name": "cash", "amount": "10.00", "description": "Steal"},
        headers={"Authorization": f"Bearer {test_user.login}"},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Wallet 'cash' not found"


def test_expense_exact_zero_balance(client, test_user, test_wallet):
    response = client.post(
        "api/v1/operations/expense",
        json={"wallet_name": test_wallet.name, "amount": "200.20", "description": "All in"},
        headers={"Authorization": f"Bearer {test_user.login}"},
    )

    assert response.status_code == 200
    assert Decimal(str(response.json()["new_balance"])) == Decimal("0.0000")


def test_expense_one_penny_overflow(client, test_user, test_wallet):
    response = client.post(
        "api/v1/operations/expense",
        json={"wallet_name": test_wallet.name, "amount": "200.21", "description": "Overdraft"},
        headers={"Authorization": f"Bearer {test_user.login}"},
    )

    assert response.status_code == 400
    assert "Insufficient funds" in response.json()["detail"]
