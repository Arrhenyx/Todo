from fastapi import APIRouter, Depends, HTTPException, Path, status
from typing import Annotated
from sqlalchemy.orm import Session
from models import Todos
from database import SessionLocal
from pydantic import BaseModel, Field
from .auth import get_current_user

router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]
user_dependency= Annotated[dict, Depends(get_current_user())]


class TodoRequest(BaseModel):
    title: str = Field(min_length=3)
    description: str = Field(min_length=3, max_length=100)
    priority: int = Field(gt=0, lt=6)
    complete: bool


@router.get('/', status_code=status.HTTP_200_OK)
async def read_all(db: db_dependency):
    return db.query(Todos).filter(Todos.owner_id == user.get("id").all)


@router.get("/todo/{todo_id}", status_code=status.HTTP_200_OK)
async def read_todo(user:user_dependency, db: db_dependency, todo_id: int = Path(gt=0)):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed.")

    todo_model = (db.query(Todos).filter(Todos.id == todo_id)\
                  .filter(Todos.owner_id == user.get("id")).first())
    if todo_model is not None:
        return todo_model
    raise HTTPException(status_code=404, detail="TODO IS NOT FOUND!")


@router.post("/todo", status_code=status.HTTP_201_CREATED)
async def create_todo(user: user_dependency,
                      db: db_dependency,
                      todo_request: TodoRequest):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed.")

    todo_model = Todos(**todo_request.dict(),owner_id=user.get("id"))
    db.add(todo_model)
    db.commit()  # Fixed: removed todo_model from commit
    db.refresh(todo_model)  # Optional: refresh to get the generated ID
    return todo_model


@router.put("/todo/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_todo(user: user_dependency,
                      db: db_dependency,
                      todo_request: TodoRequest,  # Fixed typo: todo_requst -> todo_request
                      todo_id: int = Path(gt=0)):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed.")

    todo_model = db.query(Todos).filter(Todos.id == todo_id)\
        .filter(Todos.owner_id == user.get('id')).first()
    if todo_model is None:
        raise HTTPException(status_code=404, detail="TODO IS NOT HERE")

    todo_model.title = todo_request.title  # Fixed: todo.request -> todo_request
    todo_model.description = todo_request.description  # Fixed: todo_rquest -> todo_request
    todo_model.priority = todo_request.priority  # Fixed: todo.request -> todo_request
    todo_model.complete = todo_request.complete

    db.add(todo_model)
    db.commit()  # Fixed: db, commit -> db.commit


@router.delete("/todo/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)  # Fixed: added missing slash
async def delete_todo( user: user_dependency, db: db_dependency, todo_id: int = Path(gt=0)):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed.")

    todo_model = db.query(Todos).filter(Todos.id == todo_id)\
        .filter(Todos.owner_id == user.get('id')).first()

    if todo_model is None:
        raise HTTPException(status_code=404, detail="TODO NOT FOUND")  # Fixed spelling
    db.query(Todos).filter(Todos.id == todo_id).filter(Todos.owner_id == user.get("id")).delete()
    db.commit()