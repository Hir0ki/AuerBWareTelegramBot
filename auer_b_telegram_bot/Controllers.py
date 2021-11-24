from auer_b_telegram_bot.database import Database
import texttable
import logging


class AuerController:
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

        for entry in self.get_current_data():
            table.add_row([entry.artnr, entry.verfügbar, f"{entry.preis_neu:.2f} €"])
        table_string = str(table.draw())
        table_string = "<pre>" + table_string + "</pre>"
        return table_string
