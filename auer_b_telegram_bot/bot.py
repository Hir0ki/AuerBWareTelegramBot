import auer_scraper
from telegram import Update, ParseMode
from telegram.ext import (
    Updater,
    CommandHandler,
    CallbackContext,
)
from config import settings
from auer_b_telegram_bot.Controllers.AuerController import AuerController
from auer_b_telegram_bot.Controllers.AlertController import AlertController
from datetime import time
import pytz
import logging

TIME = range(1)


# Define a few command handlers. These usually take the two arguments update and
# context. Error handlers also receive the raised TelegramError object in error.
def start(update: Update, _: CallbackContext) -> None:
    update.message.reply_text("Hi! Use /set <seconds> to set a timer")


def add_alert(update: Update, context: CallbackContext):
    command_string = "/add_alert"
    alert_controller = AlertController()
    chat_id = update.message.chat_id
    search_string = update.message.text
    search_string = search_string.replace(command_string, "").strip()
    alert_controller.add_alert(chat_id, search_string)
    update.message.reply_text(f"{search_string} hinzugefügt")


def evaluate_alerts(context: CallbackContext) -> None:
    alert_controller = AlertController()
    alert_controller.evaluate_alerts()
    #for client in clients:
    #    context.bot.send_message(client[0], text, parse_mode=ParseMode.HTML)

def get_current_angebote(update: Update, context: CallbackContext) -> None:

    data: AuerController = AuerController()
    update.message.reply_text(
        data.text_table_of_current_data(), parse_mode=ParseMode.HTML
    )


def get_current_angebote_job(context: CallbackContext) -> None:
    logger = logging.getLogger("auer_b_telegram_bot.Bot")
    logger.info("Send daily message to all users")
    data: AuerController = AuerController()
    text = data.text_table_of_current_data()
    clients = data.database.get_all_clients()
    for client in clients:
        context.bot.send_message(client[0], text, parse_mode=ParseMode.HTML)


def main() -> None:
    """Run bot."""
    # Create the Updater and pass it your bot's token.
    updater = Updater(settings.BOT_TOKEN)

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    daily_run_time = time(20, 1, tzinfo=pytz.timezone("Europe/Berlin"))

    updater.job_queue.run_once(when=0, callback=auer_scraper.scrape_site)
    updater.job_queue.run_repeating(
        callback=evaluate_alerts,
        interval=10,
        job_kwargs=[],
    )
    updater.job_queue.run_repeating(
        callback=auer_scraper.scrape_site,
        interval=int(settings.AUER_SCRAPE_INTERVAL),
        job_kwargs=[],
    )
    updater.job_queue.run_daily(callback=get_current_angebote_job, time=daily_run_time)

    # on different commands - answer in Telegram
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("angebote", get_current_angebote))
    dispatcher.add_handler(CommandHandler("add_alert", add_alert))
    # Start the Bot
    updater.start_polling()

    # Block until you press Ctrl-C or the process receives SIGINT, SIGTERM or
    # SIGABRT. This should be used most of the time, since start_polling() is
    # non-blocking and will stop the bot gracefully.
    updater.idle()
