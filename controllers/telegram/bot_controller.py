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

from services.interfaces import AbstractDishService, AbstractUserService


class AddDish(StatesGroup):
    waiting_for_name = State()


class TelegramBotController:
    def __init__(self, dp: Dispatcher, dish_service: AbstractDishService, user_service: AbstractUserService) -> None:
        self.dp = dp
        self.dish_service = dish_service
        self.user_service = user_service

    def register_handlers(self) -> None:
        self.dp.message()(self.track_user)
        self.dp.callback_query(F.data.startswith("delete_"))(self.delete_dish)
        self.dp.callback_query(F.data == "add_dish_inline")(self.inline_add_dish)

    async def track_user(self, message: Message, state: FSMContext) -> None:
        await self.user_service.add_user_if_needed(
            message.from_user.id, message.from_user.username
        )
        current_state = await state.get_state()
        if current_state == AddDish.waiting_for_name.state:
            await self.receive_dish_name(message, state)
            return
        if message.text == "/start":
            await self.cmd_start(message)
        elif message.text and message.text.lower() == "добавить блюдо":
            await self.ask_for_dish_name(message, state)
        elif message.text and message.text.lower() == "отмена":
            await self.cancel_add(message, state)
        elif message.text and message.text.lower() == "список блюд":
            await self.show_dishes(message)
        elif message.text and message.text.startswith("/add_user"):
            await self.cmd_add_user(message)
        elif message.text and message.text.startswith("/delete_user"):
            await self.cmd_delete_user(message)

    async def cmd_start(self, message: Message) -> None:
        kb = ReplyKeyboardMarkup(resize_keyboard=True, keyboard=[[KeyboardButton(text="Добавить блюдо")], [KeyboardButton(text="Список блюд")]])
        await message.answer("Привет! Я бот для хранения списка блюд.", reply_markup=kb)

    async def ask_for_dish_name(self, message: Message, state: FSMContext) -> None:
        kb = ReplyKeyboardMarkup(resize_keyboard=True, keyboard=[[KeyboardButton(text="Отмена")]])
        await message.answer("Введите название блюда:", reply_markup=kb)
        await state.set_state(AddDish.waiting_for_name)

    async def cancel_add(self, message: Message, state: FSMContext) -> None:
        if await state.get_state() is not None:
            await state.clear()
            kb = ReplyKeyboardMarkup(resize_keyboard=True, keyboard=[[KeyboardButton(text="Добавить блюдо")], [KeyboardButton(text="Список блюд")]])
            await message.answer("Добавление отменено.", reply_markup=kb)
        else:
            await message.answer("Нечего отменять.")

    async def receive_dish_name(self, message: Message, state: FSMContext) -> None:
        dish_name = message.text.strip()
        if not dish_name:
            await message.answer("Пожалуйста, введите корректное название.")
            return
        await self.dish_service.add_dish(dish_name, message.from_user.id)
        await self.user_service.notify_users(
            f"\U0001F37D Добавлено новое блюдо: <b>{dish_name}</b>",
            exclude_user_id=message.from_user.id,
        )
        kb = ReplyKeyboardMarkup(resize_keyboard=True, keyboard=[[KeyboardButton(text="Добавить блюдо")], [KeyboardButton(text="Список блюд")]])
        await message.answer(f"Блюдо <b>{dish_name}</b> добавлено!", reply_markup=kb)
        await state.clear()

    async def show_dishes(self, message: Message) -> None:
        dishes = await self.dish_service.get_dishes()
        if not dishes:
            await message.answer("Список блюд пуст.")
            return
        for dish in dishes:
            kb = InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(
                            text="Удалить", callback_data=f"delete_{dish.id}"
                        ),
                        InlineKeyboardButton(
                            text="\u2795 Добавить", callback_data="add_dish_inline"
                        ),
                    ]
                ]
            )
            await message.answer(f"{dish.id}. {dish.name}", reply_markup=kb)

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

    async def delete_dish(self, callback: CallbackQuery) -> None:
        dish_id = int(callback.data.split("_")[1])
        await self.dish_service.delete_dish(dish_id)
        await callback.message.edit_text("Блюдо удалено \u2705")
        await callback.answer("Удалено!")

    async def inline_add_dish(self, callback: CallbackQuery, state: FSMContext) -> None:
        kb = ReplyKeyboardMarkup(resize_keyboard=True, keyboard=[[KeyboardButton(text="Отмена")]])
        await callback.message.answer("Введите название нового блюда:", reply_markup=kb)
        await state.set_state(AddDish.waiting_for_name)
        await callback.answer()
