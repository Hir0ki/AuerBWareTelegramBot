from auer_b_telegram_bot.records import Angebot
from auer_b_telegram_bot.database import Database
from typing import List
import texttable
import logging


class AuerController:
    def __init__(self):
        self.logger = logging.getLogger("auer_b_telegram_bot.controller")
        self.logger.info("Inserting scraped data into db")
        self.database = Database()

    def write_data_to_db(self, angebote: List[Angebot]):

        for angebot in angebote:
            self.database.execute_query(
                """INSERT INTO artikel ( 
                                         artnr, 
                                         außenmaße, 
                                         stück_auf_palette, 
                                         besonderheit1,
                                         besonderheit2,
                                         kategorie_id ) 
                                VALUES 
                                    ( %s, %s, %s, %s, %s, %s ) 
                                ON CONFLICT (artnr)
                                DO
                                    UPDATE SET 
                                         artnr =%s, 
                                         außenmaße=%s, 
                                         stück_auf_palette=%s, 
                                         besonderheit1=%s,
                                         besonderheit2=%s,
                                         kategorie_id=%s;""",
                [
                    angebot.artnr,
                    angebot.außenmaße,
                    angebot.stück_auf_palette,
                    angebot.besonderheit1,
                    angebot.besonderheit2,
                    angebot.kategorie_id,
                    angebot.artnr,
                    angebot.außenmaße,
                    angebot.stück_auf_palette,
                    angebot.besonderheit1,
                    angebot.besonderheit2,
                    angebot.kategorie_id,
                ],
                run_commit=False,
            )
            # check if preis  is same as last entry in db
            db_preise = self.database._execute_select(
                """
                    SELECT created_datetime,
                        artnr,
                        preis_neu,
                        preis_b_ware,
                        preis_pro_stück_palatte_neu,
                        preis_pro_stück_palatte_b_ware,
                        währung FROM preise 
                        WHERE  artnr = %s 
                        ORDER BY created_datetime DESC
                        LIMIT 1
                """,
                [angebot.artnr],
            )
            if len(db_preise) != 0:
                db_preise = db_preise[0]
                # if data is diff insert
                if db_preise != None and (
                    db_preise[2] != angebot.preis_neu
                    or db_preise[3] != angebot.preis_b
                    or db_preise[4] != angebot.preis_stück_pro_palette_neu
                    or db_preise[5] != angebot.preis_stück_pro_palette_b
                ):
                    self.insert_preis(angebot)
            # insert first entry
            else:
                self.insert_preis(angebot)

            # check if bestands data is same as last entry in db
            db_bestand = self.database._execute_select(
                """
                SELECT created_datetime,
                        artnr,
                        verfügbar
                        FROM bestand 
                        WHERE  artnr = %s 
                        ORDER BY created_datetime DESC
                        LIMIT 1
                """,
                [angebot.artnr],
            )

            if len(db_bestand) != 0:
                db_bestand = db_bestand[0]
                # if data is diff insert
                if db_bestand[2] != angebot.verfügbar:
                    self.insert_bestand(angebot)
            # insert first entry
            else:
                self.insert_bestand(angebot)

            self.database.database_connection.commit()

    def get_current_data(self):
        return self.database.get_active_data()

    def text_table_of_current_data(self):
        table = texttable.Texttable()
        table.set_cols_align(("l", "l", "l"))
        table.set_cols_dtype(("t", "i", "t"))
        table.add_row(("Type", "Menge", "Preis"))

        for entry in self.get_current_data():
            table.add_row([entry.artnr, entry.verfügbar, f"{entry.preis_neu:.2f} €"])
        table_string = str(table.draw())
        table_string = "<pre>" + table_string + "</pre>"
        return table_string

    def insert_preis(self, angebot):
        self.database.execute_query(
            """
                            INSERT INTO preise ( 
                                created_datetime ,
                                artnr,
                                preis_neu,
                                preis_b_ware,
                                preis_pro_stück_palatte_neu,
                                preis_pro_stück_palatte_b_ware,
                                währung )
                            VALUES
                                (%s, %s, %s, %s, %s, %s, %s);
                            """,
            [
                angebot.scraped_at,
                angebot.artnr,
                angebot.preis_neu,
                angebot.preis_b,
                angebot.preis_stück_pro_palette_neu,
                angebot.preis_stück_pro_palette_b,
                angebot.währung,
            ],
            run_commit=False,
        )

    def insert_bestand(self, angebot):
        self.database.execute_query(
            """
                            INSERT INTO bestand ( 
                                created_datetime,
                                artnr,
                                verfügbar
                                )
                            VALUES
                                (%s, %s, %s);
                            """,
            [
                angebot.scraped_at,
                angebot.artnr,
                angebot.verfügbar,
            ],
            run_commit=False,
        )
