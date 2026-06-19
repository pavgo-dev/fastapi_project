from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.dependency import get_current_user, get_db
from app.models import UserOrm
from app.schemas.operations import OperationRequest
from app.service import operations as operations_service

router = APIRouter()


@router.post("/operations/income")
def add_income(
    operation: OperationRequest, session: Session = Depends(get_db), user: UserOrm = Depends(get_current_user)
):
    return operations_service.add_income(session, user, operation)


@router.post("/operations/expense")
def add_expense(
    operation: OperationRequest, session: Session = Depends(get_db), user: UserOrm = Depends(get_current_user)
):
    return operations_service.add_expense(session, user, operation)
