from pydantic import BaseModel, Field
from typing import Optional

# ====================================================================
# Token Models
# ====================================================================

class Token(BaseModel):
    """
    Standard response model for the /token endpoint.
    This is what the client receives upon successful login.
    """
    access_token: str
    token_type: str

class TokenData(BaseModel):
    """
    Model for the data encoded within a JWT.
    This is used internally to validate the token's payload.
    """
    username: Optional[str] = None


# ====================================================================
# User Models
# ====================================================================

class UserBase(BaseModel):
    """
    Base model for a user. Contains shared properties.
    """
    username: str = Field(..., min_length=3, max_length=50, description="The user's unique username.")

class UserCreate(UserBase):
    """
    Model used for creating a new user during registration.
    It requires a plain-text password which will be hashed before storage.
    This model is used as the input for the /register endpoint.
    """
    password: str = Field(..., min_length=8, description="The user's master password (will be hashed).")

class User(UserBase):
    """
    Model for representing a user in API responses.
    It inherits the username and adds non-sensitive fields.
    Crucially, it does NOT include the password hash.
    """
    disabled: Optional[bool] = False

    class Config:
        # This allows the model to be created from ORM objects (like SQLAlchemy models)
        # or other objects with attributes, not just dicts.
        from_attributes = True

class UserInDB(User):
    """
    Model representing the full user object as stored in the database.
    It includes the hashed password, which should never be exposed in API responses.
    """
    hashed_password: str


# ====================================================================
# User Models
# ====================================================================

class PasswordData(BaseModel):
    """
    Model for representing a decrypted password.
    This is used in the response of the /passwords/{service_name} endpoint.
    """
    service_name: str = Field(..., description="The name of the service for which the password is stored.")
    username: str = Field(..., description="The decrypted username for the service.")
    password: str = Field(..., description="The decrypted password for the service.")