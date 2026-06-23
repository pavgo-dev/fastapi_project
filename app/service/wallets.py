from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models import UserOrm, WalletOrm
from app.repository import wallets as wallets_repository
from app.schemas.wallets import CreateWalletRequest


def get_balance(session: Session, current_user: UserOrm, wallet_name: str | None = None):
    user_id = current_user.id
    # Если имя кошелька не указано, возвращаем список всех кошельков
    if wallet_name is None:
        wallets = wallets_repository.get_all_wallets(session, user_id)
        return {
            "wallets": [
                {"wallet_name": name, "balance": balance, "currency": currency}
                for name, balance, currency, _ in wallets
            ]
        }
    # Если имя указано, запрашиваем баланс конкретного кошелька
    balance_data = wallets_repository.get_wallet_balance_by_name(session, wallet_name, user_id)
    # Если метод вернул None значит кошелька не существует
    if balance_data is None:
        raise HTTPException(status_code=404, detail=f"Wallet '{wallet_name}' not found")

    # Обращаемся по индексам (0 баланс, 1 валюта)
    return {"wallet_name": wallet_name, "balance": balance_data[0], "currency": balance_data[1]}


def create_wallet(session: Session, current_user: UserOrm, wallet: CreateWalletRequest) -> WalletOrm:
    user_id = current_user.id
    if wallets_repository.get_wallet_balance_by_name(session, wallet.name, user_id) is not None:
        raise HTTPException(status_code=400, detail=f"Wallet '{wallet.name}' already exists")

    # Если кошелька нет, создаём кошелёк
    new_wallet = wallets_repository.create_wallet(
        session, wallet_name=wallet.name, user_id=user_id, amount=wallet.initial_balance, currency=wallet.currency
    )
    session.commit()
    return new_wallet
