from fastapi import HTTPException, status

from backend.core.services.token_service import TokenService
from backend.core.crypto import Crypto
from backend.core import database

class AuthenticationService:

    @staticmethod
    async def authenticate_user(username: str, password: str):
        """
        Authenticate a user by checking the username and password.
        Returns the username if authentication is successful, otherwise None.
        """
        user = await database.get_user(username)
        if not user or not AuthenticationService.verify_password(password, user['password']):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials (user or password)",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return user
    
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        return Crypto.verify_key(plain_password, hashed_password)