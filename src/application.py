import base64

import src.crypto as crypto
import src.aux as aux
import src.communicator as com
from src.commandParser import CommandParserGenerator

# Main application
class App():
    def __init__(self):
        self.crypto = crypto.CryptoAux()
        self.communicator = com.Communicator()
        self.command_parser_generator = CommandParserGenerator()
        self.menu_arg_parser = self.command_parser_generator.generate_menu_parser()
        self.authenticated_arg_parser = self.command_parser_generator.generate_authenticated_parser()

        self.master_key = None
        self.authenticated = False
        # authentication or not is just a matter of checking whether the correct master key was provided;
        # even if manipulated, the generated fernet object will be useless without the correct master key

    def run(self) -> None:

        print(f"\nWelcome to the password manager! Write '-h' for more information or '-q' to quit.")

        self.running = True

        while self.running and not self.authenticated:
            command = input("\nEnter command: ")

            if command == "-q":
                print("Exiting...")
                self.running = False
                break

            try:
                action = self.menu_arg_parser.parse_args(command.split())

            except SystemExit:
                print("Invalid command. Write '-h' for help.")
                continue

            if action.register:

                if action.stash_name is not None:
                    self.register(action.stash_name)
                else:
                    self.register(aux.get_options()["default_stash"])

            elif action.enter:

                if action.stash_name is not None and action.master_key is not None:
                    self.enter(action.stash_name, action.master_key)

                elif action.stash_name is None and action.master_key is None:
                    self.enter(aux.get_options()["default_stash"], aux.get_master_key())

                else:

                    if action.give_stash_name:
                        # only argument is stash name
                        self.enter(action.stash_name, aux.get_master_key())

                    else:
                        # inverting to make it so you can enter a stash just by providing the mpw (given it's the default stash)
                        action.master_key = action.stash_name
                    
                        # only argument is master key
                        self.enter(aux.get_options()["default_stash"], action.master_key)

            elif action.list:
                self.list_stashes()

            elif not action.register and not action.enter and not action.list:
                    if action.give_stash_name:
                        # only argument is stash name
                        self.enter(action.stash_name, aux.get_master_key())

                    else:
                        # inverting to make it so you can enter a stash just by providing the mpw (given it's the default stash)
                        action.master_key = action.stash_name
                    
                        # only argument is master key
                        self.enter(aux.get_options()["default_stash"], action.master_key)
            
            else:
                print("Invalid command. Write '-h' for help.")

    def run_authenticated(self, stash: str) -> None:

        self.authenticated = True
        print(f"\nAuthenticated. Accessed stash '{stash}'. Write '-q' to quit and '-h' for help.")

        while self.running and self.authenticated:
            command = input("\nEnter command: ")

            if command == "-q":
                print("Logging out...")
                self.authenticated = False
                self.crypto.delete_fernet()
                self.delete_master_key()
                break

            try:
                action = self.authenticated_arg_parser.parse_args(command.split())

            except SystemExit:
                print("Invalid command. Write '-h' for help.")
                continue

            if action.add:
                if action.service and action.username and action.password:
                    self.add_password(stash, action.service, action.username, action.password)
                else:
                    print("Please provide the service, username, and password.")

            elif action.get:
                if action.service:
                    self.get_password(stash, action.service)
                else:
                    print("Please provide the service name.")

            else:
                print("Invalid command. Write '-h' for help.")

    def enter(self, stash: str, master_key: str) -> None:
        
        # gets the hash of the schema's registered master key
        try:
            hashed_master_key = self.communicator.get_master_key_hash(stash)
        except:
            print(f"Stash '{stash}' not found. (maybe check default stash name in config file, or remove the '-gs' flag)")
            return

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
            print("Maybe try this: Stashes names must start with either a letter or an underscore, and can only contain letters, numbers, and underscores. (and cannot be identical)")
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

    def delete_master_key(self) -> None:
        del self.master_key