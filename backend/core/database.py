# backend/core/database.py

import os
import asyncpg
import functools
from typing import Callable, Coroutine, TypeVar, ParamSpec, Optional, Any, Concatenate

from api import models

P = ParamSpec('P')
R = TypeVar('R')

# --- Connection Pool Management ---

pool: Optional[asyncpg.Pool] = None

# manually defining types for pylance compatibility
def with_connection(func: Callable[Concatenate[asyncpg.Connection, P], Coroutine[Any, Any, R]]) -> Callable[P, Coroutine[Any, Any, R]]:
    """
    Decorator that provides a database connection to a function.
    """
    @functools.wraps(func)
    async def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        if pool is None:
            raise RuntimeError("Database connection pool is not initialized.")
        
        async with pool.acquire() as connection:
            return await func(connection, *args, **kwargs)
    return wrapper

async def connect_to_db():
    """Creates the database connection pool. Called on application startup."""
    global pool
    db_user = os.getenv("POSTGRES_USER")
    db_password = os.getenv("POSTGRES_PASSWORD")
    db_host = os.getenv("POSTGRES_HOST", "db")
    db_name = os.getenv("POSTGRES_DB")
    
    if not all([db_user, db_password, db_host, db_name]):
        raise ValueError("Database environment variables are not fully set.")

    pool = await asyncpg.create_pool(
        user=db_user,
        password=db_password,
        host=db_host,
        database=db_name
    )

async def close_db_connection():
    """Closes the database connection pool. Called on application shutdown."""
    global pool
    if pool:
        await pool.close()

# --- Database Functions ---

@with_connection
async def get_user(connection: asyncpg.Connection, username: str) -> Optional['models.UserInDB']:
    """
    Fetches a user by their username.
    This function corresponds to your old get_master_key_hash.
    """
    query = "SELECT username, hashed_master_password FROM users WHERE username = $1"
    user_record = await connection.fetchrow(query, username)
    if user_record:
        return models.UserInDB(
            username=user_record['username'],
            hashed_password=user_record['hashed_master_password']
        )

@with_connection
async def save_user(connection: asyncpg.Connection, db_user: 'models.UserInDB'):
    """Saves a new user to the database."""
    query = "INSERT INTO users (username, hashed_master_password) VALUES ($1, $2)"
    await connection.execute(query, db_user.username, db_user.hashed_password)

@with_connection
async def get_encrypted_password(connection: asyncpg.Connection, username: str, service_name: str) -> Optional['models.EncryptedPasswordData']:
    """
    Retrieves the encrypted username and password for a given service.
    This replaces your old retrieve_password method.
    """
    query = """
        SELECT p.encrypted_username, p.encrypted_password
        FROM passwords p
        JOIN users u ON p.user_id = u.id
        WHERE u.username = $1 AND p.service_name = $2
    """
    record = await connection.fetchrow(query, username, service_name)
    if record:
        return models.EncryptedPasswordData(
            service_name=service_name,
            encrypted_username=record['encrypted_username'],
            encrypted_password=record['encrypted_password']
        )
    return None

@with_connection
async def store_encrypted_password(
    connection: asyncpg.Connection,
    username: str, 
    service_name: str, 
    encrypted_username: str, 
    encrypted_password: str
):
    """
    Saves or updates an encrypted password for a given service (upsert).
    """
    query = """
        INSERT INTO passwords (user_id, service_name, encrypted_username, encrypted_password)
        VALUES (
            (SELECT id FROM users WHERE username = $1),
            $2, $3, $4
        )
        ON CONFLICT (user_id, service_name) 
        DO UPDATE SET
            encrypted_username = EXCLUDED.encrypted_username,
            encrypted_password = EXCLUDED.encrypted_password,
            updated_at = CURRENT_TIMESTAMP;
    """
    await connection.execute(
        query, 
        username, 
        service_name, 
        encrypted_username, 
        encrypted_password
    )

@with_connection
async def delete_encrypted_password(connection: asyncpg.Connection, username: str, service_name: str):
    """
    Deletes an encrypted password entry for a given service.
    """
    query = """
        DELETE FROM passwords
        WHERE user_id = (SELECT id FROM users WHERE username = $1)
        AND service_name = $2
    """
    await connection.execute(query, username, service_name)
    
@with_connection
async def list_passwords(connection: asyncpg.Connection, username: str) -> list[dict]:
    """
    Retrieves metadata for all passwords belonging to a user.
    """
    query = """
        SELECT p.service_name, p.encrypted_username, p.updated_at
        FROM passwords p
        JOIN users u ON p.user_id = u.id
        WHERE u.username = $1
    """
    return await connection.fetch(query, username)

