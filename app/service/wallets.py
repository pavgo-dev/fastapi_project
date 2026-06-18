from decimal import Decimal

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models import UserOrm
from app.repository import users as user_repository
from app.repository import wallets as wallets_repository
from app.schemas import CreateWalletRequest, CreateWalletResponse


def get_balance(session: Session, wallet_name: str | None = None):
    # Если имя кошелька не указано, считаем и возвращаем общий баланс
    if wallet_name is None:
        wallets = wallets_repository.get_all_wallets(session)
        return {"total_balance": sum(wallets.values(), Decimal("0"))}
    # Проверяем существует ли запрашиваемый кошелек Fasle=возвращать ошибку
    if not wallets_repository.is_wallet_exist(session, wallet_name):
        raise HTTPException(status_code=404, detail=f"Wallet '{wallet_name}' not found")
    # Если существует возвращаем баланс конкретного кошелька
    balance = wallets_repository.get_wallet_balance_by_name(session, wallet_name)
    return {"wallet": wallet_name, "balance": balance}


def create_wallet(session: Session, current_user: UserOrm, wallet: CreateWalletRequest) -> CreateWalletResponse:
    # Проверяю есть ли пользователь, которому добавляем кошелёк
    user_id = current_user.id
    # Если кошелёк есть, возвращаем ошибку
    if wallets_repository.is_wallet_exist(session, wallet.name):
        raise HTTPException(status_code=400, detail=f"Wallet '{wallet.name}' already exists")

    # Если кошелька нет, создаём кошелёк с изначальным балансом
    new_wallet = wallets_repository.create_wallet(
        session, wallet_name=wallet.name, user_id=user_id, amount=wallet.initial_balance
    )
    session.commit()
    # Возвращаем информацию о созданном кошельке
    return CreateWalletResponse.model_validate(new_wallet)
