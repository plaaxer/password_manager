from fastapi import HTTPException, status
from typing import Optional

from .. import database, crypto, models

class UserService:

    @staticmethod
    async def create_user(user: 'models.UserCreate') -> 'models.UserInDB':
        """
        Creates a new user in the database.
        This function will:
        1. Check if the user already exists.
        2. Hash the master password.
        3. Save the user to the database.
        """
        # Check if user already exists
        existing_user = await database.get_user(user.username)

        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already registered",
            )
        
        hashed_password = crypto.hash_key(user.password)
        
        db_user = models.UserInDB(username=user.username, hashed_password=hashed_password)
        await database.save_user(db_user)

        if not db_user:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create user",
            )
        
        return db_user
    
    @staticmethod
    async def get_and_decrypt_password(username: str, service_name: str, master_password: str) -> 'models.PasswordData':
        """
        Retrieves and decrypts the password for a given service.
        """
        encrypted_data: Optional['models.EncryptedPasswordData'] = await database.get_encrypted_password(username, service_name)

        if not encrypted_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Password not found",
            )
        
        decrypted_username, decrypted_password = crypto.get_decrypted(encrypted_username=encrypted_data.encrypted_username,
                                                                      encrypted_password=encrypted_data.encrypted_password,
                                                                      master_key=master_password)

        return models.PasswordData(
            service_name=service_name,
            username=decrypted_username,
            password=decrypted_password
        )
    
    @staticmethod
    async def store_and_encrypt_password(username: str, service_name: str, password_create: 'models.PasswordCreate'):
        """
        Encrypts and stores the password for a given service.
        """
        encrypted_data = crypto.get_encrypted(
            username=password_create.username,
            password=password_create.password,
            master_key=password_create.master_password
        )
        await database.store_encrypted_password(
            username=username,
            service_name=service_name,
            encrypted_username=encrypted_data[0],
            encrypted_password=encrypted_data[1]
        )