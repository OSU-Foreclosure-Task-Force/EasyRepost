import configparser
import os.path
import secrets
from pathlib import Path
from logging import getLogger
import hashlib
import base64

logger = getLogger(__name__)

ROOT = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(ROOT, "config.ini")
config = configparser.ConfigParser()
config.read(CONFIG_PATH)

# Database

USE_MEMORY = config["Database"]["USE_MEMORY"].lower() == 'true'
SQLITE_PATH = config["Database"]["SQLITE_PATH"]
if USE_MEMORY:
    logger.warning('using memory database')
    SQLITE_PATH = ':memory:'

elif not os.path.exists(SQLITE_PATH):
    logger.warning(f'sqlite path {SQLITE_PATH} not detected, switching to working directory and default name')
    SQLITE_PATH = os.path.join(os.getcwd(), 'EasyRepost.db')
config["Database"]["SQLITE_PATH"] = SQLITE_PATH
SQLITE_URL = f'sqlite+aiosqlite:///{SQLITE_PATH}'
logger.warning(f'using {SQLITE_PATH} as db file')
logger.warning(f'using {SQLITE_URL} as db url')

# Subscription Token (used in self-subscribing)
SUBSCRIPTION_TOKEN = secrets.token_hex()


# App Token (used for validating requests)
APP_TOKEN: str = config["Auth"]["APP_TOKEN"] if config["Auth"]["APP_TOKEN"] != "" else None

_key = config["Auth"]["WEB_HUB_SECRET_KEY"]
_hash_key = hashlib.sha256(_key.encode()).digest()
WEB_HUB_SECRET_KEY = base64.urlsafe_b64encode(_hash_key)


# Cache
CACHE_PATH: Path = Path(config["Cache"]["CACHE_PATH"])
CACHE_MAX_SIZE: int = int(config["Cache"]["CACHE_MAX_SIZE"])
CACHE_CHECK_SIZE_INTERVAL: int = int(config["Cache"]["CACHE_CHECK_SIZE_INTERVAL"])

# Retry
DOWNLOAD_AUTO_RETRY: bool = config["Retry"]["DOWNLOAD_AUTO_RETRY"].lower() == 'true'
UPLOAD_AUTO_RETRY: bool = config["Retry"]["UPLOAD_AUTO_RETRY"].lower() == 'true'
# delay in minutes
DOWNLOAD_RETRY_DELAY: int = int(config["Retry"]["DOWNLOAD_RETRY_DELAY"])
UPLOAD_RETRY_DELAY: int = int(config["Retry"]["UPLOAD_RETRY_DELAY"])

# Max Concurrent
DOWNLOAD_MAX_CONCURRENT: int = int(config["Concurrent"]["DOWNLOAD_MAX_CONCURRENT"])
UPLOAD_MAX_CONCURRENT: int = int(config["Concurrent"]["UPLOAD_MAX_CONCURRENT"])

# Automation
ENABLE_AUTO_SUBSCRIPTION: bool = config["Automation"]["ENABLE_AUTO_SUBSCRIPTION"].lower() == 'true'
ENABLE_AUTO_DOWNLOAD: bool = config["Automation"]["ENABLE_AUTO_DOWNLOAD"].lower() == 'true'
ENABLE_AUTO_UPLOAD: bool = config["Automation"]["ENABLE_AUTO_UPLOAD"].lower() == 'true'
AUTO_DOWNLOAD_WAIT_TIME = int(config["Automation"]["AUTO_DOWNLOAD_WAIT_TIME"])
AUTO_DOWNLOAD_WAIT_TIME: int | None = None if AUTO_DOWNLOAD_WAIT_TIME <= 0 else AUTO_DOWNLOAD_WAIT_TIME
AUTO_UPLOAD_WAIT_TIME = int(config["Automation"]["AUTO_UPLOAD_WAIT_TIME"])
AUTO_UPLOAD_WAIT_TIME: int | None = None if AUTO_UPLOAD_WAIT_TIME <= 0 else AUTO_UPLOAD_WAIT_TIME
CALL_BACK_URL: str = config["Automation"]["CALL_BACK_URL"]
VALIDATION_INTERVAL: int = int(config["Automation"]["VALIDATION_INTERVAL"])


def write_back():
    with open(CONFIG_PATH, 'w') as f:
        config.write(f)
