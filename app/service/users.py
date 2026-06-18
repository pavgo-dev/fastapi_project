from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.repository import users as users_repository
from app.schemas import CreateUserRequest, CreateUserResponse


def create_user(session: Session, payload: CreateUserRequest) -> CreateUserResponse:
    if users_repository.get_user(session, payload.login):
        raise HTTPException(status_code=400, detail="User already exists")

    user = users_repository.create_user(session, payload.login)
    session.commit()
    return CreateUserResponse.model_validate(user)
