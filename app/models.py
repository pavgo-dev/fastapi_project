import uuid
from decimal import Decimal
from typing import Annotated

from sqlalchemy import UUID, ForeignKey, Numeric, String, UniqueConstraint
from sqlalchemy import Enum as SqlalchemyEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from uuid_utils import uuid7

from app.database import Base
from app.enum import CurrencyEnum

id_pk = Annotated[
    uuid.UUID, mapped_column(UUID(as_uuid=True), default=lambda: uuid.UUID(bytes=uuid7().bytes), primary_key=True)
]


class UserOrm(Base):
    __tablename__ = "users"

    id: Mapped[id_pk]
    login: Mapped[str] = mapped_column(String(127), unique=True)

    wallets: Mapped[list["WalletOrm"]] = relationship("WalletOrm", back_populates="user", cascade="all, delete-orphan")


class WalletOrm(Base):
    __tablename__ = "wallets"
    __table_args__ = (UniqueConstraint("user_id", "name", name="uq_user_wallet_name"),)

    id: Mapped[id_pk]
    name: Mapped[str] = mapped_column(String(127))
    balance: Mapped[Decimal] = mapped_column(Numeric(precision=18, scale=4), default=Decimal("0"))
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    currency: Mapped[CurrencyEnum] = mapped_column(
        SqlalchemyEnum(CurrencyEnum), default=CurrencyEnum.RUB, nullable=False
    )

    user: Mapped["UserOrm"] = relationship("UserOrm", back_populates="wallets")
