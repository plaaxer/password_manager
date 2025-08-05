# ./password_manager/backend/run.py

from fastapi import FastAPI
from contextlib import asynccontextmanager
from .api import routes
from .core import database

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    This function manages the lifespan of the application, handling startup and shutdown events.
    """
    print("Application startup: Connecting to the database...")
    await database.connect_to_db()
    print("Database connection established.")
    yield
    print("Application shutdown: Closing database connection...")
    await database.close_db_connection()
    print("Database connection closed.")

app = FastAPI(
    title="Password Manager API",
    description="A secure API for managing passwords.",
    version="2.0.0",
    lifespan=lifespan,
)

app.include_router(routes.router, prefix="/api/v1")

@app.get("/", tags=["Health Check"])
def read_root():
    return {"message": "Password Manager API is running"}

