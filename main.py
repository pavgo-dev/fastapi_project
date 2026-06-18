from fastapi import FastAPI
from fastapi.responses import Response

from app.api.v1.operations import router as operations_router
from app.api.v1.wallets import router as wallet_router
from app.database import Base, engine

# Создание таблиц
Base.metadata.create_all(bind=engine)


# инициализация FastAPI приложения
app = FastAPI()


# делаем  health check endpoint
@app.get("/health/")
def health_check():
    return Response(status_code=200)


app.include_router(wallet_router, prefix="/api/v1", tags=["wallet"])
app.include_router(operations_router, prefix="/api/v1", tags=["operations"])

# if __name__ == "__main__":
