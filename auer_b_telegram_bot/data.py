from config import settings
from typing import List, Iterable
from dataclasses import dataclass
from datetime import datetime
from json import dumps
import logging
import psycopg2
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
        offset = 0
        if "KLT" in self.artnr:
            offset = 1
        if "EO" in self.artnr:
            offset = -1
        if offset == -1 or offset == 1:
            self.handgriff = None
        else: 
            self.handgriff = tds[2].text

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
        self.logger = logging.getLogger("root.Database")
        self.logger.debug(
            f"postgres paramter: database: {settings.POSTGRES_DBNAME} / Hostname: {settings.POSTGRES_HOSTNAME} / Username: {settings.POSTGRES_USERNAME} / Port: {settings.POSTGRES_PORT}"
        )
        self.database_connection = psycopg2.connect(
            dbname=settings.POSTGRES_DBNAME,
            host=settings.POSTGRES_HOSTNAME,
            user=settings.POSTGRES_USERNAME,
            password=settings.POSTGRES_PASSWORD,
            port=settings.POSTGRES_PORT,
        )
        self.logger.info("connected to postgres")
        curr = self.database_connection.cursor()
        curr.execute(
            "CREATE TABLE IF NOT EXISTS clients( client_id VARCHAR(32), PRIMARY KEY( client_id ));"
        )
        curr.execute("""CREATE TABLE IF NOT EXISTS artikel( artnr VARCHAR(32), 
                                                            außenmaße VARCHAR(50), 
                                                            handgriff VARCHAR(30), 
                                                            preis_alt REAL, 
                                                            preis_neu REAL,
                                                            währung VARCHAR(10),  
                                                            stück_auf_palette INT,
                                                            preis_stück_pro_palette_alt REAL,
                                                            preis_stück_pro_palette_neu REAL,
                                                            verfügbar INT,
                                                            versandfertig_link VARCHAR(300),
                                                            ist_aktive BOOLEAN,
                                                        PRIMARY KEY( artnr ) );""")
        self.database_connection.commit()
        curr.close()
        self.logger.info("postgres init complete")

    def _execute_query(self, query: str, arguments: Iterable, run_commit: bool):
        curr = self.database_connection.cursor()
        result = curr.execute(query, arguments)
        if run_commit == True:
            self.database_connection.commit()
        curr.close()
        return result

    def _execute_select(self, query, arguments):
        curr = self.database_connection.cursor()
        result = curr.execute(query, arguments).fetchall()

        curr.close()
        return result

    def _convert_angebote_to_influx_json(self, angebote: List[Angebot]):
        influx_write_list = []
        for angebot in angebote:
            influx_dict = {}
            influx_dict["measurement"] = "auer_b_ware"
            influx_dict["tags"] = {"artnr": angebot.artnr}
            influx_dict["fields"] = {"Int_value": angebot.verfügbar}
            influx_dict["time"] = angebot.scraped_at.isoformat("T") + "Z"
            # influx_write_list.append(influx_dict)
        # self._influx_client.write_points(influx_write_list)

    def modify_artikel(self, angebote: List[Angebot]):
        self._convert_angebote_to_influx_json(angebote)
        self._execute_query("UPDATE artikel SET ist_aktive = FALSE WHERE artnr NOT IN %s ", [ tuple([ angebot.artnr for angebot in angebote  ])], run_commit=True)
        for angebot in angebote:
            
            self._execute_query(
            """INSERT INTO artikel ( artnr, 
                                         außenmaße, 
                                         preis_alt, 
                                         preis_neu, 
                                         währung, 
                                         stück_auf_palette, 
                                         preis_stück_pro_palette_alt, 
                                         preis_stück_pro_palette_neu, 
                                         verfügbar, 
                                         versandfertig_link,
                                         ist_aktive,
                                         handgriff ) 
                                VALUES 
                                    ( %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s ) 
                                ON CONFLICT (artnr)
                                DO
                                    UPDATE SET 
                                            artnr = %s,
                                            außenmaße = %s,
                                            preis_alt = %s,
                                            preis_neu = %s,
                                            währung = %s,
                                            stück_auf_palette = %s,
                                            preis_stück_pro_palette_alt = %s,
                                            preis_stück_pro_palette_neu = %s,
                                            verfügbar = %s,
                                            versandfertig_link = %s,
                                            ist_aktive = %s,
                                            handgriff = %s;""", 
                                        [angebot.artnr,
                                         angebot.außenmaße,
                                         angebot.preis_alt,
                                         angebot.preis_neu,
                                         angebot.währung,
                                         angebot.stück_auf_palette,
                                         angebot.preis_stück_pro_palette_alt,
                                         angebot.preis_stück_pro_palette_neu,
                                         angebot.verfügbar,
                                         angebot.versandfertig_link,
                                         True, # ist_akive is set to true
                                         angebot.handgriff,
                                         angebot.artnr,
                                         angebot.außenmaße,
                                         angebot.preis_alt,
                                         angebot.preis_neu,
                                         angebot.währung,
                                         angebot.stück_auf_palette,
                                         angebot.preis_stück_pro_palette_alt,
                                         angebot.preis_stück_pro_palette_neu,
                                         angebot.verfügbar,
                                         angebot.versandfertig_link,
                                         True, # ist_aktive is set to true
                                         angebot.handgriff
                                         ], run_commit=True
            )
            
        self.logger.debug("Done inserting items")

    def insert_new_client(self, client):
        self.logger.debug(f"Try to insert new client with id {client}")
        try:
            self._execute_query(
                "INSERT INTO clients VALUES ( %s ) ", [client], run_commit=True
            )
        except psycopg2.IntegrityError:
            pass
        self.logger.debug("Done inserting client")

    def delete_client(self, client):
        self.logger.debug(f"Try to delet client with id {client}")
        if client is not None:
            try:
                self._execute_query(
                    "DELETE FROM clients WHERE client_id = ( %s ) ",
                    [client],
                    run_commit=True,
                )
            except psycopg2.IntegrityError:
                pass
        self.logger.debug("Done deleting client")

    def get_all_clients(self):
        return self._execute_select("SELECT * FROM clients", ())

    def get_active_data(self):
        return self._execute_query("SELECT * FROM artikel WHERE aktive = True", (), run_commit=False)


class AuerData:
    

    def __init__(self):
        self.logger = logging.getLogger("root.dataclass")
        self.logger.info("Creating new DataClass instance")
        self.database = Database()

    def set_new_data(self, data):
        self.database.modify_artikel(data)

    def get_current_data(self):
        return self.database.get_active_data()

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
