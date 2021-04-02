import requests
from bs4 import BeautifulSoup
from dataclasses import dataclass
from datetime import datetime
import logging


@dataclass
class Angebot():
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
        tds = tr.find_all("td")
        self.außenmaße = tds[0].text
        self.artnr = tds[1].text
        self.handgriff = tds[2].text 
        
        preis_td = tds[3].find_all("span")
        self.preis_alt = float(preis_td[1].text.replace("€", "").replace(",","."))
        self.preis_neu = float(preis_td[2].text.replace("€", "").replace(",","."))
        self.stück_auf_palette = int(tds[4].text)
 
        preis_td = tds[5].find_all("span")
        self.preis_stück_pro_palette_alt= float(preis_td[1].text.replace("€", "").replace(",","."))
        self.preis_stück_pro_palette_neu = float(preis_td[2].text.replace("€", "").replace(",","."))
        
        self.verfügbar = int(tds[6].text)
        self.versandfertig_link = tds[7].find("img")["title"]

        self.währung = "€"

        self.scraped_at = scraped_at

def scrape_site(url):
    logger = logging.getLogger("Scraper")
    logger.info("Starting to Scraper site")
    html = BeautifulSoup(requests.get(url).text, "html.parser" )
    table = html.select("form.categoryForm")[0].find("tbody").find_all("tr")
    scraped_at = datetime.now()
    angebote = []
    for row in table:
        angebote.append(Angebot(row, scraped_at))
    logger.info(f"Done Scraping found {len(angebote)} listings")
    return angebote





