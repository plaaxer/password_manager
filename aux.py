import yaml
import argparse
import getpass

def get_conn_params() -> dict:
    with open("config.yaml", "r") as file:
        return yaml.safe_load(file)["conn_params"]

def get_options() -> str:
    with open("config.yaml", "r") as file:
        return yaml.safe_load(file)["options"]

def set_dbname(dbname: str) -> None:
    with open("config.yaml", "r") as file:
        data = yaml.safe_load(file)
        data["conn_params"]["dbname"] = dbname
    with open("config.yaml", "w") as file:
        yaml.dump(data, file)

def get_active_status() -> str:
    with open("config.yaml", "r") as file:
        return yaml.safe_load(file)["active_status"]

def set_active_status(status: bool) -> None:
    with open("config.yaml", "r") as file:
        data = yaml.safe_load(file)
        data["active_status"] = status
    with open("config.yaml", "w") as file:
        yaml.dump(data, file)

def menu_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Password manager.")
    parser.add_argument("--register", "-r", action="store_true", help="Register a new password stash.")
    parser.add_argument("--enter", "-e", action="store_true", help="Enter a password stash.")
    parser.add_argument("--list", "-l", action="store_true", help="List all created stashes.")
    parser.add_argument("stash_name", type=str, nargs='?', help="Name of the password stash you wish to access or create. Defaults to the one set at the yaml file (in case of registering).", default=get_options()["default_stash"])    
    parser.add_argument("master_key", type=str, nargs='?', help="Master key to access the password stash.", default=None)

    return parser

def authenticated_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Password manager.")
    parser.add_argument("--add", "-a", action="store_true", help="Add a new password.")
    parser.add_argument("--get", "-g", action="store_true", help="Get a password.")
    parser.add_argument("service", type=str, nargs='?', help="Service to store or retrieve password.", default=None)
    parser.add_argument("username", type=str, nargs='?', help="Username for the service.", default=None)
    parser.add_argument("password", type=str, nargs='?', help="Password for the service.", default=None)
    parser.add_argument("--list", "-l", action="store_true", help="List all stored passwords.")

    return parser

def get_master_key() -> str:
    while True:
        mk = getpass.getpass("Enter master key: ")
        mk2 = getpass.getpass("Confirm master key: ")
        if mk == mk2:
            return mk
        print("Master keys do not match. Try again.")

info_no_database =  "Wrong password or default connection not found. Please refer to the setup instructions on readme."