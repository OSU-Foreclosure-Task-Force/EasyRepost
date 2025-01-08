import configparser
import datetime
import os.path
import secrets
from pathlib import Path
import logging
import hashlib
import base64


logger = logging.getLogger(__name__)

ROOT = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.environ.get('CONFIG',os.path.join(ROOT, "config.ini"))
print(f'*** using config from "{CONFIG_PATH}" ***')
config = configparser.ConfigParser()
config.read(CONFIG_PATH)

# logging

_LEVELS = {
    "notset": logging.NOTSET,
    "debug": logging.DEBUG,
    "info": logging.INFO,
    "warning": logging.WARNING,
    "error": logging.ERROR,
    "critical": logging.CRITICAL,
}

LOG_DIR: str = config["logging"]["log_dir_path"]
LOG_LEVEL: str = config["logging"]["log_level"] if config["logging"]["log_level"].lower() in _LEVELS else "INFO"
_LOG_LEVEL: int = _LEVELS.get(LOG_LEVEL.lower(), logging.INFO)
if not os.path.exists(LOG_DIR):
    logger.warning(f'log directory "{LOG_DIR}" not detected, attempting to create')
    try:
        os.makedirs(LOG_DIR, exist_ok=True)
    except Exception as e:
        logger.warning(f'failed to create log directory "{LOG_DIR}"')
        logger.warning(f'error: {e}')
        LOG_DIR = os.path.join(ROOT, 'logs')
        logger.warning(f'using default log path "{LOG_DIR}"')
_datetime = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
_log_file_name = _datetime + '.log'
_log_file_path = os.path.join(LOG_DIR, _log_file_name)
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=_LOG_LEVEL,
                    handlers=[
                        logging.StreamHandler(),
                        logging.FileHandler(_log_file_path, mode='w')
                    ])
logger.info(f'using "{LOG_DIR}" as log directory')
logger.info(f'start logging at "{_datetime}", saving at "{_log_file_path}"')
logger.info(f'using log level "{LOG_LEVEL}"')

config["logging"]["log_dir_path"] = LOG_DIR
config["logging"]["log_level"] = LOG_LEVEL

# Database

USE_MEMORY = config["Database"]["USE_MEMORY"].lower() == 'true'
SQLITE_PATH = config["Database"]["SQLITE_PATH"]
if USE_MEMORY:
    logger.warning('using memory database')
    SQLITE_PATH = ':memory:'
elif not os.path.exists(SQLITE_PATH):
    logger.warning(f'sqlite file "{SQLITE_PATH}" not detected, attempting to create')
    try:
        os.makedirs(os.path.dirname(SQLITE_PATH), exist_ok=True)
    except Exception as e:
        logger.warning(f'failed to create directory for sqlite file "{SQLITE_PATH}"')
        logger.warning(f'error: {e}')
        SQLITE_PATH = os.path.join(ROOT, 'EasyRepost.db')
        logger.warning(f'using default path "{SQLITE_PATH}"')
config["Database"]["SQLITE_PATH"] = SQLITE_PATH
SQLITE_URL = f'sqlite+aiosqlite:///{SQLITE_PATH}'
logger.info(f'using "{SQLITE_PATH}" as db file')
logger.info(f'using "{SQLITE_URL}" as db url')

# Subscription Token (used in self-subscribing)
SUBSCRIPTION_TOKEN = secrets.token_hex()


# App Token (used for validating requests)
APP_TOKEN: str = config["Auth"]["APP_TOKEN"] if config["Auth"]["APP_TOKEN"] != "" else None

_key = config["Auth"]["WEB_HUB_SECRET_KEY"]
_hash_key = hashlib.sha256(_key.encode()).digest()
WEB_HUB_SECRET_KEY = base64.urlsafe_b64encode(_hash_key)


# Cache
_CACHE_PATH = config["Cache"]["CACHE_PATH"]
if not os.path.exists(_CACHE_PATH):
    logger.warning(f'cache path "{_CACHE_PATH}" not detected, attempting to create')
    try:
        os.makedirs(_CACHE_PATH, exist_ok=True)
    except Exception as e:
        logger.warning(f'failed to create directory for cache "{_CACHE_PATH}"')
        logger.warning(f'error: {e}')
        _CACHE_PATH = os.path.join(ROOT, 'cache')
        logger.warning(f'using default cache path "{_CACHE_PATH}"')
CACHE_PATH: Path = Path(_CACHE_PATH)
CACHE_MAX_SIZE: int = int(config["Cache"]["CACHE_MAX_SIZE"])
CACHE_CHECK_SIZE_INTERVAL: int = int(config["Cache"]["CACHE_CHECK_SIZE_INTERVAL"])

logger.info(f'using "{_CACHE_PATH}" as cache path')

config["Cache"]["CACHE_PATH"] = _CACHE_PATH
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
