from decimal import Decimal

import pytest

from app.models import UserOrm, WalletOrm


@pytest.fixture
def test_user(db_session):
    user = UserOrm(login="test_user")
    db_session.add(user)
    db_session.flush()
    return user


@pytest.fixture
def test_wallet(db_session, test_user):
    wallet = WalletOrm(name="card", balance=Decimal("200.20"), user_id=test_user.id, currency="RUB")
    db_session.add(wallet)
    db_session.flush()
    return wallet


@pytest.fixture
def test_wallet_2(db_session, test_user):
    wallet_2 = WalletOrm(name="cash", balance=Decimal("100.50"), user_id=test_user.id, currency="USD")
    db_session.add(wallet_2)
    db_session.flush()
    return wallet_2


@pytest.fixture
def test_user_1(db_session):
    user_1 = UserOrm(login="test_user_1")
    db_session.add(user_1)
    db_session.flush()
    return user_1


@pytest.fixture
def test_wallet_3(db_session, test_user_1):
    wallet_3 = WalletOrm(name="cash", balance=Decimal("5050"), user_id=test_user_1.id, currency="RUB")
    db_session.add(wallet_3)
    db_session.flush()
    return wallet_3
