from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.dependency import get_db
from app.schemas import CreateWalletRequest
from app.service import wallets as wallets_service

router = APIRouter()


@router.get("/balance")
def get_balance(wallet_name: str | None = None, session: Session = Depends(get_db)):
    return wallets_service.get_balance(session, wallet_name)


@router.post("/wallets")
def create_wallet(wallet: CreateWalletRequest, session: Session = Depends(get_db)):
    return wallets_service.create_wallet(session, wallet)
