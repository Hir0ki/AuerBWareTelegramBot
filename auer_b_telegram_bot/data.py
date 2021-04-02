import sqlite3
from config import settings
import logging
from auer_scraper import Angebot
from typing import List
class Database:


    def __init__(self):
        self.logger = logging.getLogger("Database")
        self.database_connection = sqlite3.connect(settings.SQLITE_PATH)
        self.logger.info("connected to sqlite")
        self.database_connection.execute( "CREATE TABLE IF NOT EXISTS client_alter( client_id VARCHAR(32), artnr VARCHAR(32), PRIMARY KEY( client_id, artnr ));") 
        self.database_connection.execute( "CREATE TABLE IF NOT EXISTS artikel( artnr VARCHAR(32) );" )
        self.database_connection.commit()
        self.logger.info("sqlite init complete")


    
    def insert_new_artnr(self, angebote: List[Angebot]):
        self.logger.info(f"Try to insert {len(angebote)} items into local db")
        for angebot in angebote:
            self.database_connection.execute("INSERT INTO artikel VALUES ( ? ) ", [ angebot.artnr ] )
            self.database_connection.commit()
