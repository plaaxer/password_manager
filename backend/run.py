# ./password_manager/backend/run.py

from fastapi import FastAPI
from contextlib import asynccontextmanager
from .api import routes as api_routes
from .core import database

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    This function manages the lifespan of the application, handling startup and shutdown events.
    """
    # Startup event
    print("Application startup: Connecting to the database...")
    await database.connect_to_db()
    print("Database connection established.")
    yield # The application will run until this point
    # Shutdown event
    print("Application shutdown: Closing database connection...")
    await database.close_db_connection()
    print("Database connection closed.")

# --- Main FastAPI Application Instance ---
app = FastAPI(
    title="Password Manager API",
    description="A secure API for managing passwords.",
    version="2.0.0",
    lifespan=lifespan,
)

# --- API Router ---
# Include all the endpoints from your routes.py file.
# The prefix="/api/v1" means all routes defined in routes.py
# will be accessible under a path like http://localhost:8000/api/v1/token
app.include_router(api_routes.router, prefix="/api/v1")


# --- Root Endpoint ---
@app.get("/", tags=["Health Check"])
def read_root():
    """
    Root endpoint for the API. Provides a simple welcome message.
    """
    return {"message": "Password Manager API is running"}

