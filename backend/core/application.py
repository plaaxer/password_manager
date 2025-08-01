# backend/core/application.py

import os
from datetime import datetime, timedelta, timezone
from typing import Optional

from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status

from backend.core.services.token_service import TokenService
from backend.core.services.authentication_service import AuthenticationService
from backend.core.services.user_service import UserService
from backend.core import database, models

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

# --- TOKENS ---

def get_username_from_token(token: str) -> Optional[str]:
    return TokenService.get_username_from_token(token)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    return TokenService.create_access_token(data, expires_delta)

# --- AUTHENTICATION ---

async def authenticate_user(username: str, password: str) -> models.UserInDB:
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