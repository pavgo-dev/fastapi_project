from decimal import Decimal
from typing import cast

from sqlalchemy import select, update
from sqlalchemy.orm import Session

from app.models import WalletOrm


def is_wallet_exist(session: Session, wallet_name: str) -> bool:
    # with SessionLocal() as session:
    query = select(WalletOrm).where(WalletOrm.name == wallet_name)
    wallet = session.scalar(query)
    return wallet is not None


def add_income(session: Session, wallet_name: str, amount: Decimal) -> Decimal:
    # with SessionLocal() as session:
    query = (
        update(WalletOrm)
        .where(WalletOrm.name == wallet_name)
        .values(balance=WalletOrm.balance + amount)
        .returning(WalletOrm.balance)
    )
    new_balance = session.execute(query).scalar()
    # C помощью cast() говорю линтеру, что это decimal
    return cast(Decimal, new_balance)


def get_wallet_balance_by_name(session: Session, wallet_name: str) -> Decimal:
    # with SessionLocal() as session:
    balance = session.scalar(select(WalletOrm.balance).where(WalletOrm.name == wallet_name))
    return cast(Decimal, balance)


def set_new_balance(session: Session, wallet_name: str, new_balance: Decimal) -> Decimal:
    # with SessionLocal() as session:
    query = (
        update(WalletOrm).where(WalletOrm.name == wallet_name).values(balance=new_balance).returning(WalletOrm.balance)
    )
    result_balance = session.execute(query).scalar()
    return cast(Decimal, result_balance)


def get_all_wallets(session: Session) -> dict[str, Decimal]:
    # with SessionLocal() as session:
    query = select(WalletOrm.name, WalletOrm.balance)
    result = session.execute(query)
    return {name: Decimal(balance) for name, balance in result}


def create_wallet(session: Session, wallet_name: str, amount: Decimal = Decimal("0")) -> WalletOrm:
    # with SessionLocal() as session:
    new_wallet = WalletOrm(name=wallet_name, balance=amount)
    session.add(new_wallet)
    session.flush()
    session.refresh(new_wallet)
    return new_wallet
