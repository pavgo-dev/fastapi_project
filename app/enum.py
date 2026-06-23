from enum import StrEnum, auto


class CurrencyEnum(StrEnum):
    RUB = "RUB"
    USD = "USD"
    EUR = "EUR"


class OperationTypeEnum(StrEnum):
    EXPENSE = auto()
    INCOME = auto()
    TRANSFER = auto()
