from config import settings
from typing import List, Iterable
from dataclasses import dataclass
from datetime import datetime
from influxdb import InfluxDBClient
from json import dumps
import logging
import sqlite3
import texttable


@dataclass
class Angebot:
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
        if "KLT" in self.artnr:
            offset = 1
        if "EO" in self.artnr:
            offset = -1

        preis_td = tds[3 + offset].find_all("span")
        logging.getLogger("scraper").debug(
            f"Current artnr: {self.artnr} offset: {offset}"
        )
        self.preis_alt = float(preis_td[1].text.replace("€", "").replace(",", "."))
        self.preis_neu = float(preis_td[2].text.replace("€", "").replace(",", "."))
        self.stück_auf_palette = int(tds[4 + offset].text)

        preis_td = tds[5 + offset].find_all("span")
        self.preis_stück_pro_palette_alt = float(
            preis_td[1].text.replace("€", "").replace(",", ".")
        )
        self.preis_stück_pro_palette_neu = float(
            preis_td[2].text.replace("€", "").replace(",", ".")
        )

        self.verfügbar = int(tds[6 + offset].text)
        self.versandfertig_link = tds[7 + offset].find("img")["title"]

        self.währung = "€"

        self.scraped_at = scraped_at


class Database:
    def __init__(self):
        self.logger = logging.getLogger("Database")
        database_connection = sqlite3.connect(settings.SQLITE_PATH)
        self.logger.info("connected to sqlite")
        database_connection.execute(
            "CREATE TABLE IF NOT EXISTS clients( client_id VARCHAR(32), PRIMARY KEY( client_id ));"
        )
        database_connection.execute(
            "CREATE TABLE IF NOT EXISTS artikel( artnr VARCHAR(32) );"
        )
        database_connection.commit()
        database_connection.close()
        self.logger.info("sqlite init complete")
        self.logger.info("conencted to influxdb")
        self._influx_client = InfluxDBClient(
            host=settings.INFLUXDB_HOST,
            port=settings.INFLUXDB_PORT,
            username=settings.INFLUXDB_USERNAME,
            password=settings.INFLUXDB_PASSWORD,
            database=settings.INFLUXDB_DATABASE,
        )
        self._influx_client.create_database(settings.INFLUXDB_DATABASE)

        self.logger.info("done connecting to influxdb")

    def _execute_query(self, query: str, arguments: Iterable, run_commit: bool):

        database_connection = sqlite3.connect(settings.SQLITE_PATH)
        result = database_connection.execute(query, arguments)
        if run_commit == True:
            database_connection.commit()
        database_connection.close()
        return result

    def _execute_select(self, query, arguments):
        database_connection = sqlite3.connect(settings.SQLITE_PATH)
        result = database_connection.execute(query, arguments).fetchall()

        database_connection.close()
        return result

    def _convert_angebote_to_influx_json(self, angebote: List[Angebot]):
        influx_write_list = [] 
        for angebot in angebote:
            influx_dict = {}
            influx_dict['measurement'] = "auer_b_ware"
            influx_dict['tags'] = { "artnr": angebot.artnr }
            influx_dict['fields'] = {"Int_value": angebot.verfügbar }
            influx_dict['time'] = angebot.scraped_at.isoformat("T") + "Z"
            influx_write_list.append(influx_dict)
        self._influx_client.write_points(influx_write_list)


    def insert_new_artnr(self, angebote: List[Angebot]):
        self.logger.debug(f"Try to insert {len(angebote)} items into local db")
        self._convert_angebote_to_influx_json(angebote)
        for angebot in angebote:
            self._execute_query(
                "INSERT INTO artikel VALUES ( ? ) ", [angebot.artnr], run_commit=True
            )
        self.logger.debug("Done inserting items")

    def insert_new_client(self, client):
        self.logger.debug(f"Try to insert new client with id {client}")
        try:
            self._execute_query(
                "INSERT INTO clients VALUES ( ? ) ", [client], run_commit=True
            )
        except sqlite3.IntegrityError:
            pass
        self.logger.debug("Done inserting client")

    def delete_client(self, client):
        self.logger.debug(f"Try to delet client with id {client}")
        if client is not None:
            try:
                self._execute_query(
                    "DELETE FROM clients WHERE client_id = ( ? ) ",
                    [client],
                    run_commit=True,
                )
            except sqlite3.IntegrityError:
                pass
        self.logger.debug("Done deleting client")

    def get_all_clients(self):
        return self._execute_select("SELECT * FROM clients", ())


class AuerData:
    _instance = None

    @classmethod
    def instance(cls):
        logger = logging.getLogger("DataClass")
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
        table.set_cols_align(("l", "l", "l"))
        table.set_cols_dtype(("t", "i", "t"))
        table.add_row(("Type", "Menge", "Preis"))

        for entry in self.data:
            table.add_row([entry.artnr, entry.verfügbar, f"{entry.preis_neu:.2f} €"])
        table_string = str(table.draw())
        table_string = "<pre>" + table_string + "</pre>"
        return table_string
