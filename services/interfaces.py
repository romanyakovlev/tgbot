from abc import ABC, abstractmethod
from typing import Sequence

from models.dish import Dish
from models.user import User


class AbstractDishService(ABC):
    @abstractmethod
    async def add_dish(self, name: str, author_id: int) -> None:
        pass

    @abstractmethod
    async def get_dishes(self) -> Sequence[Dish]:
        pass

    @abstractmethod
    async def delete_dish(self, dish_id: int) -> None:
        pass


class AbstractUserService(ABC):
    @abstractmethod
    async def add_user_if_needed(self, user_id: int, username: str | None) -> None:
        pass

    @abstractmethod
    async def get_users(self) -> Sequence[User]:
        pass

    @abstractmethod
    async def notify_users(self, message: str, exclude_user_id: int | None = None) -> None:
        pass

    @abstractmethod
    async def delete_user(self, user_id: int) -> None:
        pass

    @abstractmethod
    async def is_admin(self, user_id: int) -> bool:
        pass
