# backend/core/application.py

import os
from datetime import datetime, timedelta, timezone
from typing import Optional

from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import SecretStr

from core.services.token_service import TokenService
from core.services.authentication_service import AuthenticationService
from core.services.user_service import UserService
from core.utils.logger import Logger
from core import database, models

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

    # 1. Authenticate the user. The service layer handles exceptions.
    user = await authenticate_user(form_data.username, form_data.password)

    logger.debug(f"User {user.username} authenticated successfully.")   

    # 2. If valid, create a JWT access token.
    access_token = create_access_token(data={"sub": user.username})

    logger.debug(f"Access token created for user {user.username}.")
    
    # 3. Return the token. FastAPI validates this dict against models.Token.
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

    return await UserService.get_and_decrypt_password(username, service_name,
                                                      password_request.master_password)

async def store_password(token: str, service_name: str, password_data: 'models.PasswordCreate'):
    """
    Encrypts and stores the password for a given service.
    """
    username = get_username_from_token(token)
    if not username:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )

    await UserService.store_and_encrypt_password(username, service_name, password_data)