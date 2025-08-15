from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from datetime import timedelta

import core.application as application
import core.models as models

router = APIRouter()

# --- Authentication Logic ---

# This dependency will check for a valid JWT in the Authorization header.
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

from core.utils.logger import Logger
logger = Logger(__name__).get_logger()


# --- API Endpoints ---

@router.post("/login", response_model=models.Token)
async def login_token(form_data: OAuth2PasswordRequestForm = Depends()):

    """ Endpoint to log in and receive a JWT token.
    The user posts their username and password (the master password).
    If authentication is successful, it returns a JWT."""

    return await application.login(form_data=form_data)


@router.post("/register")
async def register_user(registration_data: models.UserCreate):

    """
    Endpoint to register a new user.
    """
    new_user = await application.create_user(user=registration_data)

    return {"message": f"User {new_user.username} registered successfully."}


@router.get("/passwords/{service_name}", response_model=models.PasswordData)
async def get_password(
    service_name: str, 
    request_data: 'models.PasswordRequest',
    token: str = Depends(oauth2_scheme)):

    """
    A protected endpoint to retrieve a decrypted password.
    """
    return await application.get_password(service_name=service_name, token=token, password_request=request_data)

# todo: post should be at password only, model with service name
@router.post("/passwords")
async def store_password(
    service_name: str, 
    password_data: models.PasswordCreate,
    token: str = Depends(oauth2_scheme)):

    """
    A protected endpoint to store an encrypted password.
    """

    await application.store_password(token=token, service_name=service_name, password_data=password_data)

    return {"message": f"Password for {service_name} stored successfully."}
