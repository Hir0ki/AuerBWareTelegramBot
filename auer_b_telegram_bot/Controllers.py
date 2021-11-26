from auer_b_telegram_bot.data import Angebot
from auer_b_telegram_bot.database import Database
from typing import List
import texttable
import logging


class AuerController:
    def __init__(self):
        self.logger = logging.getLogger("auer_b_telegram_bot.controller")
        self.logger.info("Creating new DataClass instance")
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
