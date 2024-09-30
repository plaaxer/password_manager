import base64

import src.crypto as crypto
import src.aux as aux
import src.communicator as com

# Main application
class App():
    def __init__(self):
        self.crypto = crypto.CryptoAux()
        self.communicator = com.Communicator()
        self.menu_arg_parser = aux.menu_arg_parser()
        self.authenticated_arg_parser = aux.authenticated_arg_parser()
        self.master_key = None
        self.running = True

    def run(self) -> None:

        print(f"\nWelcome to the password manager! Write '-h' for more information or '-q' to quit.")

        while self.running:

            command = input("\nEnter command: ")

            if command == "-q":
                print("Exiting...")
                self.running = False

            action = self.menu_arg_parser.parse_args(command.split())

            if action.register:
                if action.stash_name != None:
                    self.register(action.stash_name)
                else:
                    print("Please provide a stash name.")

            elif action.enter:
                # gotta change this after...
                if action.stash_name != None and action.master_key != None:
                    self.enter(action.stash_name, action.master_key)

                elif action.master_key != None and action.stash_name == None:
                    self.enter(aux.get_options()["default_stash"], action.stash_name)

                else:
                    self.enter(aux.get_options()["default_stash"], aux.get_master_key())
                    
            elif action.list:
                self.list_stashes()
            else:
                print("Invalid command. Write '-h' for help.")

    def run_authenticated(self, stash: str) -> None:
            
            print("\nAuthenticated. Write '-q' to quit and '-h' for help.")

            while True:
    
                command = input("\nEnter command: ")
    
                if command == "-q":
                    print("Exiting...")
                    self.running = False
                    break
    
                action = self.authenticated_arg_parser.parse_args(command.split())

                # I can do the if None verification inside the parser (maybe?)
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
        try:
            self.communicator.create_stash(name)
        except Exception as e:
            print(f"Error creating stash: {e}")
            return

        # getting master key from auxiliar function
        self.master_key = aux.get_master_key()

        # master key hashed and registered
        try:
            master_key_hash = self.crypto.hash(self.master_key)
        except Exception as e:
            print(f"Error hashing master key: {e}")
            return
        print(f"Master key hash: {master_key_hash}\nMaster key hashed and registered successfully.")

        # add stash info to stashes_info
        self.communicator.add_stash_info(name, master_key_hash)

        # create passwords table for stash
        self.communicator.create_password_table(name)
    
    def list_stashes(self) -> None:
        self.communicator.list_stashes()

    def add_password(self, stash: str, service: str, username: str, password: str) -> None:

        # generate fernet object for encryption and decryption with current master_key
        self.crypto.generate_fernet(self.master_key)

        # encrypts and salts username and password
        data_username, data_password = self.crypto.add_salt_encryption(username, password)

        # storing everything
        self.communicator.store_password(stash, service, data_username, data_password)

    def get_password(self, stash: str, service: str) -> None:

        # Retrieves data from chosen service
        encrypted_username, encrypted_password = self.communicator.retrieve_password(stash, service)
        # salted, encrypted, as string

        # decrypts and desalts username and password
        username, password = self.crypto.remove_salt_encryption(encrypted_username, encrypted_password, self.master_key)

        print(f'Username: {username}\nPassword: {password}')

