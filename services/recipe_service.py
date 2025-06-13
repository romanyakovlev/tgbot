from typing import Sequence

from models.recipe import Recipe
from reposotory.interfaces import AbstractRecipeRepository
from services.interfaces import AbstractRecipeService


class RecipeService(AbstractRecipeService):
    def __init__(self, repository: AbstractRecipeRepository) -> None:
        self.repository = repository

    async def add_recipe(self, name: str, author_id: int) -> None:
        await self.repository.add_recipe(name)

    async def get_recipes(self) -> Sequence[Recipe]:
        return await self.repository.get_recipes()

    async def delete_recipe(self, recipe_id: int) -> None:
        await self.repository.delete_recipe(recipe_id)
