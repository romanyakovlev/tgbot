from typing import Sequence, Iterable

from aiogram import Bot

from models.user import User
from reposotory.interfaces import AbstractUserRepository
from services.interfaces import AbstractUserService


class UserService(AbstractUserService):
    def __init__(
        self,
        repository: AbstractUserRepository,
        bot: Bot,
        admin_logins: Iterable[str] | None = None,
    ) -> None:
        self.repository = repository
        self.bot = bot
        self.admin_logins = set(admin_logins or [])

    async def add_user_if_needed(self, user_id: int, username: str | None) -> None:
        is_admin = username in self.admin_logins if username else False
        await self.repository.add_user(user_id, username, is_admin)

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

    async def delete_user(self, user_id: int) -> None:
        await self.repository.delete_user(user_id)

    async def is_admin(self, user_id: int) -> bool:
        user = await self.repository.get_user(user_id)
        return bool(user and user.admin)
