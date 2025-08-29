from fastapi import HTTPException, status
from typing import Optional

from api import models

from .. import database, crypto
from ..crypto import CryptoError

from ..utils.logger import Logger
logger = Logger(__name__).get_logger()

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
        existing_user = await database.get_user(user.username)

        if existing_user:
            logger.warning(f"Attempt to register already existing username: {user.username}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already registered",
            )
        
        hashed_password = crypto.hash_key(user.password)
        
        db_user = models.UserInDB(username=user.username, hashed_password=hashed_password)
        await database.save_user(db_user)

        if not db_user:
            logger.error(f"Failed to create user {user.username}.")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create user",
            )
        
        logger.info(f"User {user.username} created successfully.")
        
        return db_user
    
    @staticmethod
    async def get_and_decrypt_password(username: str, service_name: str, master_password: str) -> 'models.PasswordData':
        """
        Retrieves and decrypts the password for a given service.
        """
        encrypted_data: Optional['models.EncryptedPasswordData'] = await database.get_encrypted_password(username, service_name)

        if not encrypted_data:
            logger.warning(f"Password for service '{service_name}' not found for user '{username}'.")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Password not found",
            )
        
        logger.debug(f"Retrieving encrypted data for user '{username}' and service '{service_name}'.")
        
        try:
            decrypted_username, decrypted_password = crypto.get_decrypted(encrypted_username=encrypted_data.encrypted_username,
                                                                      encrypted_password=encrypted_data.encrypted_password,
                                                                      master_key=master_password)
        except CryptoError as e:
            logger.error(f"Decryption error for user '{username}' and service '{service_name}': {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Decryption error"
            )

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
        
        logger.debug(f"Storing encrypted data for user '{username}' and service '{service_name}'.")

        await database.store_encrypted_password(
            username=username,
            service_name=service_name,
            encrypted_username=encrypted_data[0],
            encrypted_password=encrypted_data[1]
        )

    @staticmethod
    async def list_stored_passwords(username: str, master_password: str) -> list['models.PasswordMetadata']:
        """
        Lists all stored passwords for the user without revealing sensitive data.
        """
        records = await database.list_passwords(username)
        metadata_list = [
            models.PasswordMetadata(
                service_name=record['service_name'],
                username=record['encrypted_username'],
                updated_at=record['updated_at']
            ) for record in records
        ]
        for metadata in metadata_list:
            try:
                logger.debug(f"Found stored password for service '{metadata.service_name}' for user '{username}'.")
                metadata.username = crypto.get_single_decrypted(metadata.username, master_password)
            except CryptoError as e:
                logger.error(f"Decryption error for user '{username}' and service '{metadata.service_name}': {e}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Decryption error"
                )
            
        return metadata_list