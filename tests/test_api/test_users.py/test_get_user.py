# Данные из фикстуры
# user = UserOrm(login="test_user")
# user_1 = UserOrm(login="test_user_1")


def test_success(client, test_user):
    response = client.get(
        "api/v1/users/me",
        params={},
        headers={"Authorization": f"Bearer {test_user.login}"},
    )

    assert response.status_code == 200


def test_not_authorized(client):
    response = client.get(
        "api/v1/users/me",
        params={},
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"


def test_invalid_token(client, test_user, test_user_1):
    response = client.get(
        "api/v1/users/me",
        params={},
        headers={"Authorization": "Bearer invalid_token"},
    )

    assert response.status_code == 401
