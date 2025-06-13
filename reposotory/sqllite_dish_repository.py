import aiosqlite

from models.dish import Dish
from models.user import User
from .interfaces import AbstractDishRepository


class SqlliteDishRepository(AbstractDishRepository):
    def __init__(self, db_file: str):
        self.db_file = db_file

    async def init_db(self) -> None:
        async with aiosqlite.connect(self.db_file) as db:
            await db.execute(
                """
                CREATE TABLE IF NOT EXISTS dishes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL
                )
                """
            )
            await db.execute(
                """
                CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY
                )
                """
            )
            await db.commit()

    async def add_user(self, user_id: int) -> None:
        async with aiosqlite.connect(self.db_file) as db:
            await db.execute(
                "INSERT OR IGNORE INTO users (user_id) VALUES (?)",
                (user_id,),
            )
            await db.commit()

    async def add_dish(self, name: str) -> None:
        async with aiosqlite.connect(self.db_file) as db:
            await db.execute("INSERT INTO dishes (name) VALUES (?)", (name,))
            await db.commit()

    async def delete_dish(self, dish_id: int) -> None:
        async with aiosqlite.connect(self.db_file) as db:
            await db.execute("DELETE FROM dishes WHERE id = ?", (dish_id,))
            await db.commit()

    async def get_dishes(self) -> list[Dish]:
        async with aiosqlite.connect(self.db_file) as db:
            async with db.execute("SELECT id, name FROM dishes") as cursor:
                rows = await cursor.fetchall()
        return [Dish(id=row[0], name=row[1]) for row in rows]

    async def get_users(self) -> list[User]:
        async with aiosqlite.connect(self.db_file) as db:
            async with db.execute("SELECT user_id FROM users") as cursor:
                rows = await cursor.fetchall()
        return [User(user_id=row[0]) for row in rows]
