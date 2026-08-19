from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

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
# Password Models
# ====================================================================

class PasswordData(BaseModel):
    """
    Model for representing a decrypted password.
    This is used in the response of the /passwords/{service_name} endpoint.
    """
    service_name: str = Field(..., description="The name of the service for which the password is stored.")
    username: Optional[str] = Field(None, description="The decrypted username for the service.")
    password: str = Field(..., description="The decrypted password for the service.")
    notes: Optional[str] = Field(None, description="Optional notes for the service.")
    group_name: Optional[str] = Field(None, max_length=50, description="Optional group used to organize the entry.")

class PasswordCreate(BaseModel):
    """
    Model for creating a new password entry.
    Master password is provided via the X-Master-Password header, not this body.
    """
    service_name: str = Field(..., description="The name of the service for which the password is being stored.")
    username: Optional[str] = Field(None, description="The username for the service.")
    password: str = Field(..., description="The password for the service. This will be encrypted before storage.")
    notes: Optional[str] = Field(None, description="Optional notes for the service.")
    group_name: Optional[str] = Field(None, max_length=50, description="Optional group used to organize the entry.")

class EncryptedPasswordData(BaseModel):
    """
    Model for representing a password that is yet encrypted.
    """
    service_name: str = Field(..., description="The name of the service for which the password is stored.")
    encrypted_username: Optional[str] = Field(None, description="The encrypted username for the service.")
    encrypted_password: str = Field(..., description="The encrypted password for the service.")
    encrypted_notes: Optional[str] = Field(None, description="The encrypted notes for the service.")
    group_name: Optional[str] = Field(None, description="Optional group used to organize the entry.")

class PasswordRequest(BaseModel):
    """
    Model for the request body when fetching passwords.
    This is used to securely transport the master password needed for decryption.
    """
    master_password: str = Field(..., description="The user's master password, required for on-the-fly decryption.")

class PasswordMetadata(BaseModel):
    """
    Model for listing stored passwords without revealing sensitive data.
    This is used in the response of the /passwords endpoint.
    """
    service_name: str = Field(..., description="The name of the service for which the password is stored.")
    username: str = Field(..., description="The encrypted username for the service.")
    updated_at: datetime = Field(..., description="The timestamp when the password was last updated.")
    group_name: Optional[str] = Field(None, description="Optional group used to organize the entry.")
