import pytest
from pydantic import ValidationError
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload
from src.tenant.exceptions import TenantNotFound
from tests.database import session, mock_os_data, mock_vendor_data

from src.folder.exceptions import (
    FolderNameTaken,
    FolderNotFound,
)
from src.folder.service import (
    create_folder,
    get_folder,
    get_folder_by_name,
    get_folders,
    delete_folder,
    update_folder,
    create_root_folder,
    get_root_folder,
    get_folder_ids_in_tree,
)
from src.folder.schemas import (
    FolderCreate,
    FolderUpdate,
)
from src.user.service import create_user
from src.user.schemas import UserCreate
from src.user.exceptions import UserTenantNotAssigned
from src.tag.models import Tag, entities_and_tags_table
from src.tag.service import get_tag_by_name, get_tag
from src.tag.exceptions import TagNotFound
from src.tenant.service import get_tenant
from src.entity.service import get_entity
from src.entity.exceptions import EntityNotFound
from src.device.models import Device
from src.device.service import create_device
from src.device.schemas import DeviceCreate
from src.device.utils import get_devices_in_tree
from src.folder.models import Folder


def test_create_folder(session: Session) -> None:
    folder = create_folder(session, FolderCreate(name="folder5", tenant_id=1))
    assert folder.name == "folder5"
    assert folder.tenant_id == 1
    assert len(folder.tags) == 1


def test_create_duplicated_folder(session: Session) -> None:
    with pytest.raises(FolderNameTaken):
        create_folder(session, FolderCreate(name="folder1", tenant_id=1))


def test_create_folder_after_deleting_it(session: Session) -> None:
    folder = create_folder(session, FolderCreate(name="folder5", tenant_id=1))
    assert folder.name == "folder5"
    assert len(folder.tags) == 1
    tag_name = folder.tags[0].name
    entity_id = folder.entity_id

    deleted_folder_id = delete_folder(session, folder)

    with pytest.raises(EntityNotFound):
        get_entity(session, entity_id)

    with pytest.raises(TagNotFound):
        get_tag_by_name(session, tag_name)

    with pytest.raises(FolderNotFound):
        folder = get_folder(session, deleted_folder_id)

    new_folder = create_folder(session, FolderCreate(name="folder5", tenant_id=1))
    assert new_folder.name == "folder5"
    assert len(new_folder.tags) == 1
    assert new_folder.tags[0].name == tag_name


def test_create_incomplete_folder(session: Session) -> None:
    with pytest.raises(ValidationError):
        create_folder(session, FolderCreate())


def test_create_folder_with_invalid_tenant(session: Session) -> None:
    with pytest.raises(TenantNotFound):
        create_folder(session, FolderCreate(name="folder5", tenant_id=5))


def test_get_folder(session: Session) -> None:
    folder = get_folder(session, folder_id=3)
    assert folder.name == "folder1"
    assert folder.tenant_id == 1
    assert len(folder.tags) == 3
    assert folder.tags[0].name == "folder-tenant1-folder1-tag"


def test_get_folder_with_invalid_id(session: Session) -> None:
    with pytest.raises(FolderNotFound):
        get_folder(session, folder_id=16)


def test_get_folder_by_name(session: Session) -> None:
    folder = get_folder_by_name(session, folder_name="folder1")
    assert folder.name == "folder1"
    assert folder.tenant_id == 1


def test_get_folder_with_invalid_name(session: Session) -> None:
    with pytest.raises(FolderNotFound):
        get_folder_by_name(session, folder_name="folder5")


