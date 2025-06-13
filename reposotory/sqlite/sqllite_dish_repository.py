import aiosqlite

from models.dish import Dish
from ..interfaces import AbstractDishRepository


class SqlliteDishRepository(AbstractDishRepository):
    def __init__(self, db_file: str) -> None:
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
