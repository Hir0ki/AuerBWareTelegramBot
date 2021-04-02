import auer_scraper
from config import settings
from data import Database
import bot

auer_scraper.scrape_site("https://www.auer-packaging.com/de/de/Eurobeh%C3%A4lter-geschlossen.html?bstock")
Database()


#if __name__ == '__main__':
#   bot.main()