import logging
from auer_b_telegram_bot.records import Angebot, Kategorie
from auer_b_telegram_bot.database import Database
from typing import List


class AngebotFactory:
    @staticmethod
    def create_angebot_from_html(tr, scraped_at, kategorie_id) -> Angebot:

        logger = logging.getLogger("auer_b_telegram_bot.scraper")

        if len(tr.text) == 0:
            artnr = None
            return

        tds = tr.find_all("td")
        außenmaße = tds[0].text
        artnr = tds[1].text
        offset = 0
        if "KLT" in artnr:
            offset = 0
        elif "EG" in artnr:
            offset = 0
        elif "EO" in artnr:
            offset = -2
            besonderheit1 = None
            besonderheit2 = None
        elif "RK" in artnr:
            offset = -1
            besonderheit1 = tds[2].text
            besonderheit2 = None
        elif "B H" in artnr:
            offset = -1
            besonderheit1 = tds[2].text
            besonderheit2 = None
        elif "B R" in artnr:
            offset = -1
            besonderheit1 = tds[2].text
            besonderheit2 = None
        else:
            offset = -1
            besonderheit1 = tds[2].text
            besonderheit2 = None
        if offset == 0:
            besonderheit1 = tds[2].text
            besonderheit2 = tds[3].text

        preis_td = tds[4 + offset].find_all("span")
        logger.debug(
            f"Current artnr: {artnr} offset: {offset}, len Preise: {len(preis_td)}"
        )

        preis_alt = float(preis_td[1].text.replace("€", "").replace(",", "."))
        preis_neu = float(preis_td[2].text.replace("€", "").replace(",", "."))
        stück_auf_palette = int(tds[5 + offset].text)

        preis_td = tds[6 + offset].find_all("span")
        preis_stück_pro_palette_alt = float(
            preis_td[1].text.replace("€", "").replace(",", ".")
        )
        preis_stück_pro_palette_neu = float(
            preis_td[2].text.replace("€", "").replace(",", ".")
        )

        verfügbar = int(tds[7 + offset].text.replace(".", ""))
        try:
            versandfertig_link = tds[8 + offset].find("img")["title"]
        except Exception:
            versandfertig_link = tds[8 + offset].text
        währung = "€"

        return Angebot(
            scraped_at,
            außenmaße,
            artnr,
            besonderheit1,
            besonderheit2,
            preis_alt,
            preis_neu,
            währung,
            stück_auf_palette,
            preis_stück_pro_palette_alt,
            preis_stück_pro_palette_neu,
            verfügbar,
            versandfertig_link,
            kategorie_id,
        )

    @staticmethod
    def create_angebote_from_result_list(result_list: list) -> List[Angebot]:
        return_list = []
        for entry in result_list:
            return_list.append(
                Angebot(
                    artnr=entry[0],
                    außenmaße=entry[1],
                    besonderheit1=entry[2],
                    besonderheit2=entry[3],
                    stück_auf_palette=entry[7],
                    versandfertig_link=[11],
                    kategorie_id=[12],
                    scraped_at=None,
                )
            )
        return return_list


class KategorieFactory:
    @staticmethod
    def create_Kategories_from_html(categoryview_html) -> List[Kategorie]:

        logger = logging.getLogger("auer_b_telegram_bot.scraper")

        kategories_names = [
            kategorie.text for kategorie in categoryview_html.select("div.item")
        ]
        kategorie_title = categoryview_html.select("div.title")
        kategories_links = [link.find("a")["href"] for link in kategorie_title]

        db_kategorien = KategorieFactory.get_kategories_from_db()
        db_kategorien_namen = [kategorie.name for kategorie in db_kategorien]

        output_list = []
        for i, kategorie_name in enumerate(kategories_names):
            kategorie_name = kategorie_name.strip()

            if kategorie_name not in db_kategorien_namen:
                logger.debug(f"found new kategorie: {kategorie_name}")
                output_list.append(
                    Kategorie(
                        kategorie_id=None,
                        name=kategorie_name,
                        url=kategories_links[i],
                        besonderheit_2_name=None,
                        besonderheit_1_name=None,
                    )
                )
            else:
                db_kategorie = [
                    kategorie
                    for kategorie in db_kategorien
                    if kategorie.name == kategorie_name
                ][0]

                output_list.append(db_kategorie)

        return output_list

    @staticmethod
    def get_kategories_from_db() -> List[Kategorie]:

        database = Database()

        kategories_data = database._execute_select(
            """
        SELECT 
            kategorie_id,
            name,
            url,
            besonderheit_1_name,
            besonderheit_2_name
        FROM kategorien 
        """,
            [],
        )
        kategorie_list = []
        for kategorie_data in kategories_data:
            kategorie_list.append(
                Kategorie(
                    kategorie_id=kategorie_data[0],
                    name=kategorie_data[1],
                    url=kategorie_data[2],
                    besonderheit_1_name=kategorie_data[3],
                    besonderheit_2_name=kategorie_data[4],
                )
            )
        return kategorie_list

    @staticmethod
    def write_kategories_to_db(kategories: List[Kategorie]):
        db = Database()
        for kategorie in kategories:

            if kategorie.kategorie_id == None:

                db.execute_query(
                    """
                    INSERT into kategorien (
                        name,
                        url,
                        besonderheit_1_name,
                        besonderheit_2_name 
                    )
                    VALUES ( %s, %s, %s, %s);
                    """,
                    [
                        kategorie.name,
                        kategorie.url,
                        kategorie.besonderheit_1_name,
                        kategorie.besonderheit_2_name,
                    ],
                    run_commit=True,
                )
            else:
                db.execute_query(
                    """
                    UPDATE kategorien SET 
                        name=%s,
                        url=%s,
                        besonderheit_1_name=%s,
                        besonderheit_2_name=%s
                    WHERE kategorie_id = %s;
                    """,
                    [
                        kategorie.name,
                        kategorie.url,
                        kategorie.besonderheit_1_name,
                        kategorie.besonderheit_2_name,
                        kategorie.kategorie_id,
                    ],
                    run_commit=True,
                )
