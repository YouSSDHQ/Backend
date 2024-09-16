from datetime import datetime
from uuid import uuid4

from pydantic import UUID4
from sqlalchemy import UUID, Boolean, DateTime, String
from sqlalchemy.orm import Mapped, mapped_column

from models.base import Base


class Keys(Base):
    __tablename__ = "keys"

    id: Mapped[UUID] = mapped_column(UUID, primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(
        UUID,
    )
    mnemonic: Mapped[String] = mapped_column(String)
    private_key: Mapped[String] = mapped_column(String)
    date_created: Mapped[DateTime] = mapped_column(DateTime, default=datetime.utcnow)
    last_updated: Mapped[DateTime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )
    is_current: Mapped[Boolean] = mapped_column(Boolean, default=True)
    is_expired: Mapped[Boolean] = mapped_column(Boolean, default=False)

    def __init__(
        self,
        user_id: UUID4,
        mnemonic: str,
        private_key: str,
        is_current: bool = True,
        is_expired: bool = False,
    ):
        self.user_id = user_id
        self.mnemonic = mnemonic
        self.private_key = private_key
        self.is_current = is_current
        self.is_expired = is_expired

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "user_id": self.user_id,
            "mnemonic": self.mnemonic,
            "private_key": self.private_key,
            "date_created": self.date_created,
            "last_updated": self.last_updated,
            "is_current": self.is_current,
            "is_expired": self.is_expired,
        }
