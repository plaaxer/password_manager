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

def authenticate_user(username: str, password: str) -> Optional[str]:
    return AuthenticationService.authenticate_user(username, password)

# -- USER MANAGEMENT ---
def create_user(user: models.UserCreate) -> Optional[models.User]:
    return UserService.create_user(user)

