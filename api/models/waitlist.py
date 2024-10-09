from datetime import datetime, timezone
from uuid import uuid4

from pydantic import UUID4, BaseModel, Field
from sqlalchemy import DateTime, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from models.base import Base


class Waitlist(Base):
    __tablename__ = "waitlist"

    id: Mapped[UUID4] = mapped_column(Uuid, primary_key=True, default=uuid4)
    user_id: Mapped[UUID4] = mapped_column(Uuid, nullable=True)
    phone_number: Mapped[str] = mapped_column(String(20), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=datetime.now(tz=timezone.utc)
    )

    def __init__(self, phone_number: str, user_id=None):
        self.phone_number = phone_number
        self.user_id = user_id

    def to_dict(self) -> dict[str, str]:
        return {
            "id": str(self.id),
            "phone_number": self.phone_number,
            "created_at": str(self.created_at),
        }


class WaitlistJoinRequest(BaseModel):
    phone_number: str = Field(
        ..., description="Phone number", examples=["+2348078807660"]
    )


class WaitlistJoinResponse(BaseModel):
    message: str = Field(..., description="Response message")
