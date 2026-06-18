from decimal import Decimal
from typing import Annotated

from sqlalchemy import ForeignKey, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

id_pk = Annotated[int, mapped_column(primary_key=True)]


class UserOrm(Base):
    __tablename__ = "users"

    id: Mapped[id_pk]
    login: Mapped[str] = mapped_column(String(127), unique=True)

    wallets: Mapped[list["WalletOrm"]] = relationship("WalletOrm", back_populates="user", cascade="all, delete-orphan")


class WalletOrm(Base):
    __tablename__ = "wallets"

    id: Mapped[id_pk]
    name: Mapped[str] = mapped_column(String(127))
    balance: Mapped[Decimal] = mapped_column(Numeric(precision=18, scale=4), default=Decimal("0"))
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    user: Mapped["UserOrm"] = relationship("UserOrm", back_populates="wallets")
