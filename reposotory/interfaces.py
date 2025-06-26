from abc import ABC, abstractmethod
from typing import Sequence

from models.recipe import Recipe
from models.user import User


class AbstractRecipeRepository(ABC):
    @abstractmethod
    async def init_db(self) -> None:
        pass

    @abstractmethod
    async def add_recipe(self, name: str) -> None:
        pass

    @abstractmethod
    async def delete_recipe(self, recipe_id: int) -> None:
        pass

    @abstractmethod
    async def get_recipes(self) -> Sequence[Recipe]:
        pass


class AbstractUserRepository(ABC):
    @abstractmethod
    async def init_db(self) -> None:
        pass

    @abstractmethod
    async def add_user(
        self, user_id: int, username: str | None, is_admin: bool = False
    ) -> None:
        pass

    @abstractmethod
    async def delete_user(self, user_id: int) -> None:
        pass

    @abstractmethod
    async def get_user(self, user_id: int) -> User | None:
        pass

    @abstractmethod
    async def get_users(self) -> Sequence[User]:
        pass
