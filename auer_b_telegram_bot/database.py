from auer_b_telegram_bot.data import Angebot
from config import settings
from typing import List, Iterable
import psycopg2
import logging


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
        curr.execute(
            """CREATE TABLE IF NOT EXISTS artikel( artnr VARCHAR(32), 
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
                                                        PRIMARY KEY( artnr ) );"""
        )
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
        self._execute_query(
            "UPDATE artikel SET ist_aktive = FALSE WHERE artnr NOT IN %s ",
            [tuple([angebot.artnr for angebot in angebote])],
            run_commit=True,
        )
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
                [
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
                    True,  # ist_akive is set to true
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
                    True,  # ist_aktive is set to true
                    angebot.handgriff,
                ],
                run_commit=True,
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
        sql_data = self._execute_query(
            "SELECT * FROM artikel WHERE aktive = True", (), run_commit=False
        )
        sql_data.fetch_all()
