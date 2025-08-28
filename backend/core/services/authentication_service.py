from fastapi import HTTPException, status
from typing import Optional

from .. import crypto
from .. import database
from api import models

from ..utils.logger import Logger
logger = Logger(__name__).get_logger()

class AuthenticationService:

    @staticmethod
    async def authenticate_user(username: str, password: str) -> 'models.UserInDB':
        """
        Authenticate a user by checking the username and password.
        Returns the username if authentication is successful, otherwise None.
        """
        user = await database.get_user(username)
        if not user or not AuthenticationService.verify_password(password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials (user or password)",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return user
    
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        correct_password = crypto.verify_key(plain_password, hashed_password)
        if not correct_password:
            logger.debug(f"Password verification failed.")
        return correct_password