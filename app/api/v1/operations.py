from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.dependency import get_current_user, get_session
from app.models import UserOrm
from app.schemas.operations import HistoryListResponse, OperationRequest, OperationResponse
from app.service import operations as operations_service

router = APIRouter()


@router.post("/operations/income", response_model=OperationResponse)
def add_income(
    operation: OperationRequest,
    current_user: UserOrm = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    return operations_service.add_income(session, current_user, operation)


@router.post("/operations/expense", response_model=OperationResponse)
def add_expense(
    operation: OperationRequest,
    current_user: UserOrm = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    return operations_service.add_expense(session, current_user, operation)


@router.get("/operations/logs", response_model=HistoryListResponse)
def show_logs(current_user: UserOrm = Depends(get_current_user), session: Session = Depends(get_session)):
    return operations_service.show_logs(session, current_user)
