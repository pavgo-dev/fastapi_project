# курсы валют
from decimal import Decimal

from app.enum import CurrencyEnum

FALLBACK_RATES: dict[tuple[str, str], Decimal] = {
    (CurrencyEnum.USD, CurrencyEnum.RUB): Decimal("95.0"),
    (CurrencyEnum.USD, CurrencyEnum.EUR): Decimal("0.92"),
    (CurrencyEnum.EUR, CurrencyEnum.RUB): Decimal("103.26"),
    (CurrencyEnum.RUB, CurrencyEnum.USD): Decimal("0.0105"),
    (CurrencyEnum.EUR, CurrencyEnum.USD): Decimal("1.087"),
    (CurrencyEnum.RUB, CurrencyEnum.EUR): Decimal("0.0097"),
}


def get_exchange_rate(base: CurrencyEnum, target: CurrencyEnum) -> Decimal:
    return FALLBACK_RATES.get((base, target), Decimal("1"))
