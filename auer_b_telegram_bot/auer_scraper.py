import dataclasses
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from auer_b_telegram_bot.Controllers.AuerController import AuerController
from auer_b_telegram_bot.database import Database
from auer_b_telegram_bot.factories import AngebotFactory, KategorieFactory
import logging


def get_data_from_site(kategorie):
    base_url = "https://www.auer-packaging.com"
    logging.getLogger("auer_b_telegram_bot.scraper").info(
        f"scrape item site: {kategorie.url}"
    )
    html = BeautifulSoup(requests.get(base_url + kategorie.url).text, "html.parser")
    angebote = []
    try:
        table = html.select("form.categoryForm")[0].find("tbody").find_all("tr")
        scraped_at = datetime.now()

        for row in table:
            angebote.append(
                AngebotFactory.create_angebot_from_html(
                    row, scraped_at, kategorie.kategorie_id
                )
            )
    except IndexError:
        return angebote
    return angebote


def get_kategories():
    logger = logging.getLogger("auer_b_telegram_bot.scraper")
    url = "https://www.auer-packaging.com/de/de/B-Ware.html"

    logger.info(f"Scraping kategorie urls: {url}")
    html = BeautifulSoup(requests.get(url).text, "html.parser")
    kategories = KategorieFactory.create_Kategories_from_html(
        html.select("div.categoryview")[0]
    )
    KategorieFactory.write_kategories_to_db(kategories)

    return KategorieFactory.get_kategories_from_db()


def scrape_site(context):
    logger = logging.getLogger("auer_b_telegram_bot.scraper")

    kategories = get_kategories()
    logger.info("Starting to Scraper site")
    angebote = []
    for kategorie in kategories:
        logger.debug(f"scrape site for kategorie: {kategorie}")
        angbote_new = get_data_from_site(kategorie)
        angbote_new = [angebot for angebot in angbote_new if angebot is not None]
        angebote = angebote + angbote_new
    logger.info(f"Done Scraping found {len(angebote)} listings")
    dataclass = AuerController()
    dataclass.write_data_to_db(angebote)
