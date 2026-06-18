from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import UserOrm


def get_user(session: Session, login: str) -> UserOrm | None:
    query = select(UserOrm).where(UserOrm.login == login)
    user = session.scalar(query)
    return user


def create_user(session: Session, login: str) -> UserOrm:
    new_user = UserOrm(login=login)
    session.add(new_user)
    session.flush()
    return new_user
