import os
import argon2
import base64

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

import src.aux as aux

class CryptoAux:
    def __init__(self):
        self.ph = argon2.PasswordHasher()

    # hashes the master key utilizing argon2
    def hash(self, master_key: str) -> str:
        return self.ph.hash(master_key)

    # checks if password is correct
    def verify_master_key(self, master_key: str, hash: str) -> bool:
        try:
            self.ph.verify(hash, master_key)
            return True
        except argon2.exceptions.VerifyMismatchError: # wrong password
            return False
    
    def generate_fernet(self, master_key: str, salt=os.urandom(aux.get_salt_length())) -> None:

        self.salt = salt

        # all of the documentation regarding these functions is in the cryptography library

        kdf = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=self.salt, iterations = 480000) # key derivation function

        key = base64.urlsafe_b64encode(kdf.derive(master_key.encode())) # key (256 bits) derived from master key

        self.f = Fernet(key) # key is used to generate a Fernet object

        # fernet will be resposible for encrypting and decrypting data

    def encrypt_data(self, data: bytes) -> bytes:
        return self.f.encrypt(data) # encrypts using the fernet object

    def decrypt_data(self, data: bytes) -> bytes:
        return self.f.decrypt(data) # decrypts using the fernet object
    
    def get_salt(self) -> bytes:
        return self.salt
    
    def add_salt_encryption(self, username: str, password: str) -> tuple:

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
        
        encrypted_username = encrypted_username.encode()
        encrypted_password = encrypted_password.encode()

        encrypted_username_bytes = base64.b64decode(encrypted_username)
        encrypted_password_bytes = base64.b64decode(encrypted_password)

        salt_length = aux.get_salt_length() + (aux.get_salt_length())//2
        salt = encrypted_username_bytes[-salt_length:]  # extract salt from the end
        encrypted_username_bytes = encrypted_username_bytes[:-salt_length]  # remove salt from the encrypted data
        decoded_salt = base64.b64decode(salt)  # decode the salt

        self.generate_fernet(master_key, decoded_salt)

        decrypted_username_bytes = self.decrypt_data(encrypted_username_bytes)
        decrypted_password_bytes = self.decrypt_data(encrypted_password_bytes)

        username = decrypted_username_bytes.decode()
        password = decrypted_password_bytes.decode()

        return username, password