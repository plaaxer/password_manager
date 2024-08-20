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
        self.crypto.generateKeys(self.master_key)

        # encrypting username and password
        encrypted_username = self.crypto.encrypt_data(username).decode()
        encrypted_password = self.crypto.encrypt_data(password).decode()
        print(f"Encrypted username: {encrypted_username}\nEncrypted password: {encrypted_password}")

        # appending random, unique salt to username and password
        encrypted_username += base64.urlsafe_b64encode(self.crypto.get_salt()).decode()
        encrypted_password += base64.urlsafe_b64encode(self.crypto.get_salt()).decode()

        # storing everything
        self.communicator.store_password(stash, service, encrypted_username, encrypted_password)

    def get_password(self, stash: str, service: str) -> None:

        # retrieves data from chosen service: s --> salted, e --> encrypted
        s_e_username, s_e_password = self.communicator.retrieve_password(stash, service)

        # extracting salt
        salt = s_e_username[-22:]

        # decrypting username and password
        username = self.crypto.decrypt_data(e_username.encode())    
        password = self.crypto.decrypt_data(e_password.encode())

        print(f"Username: {username}\nPassword: {password}") # change after