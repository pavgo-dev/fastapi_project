from collections.abc import Generator

from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models import UserOrm
from app.repository import users as users_repository

security = HTTPBearer()


def get_session() -> Generator[Session, None, None]:
    with SessionLocal() as session:
        yield session  # Передает сессию и держит её открытой на время запроса


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security), session: Session = Depends(get_session)
) -> UserOrm:
    token = credentials.credentials

    # Слой защиты (будущий JWT). перехват невалидного формата строки
    try:
        # Когда добавлю библиотеку PyJWT здесь будет   payload = jwt.decode(...)
        login = token
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token") from None

    # Ищу пользователя в базе данных
    user = users_repository.get_user(session, login=login)

    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")

    return user
