import argparse
import src.aux as aux

class CommandParserGenerator:

    def __init__(self):
        pass 

    def generate_menu_parser(self):
        """
        Generates and returns a parser for the menu commands.
        """
        parser = argparse.ArgumentParser(description="Password manager (menu commands).")
        parser.add_argument("--register", "-r", action="store_true", help="Register a new password stash.")
        parser.add_argument("--enter", "-e", action="store_true", help="Enter a password stash.")
        parser.add_argument("--list", "-l", action="store_true", help="List all created stashes.")
        parser.add_argument("--give_stash_name", "-gs", action="store_true", help="By doing --enter [stash_name], you can provide the stash name without the master key.")
        parser.add_argument("stash_name", type=str, nargs='?', help="Name of the password stash you wish to access or create. Defaults to the one set in the yaml file (in case of registering).", default=None)    
        parser.add_argument("master_key", type=str, nargs='?', help="Master key to access the password stash.", default=None)
        return parser

    def generate_authenticated_parser(self):
        """
        Generates and returns a parser for the authenticated commands.
        """
        parser = argparse.ArgumentParser(description="Password manager (authenticated commands).")
        parser.add_argument("--add", "-a", action="store_true", help="Add a new password.")
        parser.add_argument("--get", "-g", action="store_true", help="Get a password.")
        parser.add_argument("service", type=str, nargs='?', help="Service to store or retrieve password.", default=None)
        parser.add_argument("username", type=str, nargs='?', help="Username for the service.", default=None)
        parser.add_argument("password", type=str, nargs='?', help="Password for the service.", default=None)
        return parser