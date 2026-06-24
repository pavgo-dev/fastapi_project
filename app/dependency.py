from collections.abc import AsyncGenerator

from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import async_session_factory
from app.models import UserOrm
from app.repository import users as users_repository

security = HTTPBearer()


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_factory() as session:
        yield session  # Передает асинхронную сессию и автоматически закроет её после запроса


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security), session: AsyncSession = Depends(get_session)
) -> UserOrm:
    token = credentials.credentials

    # Слой защиты (будущий JWT). перехват невалидного формата строки
    try:
        # Когда добавлю библиотеку PyJWT здесь будет   payload = jwt.decode(...)
        login = token
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token") from None

    # Ищу пользователя в базе данных
    user = await users_repository.get_user(session, login=login)

    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")

    return user
