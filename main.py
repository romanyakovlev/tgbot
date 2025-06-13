import asyncio
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

from controllers.dish_controller import TelegramDishController
from reposotory.sqllite_dish_repository import SqlliteDishRepository
from services.dish_service import DishService
from services.user_service import UserService

API_TOKEN = "token"
DB_FILE = "dishes.db"


async def main() -> None:
    bot = Bot(token=API_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher(storage=MemoryStorage())

    repository = SqlliteDishRepository(DB_FILE)
    await repository.init_db()
    user_service = UserService(repository, bot)
    dish_service = DishService(repository)

    controller = TelegramDishController(dp, dish_service, user_service)
    controller.register_handlers()
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
