from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from models.base import Base


class Users(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    full_name: Mapped[str] = mapped_column(String(100), nullable=False)
    phone_number: Mapped[str] = mapped_column(String(15), nullable=False)
    username: Mapped[str] = mapped_column(String(30))
    password: Mapped[str] = mapped_column(String)
    private_key: Mapped[str] = mapped_column(String)
    transaction_pin: Mapped[int] = mapped_column(Integer)

    def __init__(
        self,
        full_name: str,
        phone_number: str,
        username: str,
        password: str,
        private_key: str,
        transaction_pin: int,
    ):
        self.full_name = full_name
        self.phone_number = phone_number
        self.username = username
        self.password = password
        self.private_key = private_key
        self.transaction_pin = transaction_pin

    def to_dict(self) -> dict[str, str | int]:
        return {
            "id": self.id,
            "full_name": self.full_name,
            "phone_number": self.phone_number,
            "username": self.username,
            "password": self.password,
            "private_key": self.private_key,
            "transaction_pin": self.transaction_pin,
        }
