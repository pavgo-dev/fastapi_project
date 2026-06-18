from decimal import Decimal
from typing import Annotated

from sqlalchemy import Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base

id_pk = Annotated[int, mapped_column(primary_key=True)]


class WalletOrm(Base):
    __tablename__ = "wallet"

    id: Mapped[id_pk]
    name: Mapped[str] = mapped_column(String(127))
    balance: Mapped[Decimal] = mapped_column(Numeric(precision=18, scale=4), default=Decimal("0"))
