import yaml
import argparse
import getpass

def get_conn_params() -> dict:
    with open("configs/config.yaml", "r") as file:
        return yaml.safe_load(file)["conn_params"]

def get_options() -> str:
    with open("configs/config.yaml", "r") as file:
        return yaml.safe_load(file)["options"]

def set_dbname(dbname: str) -> None:
    with open("configs/config.yaml", "r") as file:
        data = yaml.safe_load(file)
        data["conn_params"]["dbname"] = dbname
    with open("configs/config.yaml", "w") as file:
        yaml.dump(data, file)

def get_active_status() -> str:
    with open("configs/config.yaml", "r") as file:
        return yaml.safe_load(file)["active_status"]

def set_active_status(status: bool) -> None:
    with open("configs/config.yaml", "r") as file:
        data = yaml.safe_load(file)
        data["active_status"] = status
    with open("configs/config.yaml", "w") as file:
        yaml.dump(data, file)

def get_salt_length() -> int:
    with open("configs/config.yaml", "r") as file:
        return yaml.safe_load(file)["options"]["salt_length"]

def get_master_key() -> str:
    while True:
        mk = getpass.getpass("Enter master key: ")
        mk2 = getpass.getpass("Confirm master key: ")
        if mk == mk2:
            return mk
        print("Master keys do not match. Try again.")