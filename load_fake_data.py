import os
from dotenv import load_dotenv
from src.database import SessionLocal
from src.device.models import Device
from src.folder.models import Folder
from src.user.models import User
from src.tenant.models import Tenant
from src.entity.models import Entity
from src.role.models import Role
from src.tag.models import Tag

db = SessionLocal()

mock_os_data_1 = {"os_name": "android", "os_version": "10", "os_kernel_version": "6"}
mock_os_data_2 = {"os_name": "android", "os_version": "9", "os_kernel_version": "5"}

mock_vendor_data_1 = {
    "vendor_name": "samsung",
    "vendor_model": "galaxy tab s9",
    "vendor_cores": 8,
    "vendor_ram_gb": 4,
}

mock_vendor_data_2 = {
    "vendor_name": "lenovo",
    "vendor_model": "m8",
    "vendor_cores": 8,
    "vendor_ram_gb": 3,
}


# create test objects (Entity, Device, Folder, User, Tenant)
roles = [
    Role(name="admin"),
    Role(name="owner"),
    Role(name="user"),
]
entities = [Entity() for i in range(12)]

tenant_1 = Tenant(name="tenant1", entity_id=1)
tenant_2 = Tenant(name="tenant2", entity_id=2)

folder_1 = Folder(name="folder1", entity_id=3, tenant_id=1)
folder_2 = Folder(name="folder2", entity_id=4, tenant_id=1)
folder_3 = Folder(name="folder3", entity_id=5, tenant_id=2)

device_1 = Device(
    name="dev1",
    folder_id=1,
    entity_id=6,
    mac_address="61:68:0C:1E:93:8F",
    ip_address="96.119.132.44",
    **mock_os_data_1,
    **mock_vendor_data_1
)

device_2 = Device(
    name="dev2",
    folder_id=2,
    entity_id=7,
    mac_address="61:68:0C:1E:93:9F",
    ip_address="96.119.132.45",
    **mock_os_data_1,
    **mock_vendor_data_2
)

device_3 = Device(
    name="dev3",
    folder_id=3,
    entity_id=8,
    mac_address="61:68:00:1F:95:AA",
    ip_address="96.119.132.46",
    **mock_os_data_2,
    **mock_vendor_data_2
)

user_1 = User(
    username="test-user-1",
    hashed_password="$2b$12$l1p.F3cYgrWgVNNOYVeU5efgjLzGqT3AOaQQsm0oUKoHSWyNwd4oe",  # "_s3cr3tp@5sw0rd_",
    email="test-user@sia.com",
    entity_id=9,
    role_id=1,
)

user_2 = User(
    username="test-user-2",
    hashed_password="$2b$12$l1p.F3cYgrWgVNNOYVeU5efgjLzGqT3AOaQQsm0oUKoHSWyNwd4oe",  # "_s3cr3tp@5sw0rd_",
    email="test-user-2@sia.com",
    entity_id=10,
    role_id=2,
)

user_3 = User(
    username="test-user-3",
    hashed_password="$2b$12$l1p.F3cYgrWgVNNOYVeU5efgjLzGqT3AOaQQsm0oUKoHSWyNwd4oe",  # "_s3cr3tp@5sw0rd_",
    email="test-user-3@sia.com",
    entity_id=11,
    role_id=3,
)


tenants_and_users = [
    user_1.tenants.append(tenant_1),
    user_1.tenants.append(tenant_2),
    user_3.tenants.append(tenant_1),
    user_2.tenants.append(tenant_2),
]

db.add_all(roles)
db.add_all(entities)
db.add_all(
    [
        tenant_1,
        tenant_2,
        folder_1,
        folder_2,
        folder_3,
        device_1,
        device_2,
        device_3,
        user_1,
        user_2,
        user_3,
    ]
)
db.commit()


def get_entity_for_obj(db, obj):
    return db.query(Entity).filter(Entity.id == obj.entity_id).first()

tag_1 = Tag(name="tag-1", tenant_id=1)
tag_1.entities.append(get_entity_for_obj(db, user_1))
tag_1.entities.append(get_entity_for_obj(db, device_1))
tag_1.entities.append(get_entity_for_obj(db, tenant_1))

tag_2 = Tag(name="tag-2", tenant_id=1)
tag_2.entities.append(get_entity_for_obj(db, user_1))
tag_2.entities.append(get_entity_for_obj(db, user_2))
tag_2.entities.append(get_entity_for_obj(db, device_2))

tag_3 = Tag(name="tag-3", tenant_id=2)
tag_3.entities.append(get_entity_for_obj(db, user_2))
tag_3.entities.append(get_entity_for_obj(db, device_1))
tag_3.entities.append(get_entity_for_obj(db, device_2))
tag_3.entities.append(get_entity_for_obj(db, tenant_2))

tag_4 = Tag(name="tag-4", tenant_id=2)
tag_4.entities.append(get_entity_for_obj(db, user_3))
tag_4.entities.append(get_entity_for_obj(db, tenant_1))

tags = [tag_1, tag_2, tag_3, tag_4]


db.add_all(tags)
db.commit()


db.close()
