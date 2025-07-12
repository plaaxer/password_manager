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