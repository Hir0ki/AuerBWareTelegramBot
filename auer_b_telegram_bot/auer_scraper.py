import requests
from bs4 import BeautifulSoup
from config import settings
from datetime import datetime
import data
import logging



def get_data_from_site():
    html = BeautifulSoup(requests.get(settings.AUER_B_URL).text, "html.parser" )
    table = html.select("form.categoryForm")[0].find("tbody").find_all("tr")
    scraped_at = datetime.now()
    angebote = []
    for row in table:
        angebote.append(data.Angebot(row, scraped_at))
    return angebote

def scrape_site(context):
    logger = logging.getLogger("Scraper")
    logger.info("Starting to Scraper site")
    angebote = get_data_from_site()
    logger.info(f"Done Scraping found {len(angebote)} listings")
    dataclass = data.AuerData.instance()
    dataclass.set_new_data(angebote) 





