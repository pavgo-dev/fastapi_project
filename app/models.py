import uuid
from datetime import UTC, datetime
from decimal import Decimal
from typing import Annotated

from sqlalchemy import UUID, ForeignKey, Index, Numeric, String, UniqueConstraint
from sqlalchemy import Enum as SqlalchemyEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from uuid_utils import uuid7

from app.database import Base
from app.enum import CurrencyEnum, OperationTypeEnum

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
    operations: Mapped[list["OperationOrm"]] = relationship(
        "OperationOrm", back_populates="wallet", cascade="all, delete-orphan"
    )


class OperationOrm(Base):
    __tablename__ = "operations"
    __table_args__ = (Index("idx_wallet_created", "wallet_id", "created_at"),)

    id: Mapped[id_pk]
    wallet_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("wallets.id", ondelete="CASCADE"), nullable=False, index=True
    )
    type: Mapped[OperationTypeEnum] = mapped_column(SqlalchemyEnum(OperationTypeEnum), nullable=False)
    amount: Mapped[Decimal] = mapped_column(Numeric(precision=18, scale=4))
    currency: Mapped[CurrencyEnum] = mapped_column(SqlalchemyEnum(CurrencyEnum), nullable=False)
    category: Mapped[str | None] = mapped_column(default=None)
    description: Mapped[str | None] = mapped_column(String(255), default=None, nullable=True)
    created_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now(UTC), nullable=False)

    wallet: Mapped["WalletOrm"] = relationship("WalletOrm", back_populates="operations")
