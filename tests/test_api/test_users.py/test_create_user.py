import pytest


def test_success(client):
    response = client.post(
        "api/v1/users",
        json={"login": "new user"},
    )

    assert response.status_code == 200
    assert "id" in response.json()
    assert response.json()["login"] == "new user"


@pytest.mark.parametrize(
    ("login"),
    [
        ("abc" * 50),  # Сценарий 1: Длинное имя
        ("   "),  # Сценарий 2: Пустое имя
        ("admin"),  # Сценарий 3: Запрещённое имя
    ],
    ids=["long_name", "empty_name", "reserved_name"],
)
def test_validation_errors(client, login):
    response = client.post(
        "api/v1/users",
        json={"login": login},
    )

    assert response.status_code == 422
