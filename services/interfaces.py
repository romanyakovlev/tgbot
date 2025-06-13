from abc import ABC, abstractmethod


class AbstractDishService(ABC):
    @abstractmethod
    async def add_dish(self, name: str, author_id: int) -> None:
        pass

    @abstractmethod
    async def get_dishes(self):
        pass

    @abstractmethod
    async def delete_dish(self, dish_id: int) -> None:
        pass


class AbstractUserService(ABC):
    @abstractmethod
    async def add_user_if_needed(self, user_id: int) -> None:
        pass

    @abstractmethod
    async def get_users(self):
        pass

    @abstractmethod
    async def notify_users(self, message: str, exclude_user_id: int | None = None) -> None:
        pass
