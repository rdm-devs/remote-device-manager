from sqlalchemy.orm import Session
from src.tenant import exceptions, models


def check_tenant_name_taken(db: Session, tenant_name: str):
    tenant = db.query(models.Tenant).filter(models.Tenant.name == tenant_name).first()
    if tenant:
        raise exceptions.TenantNameTaken()


def check_tenant_exists(db: Session, tenant_id: int):
    tenant = db.query(models.Tenant).filter(models.Tenant.id == tenant_id).first()
    if not tenant:
        raise exceptions.TenantNotFound()
