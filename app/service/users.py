from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import UserOrm
from app.repository import users as users_repository
from app.schemas.users import CreateUserRequest


async def create_user(session: AsyncSession, payload: CreateUserRequest) -> UserOrm:
    if await users_repository.get_user(session, payload.login):
        raise HTTPException(status_code=400, detail="User already exists")

    user = await users_repository.create_user(session, payload.login)
    await session.commit()
    return user
