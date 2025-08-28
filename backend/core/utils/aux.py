import os

def get_salt_length() -> int:
    try:
        return int(os.getenv("SALT_LENGTH", "16"))
    except ValueError:
        return 16