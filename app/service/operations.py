from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models import UserOrm
from app.repository import wallets as wallets_repository
from app.schemas.operations import OperationRequest


def add_income(session: Session, user: UserOrm, operation: OperationRequest):
    user_id = user.id
    # Проверяем существует ли кошелек
    if not wallets_repository.is_wallet_exist(session, user_id, operation.wallet_name):
        raise HTTPException(status_code=404, detail=f"Wallet '{operation.wallet_name}' not found")
    # Добавить доход к балансу кошелька
    new_balance = wallets_repository.add_income(session, user_id, operation.wallet_name, operation.amount)
    session.commit()
    # Возвратить информацию об операции
    return {
        "message": "Income added",
        "wallet": operation.wallet_name,
        "amount": operation.amount,
        "description": operation.description,
        "new_balance": new_balance,
    }


def add_expense(session: Session, user: UserOrm, operation: OperationRequest):
    user_id = user.id
    # Проверяем существует ли кошелек
    if not wallets_repository.is_wallet_exist(session, user_id, operation.wallet_name):
        raise HTTPException(status_code=404, detail=f"Wallet '{operation.wallet_name}' not found")
    # Проверяем хватает ли баланса
    balance = wallets_repository.get_wallet_balance_by_name(session, operation.wallet_name, user_id)
    if (new_balance := balance - operation.amount) < 0:
        raise HTTPException(
            status_code=400,
            detail=f"Insufficient funds. Available: {balance}",
        )
    # Обновляем баланс
    wallets_repository.set_new_balance(session, user_id, operation.wallet_name, new_balance)
    session.commit()
    # Возвратить информацию об операции
    return {
        "message": "Expense added",
        "wallet": operation.wallet_name,
        "amount": operation.amount,
        "description": operation.description,
        "new_balance": new_balance,
    }
