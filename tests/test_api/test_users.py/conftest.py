import pytest

from app.models import UserOrm


@pytest.fixture
def test_user(db_session):
    user = UserOrm(login="test_user")
    db_session.add(user)
    db_session.flush()
    return user


@pytest.fixture
def test_user_1(db_session):
    user_1 = UserOrm(login="test_user_1")
    db_session.add(user_1)
    db_session.flush()
    return user_1
