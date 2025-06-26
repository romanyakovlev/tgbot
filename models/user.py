from pydantic import BaseModel


class User(BaseModel):
    user_id: int
    username: str | None = None
    admin: bool = False
