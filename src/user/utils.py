from typing import Optional, List
from src.user.schemas import UserBase
from src.tenant.schemas import Tenant


class UserTenant(UserBase):  # used when reading user info
    id: int
    entity_id: int
    tenants: Optional[List[Tenant]] = []
    model_config = {"from_attributes": True}
