import os
import argon2
import base64
import sys

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

import aux

# TODO: make this stateless

class Crypto:
    def __init__(self):
        self.ph = argon2.PasswordHasher()
        self.f = None

    def hash(self, master_key: str) -> str:
        """Hashes the key utilizing argon2"""
        return self.ph.hash(master_key)

    def verify_key(self, master_key: str, hash: str) -> bool:
        """Checks if the provided master key matches the hash"""
        try:
            self.ph.verify(hash, master_key)
            return True
        except argon2.exceptions.VerifyMismatchError:
            return False
    
    def generate_fernet(self, master_key: str, salt=os.urandom(aux.get_salt_length())) -> Fernet:
        """
        Generates a Fernet object for encryption/decryption.

        This method derives a key from the master key and a salt using PBKDF2HMAC,
        then uses this key to create a Fernet symmetric encryption object.
        """
        self.salt = salt

        kdf = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=self.salt, iterations = 480000) # key derivation function

        key = base64.urlsafe_b64encode(kdf.derive(master_key.encode())) # key (256 bits) derived from master key

        self.f = Fernet(key) # key is used to generate a Fernet object
    
    def delete_fernet(self) -> None:
        """Deletes the Fernet object from memory to prevent leaks."""
        # delete the fernet object to prevent memory leaks and later access
        if self.f:
            del self.f

    def encrypt_data(self, data: bytes) -> bytes:
        """Encrypts the given data using the generated Fernet object."""
        return self.f.encrypt(data) # encrypts using the fernet object

    def decrypt_data(self, data: bytes) -> bytes:
        """Decrypts the given data using the generated Fernet object."""
        return self.f.decrypt(data) # decrypts using the fernet object
    
    def get_salt(self) -> bytes:
        """Returns the salt used for key derivation."""
        return self.salt
    
    def add_salt_encryption(self, username: str, password: str) -> tuple:
        """
        Encrypts username and password, appends the salt to each,
        and returns them as base64 encoded strings.
        """
        username = username.encode()
        password = password.encode()

        encrypted_username = self.encrypt_data(username)
        encrypted_password = self.encrypt_data(password)
        print(f"Encrypted username: {encrypted_username}\nEncrypted password: {encrypted_password}")

        salt = self.get_salt()
        encoded_salt = base64.b64encode(salt)

        data_username = base64.b64encode(encrypted_username + encoded_salt).decode()
        data_password = base64.b64encode(encrypted_password + encoded_salt).decode()

        return data_username, data_password

    def remove_salt_encryption(self, encrypted_username: str, encrypted_password: str, master_key: str) -> tuple:
        """
        Extracts salt from encrypted data, regenerates the Fernet key,
        and decrypts the username and password.
        """
        encrypted_username = encrypted_username.encode()
        encrypted_password = encrypted_password.encode()

        encrypted_username_bytes = base64.b64decode(encrypted_username)
        encrypted_password_bytes = base64.b64decode(encrypted_password)

        salt_length = aux.get_salt_length() + (aux.get_salt_length())//2 # 150% of original size due to base64 encoding
        salt = encrypted_username_bytes[-salt_length:]  # extract salt from the end
        encrypted_username_bytes = encrypted_username_bytes[:-salt_length]  # remove salt from the encrypted data

        try:
            decoded_salt = base64.b64decode(salt)  # decode the salt. will not work if the salt is not the correct length
        except Exception as e:
            print(f"Error decoding salt: {e}")
            print("ATTENTION: Salt length might be incorrect. Have you changed it in config.yaml?")
            sys.exit(1)

        self.generate_fernet(master_key, decoded_salt)

        decrypted_username_bytes = self.decrypt_data(encrypted_username_bytes)
        decrypted_password_bytes = self.decrypt_data(encrypted_password_bytes)

        username = decrypted_username_bytes.decode()
        password = decrypted_password_bytes.decode()

        return username, password