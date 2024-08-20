import crypto as cr

def test_crypto():
    # Test the CryptoAux class
    crypto = cr.CryptoAux()

    # Test the generate_key method
    key = crypto.generate_fernet("a")


    # Test the encrypt and decrypt methods
    message = "Hello, world!"
    print("encrypt and decrypt methods test:")
    print(f"Original message: {message}")
    encrypted = crypto.encrypt_data(message)
    print(f"Encrypted message: {encrypted}")
    print(type(encrypted))
    decrypted = crypto.decrypt_data(encrypted)
    print(f"Decrypted message: {decrypted}")

test_crypto()