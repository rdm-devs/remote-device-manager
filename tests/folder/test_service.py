import pytest
from pydantic import ValidationError
from sqlalchemy.orm import Session
from src.tenant.exceptions import TenantNotFoundError
from tests.database import session

from src.folder.exceptions import (
    FolderNameTakenError,
    FolderNotFoundError,
)
from src.folder.service import (
    create_folder,
    get_folder,
    get_folder_by_name,
    get_folders,
    delete_folder,
    update_folder,
)
from src.folder.schemas import (
    FolderCreate,
    FolderUpdate,
)


def test_create_folder(session: Session) -> None:
    folder = create_folder(session, FolderCreate(name="dev-group5"))
    assert folder.name == "dev-group5"
    assert folder.tenant_id == None


def test_create_duplicated_device(session: Session) -> None:
    with pytest.raises(FolderNameTakenError):
        create_folder(session, FolderCreate(name="dev-group1"))


def test_create_incomplete_device(session: Session) -> None:
    with pytest.raises(ValidationError):
        create_folder(session, FolderCreate())


def test_create_folder_with_invalid_tenant(session: Session) -> None:
    with pytest.raises(TenantNotFoundError):
        create_folder(session, FolderCreate(name="dev-group5", tenant_id=5))


def test_get_folder(session: Session) -> None:
    folder = get_folder(session, folder_id=1)
    assert folder.name == "dev-group1"
    assert folder.tenant_id == 1


def test_get_folder_with_invalid_id(session: Session) -> None:
    with pytest.raises(FolderNotFoundError):
        get_folder(session, folder_id=5)


def test_get_folder_by_name(session: Session) -> None:
    folder = get_folder_by_name(session, folder_name="dev-group1")
    assert folder.name == "dev-group1"
    assert folder.tenant_id == 1


def test_get_folder_with_invalid_name(session: Session) -> None:
    with pytest.raises(FolderNotFoundError):
        get_folder_by_name(session, folder_name="dev-group5")


def test_get_folders(session: Session) -> None:
    # two device groups were created in tests/database.py
    folders = get_folders(session)
    assert len(folders) == 2


def test_update_folder(session: Session) -> None:
    folder = create_folder(
        session, FolderCreate(name="dev-group5", tenant_id=None)
    )
    db_folder = get_folder(session, folder.id)

    folder = update_folder(
        session,
        db_folder=db_folder,
        updated_folder=FolderUpdate(name="dev-group-custom", tenant_id=1),
    )
    assert folder.name == "dev-group-custom"
    assert folder.tenant_id == 1


def test_update_folder_with_invalid_tenant(session: Session) -> None:
    folder = create_folder(
        session, FolderCreate(name="dev-group5", tenant_id=1)
    )
    db_folder = get_folder(session, folder.id)

    with pytest.raises(TenantNotFoundError):
        folder = update_folder(
            session,
            db_folder=db_folder,
            updated_folder=FolderUpdate(
                name="dev-group-custom", tenant_id=5
            ),
        )


def test_update_folder_with_incomplete_data(session: Session) -> None:
    folder = create_folder(
        session, FolderCreate(name="dev-group5", tenant_id=1)
    )
    db_folder = get_folder(session, folder.id)

    with pytest.raises(ValidationError):
        folder = update_folder(
            session,
            db_folder=db_folder,
            updated_folder=FolderUpdate(tenant_id=1, tag="my-custom-tag"),
        )


def test_update_folder_with_invalid_id(session: Session) -> None:
    db_folder = get_folder(session, 1)
    db_folder.id = 5

    with pytest.raises(FolderNotFoundError):
        update_folder(
            session,
            db_folder=db_folder,
            updated_folder=FolderUpdate(
                name="dev-group-custom", tenant_id=1
            ),
        )


def test_delete_group_device(session: Session) -> None:
    folder = create_folder(
        session, FolderCreate(name="dev-group5delete", tenant_id=1)
    )
    db_folder = get_folder(session, folder.id)

    folder_id = folder.id
    deleted_folder_id = delete_folder(
        session, db_folder=db_folder
    )
    assert deleted_folder_id == folder_id

    with pytest.raises(FolderNotFoundError):
        get_folder(session, folder.id)


def test_delete_folder_with_invalid_id(session: Session) -> None:
    folder = create_folder(
        session, FolderCreate(name="dev-group5delete", tenant_id=1)
    )
    db_folder = get_folder(session, folder.id)

    db_folder.id = 5
    with pytest.raises(FolderNotFoundError):
        delete_folder(session, db_folder=db_folder)
