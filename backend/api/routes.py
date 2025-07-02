
# backend/api/routes.py
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from datetime import timedelta

from ..core import services, crypto, models

router = APIRouter()

# --- Pydantic Models for Request/Response ---

class PasswordRequest(BaseModel):
    master_password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class PasswordData(BaseModel):
    service: str
    username: str
    password: str


# --- Authentication Logic ---

# This dependency will check for a valid JWT in the Authorization header
# It doesn't know what to DO with the token yet, just that it's there.
# We'll build on this to create a real "get_current_user" dependency.
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


# --- API Endpoints ---

@router.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    Handles the initial login. The user posts their username (the stash name)
    and password (the master password).
    
    FastAPI's OAuth2PasswordRequestForm makes the client send it as form data,
    which is standard for token endpoints.
    
    If authentication is successful, it returns a JWT.
    """
    # 1. Authenticate the user against the database/verification hash
    #    The 'authenticate_user' service will return the user/stash object if valid, or False.
    user = await services.authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 2. If valid, create a JWT access token
    access_token_expires = timedelta(minutes=services.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = services.create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    
    # 3. Return the token
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/register")
async def register_stash(registration_data: models.UserCreate):
    """
    Endpoint to register a new user/stash.
    This will call a service function that:
    1. Checks if the user already exists.
    2. Creates the verification hash from the master password.
    3. Stores the new user and verification hash in the database.
    """
    # You would expand this UserCreate model in models.py
    # It would contain username and master_password
    new_user = await services.create_user(user=registration_data)
    if not new_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered",
        )
    return {"message": f"User {new_user.username} registered successfully."}


@router.get("/passwords/{service_name}", response_model=PasswordData)
async def get_password(
    service_name: str, 
    request_data: PasswordRequest,
    token: str = Depends(oauth2_scheme) # This ensures the user has a valid JWT
):
    """
    A protected endpoint to retrieve a decrypted password.
    
    The client MUST provide:
    1. A valid JWT in the 'Authorization: Bearer <token>' header.
    2. The master_password in the JSON request body.
    """
    # The 'Depends(oauth2_scheme)' already validated the token's format and presence.
    # A more advanced version would decode the token here to get the username.
    # For now, we'll assume the token is valid and proceed.
    
    # Let's decode the token to get the username (stash_name)
    # This is the proper way to link the token to the user
    username = services.get_username_from_token(token)
    if username is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        )

    # Call the service function to do the heavy lifting.
    # This function will contain the logic you described:
    # - Fetch encrypted data from DB for the given user and service.
    # - Use the provided master_password to derive the key and decrypt.
    # - Return the decrypted data.
    decrypted_data = await services.get_and_decrypt_password(
        username=username,
        service_name=service_name,
        master_password=request_data.master_password
    )

    if not decrypted_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Service '{service_name}' not found for user '{username}'."
        )

    return decrypted_data
