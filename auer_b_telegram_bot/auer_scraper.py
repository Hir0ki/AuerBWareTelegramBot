import requests
from bs4 import BeautifulSoup
from datetime import datetime
from auer_b_telegram_bot.Controllers import AuerController
from auer_b_telegram_bot.data import AngebotFactory
import logging


def get_data_from_site(url):
    logging.getLogger("auer_b_telegram_bot.scraper").info(f"Scraping url: {url}")
    html = BeautifulSoup(requests.get(url).text, "html.parser")
    table = html.select("form.categoryForm")[0].find("tbody").find_all("tr")
    scraped_at = datetime.now()
    angebote = []
    for row in table:
        angebote.append(AngebotFactory.create_angebot_from_html(row, scraped_at))
    return angebote

def get_urls():
    logger = logging.getLogger("auer_b_telegram_bot.scraper")
    url ="https://www.auer-packaging.com/de/de/B-Ware.html"
    base_url = 'https://www.auer-packaging.com'
    logger.info(f"Scraping urls: {url}")
    html = BeautifulSoup(requests.get(url).text, "html.parser")
    html_a_links = html.select("div.categoryview")[0].find_all("a")
    urls = [ base_url+link['href'] for link in html_a_links if link['href'] != "/de/de/Toolboxen-Pro.html?bstock"]

    # turn into set to remove duplicats 
    urls = set(urls)

    return urls

def scrape_site(context):
    logger = logging.getLogger("auer_b_telegram_bot.scraper")
    
    urls = get_urls()
    logger.info("Starting to Scraper site")
    angebote = []
    for url in urls:
        angbote_new = get_data_from_site(url)
        angbote_new = [angebot for angebot in angbote_new if angebot is not None]
        angebote = angebote + angbote_new
    logger.info(f"Done Scraping found {len(angebote)} listings")
    dataclass = AuerController()
    dataclass.set_new_data(angebote)
