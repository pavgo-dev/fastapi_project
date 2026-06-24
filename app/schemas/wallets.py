import uuid
from decimal import Decimal
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.enum import CurrencyEnum


class CreateWalletRequest(BaseModel):
    name: str = Field(max_length=127)
    initial_balance: Annotated[
        Decimal,
        Field(
            max_digits=18,
            decimal_places=4,
            ge=Decimal("0.0000"),
            description="Initial balance cannot be negative",
        ),
    ] = Decimal("0.0000")
    currency: CurrencyEnum = CurrencyEnum.RUB

    @field_validator("name")
    @classmethod
    def check_name(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("Wallet name can not be empty")
        if v.lower() in ["admin", "root"]:
            raise ValueError("Name is reserved")

        return v


class CreateWalletResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    user_id: uuid.UUID
    balance: Decimal
    currency: CurrencyEnum = CurrencyEnum.RUB


class AllWalletsResponse(BaseModel):
    wallets: list[CreateWalletResponse]


class SingleWalletBalanceResponse(BaseModel):
    wallet_name: str
    balance: Decimal
    currency: CurrencyEnum
