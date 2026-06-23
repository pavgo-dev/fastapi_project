import uuid
from datetime import datetime

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.enum import OperationTypeEnum
from app.models import UserOrm
from app.repository import operations as operations_repository
from app.repository import wallets as wallets_repository
from app.schemas.operations import OperationRequest, TransferCreateRequest
from app.service.exchange_service import get_exchange_rate


def add_income(session: Session, user: UserOrm, operation: OperationRequest) -> dict:
    user_id = user.id

    # Блокировать кошелек и получить его данные (нужен wallet_id)
    wallet_data = wallets_repository.get_balance_for_update(session, operation.wallet_name, user_id)
    if wallet_data is None:
        raise HTTPException(status_code=404, detail=f"Wallet '{operation.wallet_name}' not found")

    wallet_id, balance, currency = wallet_data
    new_balance = balance + operation.amount

    # Обновлить кошелек
    wallets_repository.set_new_balance(session, user_id, operation.wallet_name, new_balance)

    # Записать лог в историю операций
    log_entry = operations_repository.create_operation_log(
        session,
        wallet_id=wallet_id,
        op_type=OperationTypeEnum.INCOME,
        amount=operation.amount,
        currency=currency,
        category=operation.category,
        description=operation.description,
    )

    session.commit()

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


def add_expense(session: Session, user: UserOrm, operation: OperationRequest) -> dict:
    user_id = user.id

    # Заблокировать кошелек и получить данные
    wallet_data = wallets_repository.get_balance_for_update(session, operation.wallet_name, user_id)
    if wallet_data is None:
        raise HTTPException(status_code=404, detail=f"Wallet '{operation.wallet_name}' not found")

    wallet_id, balance, currency = wallet_data

    if (new_balance := balance - operation.amount) < 0:
        raise HTTPException(
            status_code=400,
            detail=f"Insufficient funds. Available: {balance} {currency}",
        )

    # Обновить кошель
    wallets_repository.set_new_balance(session, user_id, operation.wallet_name, new_balance)

    # Записать лог в историю операций
    log_entry = operations_repository.create_operation_log(
        session,
        wallet_id=wallet_id,
        op_type=OperationTypeEnum.EXPENSE,
        amount=operation.amount,
        currency=currency,
        category=operation.category,
        description=operation.description,
    )

    session.commit()

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


def get_operations_list(
    session: Session,
    user: UserOrm,
    wallet_id: uuid.UUID | None = None,
    date_from: datetime | None = None,
    date_to: datetime | None = None,
) -> dict:

    if wallet_id:
        wallet = wallets_repository.get_wallet_by_id_readonly(session, user.id, wallet_id)
        if wallet is None:
            raise HTTPException(status_code=404, detail=f"Wallet '{wallet_id}' not found")
        wallets_ids = [wallet.id]
    else:
        wallets = wallets_repository.get_all_wallets(session, user.id)
        wallets_ids = [wallet[3] for wallet in wallets]

    operations = operations_repository.get_operations_list(session, wallets_ids, date_from, date_to)
    return {"operations": operations}


def transfer_between_wallets(
    session: Session,
    user: UserOrm,
    operation: TransferCreateRequest,
) -> dict:  # OperationResponse Schema

    from_wallet = wallets_repository.get_wallet_by_id_for_update(session, user.id, operation.from_wallet_id)
    to_wallet = wallets_repository.get_wallet_by_id_for_update(session, user.id, operation.to_wallet_id)

    if not from_wallet:
        raise HTTPException(status_code=404, detail="Debiting wallet did not exists")
    if not to_wallet:
        raise HTTPException(status_code=404, detail="Wallet for transfer was not found")

    if (new_from_walet_balance := from_wallet.balance - operation.amount) < 0:
        raise HTTPException(status_code=400, detail=f"Not enough balance: {from_wallet.balance} {from_wallet.currency}")

    # Привести валюты по курсу
    if from_wallet.currency != to_wallet.currency:
        exchange_rate = get_exchange_rate(from_wallet.currency, to_wallet.currency)
        target_amount = round(operation.amount * exchange_rate, 4)  # Сколько придёт получателю
    else:
        target_amount = operation.amount  # Сколько придёт получателю

    # Обновить кошель
    # wallets_repository.set_new_balance(session, user.id, from_wallet.name, new_from_walet_balance)
    # wallets_repository.set_new_balance(session, user.id, to_wallet.name, to_wallet.balance + target_amount)

    from_wallet.balance = round(new_from_walet_balance, 4)
    to_wallet.balance = round(to_wallet.balance + target_amount, 4)

    # Алихимия через Persistent Map должна сделать автоматом, нужно проверить
    # session.add(from_wallet)
    # session.add(to_wallet)

    # Записать историю операций
    operations_repository.create_operation_log(
        session,
        wallet_id=from_wallet.id,
        op_type=OperationTypeEnum.EXPENSE,
        amount=operation.amount,
        currency=from_wallet.currency,
        description=operation.description,
    )

    to_wallet_log = operations_repository.create_operation_log(
        session,
        wallet_id=to_wallet.id,
        op_type=OperationTypeEnum.INCOME,
        amount=target_amount,
        currency=to_wallet.currency,
        description=operation.description,
    )

    session.commit()

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
