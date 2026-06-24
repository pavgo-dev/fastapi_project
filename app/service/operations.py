import uuid
from datetime import datetime
from decimal import ROUND_HALF_UP, Decimal

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.enum import OperationTypeEnum
from app.models import UserOrm
from app.repository import operations as operations_repository
from app.repository import wallets as wallets_repository
from app.schemas.operations import OperationRequest, TransferCreateRequest
from app.service.exchange_service import get_exchange_rate


async def add_income(session: AsyncSession, user: UserOrm, operation: OperationRequest) -> dict:
    user_id = user.id

    wallet_data = await wallets_repository.get_balance_for_update(session, operation.wallet_name, user_id)
    if wallet_data is None:
        raise HTTPException(status_code=404, detail=f"Wallet '{operation.wallet_name}' not found")

    wallet_id, balance, currency = wallet_data
    new_balance = balance + operation.amount

    wallet = await wallets_repository.get_wallet_by_id_for_update(session, user_id, wallet_id)

    if wallet is None:
        raise HTTPException(status_code=404, detail=f"Wallet '{operation.wallet_name}' not found")
    wallet.balance = new_balance

    log_entry = await operations_repository.create_operation_log(
        session,
        wallet_id=wallet_id,
        op_type=OperationTypeEnum.INCOME,
        amount=operation.amount,
        currency=currency,
        category=operation.category,
        description=operation.description,
    )

    await session.commit()

    return {
        "id": log_entry.id,
        "message": "Income added",
        "wallet_name": operation.wallet_name,
        "type": log_entry.type,
        "amount": operation.amount,
        "currency": currency,
        "category": operation.category,
        "description": operation.description,
        "new_balance": new_balance,
        "created_at": log_entry.created_at,
    }


async def add_expense(session: AsyncSession, user: UserOrm, operation: OperationRequest) -> dict:
    user_id = user.id

    wallet_data = await wallets_repository.get_balance_for_update(session, operation.wallet_name, user_id)
    if wallet_data is None:
        raise HTTPException(status_code=404, detail=f"Wallet '{operation.wallet_name}' not found")

    wallet_id, balance, currency = wallet_data

    if (new_balance := balance - operation.amount) < 0:
        raise HTTPException(
            status_code=400,
            detail=f"Insufficient funds. Available: {balance} {currency}",
        )

    # Извлекаем объект кошелька и обновляем баланс (Unit of Work)
    wallet = await wallets_repository.get_wallet_by_id_for_update(session, user_id, wallet_id)

    if wallet is None:
        raise HTTPException(status_code=404, detail=f"Wallet '{operation.wallet_name}' not found")
    wallet.balance = new_balance

    log_entry = await operations_repository.create_operation_log(
        session,
        wallet_id=wallet_id,
        op_type=OperationTypeEnum.EXPENSE,
        amount=operation.amount,
        currency=currency,
        category=operation.category,
        description=operation.description,
    )

    await session.commit()

    return {
        "id": log_entry.id,
        "message": "Expense added",
        "wallet_name": operation.wallet_name,
        "type": log_entry.type,
        "amount": operation.amount,
        "currency": currency,
        "category": operation.category,
        "description": operation.description,
        "new_balance": new_balance,
        "created_at": log_entry.created_at,
    }


async def get_operations_list(
    session: AsyncSession,
    user: UserOrm,
    wallet_id: uuid.UUID | None = None,
    date_from: datetime | None = None,
    date_to: datetime | None = None,
) -> dict:

    if wallet_id:
        wallet = await wallets_repository.get_wallet_by_id_readonly(session, user.id, wallet_id)
        if wallet is None:
            raise HTTPException(status_code=404, detail=f"Wallet '{wallet_id}' not found")
        wallets_ids = [wallet.id]
    else:
        wallets = await wallets_repository.get_all_wallets(session, user.id)
        wallets_ids = [wallet.id for wallet in wallets]

    operations = await operations_repository.get_operations_list(session, wallets_ids, date_from, date_to)
    return {"operations": operations}


async def transfer_between_wallets(
    session: AsyncSession,
    user: UserOrm,
    operation: TransferCreateRequest,
) -> dict:

    # ЗАЩИТА ОТ DEADLOCK: Блокируем строки в БД в строго фиксированном порядке по UUID
    if operation.from_wallet_id < operation.to_wallet_id:
        from_wallet = await wallets_repository.get_wallet_by_id_for_update(session, user.id, operation.from_wallet_id)
        # Получателя ищем БЕЗ привязки к user.id отправителя, чтобы разрешить межпользовательские переводы
        to_wallet = await wallets_repository.get_wallet_by_id_for_update_no_user(session, operation.to_wallet_id)
    else:
        to_wallet = await wallets_repository.get_wallet_by_id_for_update_no_user(session, operation.to_wallet_id)
        from_wallet = await wallets_repository.get_wallet_by_id_for_update(session, user.id, operation.from_wallet_id)

    if not from_wallet:
        raise HTTPException(status_code=404, detail="Debiting wallet does not exist")
    if not to_wallet:
        raise HTTPException(status_code=404, detail="Wallet for transfer was not found")

    if (new_from_wallet_balance := from_wallet.balance - operation.amount) < 0:
        raise HTTPException(status_code=400, detail=f"Not enough balance: {from_wallet.balance} {from_wallet.currency}")

    precision = Decimal("0.0001")

    # Расчет курса обмена
    if from_wallet.currency != to_wallet.currency:
        exchange_rate = await get_exchange_rate(from_wallet.currency, to_wallet.currency)
        target_amount = (operation.amount * exchange_rate).quantize(precision, rounding=ROUND_HALF_UP)
    else:
        target_amount = operation.amount

    from_wallet.balance = (new_from_wallet_balance).quantize(precision, rounding=ROUND_HALF_UP)
    to_wallet.balance = (to_wallet.balance + target_amount).quantize(precision, rounding=ROUND_HALF_UP)

    # Логирование операций
    await operations_repository.create_operation_log(
        session,
        wallet_id=from_wallet.id,
        op_type=OperationTypeEnum.TRANSFER,
        amount=operation.amount,
        currency=from_wallet.currency,
        description=operation.description,
    )

    to_wallet_log = await operations_repository.create_operation_log(
        session,
        wallet_id=to_wallet.id,
        op_type=OperationTypeEnum.TRANSFER,
        amount=target_amount,
        currency=to_wallet.currency,
        description=operation.description,
    )

    await session.commit()

    return {
        "from_wallet_id": from_wallet.id,
        "from_wallet_name": from_wallet.name,
        "debiting_amount": operation.amount,
        "debiting_currency": from_wallet.currency,
        "from_wallet_new_balance": from_wallet.balance,
        "to_wallet_id": to_wallet.id,
        "to_wallet_name": to_wallet.name,
        "replenishment_amount": target_amount,
        "replenishment_currency": to_wallet.currency,
        "to_wallet_new_balance": to_wallet.balance,
        "type": OperationTypeEnum.TRANSFER,
        "description": operation.description,
        "created_at": to_wallet_log.created_at,
    }
