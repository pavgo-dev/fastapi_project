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
    wallet = WalletOrm(name="card", balance=Decimal("200.20"), user_id=test_user.id)
    db_session.add(wallet)
    db_session.flush()
    return wallet
