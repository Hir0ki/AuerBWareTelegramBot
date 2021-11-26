from auer_b_telegram_bot.data import Angebot, AngebotFactory
from config import settings
from typing import List, Iterable
import psycopg2
import logging


class Database:
    def __init__(self):
        self.logger = logging.getLogger("auer_b_telegram_bot.database")
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
        
    def execute_query(self, query: str, arguments: Iterable, run_commit: bool):
        curr = self.database_connection.cursor()
        self.logger.debug(f"Execute Query: {query}")
        self.logger.debug(f"Query Parameter: {arguments}")
        result = curr.execute(query, arguments)
        if run_commit == True:
            self.database_connection.commit()
        curr.close()
        return result

    def _execute_select(self, query, arguments):
        curr = self.database_connection.cursor()
        curr.execute(query, arguments)
        result = curr.fetchall()
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


    def insert_new_client(self, client):
        self.logger.debug(f"Try to insert new client with id {client}")
        try:
            self.execute_query(
                "INSERT INTO clients VALUES ( %s ) ", [client], run_commit=True
            )
        except psycopg2.IntegrityError:
            pass
        self.logger.debug("Done inserting client")

    def delete_client(self, client):
        self.logger.debug(f"Try to delet client with id {client}")
        if client is not None:
            try:
                self.execute_query(
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
        result_list = self._execute_select(
            "SELECT * FROM artikel WHERE ist_aktive  = True", ()
        )
        return AngebotFactory.create_angebote_from_result_list(result_list)
