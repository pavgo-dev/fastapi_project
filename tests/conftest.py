from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.config import settings
from app.database import Base
from app.dependency import get_session
from main import app

test_engine = create_engine(url=settings.TESTDATABASE_URL_psycopg_sync)
testSessionLocal = sessionmaker(bind=test_engine, autoflush=False)


# 1. Создаю и удаляею таблицы единожды за весь запуск тестов
@pytest.fixture(scope="session", autouse=True)  # scope="session" ЗАПУСКАЕТ ОДИН РАЗ ПЕРЕД СЕССИЕЙ ТЕСТОВ
def setup_db():
    Base.metadata.create_all(bind=test_engine)
    yield
    Base.metadata.drop_all(bind=test_engine)


# 2. Главная фикстура, которая держит транзакцию для всего теста
@pytest.fixture  # ПО УМОЛЧАНИЮ scope="function". scope="session" ЗАПУСКАЕТ ОДИН РАЗ ПЕРЕД СЕССИЕЙ ТЕСТОВ
def db_session() -> Generator[Session, None, None]:
    connection = test_engine.connect()
    # Начинаю внешнюю транзакцию
    transaction = connection.begin()
    # Привязываю сессию к конкретному коннекту с транзакцией
    session = testSessionLocal(bind=connection)

    yield session

    # Закрываю все + ROLLBACK. База чистая
    session.close()
    transaction.rollback()
    connection.close()


# 3. Переопределить зависимость FastAPI, используя ту же фикстуру db_session
@pytest.fixture(autouse=True)
def override_dependency(db_session):
    # Внутренняя функция для FastAPI должна быть обычной функцией/генератором, а не фикстурой
    def get_test_session() -> Generator[Session, None, None]:
        yield db_session

    app.dependency_overrides[get_session] = get_test_session
    yield
    app.dependency_overrides.clear()


@pytest.fixture
def client():
    return TestClient(app)
