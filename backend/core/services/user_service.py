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
            decrypted_password = crypto.get_single_decrypted(encrypted_data.encrypted_password, master_password)
            decrypted_username = crypto.get_single_decrypted(encrypted_data.encrypted_username, master_password) if encrypted_data.encrypted_username else None
            decrypted_notes = crypto.get_single_decrypted(encrypted_data.encrypted_notes, master_password) if encrypted_data.encrypted_notes else None
        except CryptoError as e:
            logger.error(f"Decryption error for user '{username}' and service '{service_name}': {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Decryption error"
            )

        return models.PasswordData(
            service_name=service_name,
            username=decrypted_username,
            password=decrypted_password,
            notes=decrypted_notes,
            group_name=encrypted_data.group_name
        )
    
    @staticmethod
    async def store_and_encrypt_password(username: str, service_name: str, password_create: 'models.PasswordCreate', master_password: str):
        """
        Encrypts and stores the password for a given service.
        """
        encrypted_password = crypto.get_single_encrypted(password_create.password, master_password)
        encrypted_username = crypto.get_single_encrypted(password_create.username, master_password) if password_create.username else None
        encrypted_notes = crypto.get_single_encrypted(password_create.notes, master_password) if password_create.notes else None

        logger.debug(f"Storing encrypted data for user '{username}' and service '{service_name}'.")

        await database.store_encrypted_password(
            username=username,
            service_name=service_name,
            encrypted_username=encrypted_username,
            encrypted_password=encrypted_password,
            encrypted_notes=encrypted_notes,
            group_name=password_create.group_name.strip() if password_create.group_name else None
        )

    @staticmethod
    async def list_stored_passwords(username: str, master_password: str) -> list['models.PasswordMetadata']:
        """
        Lists all stored passwords for the user without revealing sensitive data.
        """
        records = await database.list_passwords(username)
        metadata_list = []
        for record in records:
            logger.debug(f"Found stored password for service '{record['service_name']}' for user '{username}'.")
            decrypted_username = None
            if record['encrypted_username']:
                try:
                    decrypted_username = crypto.get_single_decrypted(record['encrypted_username'], master_password)
                except CryptoError as e:
                    logger.error(f"Decryption error for user '{username}' and service '{record['service_name']}': {e}")
                    raise HTTPException(
                        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        detail="Decryption error"
                    )
            metadata_list.append(models.PasswordMetadata(
                service_name=record['service_name'],
                username=decrypted_username or "",
                updated_at=record['updated_at'],
                group_name=record['group_name']
            ))
        return metadata_list
