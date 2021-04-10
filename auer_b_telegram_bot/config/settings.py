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

SQLITE_PATH = os.getenv("SQLITE_PATH", "./bot_db.db")

INFLUXDB_HOST = os.getenv("INFLUXDB_HOST", "")
INFLUXDB_USERNAME = os.getenv("INFLUXDB_USERNAME", "")
INFLUXDB_PASSWORD = os.getenv("INFLUXDB_PASSWORD", "")
INFLUXDB_DATABASE = os.getenv("INFLUXDB_DATABASE", "AUER_B_WARE_SCRAPER")
INFLUXDB_PORT = os.getenv("INFLUXDB_PORT", "8086")


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
