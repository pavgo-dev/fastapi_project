from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.dependency import get_current_user, get_session
from app.models import UserOrm
from app.schemas.wallets import (
    AllWalletsResponse,
    CreateWalletRequest,
    CreateWalletResponse,
    SingleWalletBalanceResponse,
)
from app.service import wallets as wallets_service

router = APIRouter()


@router.get("/balance", response_model=SingleWalletBalanceResponse)
def get_balance(
    wallet_name: str,
    current_user: UserOrm = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    return wallets_service.get_balance(session, current_user, wallet_name)


@router.post("/wallets", response_model=CreateWalletResponse)
def create_wallet(
    wallet: CreateWalletRequest,
    current_user: UserOrm = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    return wallets_service.create_wallet(session, current_user, wallet)


@router.get("/wallets", response_model=AllWalletsResponse)
def get_wallets(
    current_user: UserOrm = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    wallets_list = wallets_service.get_wallets(session, current_user)
    return {"wallets": wallets_list}
