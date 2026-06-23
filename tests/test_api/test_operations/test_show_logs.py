from datetime import UTC, datetime, timedelta
from decimal import Decimal


def test_show_logs_success(client, test_user, test_wallet, test_operation_income, test_operation_expense):
    # История операций запрошена
    response = client.get(
        "api/v1/operations",
        headers={"Authorization": f"Bearer {test_user.login}"},
    )

    # Проверка что вернулся список из двух операций
    assert response.status_code == 200
    data = response.json()

    assert "operations" in data
    operations_list = data["operations"]
    assert len(operations_list) == 2  # Лога должно быть ровно два

    # Проверка по сортировке. Самая свежая - это расход
    assert operations_list[0]["type"] == "expense"
    assert Decimal(str(operations_list[0]["amount"])) == Decimal("50.00")
    assert operations_list[0]["category"] == "Food"

    # Вторая операция - это доход
    assert operations_list[1]["type"] == "income"
    assert Decimal(str(operations_list[1]["amount"])) == Decimal("150.00")
    assert operations_list[1]["category"] == "Work"


def test_show_logs_not_authorized(client):
    response = client.get("api/v1/operations")

    assert response.status_code == 401


def test_show_logs_filter_by_wallet(
    client,
    test_user,
    test_wallet,
    test_wallet_2,
    test_operation_income,  # Фикстура привязана к test_wallet
):
    # В params строго ID первого кошелька
    response = client.get(
        "api/v1/operations",
        params={"wallet_id": str(test_wallet.id)},
        headers={"Authorization": f"Bearer {test_user.login}"},
    )

    assert response.status_code == 200
    operations_list = response.json()["operations"]

    # Должна вернуться только одна операция, связанная с этим кошельком
    assert len(operations_list) == 1
    assert operations_list[0]["wallet_id"] == str(test_wallet.id)


def test_show_logs_foreign_wallet_access_denied(client, test_user_1, test_wallet):
    response = client.get(
        "api/v1/operations",
        params={"wallet_id": str(test_wallet.id)},  # Кошелек первого юзера
        headers={"Authorization": f"Bearer {test_user_1.login}"},  # Токен второго юзера
    )

    assert response.status_code == 404
    assert "not found" in response.json()["detail"]


def test_show_logs_filter_by_date_range(client, test_user, test_operation_income, test_operation_expense):
    now = datetime.now(UTC)
    future_time = now + timedelta(days=5)
    past_time = now - timedelta(days=5)

    # Фильтр "date_from" указывает на будующее (логов быть не должно)
    response_future = client.get(
        "api/v1/operations",
        params={"date_from": future_time.isoformat()},
        headers={"Authorization": f"Bearer {test_user.login}"},
    )
    assert response_future.status_code == 200
    assert len(response_future.json()["operations"]) == 0

    # Фильтр "date_to" указывает на прошлое, логов быть не должно
    response_past = client.get(
        "api/v1/operations",
        params={"date_to": past_time.isoformat()},
        headers={"Authorization": f"Bearer {test_user.login}"},
    )
    assert response_past.status_code == 200
    assert len(response_past.json()["operations"]) == 0
