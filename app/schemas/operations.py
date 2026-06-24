import uuid
from datetime import datetime
from decimal import Decimal
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.enum import CurrencyEnum, OperationTypeEnum


class OperationRequest(BaseModel):
    wallet_name: str = Field(max_length=127)
    amount: Annotated[
        Decimal,
        Field(
            max_digits=18,
            decimal_places=4,
            gt=Decimal("0.0000"),
            description="Amount must be positive",
        ),
    ]
    category: str | None = Field(default=None, max_length=127)
    description: str | None = Field(default=None, max_length=255)

    @field_validator("wallet_name")
    @classmethod
    def check_wallet_name(cls, v: str) -> str:
        # Пробелы по краям
        v = v.strip()
        # Пустая строка
        if not v:
            raise ValueError("Wallet name cannot be empty")
        # Проверка на запретные слова
        if v.lower() in ["admin", "root"]:
            raise ValueError("This wallet name is reserved")
        # Если всё ок, возвращаю имя
        return v

    @field_validator("category")
    @classmethod
    def clean_category(cls, v: str | None) -> str | None:
        if v is not None:
            v = v.strip()
            if not v:
                return None
        return v


class OperationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    message: str
    wallet_name: str
    type: OperationTypeEnum
    amount: Decimal
    currency: CurrencyEnum
    category: str | None
    description: str | None
    new_balance: Decimal
    created_at: datetime


class SingleOperationLogResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    wallet_id: uuid.UUID
    type: OperationTypeEnum
    amount: Decimal
    currency: CurrencyEnum
    category: str | None
    description: str | None
    created_at: datetime


class HistoryListResponse(BaseModel):
    operations: list[SingleOperationLogResponse]


class TransferCreateRequest(BaseModel):
    from_wallet_id: uuid.UUID
    to_wallet_id: uuid.UUID
    amount: Decimal = Field(gt=Decimal("0"), description="Amount must be positive")
    description: str | None = Field(default=None, max_length=255)

    @field_validator("to_wallet_id")
    @classmethod
    def not_same_wallets(cls, v: uuid.UUID, info) -> uuid.UUID:
        if "from_wallet_id" in info.data and v == info.data["from_wallet_id"]:
            raise ValueError("Can not transfer to the same wallet")
        return v


class TransferCreateResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    from_wallet_id: uuid.UUID
    from_wallet_name: str
    debiting_amount: Decimal
    debiting_currency: CurrencyEnum
    from_wallet_new_balance: Decimal

    to_wallet_id: uuid.UUID
    to_wallet_name: str
    replenishment_amount: Decimal
    replenishment_currency: CurrencyEnum
    to_wallet_new_balance: Decimal

    type: OperationTypeEnum
    description: str | None
    created_at: datetime
