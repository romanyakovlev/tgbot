from reposotory.interfaces import AbstractDishRepository
from services.interfaces import AbstractUserService, AbstractDishService


class DishService(AbstractDishService):
    def __init__(self, repository: AbstractDishRepository, user_service: AbstractUserService) -> None:
        self.repository = repository
        self.user_service = user_service

    async def add_dish(self, name: str, author_id: int) -> None:
        await self.repository.add_dish(name)
        await self.user_service.notify_users(
            f"\U0001F37D Добавлено новое блюдо: <b>{name}</b>", exclude_user_id=author_id
        )

    async def get_dishes(self):
        return await self.repository.get_dishes()

    async def delete_dish(self, dish_id: int) -> None:
        await self.repository.delete_dish(dish_id)
