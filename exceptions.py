class UserAlreadyExistsError(Exception):
    """Raised when attempting to add a user that already exists."""

    def __init__(self, user_id: int) -> None:
        self.user_id = user_id
        super().__init__(f"User {user_id} already exists")

