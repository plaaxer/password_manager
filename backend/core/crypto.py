import os
import argon2
import base64
import sys

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

import aux

class Crypto:

    @staticmethod
    def hash(master_key: str) -> str:
        """Hashes the key utilizing argon2"""
        return argon2.PasswordHasher().hash(master_key)

    @staticmethod
    def verify_key(master_key: str, hash: str) -> bool:
        """Checks if the provided master key matches the hash"""
        try:
            argon2.PasswordHasher().verify(hash, master_key)
            return True
        except argon2.exceptions.VerifyMismatchError:
            return False
    
    @staticmethod
    def generate_fernet(master_key: str, salt=os.urandom(aux.get_salt_length())) -> Fernet:
        """
        Generates a Fernet object for encryption/decryption.

        This method derives a key from the master key and a salt using PBKDF2HMAC,
        then uses this key to create a Fernet symmetric encryption object.
        """
        kdf = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=salt, iterations = 480000) # key derivation function
        key = base64.urlsafe_b64encode(kdf.derive(master_key.encode())) # key (256 bits) derived from master key
        return Fernet(key) # key is used to generate a Fernet object

    @staticmethod
    def encrypt_data(data: bytes, fernet: Fernet) -> bytes:
        """Encrypts the given data using the generated Fernet object."""
        return fernet.encrypt(data) # encrypts using the fernet object

    @staticmethod
    def decrypt_data(data: bytes, fernet: Fernet) -> bytes:
        """Decrypts the given data using the generated Fernet object."""
        return fernet.decrypt(data) # decrypts using the fernet object
    
    @staticmethod
    def encrypt_with_salt(username: str, password: str, fernet: Fernet, salt: bytes) -> tuple:
        """
        Encrypts username and password, appends the salt to each,
        and returns them as base64 encoded strings.
        """
        encrypted_username = Crypto.encrypt_data(username.encode(), fernet)
        encrypted_password = Crypto.encrypt_data(password.encode(), fernet)
        print(f"Encrypted username: {encrypted_username}\nEncrypted password: {encrypted_password}")

        encoded_salt = base64.b64encode(salt)

        data_username = base64.b64encode(encrypted_username + encoded_salt).decode()
        data_password = base64.b64encode(encrypted_password + encoded_salt).decode()

        return data_username, data_password
    
    @staticmethod
    def get_encrypted(username: str, password: str, master_key: str) -> tuple:
        """
        Generates a Fernet key using the master key and a new salt,
        then encrypts the username and password.
        Returns the encrypted username and password as base64 encoded strings.
        """
        salt = os.urandom(aux.get_salt_length())
        fernet = Crypto.generate_fernet(master_key, salt)
        return Crypto.encrypt_with_salt(username, password, fernet, salt)

    @staticmethod
    def get_decrypted(encrypted_username: str, encrypted_password: str, master_key: str) -> tuple:
        """
        Extracts salt from encrypted data, regenerates the Fernet key,
        and decrypts the username and password.
        """
        encrypted_username_bytes = base64.b64decode(encrypted_username.encode())
        encrypted_password_bytes = base64.b64decode(encrypted_password.encode())

        salt_length = aux.get_salt_length() + (aux.get_salt_length())//2 # 150% of original size due to base64 encoding
        salt = encrypted_username_bytes[-salt_length:]  # extract salt from the end
        encrypted_username_bytes = encrypted_username_bytes[:-salt_length]  # remove salt from the encrypted data

        try:
            decoded_salt = base64.b64decode(salt)  # decode the salt. will not work if the salt is not the correct length
        except Exception as e:
            print(f"Error decoding salt: {e}")
            print("ATTENTION: Salt length might be incorrect. Have you changed it in config.yaml?")
            sys.exit(1)

        fernet = Crypto.generate_fernet(master_key, decoded_salt)

        decrypted_username_bytes = Crypto.decrypt_data(encrypted_username_bytes, fernet)
        decrypted_password_bytes = Crypto.decrypt_data(encrypted_password_bytes, fernet)

        return decrypted_username_bytes.decode(), decrypted_password_bytes.decode()