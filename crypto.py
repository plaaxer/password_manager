import os
import argon2
import base64
import aux

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

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

    def encrypt_data(self, data: str) -> str:
        return self.f.encrypt(data.encode()) # encrypts using the fernet object

    def decrypt_data(self, data: bytes) -> str:
        return (self.f.decrypt(data)).decode() # decrypts using the fernet object
    
    def get_salt(self) -> bytes:
        return self.salt