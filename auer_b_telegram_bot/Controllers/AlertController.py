import logging
from re import match
from auer_b_telegram_bot.records import Angebot
from auer_b_telegram_bot.database import Database


class AlertController:
    def __init__(self) -> None:
        self.logger = logging.getLogger("uer_b_telegram_bot.AlertController")
        self.database = Database()

    def add_alert(self, chat_id, search_stirng):
        self.logger.debug(f"adding alert for {chat_id} with search {search_stirng}")
        self.database.execute_query(
            """
                INSERT INTO alert_search
                    VALUES (%s)
                    ON CONFLICT (search_str)
                    DO NOTHING;
            """,
            [search_stirng],
            run_commit=True,
        )

        self.database.execute_query(
            """
                INSERT INTO alert_chat
                    values(%s,%s)
            """,
            [chat_id, search_stirng],
            run_commit=True,
        )

    def evaluate_alerts(self) -> list:

        search_strings = self.database._execute_select(
            """
            SELECT search_str FROM alert_search;
            """,
            [],
        )
        search_strings = [search_string[0] for search_string in search_strings]
        all_artnr = self.database._execute_select(
            "SELECT artnr from artikel", []
        )
        all_artnr = [artnr[0] for artnr in all_artnr]

        current_bestand = self.database._execute_select(
            """
            SELECT artnr, max(created_datetime) as max_date
	            FROM bestand
	            where "verfügbar" > 0
	            group by artnr
	            order by max_date
            """,
            []
        )

        # clean strings before matching them
        search_strings = [search_string.replace(" ", "").lower() for search_string in search_strings]
        all_artnr = [artnr.replace(" ", "").lower() for artnr in all_artnr]

        matches = []
        for search in search_strings:
            for artnr in all_artnr:
                self.logger.debug(f"search: {search} artnr: {artnr} matches: {artnr.find(search)}")
                if artnr.find(search) >= 0:
                    matches.append((artnr, search))
        return matches

