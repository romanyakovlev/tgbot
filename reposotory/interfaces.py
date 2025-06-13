from abc import ABC, abstractmethod


class AbstractDishRepository(ABC):
    @abstractmethod
    async def init_db(self) -> None:
        pass

    @abstractmethod
    async def add_user(self, user_id: int) -> None:
        pass

    @abstractmethod
    async def add_dish(self, name: str) -> None:
        pass

    @abstractmethod
    async def delete_dish(self, dish_id: int) -> None:
        pass

    @abstractmethod
    async def get_dishes(self):
        pass

    @abstractmethod
    async def get_users(self):
        pass
