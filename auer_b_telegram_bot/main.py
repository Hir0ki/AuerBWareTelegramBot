import auer_scraper
from config import settings
from data import Database
import bot

auer_scraper.scrape_site(settings.AUER_B_URL)
Database()


if __name__ == '__main__':
   bot.main()