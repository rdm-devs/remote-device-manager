from fastapi import Depends, APIRouter, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from . import service, schemas

router = APIRouter(prefix="/tags", tags=["tags"])


@router.post("/", response_model=schemas.Tag)
def create_tag(tag: schemas.TagCreate, db: Session = Depends(get_db)):
    db_tag = service.create_tag(db, tag)
    return db_tag


@router.get("/{tag_id}", response_model=schemas.Tag)
def read_tag(tag_id: int, db: Session = Depends(get_db)):
    db_tag = service.get_tag(db, tag_id)
    return db_tag


@router.get("/", response_model=list[schemas.Tag])
def read_tags(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return service.get_tags(db, skip=skip, limit=limit)


@router.patch("/{tag_id}", response_model=schemas.Tag)
def update_tag(tag_id: int, tag: schemas.TagUpdate, db: Session = Depends(get_db)):
    db_tag = read_tag(tag_id, db)
    updated_device = service.update_tag(db, db_tag, updated_tag=tag)
    if not updated_device:
        raise HTTPException(status_code=400, detail="Tag could not be updated")
    return updated_device


@router.delete("/{tag_id}", response_model=schemas.TagDelete)
def delete_device(tag_id: int, db: Session = Depends(get_db)):
    db_tag_group = read_tag(tag_id, db)
    deleted_tag_id = service.delete_tag(db, db_tag_group)
    if not deleted_tag_id:
        raise HTTPException(status_code=400, detail="Tag could not be deleted")
    return {
        "id": deleted_tag_id,
        "msg": f"Tag {deleted_tag_id} removed succesfully!",
    }
