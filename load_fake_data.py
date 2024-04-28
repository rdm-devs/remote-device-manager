import os
from dotenv import load_dotenv
from src.database import SessionLocal
from src.tenant.service import create_tenant
from src.tenant.schemas import TenantCreate
from src.folder.service import create_folder
from src.folder.schemas import FolderCreate
from src.device.service import create_device
from src.device.schemas import DeviceCreate
from src.user.service import create_user, assign_role
from src.user.schemas import UserCreate
from src.entity.service import create_entity_auto
from src.role.service import create_role
from src.role.schemas import RoleCreate
from src.tag.service import create_tag
from src.tag.schemas import TagCreate

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
    create_role(db, RoleCreate(name="admin")),
    create_role(db, RoleCreate(name="owner")),
    create_role(db, RoleCreate(name="user")),
]
# entities = [Entity() for i in range(17)]

tenant_1 = create_tenant(db, TenantCreate(name="tenant1"))
tenant_2 = create_tenant(db, TenantCreate(name="tenant2"))

folder_1 = create_folder(db, FolderCreate(name="folder1", tenant_id=tenant_1.id))

subfolder_1_1 = create_folder(
    db, FolderCreate(name="sub11", tenant_id=tenant_1.id, parent_id=folder_1.id)
)
subfolder_1_2 = create_folder(
    db, FolderCreate(name="sub12", tenant_id=tenant_1.id, parent_id=folder_1.id)
)

folder_2 = create_folder(db, FolderCreate(name="folder2", tenant_id=tenant_1.id))
subfolder_2_1 = create_folder(
    db, FolderCreate(name="sub21", tenant_id=tenant_1.id, parent_id=folder_2.id)
)
subfolder_2_2 = create_folder(
    db, FolderCreate(name="sub22", tenant_id=tenant_1.id, parent_id=folder_2.id)
)

folder_3 = create_folder(db, FolderCreate(name="folder3", tenant_id=tenant_2.id))
subfolder_3_1 = create_folder(
    db, FolderCreate(name="sub31", tenant_id=tenant_2.id, parent_id=folder_3.id)
)

device_1 = create_device(
    db,
    DeviceCreate(
        name="dev1",
        folder_id=folder_1.id,
        mac_address="61:68:0C:1E:93:8F",
        ip_address="96.119.132.44",
        **mock_os_data_1,
        **mock_vendor_data_1
    ),
)

device_2 = create_device(
    db,
    DeviceCreate(
        name="dev2",
        folder_id=folder_2.id,
        mac_address="61:68:0C:1E:93:9F",
        ip_address="96.119.132.45",
        **mock_os_data_1,
        **mock_vendor_data_2
    ),
)

device_3 = create_device(
    db,
    DeviceCreate(
        name="dev3",
        folder_id=folder_3.id,
        mac_address="61:68:00:1F:95:AA",
        ip_address="96.119.132.46",
        **mock_os_data_2,
        **mock_vendor_data_2
    ),
)

user_1 = create_user(
    db,
    UserCreate(
        username="test-user-1",
        password="_s3cr3tp@5sw0rd_", #"$2b$12$l1p.F3cYgrWgVNNOYVeU5efgjLzGqT3AOaQQsm0oUKoHSWyNwd4oe",
        email="test-user@sia.com",
    ),
)
assign_role(db, user_1.id, roles[0].id)

user_2 = create_user(
    db,
    UserCreate(
        username="test-user-2",
        password="_s3cr3tp@5sw0rd_", #"$2b$12$l1p.F3cYgrWgVNNOYVeU5efgjLzGqT3AOaQQsm0oUKoHSWyNwd4oe",
        email="test-user-2@sia.com",
    ),
)
assign_role(db, user_2.id, roles[1].id)

user_3 = create_user(
    db,
    UserCreate(
        username="test-user-3",
        password="_s3cr3tp@5sw0rd_", #"$2b$12$l1p.F3cYgrWgVNNOYVeU5efgjLzGqT3AOaQQsm0oUKoHSWyNwd4oe",
        email="test-user-3@sia.com",
    ),
)
assign_role(db, user_3.id, roles[2].id)


tenants_and_users = [
    user_1.add_tenant(tenant_1),
    user_1.add_tenant(tenant_2),
    user_3.add_tenant(tenant_1),
    user_2.add_tenant(tenant_2),
]

tag_1 = create_tag(db, TagCreate(name="tag-1", tenant_id=tenant_1.id))
user_1.add_tag(tag_1)
device_1.add_tag(tag_1)
tenant_1.add_tag(tag_1)
folder_1.add_tag(tag_1)

tag_2 = create_tag(db, TagCreate(name="tag-2", tenant_id=tenant_1.id))
user_1.add_tag(tag_2)
user_2.add_tag(tag_2)
device_2.add_tag(tag_2)
folder_1.add_tag(tag_2)

tag_3 = create_tag(db, TagCreate(name="tag-3", tenant_id=tenant_2.id))
user_2.add_tag(tag_3)
device_1.add_tag(tag_3)
device_2.add_tag(tag_3)
tenant_2.add_tag(tag_3)
folder_2.add_tag(tag_3)

tag_4 = create_tag(db, TagCreate(name="tag-4", tenant_id=tenant_2.id))
user_3.add_tag(tag_4)
tenant_1.add_tag(tag_4)
folder_2.add_tag(tag_4)

# guardamos modificaciones (tags) a objetos previamente creados
db.add_all(
    [
        tenant_1,
        tenant_2,
        folder_1,
        folder_2,
        device_1,
        device_2,
        user_1,
        user_2,
        user_3,
    ]
)
db.commit()


db.close()
