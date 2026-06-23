import uuid
from decimal import Decimal
from typing import cast

from sqlalchemy import select, update
from sqlalchemy.orm import Session

from app.enum import CurrencyEnum
from app.models import WalletOrm


def get_balance_for_update(
    session: Session, wallet_name: str, user_id: uuid.UUID
) -> tuple[uuid.UUID, Decimal, CurrencyEnum] | None:

    query = (
        select(WalletOrm.id, WalletOrm.balance, WalletOrm.currency)
        .where(WalletOrm.name == wallet_name, WalletOrm.user_id == user_id)
        .with_for_update()  # Защита от Race Condition на этапе чтения
    )
    result = session.execute(query).one_or_none()
    if result is None:
        return None
    return result.id, result.balance, result.currency


def get_wallet_balance_by_name(
    session: Session, wallet_name: str, user_id: uuid.UUID
) -> tuple[Decimal, CurrencyEnum] | None:
    query = select(WalletOrm.balance, WalletOrm.currency).where(
        WalletOrm.name == wallet_name, WalletOrm.user_id == user_id
    )
    result = session.execute(query).one_or_none()
    if result is None:
        return None
    return result.balance, result.currency


def set_new_balance(session: Session, user_id: uuid.UUID, wallet_name: str, new_balance: Decimal) -> Decimal:
    query = (
        update(WalletOrm)
        .where(WalletOrm.name == wallet_name, WalletOrm.user_id == user_id)
        .values(balance=new_balance)
        .returning(WalletOrm.balance)
    )
    result_balance = session.execute(query).scalar()
    return cast(Decimal, result_balance)


def get_all_wallets(session: Session, user_id: uuid.UUID) -> list[tuple[str, Decimal, CurrencyEnum, uuid.UUID]]:
    query = select(WalletOrm.name, WalletOrm.balance, WalletOrm.currency, WalletOrm.id).where(
        WalletOrm.user_id == user_id
    )
    result = session.execute(query).all()
    return [(row.name, row.balance, row.currency, row.id) for row in result]


def create_wallet(
    session: Session, wallet_name: str, user_id: uuid.UUID, currency: CurrencyEnum, amount: Decimal = Decimal("0")
) -> WalletOrm:
    new_wallet = WalletOrm(name=wallet_name, balance=amount, user_id=user_id, currency=currency)
    session.add(new_wallet)
    session.flush()
    session.refresh(new_wallet)
    return new_wallet


def get_wallet_by_id_for_update(session: Session, user_id: uuid.UUID, wallet_id: uuid.UUID) -> WalletOrm | None:
    query = (
        select(WalletOrm)
        .where(WalletOrm.id == wallet_id, WalletOrm.user_id == user_id)
        .with_for_update()  # Защита от Race Condition на этапе чтения
    )
    return session.scalar(query)


def get_wallet_by_id_readonly(session: Session, user_id: uuid.UUID, wallet_id: uuid.UUID) -> WalletOrm | None:
    query = select(WalletOrm).where(WalletOrm.id == wallet_id, WalletOrm.user_id == user_id)
    return session.scalar(query)
