from sqlalchemy.orm import Session
from src.tenant import exceptions, models
from typing import Optional

def check_tenant_name_taken(db: Session, tenant_name: str, tenant_id: Optional[int] = None):
    tenant = db.query(models.Tenant).filter(models.Tenant.name == tenant_name).first()
    if tenant:
        if tenant_id and tenant_id != tenant.id:
            raise exceptions.TenantNameTaken()
        if not tenant_id:
            raise exceptions.TenantNameTaken()


def check_tenant_exists(db: Session, tenant_id: int):
    tenant = db.query(models.Tenant).filter(models.Tenant.id == tenant_id).first()
    if not tenant:
        raise exceptions.TenantNotFound()


def filter_tag_ids(tags: dict, valid_tenant_id: int):
    # filtering tags that don't belong to the object's tenant (Device/Folder)
    tag_ids = []
    for t in tags:
        if t["tenant_id"] == None:  # handling "global" tag type
            tag_ids.append(t["id"])
        elif t["tenant_id"] == valid_tenant_id:
            tag_ids.append(t["id"])
    return tag_ids
