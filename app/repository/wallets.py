import uuid
from decimal import Decimal
from typing import cast

from sqlalchemy import select, update
from sqlalchemy.orm import Session

from app.models import WalletOrm


def is_wallet_exist(session: Session, user_id: uuid.UUID, wallet_name: str) -> bool:
    query = select(WalletOrm).where(WalletOrm.name == wallet_name, WalletOrm.user_id == user_id)
    wallet = session.scalar(query)
    return wallet is not None


def add_income(session: Session, user_id: uuid.UUID, wallet_name: str, amount: Decimal) -> Decimal:
    query = (
        update(WalletOrm)
        .where(WalletOrm.name == wallet_name, WalletOrm.user_id == user_id)
        .values(balance=WalletOrm.balance + amount)
        .returning(WalletOrm.balance)
    )
    new_balance = session.execute(query).scalar()
    # C помощью cast() говорю линтеру, что это decimal
    return cast(Decimal, new_balance)


def get_wallet_balance_by_name(session: Session, wallet_name: str, user_id: uuid.UUID) -> Decimal:
    balance = session.scalar(
        select(WalletOrm.balance).where(WalletOrm.name == wallet_name, WalletOrm.user_id == user_id)
    )
    return cast(Decimal, balance)


def set_new_balance(session: Session, user_id: uuid.UUID, wallet_name: str, new_balance: Decimal) -> Decimal:
    query = (
        update(WalletOrm)
        .where(WalletOrm.name == wallet_name, WalletOrm.user_id == user_id)
        .values(balance=new_balance)
        .returning(WalletOrm.balance)
    )
    result_balance = session.execute(query).scalar()
    return cast(Decimal, result_balance)


def get_all_wallets(session: Session, user_id: uuid.UUID) -> dict[str, Decimal]:
    query = select(WalletOrm.name, WalletOrm.balance).where(WalletOrm.user_id == user_id)
    result = session.execute(query)
    return {name: Decimal(balance) for name, balance in result}


def create_wallet(session: Session, wallet_name: str, user_id: uuid.UUID, amount: Decimal = Decimal("0")) -> WalletOrm:
    new_wallet = WalletOrm(name=wallet_name, balance=amount, user_id=user_id)
    session.add(new_wallet)
    session.flush()
    session.refresh(new_wallet)
    return new_wallet
