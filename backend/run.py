# /backend/run.py

from fastapi import FastAPI
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware

from api import routes
from core import database

from core.utils.logger import Logger
logger = Logger(__name__).get_logger()

@asynccontextmanager
async def lifespan(app: FastAPI):

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
    title="Argus Password Manager API",
    description="A secure API for storing and retrieving passwords.",
    version="2.0.0",
    lifespan=lifespan,
    openapi_extra=security_schemes,
)

origins = [
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(routes.router, prefix="/api/v2")

@app.get("/", tags=["Health Check"])
def read_root():
    return {"message": "Argus Password Manager API is running"}

