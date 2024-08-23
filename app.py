import base64

import crypto
import aux
import communicator as com

# Main application
class App():
    def __init__(self):
        self.crypto = crypto.CryptoAux()
        self.communicator = com.Communicator()
        self.menu_arg_parser = aux.menu_arg_parser()
        self.authenticated_arg_parser = aux.authenticated_arg_parser()
        self.run()

    def run(self) -> None:

        print(f"\nWelcome to the password manager! Write '-h' for more information or '-q' to quit.")

        while True:

            command = input("\nEnter command: ")

            if command == "-q":
                print("Exiting...")
                break

            action = self.menu_arg_parser.parse_args(command.split())

            if action.register:
                if action.stash_name != None:
                    self.register(action.stash_name)
                else:
                    print("Please provide a stash name.")
            elif action.enter:
                if action.stash_name != None and action.master_key != None:
                    self.enter(action.stash_name, action.master_key)
                else:
                    print("Please provide a stash name and master key.")
            elif action.list:
                stashes = aux.get_created_stashes()
                print("Stashes created:")
                for stash in stashes:
                    print(stash, end=" ")
            else:
                print("Invalid command. Write '-h' for help.")

    def run_authenticated(self, stash: str) -> None:
            
            print("\nAuthenticated. Write '-q' to quit and '-h' for help.")

            while True:
    
                command = input("\nEnter command: ")
    
                if command == "-q":
                    print("Exiting...")
                    break
    
                action = self.authenticated_arg_parser.parse_args(command.split())

                # I can do the if None verification inside the parser
                if action.add:
                    self.add_password(stash, action.service, action.username, action.password)
                elif action.get:
                    self.get_password(stash, action.service)
                elif action.list:
                    self.list()
                else:
                    print("Invalid command. Write '-h' for help.")

    def enter(self, stash: str, master_key: str) -> None:
        
        # gets the hash of the schema's registered master key
        hashed_master_key = self.communicator.get_master_key_hash(stash)

        # checks if the master key is correct
        if not self.crypto.verify_master_key(master_key, hashed_master_key):
            print("Authentication failed.")
            return

        # enters authenticated mode
        self.run_authenticated(stash)

    def register(self, name: str)-> None:

        print("Creating a stash named", name)

        # create schema/stash with given name
        self.communicator.create_stash(name)

        # getting master key from auxiliar function
        self.master_key = aux.get_master_key()

        # master key hashed and registered
        master_key_hash = self.crypto.hash(self.master_key)
        print(f"Master key hash: {master_key_hash}\nMaster key hashed and registered successfully.")

        # create info table for stash (storing master key hash)
        self.communicator.create_info_table(name, master_key_hash)

        # create passwords table for stash
        self.communicator.create_password_table(name)
    
    def list(self) -> None:
        pass

    def add_password(self, stash: str, service: str, username: str, password: str) -> None:

        # generate fernet object for encryption and decryption with current master_key
        self.crypto.generate_fernet(self.master_key)

        # encrypting username and password
        encrypted_username = self.crypto.encrypt_data(username)
        encrypted_password = self.crypto.encrypt_data(password)
        print(f"Encrypted username: {encrypted_username}\nEncrypted password: {encrypted_password}")

        # appending random, unique (per session) salt to username and password
        encrypted_username += self.crypto.get_salt()
        encrypted_password += self.crypto.get_salt()

        # transforming bytes into string for storage
        encrypted_username = encrypted_username.decode()
        encrypted_password = encrypted_password.decode()

        # storing everything
        self.communicator.store_password(stash, service, encrypted_username, encrypted_password)

def get_password(self, stash: str, service: str) -> None:

    # Retrieves data from chosen service
    username, password = self.communicator.retrieve_password(stash, service)
    # salted, encrypted, as string

    username = username.encode()
    password = password.encode()

    # Salt length in bytes
    salt_length = aux.get_salt_length()

    # Extract the salt from the end of the decoded username data
    # salt = decoded_username[-salt_length:]

    # Extract the username from the decoded username data (excluding the salt)
    # username = decoded_username[:-salt_length].decode()

    # decryption
    # username = self.crypto.decrypt_data(decoded_username.decode())
    # password = self.crypto.decrypt_data(decoded_password.decode())

    # print(f"Username: {username}\nPassword: {password}")
