import os
import pytest
from typing import Generator
from sqlalchemy import StaticPool, create_engine
from sqlalchemy.orm import sessionmaker, Session
from dotenv import load_dotenv
from src import device_group
from src.main import app
from src.database import get_db, Base
from src.device.models import Device
from src.device_group.models import DeviceGroup
from src.user.models import User
from src.user_group.models import UserGroup
from src.tenant.models import Tenant

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
def session() -> Generator[Session, None, None]:
    # Create the tables in the test database
    Base.metadata.create_all(bind=engine)

    db_session = TestingSessionLocal()

    # create test objects (Device, DeviceGroup, User, UserGroup, Tenant)
    db_tenant = Tenant(id=1, name="tenant1")
    db_device_group = DeviceGroup(id=1, name="dev-group1", tenant_id=1)
    db_device_group_2 = DeviceGroup(id=2, name="dev-group2")
    db_device = Device(id=1, name="dev1", device_group_id=1)
    db_device_2 = Device(id=2, name="dev2", device_group_id=1)
    db_user_group = UserGroup(id=1, name="user-group1", device_group_id=1)
    db_user = User(
        id=1, hashed_password="_s3cr3tp@5sw0rd_", email="test-user@sia.com", group_id=1
    )

    db_session.add_all(
        [
            db_tenant,
            db_device_group,
            db_device_group_2,
            db_device,
            db_device_2,
            db_user,
            db_user_group,
        ]
    )
    db_session.commit()

    yield db_session

    db_session.close()
    Base.metadata.drop_all(bind=engine)
