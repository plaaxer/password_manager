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

@router.post("/token", response_model=models.Token)
async def login_token(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    Handles the initial login. The user posts their username
    and password (the master password).
    
    If authentication is successful, it returns a JWT.
    """

    print("AAAAA")

    logger.debug(f"[DEBUG] Attempting to authenticate user {form_data.username}.")

    # 1. Authenticate the user. The service layer handles exceptions.
    user = await application.authenticate_user(form_data.username, form_data.password)

    logger.debug(f"[DEBUG] User {user.username} authenticated successfully.")
    print("BBBBB")

    # 2. If valid, create a JWT access token.
    access_token = application.create_access_token(data={"sub": user.username})

    logger.debug(f"[DEBUG] Access token created for user {user.username}.")
    print("CCCCC")
    
    # 3. Return the token. FastAPI validates this dict against models.Token.
    return {"access_token": access_token, "token_type": "bearer"}


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
