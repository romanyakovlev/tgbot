import asyncio
import json
import os
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

from telegram.controllers.bot_controller import TelegramBotController
from reposotory.sqlite.sqllite_dish_repository import SqlliteDishRepository
from reposotory.sqlite.sqllite_user_repository import SqlliteUserRepository
from services.dish_service import DishService
from services.user_service import UserService

API_TOKEN = "token"
DB_FILE = "dishes.db"


async def main() -> None:
    bot = Bot(token=API_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher(storage=MemoryStorage())

    dish_repo = SqlliteDishRepository(DB_FILE)
    user_repo = SqlliteUserRepository(DB_FILE)
    await dish_repo.init_db()
    await user_repo.init_db()
    admin_logins = json.loads(os.getenv("ADMIN_LOGINS", "[]"))
    user_service = UserService(user_repo, bot, admin_logins)
    dish_service = DishService(dish_repo)

    controller = TelegramBotController(dp, dish_service, user_service)
    controller.register_handlers()
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
