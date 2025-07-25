from fastapi import HTTPException, status

from backend.core import models, database, crypto

class UserService:

    @staticmethod
    async def create_user(user: 'models.UserCreate'):
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
        
        # not yes stateless; TODO
        hashed_password = crypto.Crypto.hash(user.master_password)
        
        db_user = models.UserCreate(username=user.username, hashed_master_password=hashed_password)
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
        This function will:
        1. Fetch the encrypted password from the database.
        2. Generate a Fernet key using the master password.
        3. Decrypt the password.
        """
        encrypted_data = await database.get_encrypted_password(username, service_name)

        if not encrypted_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Password not found",
            )
        
        fernet = crypto.Crypto.generate_fernet(master_password, encrypted_data.salt)
        
        decrypted_username = crypto.Crypto.decrypt_data(encrypted_data.encrypted_username, fernet).decode()
        decrypted_password = crypto.Crypto.decrypt_data(encrypted_data.encrypted_password, fernet).decode()

        return models.PasswordData(
            service_name=service_name,
            username=decrypted_username,
            password=decrypted_password
        )