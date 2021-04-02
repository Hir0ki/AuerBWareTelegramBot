import auer_scraper
from config import settings
from data import Database
import bot

items = auer_scraper.scrape_site(settings.AUER_B_URL)
db = Database()
db.insert_new_artnr(items)


#if __name__ == '__main__':
#   bot.main()