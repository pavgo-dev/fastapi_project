from decimal import Decimal

from pydantic import BaseModel, Field, field_validator


class OperationRequest(BaseModel):
    wallet_name: str = Field(max_length=127)
    amount: Decimal = Field(gt=Decimal("0"), description="Amount must be positive")
    description: str | None = Field(default=None, max_length=255)

    @field_validator("wallet_name")
    @classmethod
    def check_wallet_name(cls, v: str) -> str:
        # Убираю пробелы по краям
        v = v.strip()
        # Проверяю не пустая ли строка
        if not v:
            raise ValueError("Wallet name cannot be empty")
        # Проверка на запретные слова
        if v.lower() in ["admin", "root"]:
            raise ValueError("This wallet name is reserved")
        # Если всё ок, возвращаю имя
        return v


class OperationResponse(BaseModel):
    model_config = {"from_attributes": True}

    message: str
    wallet: str
    amount: Decimal
    description: str | None
    new_balance: Decimal
