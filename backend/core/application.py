# backend/core/application.py

import os
from datetime import datetime, timedelta, timezone
from typing import Optional

from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status

from token_service import TokenService

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

# --- TOKENS ---

def get_username_from_token(token: str) -> Optional[str]:
    return TokenService.get_username_from_token(token)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    return TokenService.create_access_token(data, expires_delta)

# --- AUTHENTICATION ---

def authenticate_user(username: str, password: str) -> Optional[str]:
    """
    Authenticate a user by checking the username and password.
    Returns the username if authentication is successful, otherwise None.
    """
    
