from decimal import Decimal

import pytest

from app.enum import OperationTypeEnum
from app.models import OperationOrm, UserOrm, WalletOrm
from app.repository import operations as operations_repository


@pytest.fixture(autouse=True)
def mock_exchange_rate(mocker):

    def fake_get_exchange_rate(base, target) -> Decimal:
        base_str = str(base).upper()
        target_str = str(target).upper()

        if base_str == target_str:
            return Decimal("1.0")

        rates = {
            ("RUB", "USD"): Decimal("0.0105"),
            ("USD", "RUB"): Decimal("95.0"),
            ("EUR", "USD"): Decimal("1.087"),
            ("USD", "EUR"): Decimal("0.92"),
            ("EUR", "RUB"): Decimal("103.26"),
            ("RUB", "EUR"): Decimal("0.0097"),
        }

        return rates.get((base_str, target_str), Decimal("1.0"))

    # Замена функции в самом модуле, где она используется бизнес-логикой
    mocker.patch("app.service.operations.get_exchange_rate", side_effect=fake_get_exchange_rate)

    return fake_get_exchange_rate


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


@pytest.fixture
def test_operation_income(db_session, test_wallet) -> OperationOrm:
    log_entry = operations_repository.create_operation_log(
        session=db_session,
        wallet_id=test_wallet.id,
        op_type=OperationTypeEnum.INCOME,
        amount=Decimal("150.00"),
        currency=test_wallet.currency,
        category="Work",
        description="Salary",
    )
    return log_entry


@pytest.fixture
def test_operation_expense(db_session, test_wallet) -> OperationOrm:
    log_entry = operations_repository.create_operation_log(
        session=db_session,
        wallet_id=test_wallet.id,
        op_type=OperationTypeEnum.EXPENSE,
        amount=Decimal("50.00"),
        currency=test_wallet.currency,
        category="Food",
        description="Coffee",
    )
    return log_entry
