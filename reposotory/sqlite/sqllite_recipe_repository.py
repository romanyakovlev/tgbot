import aiosqlite

from models.recipe import Recipe
from ..interfaces import AbstractRecipeRepository


class SqlliteRecipeRepository(AbstractRecipeRepository):
    def __init__(self, db_file: str) -> None:
        self.db_file = db_file

    async def init_db(self) -> None:
        async with aiosqlite.connect(self.db_file) as db:
            await db.execute(
                """
                CREATE TABLE IF NOT EXISTS recipes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL
                )
                """
            )
            await db.commit()

    async def add_recipe(self, name: str) -> None:
        async with aiosqlite.connect(self.db_file) as db:
            await db.execute("INSERT INTO recipes (name) VALUES (?)", (name,))
            await db.commit()

    async def delete_recipe(self, recipe_id: int) -> None:
        async with aiosqlite.connect(self.db_file) as db:
            await db.execute("DELETE FROM recipes WHERE id = ?", (recipe_id,))
            await db.commit()

    async def get_recipes(self) -> list[Recipe]:
        async with aiosqlite.connect(self.db_file) as db:
            async with db.execute("SELECT id, name FROM recipes") as cursor:
                rows = await cursor.fetchall()
        return [Recipe(id=row[0], name=row[1]) for row in rows]
