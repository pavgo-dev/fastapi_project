import uuid
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.enum import CurrencyEnum
from app.models import WalletOrm


async def get_balance_for_update(
    session: AsyncSession, wallet_name: str, user_id: uuid.UUID
) -> tuple[uuid.UUID, Decimal, CurrencyEnum] | None:

    query = (
        select(WalletOrm.id, WalletOrm.balance, WalletOrm.currency)
        .where(WalletOrm.name == wallet_name, WalletOrm.user_id == user_id)
        .with_for_update()  # Защита от Race Condition на этапе чтения
    )
    results = await session.execute(query)
    result = results.one_or_none()
    if result is None:
        return None
    return result.id, result.balance, result.currency


async def get_wallet_balance_by_name(
    session: AsyncSession, wallet_name: str, user_id: uuid.UUID
) -> tuple[Decimal, CurrencyEnum] | None:

    query = select(WalletOrm.balance, WalletOrm.currency).where(
        WalletOrm.name == wallet_name, WalletOrm.user_id == user_id
    )
    results = await session.execute(query)
    result = results.one_or_none()
    if result is None:
        return None
    return result.balance, result.currency


async def get_all_wallets(session: AsyncSession, user_id: uuid.UUID) -> list[WalletOrm]:

    query = select(WalletOrm).where(WalletOrm.user_id == user_id)
    results = await session.execute(query)
    return list(results.scalars().all())


async def create_wallet(
    session: AsyncSession, wallet_name: str, user_id: uuid.UUID, currency: CurrencyEnum, amount: Decimal = Decimal("0")
) -> WalletOrm:

    new_wallet = WalletOrm(name=wallet_name, balance=amount, user_id=user_id, currency=currency)
    session.add(new_wallet)
    await session.flush()
    await session.refresh(new_wallet)
    return new_wallet


async def get_wallet_by_id_for_update(
    session: AsyncSession, user_id: uuid.UUID, wallet_id: uuid.UUID
) -> WalletOrm | None:
    query = (
        select(WalletOrm)
        .where(WalletOrm.id == wallet_id, WalletOrm.user_id == user_id)
        .with_for_update()  # Защита от Race Condition на этапе чтения
    )

    result = await session.execute(query)
    return result.scalar_one_or_none()


async def get_wallet_by_id_for_update_no_user(session: AsyncSession, wallet_id: uuid.UUID) -> WalletOrm | None:
    query = select(WalletOrm).where(WalletOrm.id == wallet_id).with_for_update()
    result = await session.execute(query)
    return result.scalar_one_or_none()


async def get_wallet_by_id_readonly(
    session: AsyncSession, user_id: uuid.UUID, wallet_id: uuid.UUID
) -> WalletOrm | None:

    query = select(WalletOrm).where(WalletOrm.id == wallet_id, WalletOrm.user_id == user_id)
    result = await session.execute(query)
    return result.scalar_one_or_none()
