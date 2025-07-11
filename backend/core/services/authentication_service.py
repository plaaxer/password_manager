from fastapi import HTTPException, status

from backend.core.services.token_service import TokenService
from backend.core.crypto import Crypto

class AuthenticationService:
    def __init__(self, token_service: 'TokenService'):
        self.token_service = token_service

    async def authenticate_user(self, username: str, password: str):
        user = await self.get_user_by_username(username)
        if not user or not self.verify_password(password, user['password']):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return user

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return Crypto.verify_key(plain_password, hashed_password)