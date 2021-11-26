from dataclasses import dataclass
from datetime import datetime
import logging
from typing import List
import texttable


@dataclass
class Angebot:
    scraped_at: datetime
    außenmaße: str
    artnr: str
    besonderheit1: str
    besonderheit2: str
    preis_b: float
    preis_neu: float
    währung: str
    stück_auf_palette: int
    preis_stück_pro_palette_b: float
    preis_stück_pro_palette_neu: float
    verfügbar: int
    versandfertig_link: str
    kategorie_id: str


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
                    preis_alt=entry[4],
                    preis_neu=entry[5],
                    währung=entry[6],
                    stück_auf_palette=entry[7],
                    preis_stück_pro_palette_neu=entry[8],
                    preis_stück_pro_palette_alt=entry[9],
                    verfügbar=entry[10],
                    versandfertig_link=[11],
                    kategorie_id=[12],
                    scraped_at=None,
                )
            )
        return return_list
