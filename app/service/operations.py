from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.enum import OperationTypeEnum
from app.models import UserOrm
from app.repository import operations as operations_repository
from app.repository import wallets as wallets_repository
from app.schemas.operations import OperationRequest


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
        op_type=OperationTypeEnum.income,
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
        op_type=OperationTypeEnum.expense,
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


def show_logs(session: Session, user: UserOrm) -> dict:
    user_id = user.id
    # Cписок ORM объектов из базы
    history_obj_list = operations_repository.get_user_operations_history(session, user_id)

    # Дикт со списком, ConfigDict(from_attributes=True) Pydantic сам прочитает свойства каждого OperationOrm
    return {"operations": history_obj_list}
