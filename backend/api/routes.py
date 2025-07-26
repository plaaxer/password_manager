from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from datetime import timedelta

# Import all necessary components from the core package
from ..core import application
import models

router = APIRouter()

# --- Authentication Logic ---

# This dependency will check for a valid JWT in the Authorization header.
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


# --- API Endpoints ---

@router.post("/token", response_model=models.Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    Handles the initial login. The user posts their username
    and password (the master password).
    
    If authentication is successful, it returns a JWT.
    """
    # 1. Authenticate the user. The service layer handles exceptions.
    user = await application.authenticate_user(form_data.username, form_data.password)

    # 2. If valid, create a JWT access token.
    access_token_expires = timedelta(minutes=application.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = application.create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    
    # 3. Return the token. FastAPI validates this dict against models.Token.
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/register")
async def register_user(registration_data: models.UserCreate):
    """
    Endpoint to register a new user.
    """
    # The service layer handles the logic of checking for existing users,
    # hashing the password, and storing the new user.
    new_user = await application.create_user(user=registration_data)

    return {"message": f"User {new_user.username} registered successfully."}


@router.get("/passwords/{service_name}", response_model=models.PasswordData)
async def get_password(
    service_name: str, 
    request_data: models.PasswordRequest, # Use the model from models.py
    token: str = Depends(oauth2_scheme)
):
    """
    A protected endpoint to retrieve a decrypted password.
    """
    username = application.get_username_from_token(token)
    if username is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        )

    # The service function does the heavy lifting: fetches, decrypts, and returns data.
    decrypted_data = await application.get_password(
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
