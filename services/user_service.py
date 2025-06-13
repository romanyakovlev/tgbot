from aiogram import Bot

from reposotory.dish_repository import DishRepository


class UserService:
    def __init__(self, repository: DishRepository, bot: Bot) -> None:
        self.repository = repository
        self.bot = bot

    async def add_user_if_needed(self, user_id: int) -> None:
        await self.repository.add_user(user_id)

    async def get_users(self):
        return await self.repository.get_users()

    async def notify_users(self, message: str, exclude_user_id: int | None = None) -> None:
        users = await self.get_users()
        for (uid,) in users:
            if exclude_user_id is not None and uid == exclude_user_id:
                continue
            try:
                await self.bot.send_message(uid, message)
            except Exception as e:
                print(f"Не удалось отправить сообщение пользователю {uid}: {e}")
