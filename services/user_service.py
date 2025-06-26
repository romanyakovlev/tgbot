from typing import Sequence

from models.user import User
from reposotory.interfaces import AbstractUserRepository
from services.interfaces import AbstractUserService
from exceptions import UserAlreadyExistsError


class UserService(AbstractUserService):
    def __init__(self, repository: AbstractUserRepository) -> None:
        self.repository = repository

    async def add_user_if_needed(
        self, user_id: int, username: str | None, is_admin: bool = False
    ) -> None:
        existing = await self.repository.get_user(user_id)
        if existing is not None:
            raise UserAlreadyExistsError(user_id)
        await self.repository.add_user(user_id, username, is_admin)

    async def get_users(self) -> Sequence[User]:
        return await self.repository.get_users()

    async def delete_user(self, user_id: int) -> None:
        await self.repository.delete_user(user_id)

    async def is_admin(self, user_id: int) -> bool:
        user = await self.repository.get_user(user_id)
        return bool(user and user.admin)
