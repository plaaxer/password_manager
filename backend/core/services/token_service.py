
#backend/core/token_service.py

import os
from datetime import datetime, timedelta, timezone
from typing import Optional

from jose import JWTError, jwt # type: ignore
from fastapi import Depends, HTTPException, status

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))

class TokenService:

    @staticmethod
    def get_username_from_token(token: str) -> Optional[str]:
        """
        Decodes the JWT token to extract the username (subject).
        Raises HTTPException if the token is invalid.
        """
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
        if not SECRET_KEY:
            raise ValueError("SECRET_KEY environment variable not set")

        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            username: str = payload.get("sub")
            if username is None:
                raise credentials_exception
        except JWTError:
            raise credentials_exception
        
        return username

    @staticmethod
    def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
            """
            Creates a new JWT access token.
            """
            to_encode = data.copy()
            if expires_delta:
                expire = datetime.now(timezone.utc) + expires_delta
            else:
                expire = datetime.now(timezone.utc) + timedelta(minutes=15)
            to_encode.update({"exp": expire})
            
            # Ensure SECRET_KEY is loaded
            if not SECRET_KEY:
                raise ValueError("SECRET_KEY environment variable not set")

            encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
            return encoded_jwt