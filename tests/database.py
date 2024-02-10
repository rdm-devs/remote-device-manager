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


@pytest.fixture
def mock_os_data() -> Generator[dict, None, None]:
    return {"os_name": "android", "os_version": "10", "os_kernel_version": "6"}


@pytest.fixture
def mock_vendor_data() -> Generator[dict, None, None]:
    return {
        "vendor_name": "samsung",
        "vendor_model": "galaxy tab s9",
        "vendor_cores": 8,
        "vendor_ram_gb": 4,
    }


@pytest.fixture
def session(
    mock_os_data: pytest.fixture, mock_vendor_data: pytest.fixture
) -> Generator[Session, None, None]:
    # Create the tables in the test database
    Base.metadata.create_all(bind=engine)

    db_session = TestingSessionLocal()

    # create test objects (Entity, Device, Folder, User, Tenant)
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
        **mock_os_data,
        **mock_vendor_data
    )
    db_device_2 = Device(
        id=2,
        name="dev2",
        folder_id=1,
        entity_id=4,
        mac_address="61:68:0C:1E:93:9F",
        ip_address="96.119.132.45",
        **mock_os_data,
        **mock_vendor_data
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
