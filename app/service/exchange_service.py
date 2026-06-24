# курсы валют
from decimal import Decimal

import requests

# import httpx   # ДЛЯ БУДУЩЕЙ АСИНХРОННОСТИ
from fastapi import HTTPException

from app.enum import CurrencyEnum

## DEPRECATED
# FALLBACK_RATES: dict[tuple[str, str], Decimal] = {
#     (CurrencyEnum.USD, CurrencyEnum.RUB): Decimal("95.0"),
#     (CurrencyEnum.USD, CurrencyEnum.EUR): Decimal("0.92"),
#     (CurrencyEnum.EUR, CurrencyEnum.RUB): Decimal("103.26"),
#     (CurrencyEnum.RUB, CurrencyEnum.USD): Decimal("0.0105"),
#     (CurrencyEnum.EUR, CurrencyEnum.USD): Decimal("1.087"),
#     (CurrencyEnum.RUB, CurrencyEnum.EUR): Decimal("0.0097"),
# }


def get_exchange_rate(base: CurrencyEnum, target: CurrencyEnum) -> Decimal:
    if base == target:
        return Decimal("1.0")

    base_str = base.lower()
    target_str = target.lower()
    url = f"https://cdn.jsdelivr.net/npm/@fawazahmed0/currency-api@latest/v1/currencies/{base_str}.json"

    try:
        response = requests.get(url, timeout=5.0)
        response.raise_for_status()

        data = response.json()

    except Exception:
        raise HTTPException(status_code=502, detail="Service is unavailable") from None

    currency_rate = data.get(base_str, {})
    rate = currency_rate.get(target_str)

    if rate is not None:
        try:
            return Decimal(str(rate))
        except Exception:
            raise HTTPException(status_code=422, detail="Invalid rate format from provider") from None

    raise HTTPException(status_code=404, detail=f"Exchange rate for {base} - {target} is not found")
