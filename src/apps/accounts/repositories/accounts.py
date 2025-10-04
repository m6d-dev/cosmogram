from src.apps.accounts.models import User
from src.utils.bases.repositories import AbstractRepository


class UserRepository(AbstractRepository[User]):
    model = User


user_repo = UserRepository()
