from abc import ABC, abstractmethod
from typing import Sequence

from models.recipe import Recipe
from models.user import User


class AbstractRecipeService(ABC):
    @abstractmethod
    async def add_recipe(self, name: str, author_id: int) -> None:
        pass

    @abstractmethod
    async def get_recipes(self) -> Sequence[Recipe]:
        pass

    @abstractmethod
    async def delete_recipe(self, recipe_id: int) -> None:
        pass


class AbstractUserService(ABC):
    @abstractmethod
    async def add_user_if_needed(
        self, user_id: int, username: str | None, is_admin: bool = False
    ) -> None:
        pass

    @abstractmethod
    async def get_users(self) -> Sequence[User]:
        pass

    @abstractmethod
    async def delete_user(self, user_id: int) -> None:
        pass

    @abstractmethod
    async def is_admin(self, user_id: int) -> bool:
        pass
