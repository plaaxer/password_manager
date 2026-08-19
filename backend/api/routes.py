from fastapi import APIRouter, Depends, Header
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from datetime import timedelta

import core.application as application
import api.models as models

router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

from core.utils.logger import Logger
logger = Logger(__name__).get_logger()

@router.post("/login", response_model=models.Token)
async def login_token(form_data: OAuth2PasswordRequestForm = Depends()):

    """ Endpoint to log in and receive a JWT token.
    The user posts their username and password (the master password).
    If authentication is successful, it returns a JWT."""

    return await application.login(form_data=form_data)


@router.post("/register")
async def register_user(registration_data: models.UserCreate):

    """
    Endpoint to register a new user.
    """
    new_user = await application.create_user(user=registration_data)

    return {"message": f"User {new_user.username} registered successfully."}


@router.get("/passwords/{service_name}", response_model=models.PasswordData)
async def get_password(
    service_name: str, 
    x_master_password: str = Header(...),
    token: str = Depends(oauth2_scheme)
):
    """
    A protected endpoint to retrieve a decrypted password.
    """
    request_data = models.PasswordRequest(master_password=x_master_password)
    return await application.get_password(
        service_name=service_name,
        token=token,
        password_request=request_data
    )

@router.post("/passwords")
async def store_password(
    password_data: models.PasswordCreate,
    x_master_password: str = Header(...),
    token: str = Depends(oauth2_scheme)):

    """
    A protected endpoint to store an encrypted password.
    """

    await application.store_password(token=token, service_name=password_data.service_name, password_data=password_data, master_password=x_master_password)

    return {"message": f"Password for {password_data.service_name} stored successfully."}

@router.put("/passwords/{service_name}")
async def update_password(
    service_name: str,
    password_data: models.PasswordCreate,
    x_master_password: str = Header(...),
    token: str = Depends(oauth2_scheme)):

    """
    A protected endpoint to update an existing encrypted password.
    """

    await application.store_password(token=token, service_name=service_name, password_data=password_data, master_password=x_master_password)

    return {"message": f"Password for {service_name} updated successfully."}

@router.delete("/passwords/{service_name}")
async def delete_password(
    service_name: str,
    x_master_password: str = Header(...),
    token: str = Depends(oauth2_scheme)):

    """
    A protected endpoint to delete an existing password.
    """

    await application.delete_password(
        token=token,
        service_name=service_name,
        master_password=x_master_password
    )

    return {"message": f"Password for {service_name} deleted successfully."}

@router.get("/passwords", response_model=list[models.PasswordMetadata])
async def list_passwords(
    x_master_password: str = Header(...),
    token: str = Depends(oauth2_scheme)
):
    """
    A protected endpoint to list all stored passwords' metadata.
    """
    password_data = models.PasswordRequest(master_password=x_master_password)
    return await application.list_passwords(password_request=password_data, token=token)
