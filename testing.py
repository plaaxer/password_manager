import crypto as cr
import aux
import base64
import sys

def test_crypto():

    # Test the CryptoAux class
    crypto = cr.CryptoAux()

    # Test the generate_key method
    crypto.generate_fernet("a")

    # salt used at fernet
    salt = crypto.get_salt()
    print(f"\nSalt: {salt}")
    salt = base64.b64encode(salt)
    print("\nSalt after encoding: ", salt)

    message = "extremely secret message"

    message =  base64.b64encode(message.encode())

    # encrypting original message
    encrypted = crypto.encrypt_data(message)
    print(f"\nEncrypted message: {encrypted}")

    # appending salt to encrypted message (all bytes)
    encrypted += salt

    data = encrypted # data type: bytes
    print(f"\nData: {data}")

    data = data.decode()
    print(f"\nData after decoding: {data}")
    data = data.encode()
    print(f"\nData after decoding and encoding: {data}")

    # extracting salt from decrypted message
    salt = data[-(aux.get_salt_length() + 3):]
    salt = base64.b64decode(salt)
    print(f"\nSalt after extraction: {salt}")

    # removing salt from decrypted message
    data = data[:-(aux.get_salt_length() + 3)]
    print("\nData after removing salt: ", data)

    # generating second keys
    crypto.generate_fernet("a", salt)

    # decrypting message
    decrypted = crypto.decrypt_data(data)

    # b64 things
    decrypted = base64.b64decode(decrypted)

    # decoding for string
    decrypted = decrypted.decode()
    print(f"\nDecrypted message: {decrypted}")

test_crypto()