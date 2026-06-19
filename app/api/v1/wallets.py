from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.dependency import get_current_user, get_db
from app.models import UserOrm
from app.schemas.wallets import CreateWalletRequest, CreateWalletResponse
from app.service import wallets as wallets_service

router = APIRouter()


@router.get("/balance")
def get_balance(
    wallet_name: str | None = None,
    session: Session = Depends(get_db),
    current_user: UserOrm = Depends(get_current_user),
):
    return wallets_service.get_balance(session, current_user, wallet_name)


@router.post("/wallets", response_model=CreateWalletResponse)
def create_wallet(
    wallet: CreateWalletRequest, current_user: UserOrm = Depends(get_current_user), session: Session = Depends(get_db)
):
    return wallets_service.create_wallet(session, current_user, wallet)
