from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models import UserOrm
from app.repository import wallets as wallets_repository
from app.schemas.operations import OperationRequest


def add_income(session: Session, user: UserOrm, operation: OperationRequest):
    user_id = user.id
    # Репозиторий атомарно обновит баланс. Если вернет None — кошелька нет.
    new_balance = wallets_repository.add_income(session, user_id, operation.wallet_name, operation.amount)

    if new_balance is None:
        raise HTTPException(status_code=404, detail=f"Wallet '{operation.wallet_name}' not found")

    # Беру валюту кошелька для ответа в API
    _, currency = wallets_repository.get_wallet_balance_by_name(session, operation.wallet_name, user_id)
    session.commit()

    return {
        "message": "Income added",
        "wallet": operation.wallet_name,
        "amount": operation.amount,
        "description": operation.description,
        "new_balance": new_balance,
        "currency": currency,
    }


def add_expense(session: Session, user: UserOrm, operation: OperationRequest):
    user_id = user.id

    # Получаю баланс и одновременно БЛОКИРУЕМ строку кошелька в БД (with_for_update)
    # Если вернет None — кошелька нет. Заменяет собой is_wallet_exist().
    wallet_data = wallets_repository.get_balance_for_update(session, operation.wallet_name, user_id)

    if wallet_data is None:
        raise HTTPException(status_code=404, detail=f"Wallet '{operation.wallet_name}' not found")

    # Распаковка кортежа по индексам (0 — баланс, 1 — валюта)
    balance = wallet_data[0]
    currency = wallet_data[1]

    # Проверить хватает ли баланса
    if (new_balance := balance - operation.amount) < 0:
        raise HTTPException(
            status_code=400,
            detail=f"Insufficient funds. Available: {balance} {currency}",
        )

    # Обновить баланс (в рамках той же заблокированной транзакции)
    wallets_repository.set_new_balance(session, user_id, operation.wallet_name, new_balance)
    session.commit()

    return {
        "message": "Expense added",
        "wallet": operation.wallet_name,
        "amount": operation.amount,
        "description": operation.description,
        "new_balance": new_balance,
        "currency": currency,
    }
