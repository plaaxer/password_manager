import yaml
import argparse
import getpass

def get_options() -> str:
    with open("configs/config.yaml", "r") as file:
        return yaml.safe_load(file)["options"]

def set_dbname(dbname: str) -> None:
    with open("configs/config.yaml", "r") as file:
        data = yaml.safe_load(file)
        data["conn_params"]["dbname"] = dbname
    with open("configs/config.yaml", "w") as file:
        yaml.dump(data, file)

def get_salt_length() -> int:
    with open("configs/config.yaml", "r") as file:
        return yaml.safe_load(file)["options"]["salt_length"]