from typing import Sequence

from aiogram import Bot

from models.user import User
from reposotory.interfaces import AbstractDishRepository
from services.interfaces import AbstractUserService


class UserService(AbstractUserService):
    def __init__(self, repository: AbstractDishRepository, bot: Bot) -> None:
        self.repository = repository
        self.bot = bot

    async def add_user_if_needed(self, user_id: int) -> None:
        await self.repository.add_user(user_id)

    async def get_users(self) -> Sequence[User]:
        return await self.repository.get_users()

    async def notify_users(self, message: str, exclude_user_id: int | None = None) -> None:
        users = await self.get_users()
        for user in users:
            if exclude_user_id is not None and user.user_id == exclude_user_id:
                continue
            try:
                await self.bot.send_message(user.user_id, message)
            except Exception as e:
                print(
                    f"Не удалось отправить сообщение пользователю {user.user_id}: {e}"
                )
