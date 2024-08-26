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
        self.master_key = None
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
        
        # storing master_key during session
        self.master_key = master_key

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

        data_username, data_password = self.add_salt_encryption(username, password)

        # storing everything
        self.communicator.store_password(stash, service, data_username, data_password)

    def get_password(self, stash: str, service: str) -> None:

        # Retrieves data from chosen service
        encrypted_username, encrypted_password = self.communicator.retrieve_password(stash, service)
        # salted, encrypted, as string

        username, password = self.remove_salt_encryption(encrypted_username, encrypted_password)

        print(f'Username: {username}\nPassword: {password}')

    def add_salt_encryption(self, username: str, password: str) -> tuple:

        username = username.encode()
        password = password.encode()

        username = base64.b64encode(username)
        password = base64.b64encode(password)

        encrypted_username = self.crypto.encrypt_data(username)
        encrypted_password = self.crypto.encrypt_data(password)
        print(f"Encrypted username: {encrypted_username}\nEncrypted password: {encrypted_password}")

        salt = self.crypto.get_salt()
        salt = base64.b64encode(salt)

        data_username = (encrypted_username + salt).decode()
        data_password = (encrypted_password + salt).decode()

        return data_username, data_password

    def remove_salt_encryption(self, encrypted_username: str, encrypted_password: str) -> tuple:

        encrypted_username = encrypted_username.encode()
        encrypted_password = encrypted_password.encode()

        salt = username[-(aux.get_salt_length() + 3):]
        salt = base64.b64decode(salt)
        print(f"\nSalt after extraction: {salt}")

        self.crypto.generate_fernet(self.master_key, salt)

        decrypted_username = self.crypto.decrypt_data(encrypted_username)
        decrypted_password = self.crypto.decrypt_data(encrypted_password)

        decrypted_username = base64.b64decode(decrypted_username)
        decrypted_password = base64.b64decode(decrypted_password)

        username = decrypted_username.decode()
        password = decrypted_password.decode()

        return username, password

