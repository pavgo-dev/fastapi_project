import uuid
from datetime import datetime
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.enum import CurrencyEnum, OperationTypeEnum
from app.models import OperationOrm


async def create_operation_log(
    session: AsyncSession,
    wallet_id: uuid.UUID,
    op_type: OperationTypeEnum,
    amount: Decimal,
    currency: CurrencyEnum,
    category: str | None = None,
    description: str | None = None,
) -> OperationOrm:

    log_entry = OperationOrm(
        wallet_id=wallet_id, type=op_type, amount=amount, currency=currency, category=category, description=description
    )
    session.add(log_entry)
    await session.flush()  # Генерирует UUIDv7 для лога транзакции
    return log_entry


async def get_operations_list(
    session: AsyncSession,
    wallets_ids: list[uuid.UUID],
    date_from: datetime | None,
    date_to: datetime | None,
) -> list[OperationOrm]:

    query = (
        select(OperationOrm)
        .where(OperationOrm.wallet_id.in_(wallets_ids))
        .order_by(OperationOrm.created_at.desc(), OperationOrm.id.desc())
    )
    if date_from:
        query = query.filter(OperationOrm.created_at >= date_from)

    if date_to:
        query = query.filter(OperationOrm.created_at <= date_to)

    result = await session.execute(query)
    return list(result.scalars().all())
