import asyncio
import json
import os
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

from controllers.telegram.bot_controller import TelegramBotController
from reposotory.sqlite.sqllite_recipe_repository import SqlliteRecipeRepository
from reposotory.sqlite.sqllite_user_repository import SqlliteUserRepository
from services.recipe_service import RecipeService
from services.user_service import UserService

API_TOKEN = "token"
DB_FILE = "recipes.db"


async def main() -> None:
    bot = Bot(token=API_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher(storage=MemoryStorage())

    recipe_repo = SqlliteRecipeRepository(DB_FILE)
    user_repo = SqlliteUserRepository(DB_FILE)
    await recipe_repo.init_db()
    await user_repo.init_db()
    admin_logins = json.loads(os.getenv("ADMIN_LOGINS", "[]"))
    user_service = UserService(user_repo)
    for admin_id in admin_logins:
        try:
            user_id = int(admin_id)
        except (TypeError, ValueError):
            continue
        await user_service.add_user_if_needed(user_id, None, is_admin=True)
    recipe_service = RecipeService(recipe_repo)

    controller = TelegramBotController(dp, recipe_service, user_service)
    controller.register_handlers()
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
