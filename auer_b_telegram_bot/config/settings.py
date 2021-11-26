from logging.config import dictConfig
import os
import logging
import yaml
import pathlib


# Add new config parameter her

# Path to the logging config file in a yml format
LOG_CONFIG_PATH = os.getenv("LOG_CONFIG_PATH", "./logging.yml")
# Log Level for the root logger
LOG_LEVEL_ROOT = os.getenv("LOG_LEVEL_ROOT", "INFO")
# Log level for the Project root logger
LOG_LEVEL_AUER_B_TELEGRAM_BOT = os.getenv("LOG_LEVEL_AUER_B_TELEGRAM_BOT", "INFO")

BOT_TOKEN = os.getenv("BOT_TOKEN", "")

AUER_SCRAPE_INTERVAL = os.getenv("AUER_SCRAPE_INTERVAL", 20)

POSTGRES_USERNAME = os.getenv("POSTGRES_USERNAME", "auer_b_ware_bot")
POSTGRES_DBNAME = os.getenv("POSTGRES_DBNAME", "auer_b_ware_bot")
POSTGRES_HOSTNAME = os.getenv("POSTGRES_HOSTNAME", "timescaledb")
POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5432")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "")

# Load yml logging config
logging_config_path = pathlib.Path(LOG_CONFIG_PATH)
logging.info(f"Logging cofng path is {LOG_CONFIG_PATH}")
if logging_config_path.is_file():
    with open(logging_config_path, "rt") as file:
        logging_config = yaml.safe_load(file.read())
else:
    logging.error("Couldn't find the logging config", exc_info=True)
    raise ValueError("Error while loading logging config")

dictConfig(logging_config)
# set Root logger level explicitly
if LOG_LEVEL_ROOT == "INFO":
    logging.getLogger("root").setLevel(logging.INFO)
if LOG_LEVEL_ROOT == "DEBUG":
    logging.getLogger("root").setLevel(logging.DEBUG)
if LOG_LEVEL_ROOT == "CRITICAL":
    logging.getLogger("root").setLevel(logging.CRITICAL)
if LOG_LEVEL_ROOT == "ERROR":
    logging.getLogger("root").setLevel(logging.ERROR)
if LOG_LEVEL_ROOT == "WARNING":
    logging.getLogger("root").setLevel(logging.WARNING)
