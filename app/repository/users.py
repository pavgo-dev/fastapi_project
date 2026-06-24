from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import UserOrm


async def get_user(session: AsyncSession, login: str) -> UserOrm | None:
    query = select(UserOrm).where(UserOrm.login == login)
    user = await session.scalar(query)
    return user


async def create_user(session: AsyncSession, login: str) -> UserOrm:
    new_user = UserOrm(login=login)
    session.add(new_user)
    await session.flush()
    return new_user
