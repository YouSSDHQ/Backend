from typing import Union

from solders.keypair import Keypair
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from models.user import Users


class UserService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_user(self, user_dict: dict):
        username = user_dict.get("username")
        phone_number = user_dict.get("phone_number")
        full_name = user_dict.get("full_name")
        existing_user = await self.get_user_by_phone_number(phone_number)
        if existing_user:
            return "END User already exists"

        keypair = Keypair()
        user = Users(
            username=username,
            phone_number=phone_number,
            full_name=full_name,
            public_key=str(keypair.pubkey()),
            private_key=keypair.to_json(),
        )
        self.session.add(user)

        await self.session.commit()
        return user

    async def get_user(self, user_id: Union[int | str]):
        result = await self.session.execute(
            select(Users).where(or_(Users.id == user_id, Users.phone_number == user_id))
        )
        return result.scalar_one_or_none()

    async def get_user_by_phone_number(self, phone_number: str):
        result = await self.session.execute(
            select(Users).filter(Users.phone_number == phone_number)
        )
        return result.scalar_one_or_none()

    async def get_user_public_key(self, user_id: int):
        user = await self.get_user(user_id)
        return user.public_key if user else None

    async def update_user_balance(self, user_id: int, new_balance: float):
        user = await self.get_user(user_id)
        if user:
            user.balance = new_balance
            await self.session.commit()
        return user

    async def get_all_users(self):
        result = await self.session.execute(select(Users))
        return result.scalars().all()

    async def delete_user(self, user_id: int):
        user = await self.get_user(user_id)
        if user:
            await self.session.delete(user)
            await self.session.commit()
        return user
