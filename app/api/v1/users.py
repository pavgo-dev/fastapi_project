from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.dependency import get_current_user, get_db
from app.models import UserOrm
from app.schemas.users import CreateUserRequest, CreateUserResponse
from app.service import users as users_service

router = APIRouter()


@router.post("/users", response_model=CreateUserResponse)
def create_user(payload: CreateUserRequest, session: Session = Depends(get_db)):
    return users_service.create_user(session, payload)


@router.get("/users/me", response_model=CreateUserResponse)
def get_user(current_user: UserOrm = Depends(get_current_user)):
    return CreateUserResponse.model_validate(current_user)
