import uuid
from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependency import get_current_user, get_session
from app.models import UserOrm
from app.schemas.operations import (
    HistoryListResponse,
    OperationRequest,
    OperationResponse,
    TransferCreateRequest,
    TransferCreateResponse,
)
from app.service import operations as operations_service

router = APIRouter()


@router.post("/operations/income", response_model=OperationResponse)
async def add_income(
    operation: OperationRequest,
    current_user: UserOrm = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    return await operations_service.add_income(session, current_user, operation)


@router.post("/operations/expense", response_model=OperationResponse)
async def add_expense(
    operation: OperationRequest,
    current_user: UserOrm = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    return await operations_service.add_expense(session, current_user, operation)


@router.post("/operations/transfer", response_model=TransferCreateResponse)
async def transfer_between_wallets(
    operation: TransferCreateRequest,
    current_user: UserOrm = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    return await operations_service.transfer_between_wallets(session, current_user, operation)


@router.get("/operations", response_model=HistoryListResponse)
async def show_logs(
    wallet_id: Annotated[uuid.UUID | None, Query()] = None,
    date_from: Annotated[datetime | None, Query()] = None,
    date_to: Annotated[datetime | None, Query()] = None,
    current_user: UserOrm = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    return await operations_service.get_operations_list(session, current_user, wallet_id, date_from, date_to)
