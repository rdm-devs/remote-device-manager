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
from src.auth.dependencies import (
    oauth2_scheme,
    get_current_active_user,
    get_current_user,
)
from src.auth import service as auth_service
from src.auth import utils as auth_utils
from src.database import get_db, Base
from src.user.models import User
from src.device.service import create_device
from src.device.schemas import DeviceCreate
from src.folder.service import create_folder
from src.folder.schemas import FolderCreate
from src.user.models import User
from src.user.service import create_user, assign_role
from src.user.schemas import UserCreate
from src.tenant.service import create_tenant
from src.tenant.schemas import TenantCreate
from src.entity.service import create_entity_auto
from src.role.service import create_role
from src.role.schemas import RoleCreate
from src.tag.service import create_tag
from src.tag.schemas import TagCreate


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

    db = TestingSessionLocal()

    # create test objects (Entity, Device, Folder, User, Tenant)
    roles = [
        create_role(db, RoleCreate(name="admin")),
        create_role(db, RoleCreate(name="owner")),
        create_role(db, RoleCreate(name="user")),
    ]

    tenant_1 = create_tenant(db, TenantCreate(name="tenant1"))
    tenant_2 = create_tenant(db, TenantCreate(name="tenant2"))

    folder_1 = create_folder(db, FolderCreate(name="folder1", tenant_id=tenant_1.id))
    subfolder_1 = create_folder(
        db,
        FolderCreate(name="subfolder1", tenant_id=tenant_1.id, parent_id=folder_1.id),
    )
    folder_2 = create_folder(db, FolderCreate(name="folder2", tenant_id=tenant_1.id))

    folder_3 = create_folder(db, FolderCreate(name="folder3", tenant_id=tenant_2.id))
    subfolder_2 = create_folder(
        db,
        FolderCreate(name="subfolder2", tenant_id=tenant_2.id, parent_id=folder_3.id),
    )

    device_1 = create_device(
        db,
        DeviceCreate(
            name="dev1",
            folder_id=folder_1.id,
            mac_address="61:68:0C:1E:93:8F",
            ip_address="96.119.132.44",
            **mock_os_data,
            **mock_vendor_data
        ),
    )

    device_2 = create_device(
        db,
        DeviceCreate(
            name="dev2",
            folder_id=folder_2.id,
            mac_address="61:68:0C:1E:93:9F",
            ip_address="96.119.132.45",
            **mock_os_data,
            **mock_vendor_data
        ),
    )

    device_3 = create_device(
        db,
        DeviceCreate(
            name="dev3",
            folder_id=folder_3.id,
            mac_address="61:68:00:1F:95:AA",
            ip_address="96.119.132.46",
            **mock_os_data,
            **mock_vendor_data
        ),
    )

    user_1 = create_user(
        db,
        UserCreate(
            username="test-user-1@sia.com",
            password="_s3cr3tp@5sw0rd_",  # "$2b$12$l1p.F3cYgrWgVNNOYVeU5efgjLzGqT3AOaQQsm0oUKoHSWyNwd4oe",
        ),
    )
    assign_role(db, user_1.id, roles[0].id)

    user_2 = create_user(
        db,
        UserCreate(
            username="test-user-2@sia.com",
            password="_s3cr3tp@5sw0rd_",  # "$2b$12$l1p.F3cYgrWgVNNOYVeU5efgjLzGqT3AOaQQsm0oUKoHSWyNwd4oe",
        ),
    )
    assign_role(db, user_2.id, roles[1].id)

    user_3 = create_user(
        db,
        UserCreate(
            username="test-user-3@sia.com",
            password="_s3cr3tp@5sw0rd_",  # "$2b$12$l1p.F3cYgrWgVNNOYVeU5efgjLzGqT3AOaQQsm0oUKoHSWyNwd4oe",
        ),
    )
    assign_role(db, user_3.id, roles[1].id)

    user_4 = create_user(
        db,
        UserCreate(
            username="test-user-4@sia.com",
            password="_s3cr3tp@5sw0rd_",  # "$2b$12$l1p.F3cYgrWgVNNOYVeU5efgjLzGqT3AOaQQsm0oUKoHSWyNwd4oe",
        ),
    )
    assign_role(db, user_4.id, roles[2].id)

    user_2.add_tenant(tenant_1)
    user_3.add_tenant(tenant_2)
    user_4.add_tenant(tenant_1)

    # para testear tags, tag_1 debe crearse antes.
    tag_1 = create_tag(db, TagCreate(name="tag-tenant-1", tenant_id=tenant_1.id))
    user_2.add_tag(tag_1)
    tenant_1.add_tag(tag_1)
    device_1.add_tag(tag_1)
    folder_1.add_tag(tag_1)

    tag_2 = create_tag(db, TagCreate(name="tag-user-3", tenant_id=tenant_2.id))
    user_3.add_tag(tag_2)

    # tag_3 = create_tag(db, TagCreate(name="tag-folder-1", tenant_id=tenant_1.id))
    # folder_1.add_tag(tag_3)

    tag_4 = create_tag(db, TagCreate(name="tag-dev-1", tenant_id=tenant_1.id))
    device_1.add_tag(tag_4)

    # tag_5 = create_tag(db, TagCreate(name="tag-subfolder-1", tenant_id=tenant_1.id))
    # subfolder_1.add_tag(tag_5)

    tag_6 = create_tag(db, TagCreate(name="tag-tenant-2", tenant_id=tenant_2.id))
    user_3.add_tag(tag_6)
    tenant_2.add_tag(tag_6)
    device_2.add_tag(tag_6)
    folder_2.add_tag(tag_6)

    # tag_7 = create_tag(db, TagCreate(name="tag-subfolder-2", tenant_id=tenant_2.id))
    # subfolder_2.add_tag(tag_7)

    tag_8 = create_tag(db, TagCreate(name="tag-user-2", tenant_id=tenant_1.id))
    user_2.add_tag(tag_8)

    db.add_all(
        [
            tenant_1,
            tenant_2,
            folder_1,
            subfolder_1,
            folder_2,
            subfolder_2,
            device_1,
            device_2,
            user_1,
            user_2,
            user_3,
            user_4,
        ]
    )
    db.commit()

    yield db

    db.close()
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




async def get_auth_tokens(session: Session, user: User):
    refresh_token = await auth_service.create_refresh_token(session, user.id)
    access_token = auth_utils.create_access_token(user)

    return {"access_token": access_token, "refresh_token": refresh_token}

async def get_auth_tokens_with_user_id(session: Session, user_id: int):
    user = session.query(User).filter(User.id == user_id).first()
    return await get_auth_tokens(session, user)

@pytest.fixture
async def admin_auth_tokens(session: Session):
    user = session.query(User).filter(User.role_id == 1).first()
    return await get_auth_tokens(session, user)


@pytest.fixture
async def owner_2_auth_tokens(session: Session):
    user = session.query(User).filter(User.role_id == 2, User.id == 2).first()
    return await get_auth_tokens(session, user)


@pytest.fixture
async def owner_3_auth_tokens(session: Session):
    user = session.query(User).filter(User.role_id == 2, User.id == 3).first()
    return await get_auth_tokens(session, user)


@pytest.fixture
async def user_auth_tokens(session: Session):
    user = session.query(User).filter(User.role_id == 3).first()
    return await get_auth_tokens(session, user)
