from decimal import Decimal


def test_show_logs_success(client, test_user, test_wallet):
    # 1. Arrange: Две операции (доход и расход), чтобы в базе появились логи
    client.post(
        "api/v1/operations/income",
        json={"wallet_name": test_wallet.name, "amount": "150.00", "description": "Salary", "category": "Work"},
        headers={"Authorization": f"Bearer {test_user.login}"},
    )
    client.post(
        "api/v1/operations/expense",
        json={"wallet_name": test_wallet.name, "amount": "50.00", "description": "Coffee", "category": "Food"},
        headers={"Authorization": f"Bearer {test_user.login}"},
    )

    # 2. ACT: История операций запрошена
    response = client.get(
        "api/v1/operations/logs",
        headers={"Authorization": f"Bearer {test_user.login}"},
    )

    # 3. Assert: Проверка что вернулся список из двух операций
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
    response = client.get("api/v1/operations/logs")

    assert response.status_code == 401
