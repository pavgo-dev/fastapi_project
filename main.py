from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.responses import Response

from app.api.v1.operations import router as operations_router
from app.api.v1.users import router as users_router
from app.api.v1.wallets import router as wallets_router
from app.database import Base, async_engine


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Асинхронно создаем таблицы при старте приложения
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    # Тут можно прописать логику закрытия ресурсов при выключении


# инициализация FastAPI приложения
app = FastAPI(lifespan=lifespan)


# делаем  health check endpoint
@app.get("/health/")
def health_check():
    return Response(status_code=200)


app.include_router(wallets_router, prefix="/api/v1", tags=["wallets"])
app.include_router(operations_router, prefix="/api/v1", tags=["operations"])
app.include_router(users_router, prefix="/api/v1", tags=["users"])
# if __name__ == "__main__":
