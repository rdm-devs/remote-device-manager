from typing import Optional, List
from src.user.schemas import UserBase
from src.tenant.schemas import Tenant
from src.tag.schemas import Tag

class UserTenant(UserBase):  # used when reading user info
    id: int
    entity_id: int
    tenants: List[Tenant]
    tags: List[Tag]
    model_config = {"from_attributes": True}
