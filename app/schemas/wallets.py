from decimal import Decimal

from pydantic import BaseModel, Field, field_validator


class CreateWalletRequest(BaseModel):
    name: str = Field(max_length=127)
    initial_balance: Decimal = Field(
        default=Decimal("0"), ge=Decimal("0"), description="Initial balance cannot be negative"
    )

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
    model_config = {"from_attributes": True}

    id: int
    name: str
    user_id: int
    balance: Decimal


class SingleWalletBalanceResponse(BaseModel):
    wallet: str
    balance: Decimal


# Ответ, когда запросили сумму всех кошельков
class TotalBalanceResponse(BaseModel):
    total_balance: Decimal
