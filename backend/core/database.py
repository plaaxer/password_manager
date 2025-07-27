# backend/core/database.py

import os
import asyncpg
from typing import Optional, Tuple

from . import models

# --- Connection Pool Management ---
# The pool will be created when the application starts and managed globally.
pool: Optional[asyncpg.Pool] = None

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
    print("Database connection pool created successfully.")

async def close_db_connection():
    """Closes the database connection pool. Called on application shutdown."""
    global pool
    if pool:
        await pool.close()
        print("Database connection pool closed.")

# --- Database Functions (Replaces Communicator methods) ---
# Each function is async and takes a connection from the pool.

# TODO: user should return a User object, not a dict

async def get_user(username: str) -> Optional[dict]:
    """
    Fetches a user by their username.
    This function corresponds to your old get_master_key_hash.
    
    NOTE: In a real app, you'd have a proper users table instead of.
    This is adapted from your original structure.
    """
    # Use 'async with' to get a connection from the pool
    async with pool.acquire() as connection:
        # Use parameterized queries ($1, $2) to prevent SQL injection
        query = "SELECT username, hashed_master_password FROM users WHERE username = $1"
        user_record = await connection.fetchrow(query, username)
        return dict(user_record) if user_record else None

async def save_user(db_user: 'models.UserInDB'):
    """Saves a new user to the database."""
    async with pool.acquire() as connection:
        query = "INSERT INTO users (username, hashed_master_password) VALUES ($1, $2)"
        await connection.execute(query, db_user.username, db_user.hashed_password)

async def get_encrypted_password(username: str, service_name: str) -> Optional['models.EncryptedPasswordData']:
    """
    Retrieves the encrypted username and password for a given service.
    This replaces your old retrieve_password method.
    """
    # IMPORTANT: The schema-per-user model is very difficult to manage and secure.
    # A better model is to have a single 'passwords' table with a 'user_id' column.
    # This implementation follows that better practice.
    async with pool.acquire() as connection:
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
    
async def store_encrypted_password(
    username: str, service_name: str, encrypted_username: str, encrypted_password: str
):
    """
    Saves an encrypted password for a given service.
    This replaces your old save_password method.
    """
    async with pool.acquire() as connection:
        query = """
            INSERT INTO passwords (user_id, service_name, encrypted_username, encrypted_password)
            VALUES (
                (SELECT id FROM users WHERE username = $1),
                $2, $3, $4
            )
        """
        await connection.execute(query, username, service_name, encrypted_username, encrypted_password)