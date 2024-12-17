import configparser
import os.path
import secrets
from pathlib import Path
from logging import getLogger
logger = getLogger(__name__)

config = configparser.ConfigParser()
config.read("config.ini")


DEBUG = config["Dev"]["DEBUG"]

SQLITE_PATH = config["Database"]["SQLITE_PATH"]
if not os.path.exists(SQLITE_PATH):
    logger.warning(f'sqlite path {SQLITE_PATH} not detected, switching to working directory and default name')
    SQLITE_PATH = os.path.join(os.getcwd(),'EasyRepost.db')

SQLITE_URL = f'sqlite+aiosqlite:///{SQLITE_PATH}'
logger.info(f'using {SQLITE_PATH} as db file')
logger.info(f'using {SQLITE_URL} as db url')
SUBSCRIPTION_TOKEN = secrets.token_hex()

APP_TOKEN = config["Auth"]["APP_TOKEN"] if config["Auth"]["APP_TOKEN"] != "" else None

CACHE_PATH = Path(config["Cache"]["CACHE_PATH"])
CACHE_MAX_SIZE = int(config["Cache"]["CACHE_MAX_SIZE"])
CACHE_CHECK_SIZE_INTERVAL = int(config["Cache"]["CACHE_CHECK_SIZE_INTERVAL"])

DOWNLOAD_RETRY_DELAY = int(config["RetryDelay"]["DOWNLOAD_RETRY_DELAY"])
UPLOAD_RETRY_DELAY = int(config["RetryDelay"]["UPLOAD_RETRY_DELAY"])

DOWNLOAD_MAX_CONCURRENT = int(config["Concurrent"]["DOWNLOAD_MAX_CONCURRENT"])
UPLOAD_MAX_CONCURRENT = int(config["Concurrent"]["UPLOAD_MAX_CONCURRENT"])


with open("config.ini", "w") as configfile:
    config.write(configfile)