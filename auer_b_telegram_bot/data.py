from config import settings
from typing import List, Iterable
from dataclasses import dataclass
from datetime import datetime
import logging
import sqlite3
import texttable


@dataclass
class Angebot():
    scraped_at: datetime
    außenmaße: str
    artnr: str
    handgriff: str
    preis_alt: float
    preis_neu: float
    währung: str
    stück_auf_palette: int
    preis_stück_pro_palette_alt: float
    preis_stück_pro_palette_neu: float
    verfügbar: int 
    versandfertig_link: str

    def __init__(self, tr, scraped_at):
        
        if len(tr.text) == 0:
            self.artnr = None
            return

        tds = tr.find_all("td")
        self.außenmaße = tds[0].text
        self.artnr = tds[1].text
        self.handgriff = tds[2].text 
        offset = 0
        if  "KLT" in self.artnr:
            offset = 1
        if "EO" in self.artnr:
            offset = -1 

        preis_td = tds[3+offset].find_all("span")
        logging.getLogger("scraper").info(f"Current artnr: {self.artnr} offset: {offset}")
        self.preis_alt = float(preis_td[1].text.replace("€", "").replace(",","."))
        self.preis_neu = float(preis_td[2].text.replace("€", "").replace(",","."))
        self.stück_auf_palette = int(tds[4+offset].text)
 
        preis_td = tds[5+offset].find_all("span")
        self.preis_stück_pro_palette_alt= float(preis_td[1].text.replace("€", "").replace(",","."))
        self.preis_stück_pro_palette_neu = float(preis_td[2].text.replace("€", "").replace(",","."))
        
        self.verfügbar = int(tds[6+offset].text)
        self.versandfertig_link = tds[7+offset].find("img")["title"]

        self.währung = "€"

        self.scraped_at = scraped_at



class Database:


    def __init__(self):
        self.logger = logging.getLogger("Database")
        database_connection = sqlite3.connect(settings.SQLITE_PATH)
        self.logger.info("connected to sqlite")
        database_connection.execute( "CREATE TABLE IF NOT EXISTS client_alter( client_id VARCHAR(32), artnr VARCHAR(32), PRIMARY KEY( client_id, artnr ));") 
        database_connection.execute( "CREATE TABLE IF NOT EXISTS artikel( artnr VARCHAR(32) );" )
        database_connection.commit()
        database_connection.close() 
        self.logger.info("sqlite init complete")

    def _execute_query(self,query: str, arguments: Iterable, run_commit: bool):
        
        database_connection = sqlite3.connect(settings.SQLITE_PATH)
        database_connection.execute(query, arguments)
        if run_commit == True:
            database_connection.commit()
        database_connection.close()


    
    def insert_new_artnr(self, angebote: List[Angebot]):
        self.logger.info(f"Try to insert {len(angebote)} items into local db")
        for angebot in angebote:
            self._execute_query("INSERT INTO artikel VALUES ( ? ) ", [ angebot.artnr ], run_commit=True )
        self.logger.info("Done inserting items")


class AuerData:
    _instance = None


    @classmethod
    def instance(cls):
        logger = logging.getLogger("DataClass") 
        if cls._instance is None:
            logger.info("Creating new DataClass instance")
            cls._instance = cls.__new__(cls)
            cls._instance.database = Database()
        return cls._instance 

    def set_new_data(self, data):
        self.database.insert_new_artnr(data)
        self.data: List[Angebot] = data

    def get_current_data(self):
        return self.data
    
    def text_table_of_current_data(self):
        table = texttable.Texttable()
        table.set_cols_align(("l","l","l"))
        table.set_cols_dtype(("t", "i", "t"))
        table.add_row(("Type", "Verfügbare Menge", "Preis"))
        for entry in self.data:
            table.add_row([entry.artnr, entry.verfügbar, f"{entry.preis_neu:.2f} €"])
        table_string =  str(table.draw())
        table_string = "<pre>" + table_string + "</pre>"
        return table_string