def test_get_folders(session: Session) -> None:
    # five folders/subfolders were created in tests/database.py
    # pagination results only counts "/" folders as items as the others count as subfolders of them.
    folders = session.execute(get_folders(session, user_id=1)).fetchall()
    assert len(folders) == 2

    folders = session.execute(get_folders(session, user_id=2)).fetchall()
    assert len(folders) == 1

    folders = session.execute(get_folders(session, user_id=3)).fetchall()
    assert len(folders) == 1

    folders = session.execute(get_folders(session, user_id=4)).fetchall()
    assert len(folders) == 1

    user5 = create_user(
        session,
        UserCreate(
            username="test-user-5@sia.com",
            password="_s3cr3tp@5sw0rd_",
        ),
    )
    with pytest.raises(UserTenantNotAssigned):
        folders = session.execute(
            get_folders(session, user_id=5)
        ).fetchall()  # this user has no tenant asigned so it will raise an exception


def test_update_folder(session: Session) -> None:
    folder = create_folder(session, FolderCreate(name="folder5", tenant_id=1))
    db_folder = get_folder(session, folder.id)

    original_tags = folder.tags
    folder_tag_ids = [t.id for t in original_tags]

    def get_tag_ids(tenant_id: int):
        return session.scalars(select(Tag.id).where(Tag.tenant_id == tenant_id)).all()

    def update(tags):
        folder = update_folder(
            session,
            db_folder=db_folder,
            updated_folder=FolderUpdate(name="folder-custom", tags=tags),
        )
        return folder

    # tags from tenant 2 must not be present in the updated folder
    tenant_id = 2
    tenant_2 = get_tenant(session, tenant_id)

    new_tags = list(set([*folder.tags, *tenant_2.tags]))
    folder = update(tags=new_tags)
    assert folder.name == "folder-custom"
    assert folder.tenant_id == 1
    assert all(t not in folder.tags for t in tenant_2.tags)
    assert all(
        t in folder.tags for t in original_tags
    )  # tags have not changed after update

    # tags from tenant 1 must be present in the updated folder as the folder
    # was created with tenant_id=1
    tenant_id = 1
    tenant_1 = get_tenant(session, tenant_id)
    new_tags = list(set([*folder.tags, *tenant_1.tags]))
    folder = update(tags=new_tags)
    assert all(t in folder.tags for t in tenant_1.tags)

    # testing associative relationship (Entity-Tag) is working
    query = select(entities_and_tags_table.c.tag_id).where(
        entities_and_tags_table.c.entity_id == folder.entity_id,
    )
    relationship_tag_ids = session.scalars(query).all()
    assert relationship_tag_ids is not None
    assert all(t.id in relationship_tag_ids for t in folder.tags)


def test_update_folder_with_empty_lists(session: Session) -> None:
    folder = get_folder(session, 3)

    folder = update_folder(
        session,
        db_folder=folder,
        updated_folder=FolderUpdate(tags=[], devices=[], subfolders=[]),
    )
    assert len(folder.tags) == 0
    assert len(folder.subfolders) == 0
    assert len(folder.devices) == 0


def test_update_folder_with_invalid_tenant(session: Session) -> None:
    folder = create_folder(session, FolderCreate(name="folder5", tenant_id=1))
    db_folder = get_folder(session, folder.id)

    with pytest.raises(TenantNotFound):
        folder = update_folder(
            session,
            db_folder=db_folder,
            updated_folder=FolderUpdate(name="folder-custom", tenant_id=5),
        )


def test_update_folder_with_invalid_id(session: Session) -> None:
    db_folder = get_folder(session, 1)
    db_folder.id = 16

    with pytest.raises(FolderNotFound):
        update_folder(
            session,
            db_folder=db_folder,
            updated_folder=FolderUpdate(name="folder-custom", tenant_id=1),
        )


def test_delete_folder(session: Session) -> None:
    folder = create_folder(session, FolderCreate(name="folder6delete", tenant_id=1))
    db_folder = get_folder(session, folder.id)

    folder_id = folder.id
    entity = folder.entity
    tag_ids = [t.id for t in folder.tags]

    deleted_folder_id = delete_folder(session, db_folder=db_folder)
    assert deleted_folder_id == folder_id

    with pytest.raises(FolderNotFound):
        get_folder(session, folder.id)

    # after removing folder, the related entity has been deleted
    with pytest.raises(EntityNotFound):
        get_entity(session, entity_id=entity.id)

    # after removing folder, the related tags have been deleted
    with pytest.raises(TagNotFound):
        for tid in tag_ids:
            get_tag(session, tid)


