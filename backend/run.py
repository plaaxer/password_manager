# ./password_manager/backend/run.py

from fastapi import FastAPI
from contextlib import asynccontextmanager
from api import routes
from core import database

from core.utils.logger import Logger
logger = Logger(__name__).get_logger()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    This function manages the lifespan of the application, handling startup and shutdown events.
    """
    logger.info("Application startup: Connecting to the database...")
    await database.connect_to_db()
    logger.info("Database connection established.")
    yield
    logger.info("Application shutdown: Closing database connection...")
    await database.close_db_connection()
    logger.info("Database connection closed.")

security_schemes = {
    "components": {
        "securitySchemes": {
            "BearerAuth": {
                "type": "http",
                "scheme": "bearer",
                "bearerFormat": "JWT"
            }
        }
    },
    "security": [{"BearerAuth": []}],
}

app = FastAPI(
    title="Password Manager API",
    description="A secure API for managing passwords.",
    version="2.0.0",
    lifespan=lifespan,
    openapi_extra=security_schemes,
)

app.include_router(routes.router, prefix="/api/v2")

@app.get("/", tags=["Health Check"])
def read_root():
    return {"message": "Password Manager API is running"}

