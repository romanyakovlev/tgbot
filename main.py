import asyncio
from aiogram import Bot, Dispatcher, F
from aiogram.client.default import DefaultBotProperties
from aiogram.types import (
    Message, ReplyKeyboardMarkup, KeyboardButton,
    InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
)
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
import aiosqlite

API_TOKEN = "token"

bot = Bot(
    token=API_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)
dp = Dispatcher(storage=MemoryStorage())

DB_FILE = "dishes.db"

# FSM состояние
class AddDish(StatesGroup):
    waiting_for_name = State()

# Инициализация базы
async def init_db():
    async with aiosqlite.connect(DB_FILE) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS dishes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY
            )
        """)
        await db.commit()

# Отслеживание пользователей
@dp.message()
async def track_user(message: Message, state: FSMContext):
    # Сохраняем user_id в базу
    async with aiosqlite.connect(DB_FILE) as db:
        await db.execute("INSERT OR IGNORE INTO users (user_id) VALUES (?)", (message.from_user.id,))
        await db.commit()

    # Если пользователь в состоянии — перенаправляем в нужный хендлер
    current_state = await state.get_state()
    if current_state == AddDish.waiting_for_name.state:
        await receive_dish_name(message, state)
        return

    # Далее передаём управление другим хендлерам
    if message.text == "/start":
        await cmd_start(message)
    elif message.text.lower() == "добавить блюдо":
        await ask_for_dish_name(message, state)
    elif message.text.lower() == "отмена":
        await cancel_add(message, state)
    elif message.text.lower() == "список блюд":
        await show_dishes(message)

# /start
async def cmd_start(message: Message):
    kb = ReplyKeyboardMarkup(resize_keyboard=True, keyboard=[
        [KeyboardButton(text="Добавить блюдо")],
        [KeyboardButton(text="Список блюд")]
    ])
    await message.answer("Привет! Я бот для хранения списка блюд.", reply_markup=kb)

# Нажата кнопка "Добавить блюдо"
async def ask_for_dish_name(message: Message, state: FSMContext):
    kb = ReplyKeyboardMarkup(resize_keyboard=True, keyboard=[
        [KeyboardButton(text="Отмена")]
    ])
    await message.answer("Введите название блюда:", reply_markup=kb)
    await state.set_state(AddDish.waiting_for_name)

# Обработка отмены
async def cancel_add(message: Message, state: FSMContext):
    if await state.get_state() is not None:
        await state.clear()
        kb = ReplyKeyboardMarkup(resize_keyboard=True, keyboard=[
            [KeyboardButton(text="Добавить блюдо")],
            [KeyboardButton(text="Список блюд")]
        ])
        await message.answer("Добавление отменено.", reply_markup=kb)
    else:
        await message.answer("Нечего отменять.")

# Приём названия блюда
async def receive_dish_name(message: Message, state: FSMContext):
    dish_name = message.text.strip()

    if not dish_name:
        await message.answer("Пожалуйста, введите корректное название.")
        return

    async with aiosqlite.connect(DB_FILE) as db:
        await db.execute("INSERT INTO dishes (name) VALUES (?)", (dish_name,))
        await db.commit()

    # Вернём клавиатуру
    kb = ReplyKeyboardMarkup(resize_keyboard=True, keyboard=[
        [KeyboardButton(text="Добавить блюдо")],
        [KeyboardButton(text="Список блюд")]
    ])
    await message.answer(f"Блюдо <b>{dish_name}</b> добавлено!", reply_markup=kb)
    await state.clear()

    # Уведомляем всех пользователей
    async with aiosqlite.connect(DB_FILE) as db:
        async with db.execute("SELECT user_id FROM users") as cursor:
            users = await cursor.fetchall()

    for (user_id,) in users:
        try:
            if user_id != message.from_user.id:
                await bot.send_message(user_id, f"🍽 Добавлено новое блюдо: <b>{dish_name}</b>")
        except Exception as e:
            print(f"Не удалось отправить сообщение пользователю {user_id}: {e}")

# Список блюд
async def show_dishes(message: Message):
    async with aiosqlite.connect(DB_FILE) as db:
        async with db.execute("SELECT id, name FROM dishes") as cursor:
            rows = await cursor.fetchall()

    if not rows:
        await message.answer("Список блюд пуст.")
        return

    for dish_id, dish_name in rows:
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="Удалить", callback_data=f"delete_{dish_id}"),
                InlineKeyboardButton(text="➕ Добавить", callback_data="add_dish_inline")
            ]
        ])
        await message.answer(f"{dish_id}. {dish_name}", reply_markup=kb)

# Удаление блюда
@dp.callback_query(F.data.startswith("delete_"))
async def delete_dish(callback: CallbackQuery):
    dish_id = int(callback.data.split("_")[1])
    async with aiosqlite.connect(DB_FILE) as db:
        await db.execute("DELETE FROM dishes WHERE id = ?", (dish_id,))
        await db.commit()

    await callback.message.edit_text("Блюдо удалено ✅")
    await callback.answer("Удалено!")

# Inline-добавление по кнопке
@dp.callback_query(F.data == "add_dish_inline")
async def inline_add_dish(callback: CallbackQuery, state: FSMContext):
    kb = ReplyKeyboardMarkup(resize_keyboard=True, keyboard=[
        [KeyboardButton(text="Отмена")]
    ])
    await callback.message.answer("Введите название нового блюда:", reply_markup=kb)
    await state.set_state(AddDish.waiting_for_name)
    await callback.answer()

# Запуск
async def main():
    await init_db()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
