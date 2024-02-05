import os
import pytest
from typing import Generator
from sqlalchemy import StaticPool, create_engine
from sqlalchemy.orm import sessionmaker, Session
from dotenv import load_dotenv
from src import folder
from src.main import app
from src.database import get_db, Base
from src.device.models import Device
from src.folder.models import Folder
from src.user.models import User
from src.tenant.models import Tenant
from src.entity.models import Entity
from src.role.models import Role
from src.device_os.models import DeviceOS
from src.device_vendor.models import DeviceVendor

load_dotenv()

DATABASE_URL = os.getenv("DB_CONNECTION_TEST")
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        print("Using test DB!")
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db

# @pytest.fixture
# def create_entity() -> Generator[Entity, None, None]:
#     Base.metadata.create_all(bind=engine)
#     db_session = TestingSessionLocal()
#     entity = Entity()
#     db_session.add(entity)
#     db_session.commit()
#     yield db_session
#     db_session.close()
#     Base.metadata.drop_all(bind=engine)


@pytest.fixture
def session() -> Generator[Session, None, None]:
    # Create the tables in the test database
    Base.metadata.create_all(bind=engine)

    db_session = TestingSessionLocal()

    # create test objects (Entity, Device, Folder, User, Tenant)
    db_oss = [DeviceOS(id=1, name="android", version="10", kernel_version="6")]

    db_vendors = [
        DeviceVendor(id=1, brand="samsung", model="galaxy tab s9", cores=8, ram_gb=4)
    ]

    db_roles = [
        Role(id=1, name="admin"),
    ]
    db_entities = [Entity() for i in range(7)]

    db_tenant = Tenant(id=1, name="tenant1", entity_id=0)
    db_folder = Folder(id=1, name="folder1", tenant_id=1, entity_id=1)
    db_folder_2 = Folder(id=2, name="folder2", entity_id=2, tenant_id=1)
    db_device = Device(
        id=1,
        name="dev1",
        folder_id=1,
        entity_id=3,
        mac_address="61:68:0C:1E:93:8F",
        ip_address="96.119.132.44",
        os_id=1,
        vendor_id=1,
    )
    db_device_2 = Device(
        id=2,
        name="dev2",
        folder_id=1,
        entity_id=4,
        mac_address="61:68:0C:1E:93:9F",
        ip_address="96.119.132.45",
        os_id=1,
        vendor_id=1,
    )

    db_user = User(
        id=1,
        hashed_password="_s3cr3tp@5sw0rd_",
        email="test-user@sia.com",
        entity_id=5,
        role_id=1,
    )

    db_user_2 = User(
        id=2,
        hashed_password="_s3cr3tp@5sw0rd_",
        email="test-user-2@sia.com",
        entity_id=6,
        role_id=1,
    )

    db_session.add_all(db_oss)
    db_session.add_all(db_vendors)
    db_session.add_all(db_roles)
    db_session.add_all(db_entities)
    db_session.add_all(
        [
            db_tenant,
            db_folder,
            db_folder_2,
            db_device,
            db_device_2,
            db_user,
            db_user_2,
        ]
    )
    db_session.commit()

    yield db_session

    db_session.close()
    Base.metadata.drop_all(bind=engine)
