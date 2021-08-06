import requests
from bs4 import BeautifulSoup
from datetime import datetime
from auer_b_telegram_bot.Controllers import AuerController
from auer_b_telegram_bot.data import Angebot
import logging


def get_data_from_site(url):
    logging.getLogger("root.scraper").info(f"Scraping url: {url}")
    html = BeautifulSoup(requests.get(url).text, "html.parser")
    table = html.select("form.categoryForm")[0].find("tbody").find_all("tr")
    scraped_at = datetime.now()
    angebote = []
    for row in table:
        angebote.append(Angebot(row, scraped_at))
    return angebote


def scrape_site(context):
    logger = logging.getLogger("root.scraper")
    urls = [
        "https://www.auer-packaging.com/de/de/Eurobehälter-durchbrochen.html?bstock&cutomer_type=private",
        "https://www.auer-packaging.com/de/de/Eurobeh%C3%A4lter-geschlossen.html?bstock&cutomer_type=private",
        "https://www.auer-packaging.com/de/de/RL-KLT-Beh%C3%A4lter.html?bstock&cutomer_type=private",
        "https://www.auer-packaging.com/de/de/R-KLT-Beh%C3%A4lter.html?bstock&cutomer_type=private",
    ]
    logger.info("Starting to Scraper site")
    angebote = []
    for url in urls:
        angbote_new = get_data_from_site(url)
        angbote_new = [angebot for angebot in angbote_new if angebot.artnr is not None]
        angebote = angebote + angbote_new
    logger.info(f"Done Scraping found {len(angebote)} listings")
    dataclass = AuerController()
    dataclass.set_new_data(angebote)
