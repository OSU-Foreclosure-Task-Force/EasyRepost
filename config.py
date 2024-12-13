import configparser
import secrets
from pathlib import Path

config = configparser.ConfigParser()
config.read("config.ini")

DEBUG = config["Dev"]["DEBUG"]
SQLITE_URL = config["Database"]["SQLITE_PATH"]
SUBSCRIPTION_TOKEN = secrets.token_hex()

APP_TOKEN = config["Auth"]["APP_TOKEN"] if config["Auth"]["APP_TOKEN"] != "" else None
TEMP_PATH = Path(config["Temp"]["TEMP_PATH"])

DOWNLOAD_RETRY_DELAY = config["RetryDelay"]["DOWNLOAD_RETRY_DELAY"]
UPLOAD_RETRY_DELAY = config["RetryDelay"]["UPLOAD_RETRY_DELAY"]

DOWNLOAD_MAX_CONCURRENT = config["Concurrent"]["DOWNLOAD_MAX_CONCURRENT"]
UPLOAD_MAX_CONCURRENT = config["Concurrent"]["UPLOAD_MAX_CONCURRENT"]