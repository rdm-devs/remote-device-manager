import os
import pytest
from fastapi.security import OAuth2PasswordBearer
from fastapi.testclient import TestClient
from fastapi_pagination import add_pagination
from typing import Generator
from sqlalchemy import StaticPool, create_engine
from sqlalchemy.orm import sessionmaker, Session
from dotenv import load_dotenv
from src import folder
from src.main import app
from src.auth.dependencies import oauth2_scheme, get_current_active_user
from src.database import get_db, Base
from src.device.models import Device
from src.folder.models import Folder
from src.user.models import User
from src.tenant.models import Tenant
from src.entity.models import Entity
from src.role.models import Role
from src.tag.models import Tag

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


add_pagination(app)
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
        Role(id=2, name="owner"),
        Role(id=3, name="user"),
    ]
    db_entities = [Entity() for i in range(21)]

    db_tenant_1 = Tenant(id=1, name="tenant1", entity_id=1)
    db_folder_1 = Folder(id=1, name="folder1", tenant_id=1, entity_id=2)
    db_folder_2 = Folder(id=2, name="folder2", tenant_id=1, entity_id=3)
    db_device_1 = Device(
        id=1,
        name="dev1",
        folder_id=1,
        entity_id=4,
        mac_address="61:68:0C:1E:93:8F",
        ip_address="96.119.132.44",
        **mock_os_data,
        **mock_vendor_data
    )
    db_device_2 = Device(
        id=2,
        name="dev2",
        folder_id=1,
        entity_id=5,
        mac_address="61:68:0C:1E:93:9F",
        ip_address="96.119.132.45",
        **mock_os_data,
        **mock_vendor_data
    )

    db_user_1 = User(
        id=1,
        username="test-user-1",
        hashed_password="$2b$12$l1p.F3cYgrWgVNNOYVeU5efgjLzGqT3AOaQQsm0oUKoHSWyNwd4oe",  # "_s3cr3tp@5sw0rd_",
        email="test-user@sia.com",
        entity_id=6,
        role_id=1,
    )

    db_user_2 = User(
        id=2,
        username="test-user-2",
        hashed_password="$2b$12$l1p.F3cYgrWgVNNOYVeU5efgjLzGqT3AOaQQsm0oUKoHSWyNwd4oe",  # "_s3cr3tp@5sw0rd_",
        email="test-user-2@sia.com",
        entity_id=7,
        role_id=2,
    )

    db_user_3 = User(
        id=3,
        username="test-user-3",
        hashed_password="$2b$12$l1p.F3cYgrWgVNNOYVeU5efgjLzGqT3AOaQQsm0oUKoHSWyNwd4oe",  # "_s3cr3tp@5sw0rd_",
        email="test-user-3@sia.com",
        entity_id=8,
        role_id=2,
    )

    db_user_4 = User(
        id=4,
        username="test-user-4",
        hashed_password="$2b$12$l1p.F3cYgrWgVNNOYVeU5efgjLzGqT3AOaQQsm0oUKoHSWyNwd4oe",  # "_s3cr3tp@5sw0rd_",
        email="test-user-4@sia.com",
        entity_id=9,
        role_id=3,
    )

    db_subfolder_1 = Folder(
        id=3, name="subfolder1", tenant_id=1, entity_id=10, parent_id=1
    )

    db_tenant_2 = Tenant(id=2, name="tenant2", entity_id=11)
    db_folder_3 = Folder(id=4, name="folder3", tenant_id=2, entity_id=12)
    db_subfolder_2 = Folder(
        id=5, name="subfolder2", tenant_id=2, entity_id=13, parent_id=4
    )

    db_session.add_all(db_roles)
    db_session.add_all(db_entities)
    db_session.add_all(
        [
            db_tenant_1,
            db_folder_1,
            db_subfolder_1,
            db_folder_2,
            db_device_1,
            db_device_2,
            db_user_1,
            db_user_2,
            db_user_3,
            db_user_4,
            db_tenant_2,
            db_folder_3,
            db_subfolder_2,
        ]
    )
    db_user_2.tenants.append(db_tenant_1)
    db_user_3.tenants.append(db_tenant_2)
    db_session.commit()

    # para testear tags, tag_1 debe crearse antes.
    tag_1 = Tag(name="tag-tenant-1", tenant_id=1)
    tag_1.entities.append(db_user_2.entity)
    tag_1.entities.append(db_tenant_1.entity)
    tag_1.entities.append(db_device_1.entity)
    tag_1.entities.append(db_folder_1.entity)

    tag_2 = Tag(name="tag-user-1", tenant_id=1)
    tag_2.entities.append(db_user_1.entity)

    tag_3 = Tag(name="tag-folder-1", tenant_id=1)
    tag_3.entities.append(db_folder_1.entity)

    tag_4 = Tag(name="tag-dev-1", tenant_id=1)
    tag_4.entities.append(db_device_1.entity)

    tag_5 = Tag(name="tag-subfolder-1", tenant_id=1)
    tag_5.entities.append(db_subfolder_1.entity)

    tag_6 = Tag(name="tag-tenant-2", tenant_id=2)
    tag_6.entities.append(db_user_3.entity)
    tag_6.entities.append(db_tenant_2.entity)
    tag_6.entities.append(db_device_2.entity)
    tag_6.entities.append(db_folder_2.entity)

    tag_7 = Tag(name="tag-subfolder-2", tenant_id=2)
    tag_7.entities.append(db_subfolder_2.entity)

    tag_8 = Tag(name="tag-user-2", tenant_id=1)
    tag_8.entities.append(db_user_2.entity)

    db_session.add_all([tag_1, tag_2, tag_3, tag_4, tag_5, tag_6, tag_7, tag_8])
    db_session.commit()

    yield db_session

    db_session.close()
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(name="client")
def client_fixture(session: Session):
    def get_db_session_override():
        return session

    oauth2_scheme_override = OAuth2PasswordBearer(tokenUrl="auth/token")
    app.dependency_overrides[oauth2_scheme] = oauth2_scheme_override
    app.dependency_overrides[get_db] = get_db_session_override
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


@pytest.fixture
def client_authenticated(session: Session):
    """
    Returns an API client which skips the authentication
    """

    def skip_auth():
        # returning an admin user
        user = session.query(User).filter(User.role_id == 1).first()
        return user

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_active_user] = skip_auth
    return TestClient(app)
