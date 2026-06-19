from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.dependency import get_current_user, get_session
from app.models import UserOrm
from app.schemas.operations import OperationRequest, OperationResponse
from app.service import operations as operations_service

router = APIRouter()


@router.post("/operations/income", response_model=OperationResponse)
def add_income(
    operation: OperationRequest, session: Session = Depends(get_session), user: UserOrm = Depends(get_current_user)
):
    return operations_service.add_income(session, user, operation)


@router.post("/operations/expense", response_model=OperationResponse)
def add_expense(
    operation: OperationRequest, session: Session = Depends(get_session), user: UserOrm = Depends(get_current_user)
):
    return operations_service.add_expense(session, user, operation)
