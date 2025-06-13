import aiosqlite

from models.user import User
from ..interfaces import AbstractUserRepository


class SqlliteUserRepository(AbstractUserRepository):
    def __init__(self, db_file: str) -> None:
        self.db_file = db_file

    async def init_db(self) -> None:
        async with aiosqlite.connect(self.db_file) as db:
            await db.execute(
                """
                CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY,
                    username TEXT,
                    is_admin INTEGER NOT NULL DEFAULT 0
                )
                """
            )
            await db.commit()

    async def add_user(
        self, user_id: int, username: str | None, is_admin: bool = False
    ) -> None:
        async with aiosqlite.connect(self.db_file) as db:
            await db.execute(
                """
                INSERT INTO users (user_id, username, is_admin)
                VALUES (?, ?, ?)
                ON CONFLICT(user_id) DO UPDATE SET
                    username=excluded.username,
                    is_admin=excluded.is_admin
                """,
                (user_id, username, int(is_admin)),
            )
            await db.commit()

    async def delete_user(self, user_id: int) -> None:
        async with aiosqlite.connect(self.db_file) as db:
            await db.execute("DELETE FROM users WHERE user_id = ?", (user_id,))
            await db.commit()

    async def get_user(self, user_id: int) -> User | None:
        async with aiosqlite.connect(self.db_file) as db:
            async with db.execute(
                "SELECT user_id, username, is_admin FROM users WHERE user_id = ?",
                (user_id,),
            ) as cursor:
                row = await cursor.fetchone()
        if row:
            return User(user_id=row[0], username=row[1], admin=bool(row[2]))
        return None

    async def get_users(self) -> list[User]:
        async with aiosqlite.connect(self.db_file) as db:
            async with db.execute(
                "SELECT user_id, username, is_admin FROM users"
            ) as cursor:
                rows = await cursor.fetchall()
        return [
            User(user_id=row[0], username=row[1], admin=bool(row[2]))
            for row in rows
        ]