def test_delete_folder_with_invalid_id(session: Session) -> None:
    db_folder = get_folder(session, 5)

    db_folder.id = 16  # this id must not exist
    with pytest.raises(FolderNotFound):
        delete_folder(session, db_folder=db_folder)


def test_delete_folder_and_reset_devices_folder_id(session: Session) -> None:
    folder = get_folder(session, folder_id=1)
    tenant1_root_folder = get_root_folder(session, tenant_id=1)
    devices = folder.devices

    deleted_folder_id = delete_folder(session, db_folder=folder)
    assert deleted_folder_id == folder.id

    post_delete_devices_folder_id = [d.folder_id for d in devices]
    assert all(
        [
            folder_id == tenant1_root_folder.id
            for folder_id in post_delete_devices_folder_id
        ]
    )


def test_delete_folder_and_subfolders(session: Session, mock_os_data: dict, mock_vendor_data: dict) -> None:
    # folder structure where * denotes that the folder has a device.
    #
    #                    f
    #                s1*     s2*
    #             s11*     s21
    #

    folder = create_folder(session, FolderCreate(name="folder5", tenant_id=1))
    root_folder = get_root_folder(session, folder.tenant_id)
    sub1 = create_folder(session, FolderCreate(name="sub1", tenant_id=1, parent_id=folder.id))
    sub11 = create_folder(session, FolderCreate(name="sub11", tenant_id=1, parent_id=sub1.id))

    sub2 = create_folder(session, FolderCreate(name="sub2", tenant_id=1, parent_id=folder.id))
    sub21 = create_folder(session, FolderCreate(name="sub21", tenant_id=1, parent_id=sub2.id))

    dev_test = create_device(
        session,
        DeviceCreate(
            name="dev-test",
            folder_id=sub1.id,
            mac_address="61:68:0C:1E:93:8C",
            ip_address="96.119.132.41",
            id_rust="myRustDeskId",
            pass_rust="myRustDeskPass",
            serialno="DeviceSerialno0004",
            **mock_os_data,
            **mock_vendor_data
        ),
    )
    dev_test_2 = create_device(
        session,
        DeviceCreate(
            name="dev-test-2",
            folder_id=sub11.id,
            mac_address="61:68:0C:1E:93:1C",
            ip_address="96.119.132.31",
            id_rust="myRustDeskId",
            pass_rust="myRustDeskPass",
            serialno="DeviceSerialno0005",
            **mock_os_data,
            **mock_vendor_data
        ),
    )

    dev_test_3 = create_device(
        session,
        DeviceCreate(
            name="dev-test-3",
            folder_id=sub2.id,
            mac_address="61:68:0C:1E:A3:1C",
            ip_address="96.119.132.21",
            id_rust="myRustDeskId",
            pass_rust="myRustDeskPass",
            serialno="DeviceSerialno0006",
            **mock_os_data,
            **mock_vendor_data
        ),
    )

    folder_tree = get_folder_ids_in_tree(folder)
    subfolders = folder.subfolders

    deleted_folder_id = delete_folder(session, db_folder=folder)
    assert deleted_folder_id == folder.id

    # after deleting a folder, none of the subfolders should exist. (cascade)
    with pytest.raises(FolderNotFound):
        for sf_id in folder_tree:
            f = get_folder(session, sf_id)

    # after deleting a folder all the previously associated devices should now 
    # be associated with the root folder of tenant1. 
    device_ids = get_devices_in_tree(session, folder_tree)
    devs = session.scalars(select(Device).where(Device.id.in_(device_ids))).all()
    assert all(d.folder_id == root_folder.id for d in devs)
