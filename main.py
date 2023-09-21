from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session

from . import crud, models, schemas
from .database import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)

app = FastAPI()


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post("/users/", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return crud.create_user(db=db, user=user)


@app.get("/users/", response_model=list[schemas.User])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    users = crud.get_users(db, skip=skip, limit=limit)
    return users


@app.get("/users/{user_id}", response_model=schemas.User)
def read_user(user_id: int, db: Session = Depends(get_db)):
    db_user = crud.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user


@app.post("/user_group/", response_model=schemas.UserGroup)
def create_user_group(user_group: schemas.UserGroupCreate, db: Session = Depends(get_db)):
    # TODO: implement crud code
    db_user_group = crud.get_user_group_by_name(db, name=user_group.name)
    if db_user_group:
        raise HTTPException(status_code=400, detail="UserGroup name already registered")
    return crud.create_user_group(db=db, user_group=user_group)

@app.get("/user_group/{group_id}", response_model=schemas.UserGroup)
def read_user_group(group_id: int, db: Session = Depends(get_db)):
    # TODO: implement crud code
    db_user_group = crud.get_user_group(db, group_id=group_id)
    if db_user_group is None:
        raise HTTPException(status_code=404, detail="UserGroup not found")
    return db_user_group

@app.get("/user_groups/", response_model=list[schemas.UserGroup])
def read_user_groups(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    # TODO: implement crud code
    user_groups = crud.get_user_groups(db, skip=skip, limit=limit)
    return user_groups

@app.put("/user_group/{group_id}", response_model=schemas.UserGroupUpdate)
def create_user_group(user_group: schemas.UserGroupUpdate, db: Session = Depends(get_db)):
    # TODO: implement crud code
    db_user_group = crud.update_user_group(db, name=user_group.name)
    if db_user_group:
        raise HTTPException(status_code=400, detail="UserGroup could not be updated")
    return crud.create_user_group(db=db, user_group=user_group)


"""
@app.post("/users/{user_id}/items/", response_model=schemas.Item)
def create_item_for_user(
    user_id: int, item: schemas.ItemCreate, db: Session = Depends(get_db)
):
    return crud.create_user_item(db=db, item=item, user_id=user_id)


@app.get("/items/", response_model=list[schemas.Item])
def read_items(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    items = crud.get_items(db, skip=skip, limit=limit)
    return items
"""