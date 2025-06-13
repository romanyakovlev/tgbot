from pydantic import BaseModel

class Dish(BaseModel):
    id: int
    name: str
