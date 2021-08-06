from dataclasses import dataclass
from datetime import datetime
import logging
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
