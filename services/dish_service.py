from typing import Sequence

from models.dish import Dish
from reposotory.interfaces import AbstractDishRepository
from services.interfaces import AbstractDishService


class DishService(AbstractDishService):
    def __init__(self, repository: AbstractDishRepository) -> None:
        self.repository = repository

    async def add_dish(self, name: str, author_id: int) -> None:
        await self.repository.add_dish(name)

    async def get_dishes(self) -> Sequence[Dish]:
        return await self.repository.get_dishes()

    async def delete_dish(self, dish_id: int) -> None:
        await self.repository.delete_dish(dish_id)
