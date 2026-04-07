import os
import argon2
import base64
import sys

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

import core.utils.aux as aux

from core.utils.logger import Logger
logger = Logger(__name__).get_logger()

class CryptoError(Exception):
    
    """Custom exception for encryption errors."""
    INCORRECT_SALT = "The provided salt is of incorrect length."
    DECRYPTION_FAILED = "Decryption failed. Possible incorrect master key or corrupted data."
    ENCRYPTION_FAILED = "Encryption failed due to an unexpected error."
    FAILED_SALT_MANIPULATION= "Failed to extract and remove salt from encrypted data."
    
    def __init__(self, message: str):
        super().__init__(message)
        self.message = message

def hash_key(master_key: str) -> str:
    """Hashes the key utilizing argon2. Renamed from 'hash' to avoid conflict with built-in."""
    return argon2.PasswordHasher().hash(master_key)

def verify_key(master_key: str, key_hash: str) -> bool:
    """
    Checks if the provided master key matches the hash.
    The 'hash' parameter was renamed to 'key_hash' to avoid conflict with the built-in hash() function.
    """
    try:
        argon2.PasswordHasher().verify(key_hash, master_key)
        return True
    except argon2.exceptions.VerifyMismatchError:
        return False

def generate_fernet(master_key: str, salt=os.urandom(aux.get_salt_length())) -> Fernet:
    """
    Generates a Fernet object for encryption/decryption.

    This function derives a key from the master key and a salt using PBKDF2HMAC,
    then uses this key to create a Fernet symmetric encryption object.
    """
    kdf = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=salt, iterations = 480000) # key derivation function
    key = base64.urlsafe_b64encode(kdf.derive(master_key.encode())) # key (256 bits) derived from master key
    return Fernet(key) # key is used to generate a Fernet object

def _encrypt_data(data: bytes, fernet: Fernet) -> bytes:
    """Encrypts the given data using the generated Fernet object."""
    return fernet.encrypt(data) # encrypts using the fernet object

def _decrypt_data(data: bytes, fernet: Fernet) -> bytes:
    """Decrypts the given data using the generated Fernet object."""
    return fernet.decrypt(data) # decrypts using the fernet object

def encrypt_with_salt(username: str, password: str, fernet: Fernet, salt: bytes) -> tuple:
    """
    Encrypts username and password, appends the salt to each,
    and returns them as base64 encoded strings.
    """
    encrypted_username = _encrypt_data(username.encode(), fernet)
    encrypted_password = _encrypt_data(password.encode(), fernet)

    encoded_salt = base64.b64encode(salt)

    data_username = base64.b64encode(encrypted_username + encoded_salt).decode()
    data_password = base64.b64encode(encrypted_password + encoded_salt).decode()

    return data_username, data_password

def get_encrypted(username: str, password: str, master_key: str) -> tuple:
    """
    Generates a Fernet key using the master key and a new salt,
    then encrypts the username and password.
    Returns the encrypted username and password as base64 encoded strings.
    """
    salt = os.urandom(aux.get_salt_length())
    fernet = generate_fernet(master_key, salt)
    return encrypt_with_salt(username, password, fernet, salt)

def get_decrypted(encrypted_username: str, encrypted_password: str, master_key: str) -> tuple:
    """
    Extracts salt from encrypted data, regenerates the Fernet key,
    and decrypts the username and password.
    """
    encrypted_username_bytes = base64.b64decode(encrypted_username.encode())
    encrypted_password_bytes = base64.b64decode(encrypted_password.encode())

    try:
        decoded_salt = extract_salt(encrypted_username_bytes)
        encrypted_username_bytes = clear_salt(encrypted_username_bytes)
        encrypted_password_bytes = clear_salt(encrypted_password_bytes)

    except Exception as e:
        if not isinstance(e, CryptoError):
            logger.error(f"Error manipulating salt: {e}")
            raise CryptoError(CryptoError.FAILED_SALT_MANIPULATION) from e
        else:
            raise

    fernet = generate_fernet(master_key, decoded_salt)

    try:
        decrypted_username_bytes = _decrypt_data(encrypted_username_bytes, fernet)
        decrypted_password_bytes = _decrypt_data(encrypted_password_bytes, fernet)
        
    except Exception as e:
        logger.error(f"Decryption failed: {e}")
        raise CryptoError(CryptoError.DECRYPTION_FAILED) from e

    return decrypted_username_bytes.decode(), decrypted_password_bytes.decode()

def get_single_encrypted(data: str, master_key: str) -> str:
    """
    Encrypts a single string value with a fresh salt and returns it as a base64 encoded string.
    """
    salt = os.urandom(aux.get_salt_length())
    fernet = generate_fernet(master_key, salt)
    encrypted = _encrypt_data(data.encode(), fernet)
    encoded_salt = base64.b64encode(salt)
    return base64.b64encode(encrypted + encoded_salt).decode()

def get_single_decrypted(encrypted_data: str, master_key: str) -> str:
    """
    Extracts salt from encrypted data, regenerates the Fernet key,
    and decrypts the data.
    """
    encrypted_data_bytes = base64.b64decode(encrypted_data.encode())

    try:
        decoded_salt = extract_salt(encrypted_data_bytes)
        encrypted_data_bytes = clear_salt(encrypted_data_bytes)
    except Exception as e:
        if not isinstance(e, CryptoError):
            logger.error(f"Error manipulating salt: {e}")
            raise CryptoError(CryptoError.FAILED_SALT_MANIPULATION) from e
        else:
            raise

    fernet = generate_fernet(master_key, decoded_salt)

    try:
        decrypted_data_bytes = _decrypt_data(encrypted_data_bytes, fernet)
    except Exception as e:
        logger.error(f"Decryption failed: {e}")
        raise CryptoError(CryptoError.DECRYPTION_FAILED) from e

    return decrypted_data_bytes.decode()

def extract_salt(encrypted_data: bytes) -> str:
    """
    Extracts and returns the base64 encoded salt from the encrypted data.
    """

    salt_length = aux.get_salt_length() + (aux.get_salt_length())//2 # 150% of its original size due to base64 encoding
    salt = encrypted_data[-salt_length:]  # extract salt from the end

    try:
        decoded_salt = base64.b64decode(salt) # decode the salt. will not work if the salt is not the correct length

    except Exception as e:
        logger.error(f"Error decoding salt: {e}")
        raise CryptoError(CryptoError.INCORRECT_SALT) from e
    
    return decoded_salt

def clear_salt(encrypted_data: bytes) -> bytes:
    """
    Removes the salt from the end of the encrypted data.
    """
    salt_length = aux.get_salt_length() + (aux.get_salt_length())//2 # 150% of its original size due to base64 encoding
    cleaned_data = encrypted_data[:-salt_length]  # remove salt from the encrypted data
    return cleaned_data