import sqlite3
from config import settings
import logging

class Database:


    def __init__(self):
        logger = logging.getLogger("Database")
        self.database_connection = sqlite3.connect(settings.SQLITE_PATH)
        logger.info("connected to sqlite")
        self.database_connection.execute( "CREATE TABLE IF NOT EXISTS client_alter( client_id VARCHAR(32), artnr VARCHAR(32), PRIMARY KEY( client_id, artnr ));") 
        self.database_connection.execute( "CREATE TABLE IF NOT EXISTS artikel( artnr VARCHAR(32) );" )
        self.database_connection.commit()
        logger.info("sqlite init complete")