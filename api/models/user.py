from datetime import datetime, timezone
from uuid import uuid4

from pydantic import UUID4
from sqlalchemy import DateTime, Integer, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from models.base import Base


class Users(Base):
    __tablename__ = "users"

    id: Mapped[UUID4] = mapped_column(Uuid, primary_key=True, default=uuid4)
    full_name: Mapped[str] = mapped_column(String(100), nullable=False)
    phone_number: Mapped[str] = mapped_column(String(15), nullable=False)
    username: Mapped[str] = mapped_column(String(30), nullable=True)
    password: Mapped[str] = mapped_column(String, nullable=True)
    public_key: Mapped[str] = mapped_column(String(100), nullable=False)
    private_key: Mapped[str] = mapped_column(String(100), nullable=False)
    wallet_alias: Mapped[str] = mapped_column(String(100), nullable=True)
    transaction_pin: Mapped[int] = mapped_column(Integer, nullable=True)
    sol_balance: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=datetime.now(tz=timezone.utc)
    )
    last_balance_update: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    def __init__(
        self,
        full_name: str,
        phone_number: str,
        private_key: str,
        public_key: str,
        username: str,
        password: str = None,
        wallet_alias: str = None,
        transaction_pin: int = None,
    ):
        self.full_name = full_name
        self.phone_number = phone_number
        self.username = username
        self.password = password
        self.private_key = private_key
        self.public_key = public_key
        self.wallet_alias = wallet_alias
        self.transaction_pin = transaction_pin

    def to_dict(self) -> dict[str, str | int]:
        return {
            "id": self.id,
            "full_name": self.full_name,
            "phone_number": self.phone_number,
            "username": self.username,
            "public_key": self.public_key,
            "alias": self.wallet_alias,
            "balance": self.sol_balance,
            "created_at": self.created_at,
            "last_balance_update": self.last_balance_update,
        }
