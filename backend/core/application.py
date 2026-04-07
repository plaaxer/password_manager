# backend/core/application.py

from datetime import datetime, timedelta, timezone
from typing import Optional

from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import SecretStr

from api import models
from core.services.token_service import TokenService
from core.services.authentication_service import AuthenticationService
from core.services.user_service import UserService
from core.utils.logger import Logger
from core import database

logger = Logger(__name__).get_logger()

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

# --- TOKENS ---

def get_username_from_token(token: str) -> Optional[str]:
    return TokenService.get_username_from_token(token)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    return TokenService.create_access_token(data, expires_delta)

# --- AUTHENTICATION ---

async def login(form_data: 'OAuth2PasswordRequestForm') -> models.Token:
    """
    Handles the initial login. The user posts their username
    and password (the master password).
    
    If authentication is successful, it returns a JWT.
    """

    logger.debug(f"Attempting to authenticate user {form_data.username}.")

    user = await authenticate_user(form_data.username, form_data.password)

    logger.debug(f"User {user.username} authenticated successfully.")   

    access_token = create_access_token(data={"sub": user.username})

    logger.info(f"Access token created for user {user.username}.")
    
    return {"access_token": access_token, "token_type": "bearer"}

async def authenticate_user(username: str, password: SecretStr) -> models.UserInDB:
    return await AuthenticationService.authenticate_user(username, password)

# -- USER MANAGEMENT ---

async def create_user(user: models.UserCreate) -> models.UserInDB:
    return await UserService.create_user(user)

# -- PASSWORD MANAGEMENT ---

async def get_password(token: str, password_request: 'models.PasswordRequest', service_name: str) -> 'models.PasswordData':
    """
    Retrieves and decrypts the password for a given service.
    """
    username = get_username_from_token(token)
    if username is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        )
    try:
        return await UserService.get_and_decrypt_password(username, service_name,
                                                        password_request.master_password)
    except Exception as e:
        logger.error(f"Error retrieving password for user '{username}' and service '{service_name}': {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not retrieve password"
        )

async def store_password(token: str, service_name: str, password_data: 'models.PasswordCreate', master_password: str):
    """
    Encrypts and stores the password for a given service.
    """
    username = get_username_from_token(token)
    if not username:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )

    await UserService.store_and_encrypt_password(username, service_name, password_data, master_password)

async def delete_password(token: str, service_name: str):
    """
    Deletes the password entry for a given service.
    """
    username = get_username_from_token(token)
    if not username:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )
    
    await database.delete_encrypted_password(username, service_name)

async def list_passwords(password_request: models.PasswordRequest, token: str) -> list['models.PasswordMetadata']:
    """
    Lists all stored passwords for the authenticated user without revealing sensitive data.
    """
    username = get_username_from_token(token)
    if not username:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )
    try:
        return await UserService.list_stored_passwords(username, password_request.master_password)
    except Exception as e:
        logger.error(f"Error listing passwords for user '{username}': {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not retrieve passwords"
        )