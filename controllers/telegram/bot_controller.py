from aiogram import F, Dispatcher
from aiogram.types import (
    Message,
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    CallbackQuery,
)
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext

from services.interfaces import AbstractRecipeService, AbstractUserService


class AddRecipe(StatesGroup):
    waiting_for_name = State()


class TelegramBotController:
    def __init__(self, dp: Dispatcher, recipe_service: AbstractRecipeService, user_service: AbstractUserService) -> None:
        self.dp = dp
        self.recipe_service = recipe_service
        self.user_service = user_service

    def register_handlers(self) -> None:
        self.dp.message()(self.track_user)
        self.dp.callback_query(F.data.startswith("delete_"))(self.delete_recipe)
        self.dp.callback_query(F.data == "add_recipe_inline")(self.inline_add_recipe)

    async def track_user(self, message: Message, state: FSMContext) -> None:
        await self.user_service.add_user_if_needed(
            message.from_user.id, message.from_user.username
        )
        current_state = await state.get_state()
        if current_state == AddRecipe.waiting_for_name.state:
            await self.receive_recipe_name(message, state)
            return
        if message.text == "/start":
            await self.cmd_start(message)
        elif message.text and message.text.lower() == "добавить блюдо":
            await self.ask_for_recipe_name(message, state)
        elif message.text and message.text.lower() == "отмена":
            await self.cancel_add(message, state)
        elif message.text and message.text.lower() == "список блюд":
            await self.show_recipes(message)
        elif message.text and message.text.startswith("/add_user"):
            await self.cmd_add_user(message)
        elif message.text and message.text.startswith("/delete_user"):
            await self.cmd_delete_user(message)

    async def cmd_start(self, message: Message) -> None:
        kb = ReplyKeyboardMarkup(resize_keyboard=True, keyboard=[[KeyboardButton(text="Добавить блюдо")], [KeyboardButton(text="Список блюд")]])
        await message.answer("Привет! Я бот для хранения списка блюд.", reply_markup=kb)

    async def ask_for_recipe_name(self, message: Message, state: FSMContext) -> None:
        kb = ReplyKeyboardMarkup(resize_keyboard=True, keyboard=[[KeyboardButton(text="Отмена")]])
        await message.answer("Введите название блюда:", reply_markup=kb)
        await state.set_state(AddRecipe.waiting_for_name)

    async def cancel_add(self, message: Message, state: FSMContext) -> None:
        if await state.get_state() is not None:
            await state.clear()
            kb = ReplyKeyboardMarkup(resize_keyboard=True, keyboard=[[KeyboardButton(text="Добавить блюдо")], [KeyboardButton(text="Список блюд")]])
            await message.answer("Добавление отменено.", reply_markup=kb)
        else:
            await message.answer("Нечего отменять.")

    async def receive_recipe_name(self, message: Message, state: FSMContext) -> None:
        recipe_name = message.text.strip()
        if not recipe_name:
            await message.answer("Пожалуйста, введите корректное название.")
            return
        await self.recipe_service.add_recipe(recipe_name, message.from_user.id)
        await self.notify_users(
            f"\U0001F37D Добавлено новое блюдо: <b>{recipe_name}</b>",
            exclude_user_id=message.from_user.id,
        )
        kb = ReplyKeyboardMarkup(resize_keyboard=True, keyboard=[[KeyboardButton(text="Добавить блюдо")], [KeyboardButton(text="Список блюд")]])
        await message.answer(f"Блюдо <b>{recipe_name}</b> добавлено!", reply_markup=kb)
        await state.clear()

    async def show_recipes(self, message: Message) -> None:
        recipes = await self.recipe_service.get_recipes()
        if not recipes:
            await message.answer("Список блюд пуст.")
            return
        for recipe in recipes:
            kb = InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(
                            text="Удалить", callback_data=f"delete_{recipe.id}"
                        ),
                        InlineKeyboardButton(
                            text="\u2795 Добавить", callback_data="add_recipe_inline"
                        ),
                    ]
                ]
            )
            await message.answer(f"{recipe.id}. {recipe.name}", reply_markup=kb)

    async def cmd_add_user(self, message: Message) -> None:
        if not await self.user_service.is_admin(message.from_user.id):
            await message.answer("Недостаточно прав")
            return
        parts = message.text.split()
        if len(parts) < 2:
            await message.answer("Используйте /add_user <id>")
            return
        try:
            user_id = int(parts[1])
        except ValueError:
            await message.answer("Некорректный id")
            return
        await self.user_service.add_user_if_needed(user_id, None)
        await message.answer(f"Пользователь {user_id} добавлен")

    async def cmd_delete_user(self, message: Message) -> None:
        if not await self.user_service.is_admin(message.from_user.id):
            await message.answer("Недостаточно прав")
            return
        parts = message.text.split()
        if len(parts) < 2:
            await message.answer("Используйте /delete_user <id>")
            return
        try:
            user_id = int(parts[1])
        except ValueError:
            await message.answer("Некорректный id")
            return
        await self.user_service.delete_user(user_id)
        await message.answer(f"Пользователь {user_id} удален")

    async def delete_recipe(self, callback: CallbackQuery) -> None:
        recipe_id = int(callback.data.split("_")[1])
        await self.recipe_service.delete_recipe(recipe_id)
        await callback.message.edit_text("Блюдо удалено \u2705")
        await callback.answer("Удалено!")

    async def inline_add_recipe(self, callback: CallbackQuery, state: FSMContext) -> None:
        kb = ReplyKeyboardMarkup(resize_keyboard=True, keyboard=[[KeyboardButton(text="Отмена")]])
        await callback.message.answer("Введите название нового блюда:", reply_markup=kb)
        await state.set_state(AddRecipe.waiting_for_name)
        await callback.answer()

    async def notify_users(self, message: str, exclude_user_id: int | None = None) -> None:
        users = await self.user_service.get_users()
        for user in users:
            if exclude_user_id is not None and user.user_id == exclude_user_id:
                continue
            try:
                await self.dp.bot.send_message(user.user_id, message)
            except Exception as e:
                print(
                    f"Не удалось отправить сообщение пользователю {user.user_id}: {e}"
                )
