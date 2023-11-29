from typing import Optional
from .user_group.schemas import UserGroup
from .user.schemas import User

# To solve many to many relationship and circular imports we create two new schemas.
class UserGroupWithUsers(UserGroup):
    users: list[User] = []


class UserWithUserGroups(User):
    user_groups: list[UserGroup] = []
