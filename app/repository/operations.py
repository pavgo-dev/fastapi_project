import uuid
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.enum import CurrencyEnum, OperationTypeEnum
from app.models import OperationOrm, WalletOrm


def create_operation_log(
    session: Session,
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
    session.flush()  # Генерирует UUIDv7 для лога транзакции
    return log_entry


def get_user_operations_history(session: Session, user_id: uuid.UUID) -> list[OperationOrm]:
    query = (
        select(OperationOrm)
        .join(WalletOrm, OperationOrm.wallet_id == WalletOrm.id)
        .where(WalletOrm.user_id == user_id)
        .order_by(OperationOrm.created_at.desc())  # Сначала самые свежие транзакции
    )
    result = session.execute(query).scalars().all()
    return list(result)
