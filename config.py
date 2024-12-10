import configparser
import secrets

config = configparser.ConfigParser()
config.read("config.ini")

DEBUG = config["Dev"]["DEBUG"]
SQLITE_URL = config["Database"]["SQLITE_URL"]
SUBSCRIPTION_TOKEN = secrets.token_hex()

APP_TOKEN = config["Auth"]["APP_TOKEN"] if config["Auth"]["APP_TOKEN"] != "" else None
