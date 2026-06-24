from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import UserOrm, WalletOrm
from app.repository import wallets as wallets_repository
from app.schemas.wallets import CreateWalletRequest


async def get_balance(session: AsyncSession, current_user: UserOrm, wallet_name: str):
    user_id = current_user.id

    balance_data = await wallets_repository.get_wallet_balance_by_name(session, wallet_name, user_id)
    if balance_data is None:
        raise HTTPException(status_code=404, detail=f"Wallet '{wallet_name}' not found")

    return {"wallet_name": wallet_name, "balance": balance_data[0], "currency": balance_data[1]}


async def create_wallet(session: AsyncSession, current_user: UserOrm, wallet: CreateWalletRequest) -> WalletOrm:
    user_id = current_user.id
    if await wallets_repository.get_wallet_balance_by_name(session, wallet.name, user_id) is not None:
        raise HTTPException(status_code=400, detail=f"Wallet '{wallet.name}' already exists")

    new_wallet = await wallets_repository.create_wallet(
        session, wallet_name=wallet.name, user_id=user_id, amount=wallet.initial_balance, currency=wallet.currency
    )
    await session.commit()
    return new_wallet


async def get_wallets(session: AsyncSession, current_user: UserOrm) -> list[dict]:
    wallets = await wallets_repository.get_all_wallets(session, current_user.id)
    return [
        {
            "name": wallet.name,
            "balance": wallet.balance,
            "currency": wallet.currency,
            "id": wallet.id,
            "user_id": wallet.user_id,
        }
        for wallet in wallets
    ]
