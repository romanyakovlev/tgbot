from abc import ABC, abstractmethod
from typing import Sequence

from models.dish import Dish
from models.user import User


class AbstractDishRepository(ABC):
    @abstractmethod
    async def init_db(self) -> None:
        pass

    @abstractmethod
    async def add_user(
        self, user_id: int, username: str | None, is_admin: bool = False
    ) -> None:
        """Add a user or update their info."""
        pass

    @abstractmethod
    async def delete_user(self, user_id: int) -> None:
        pass

    @abstractmethod
    async def get_user(self, user_id: int) -> User | None:
        pass

    @abstractmethod
    async def add_dish(self, name: str) -> None:
        pass

    @abstractmethod
    async def delete_dish(self, dish_id: int) -> None:
        pass

    @abstractmethod
    async def get_dishes(self) -> Sequence[Dish]:
        pass

    @abstractmethod
    async def get_users(self) -> Sequence[User]:
        pass
