from app.dao.base import BaseDAO
from app.auth.models import User


class UsersDAO(BaseDAO[User]):
    model = User

