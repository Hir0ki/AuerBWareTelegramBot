import auer_scraper
from telegram import Update, ParseMode, ReplyKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackContext, ConversationHandler, MessageHandler, Filters
from config import settings
from data import AuerData
import texttable

TIME = range(1)

# Define a few command handlers. These usually take the two arguments update and
# context. Error handlers also receive the raised TelegramError object in error.
def start(update: Update, _: CallbackContext) -> None:
    update.message.reply_text('Hi! Use /set <seconds> to set a timer')

def start_update_times(update: Update, context: CallbackContext) -> None:
    reply_keyboard = [['Mo', 'Di', 'Mi'],
                      ['Do', 'Fr', 'Sa'],
                            ['So']]
    update.message.reply_text("Setze die Tage andenem eine Benarchituging gesendet werden soll", reply_markup=ReplyKeyboardMarkup(reply_keyboard))

    return TIME 

def set_times_for_update(update: UPdate, context: CallbackContext) -> None:
    replay_keyboard = [['1', '2', '3', '4', '5', '6'],
                       [ '7', '8', '9', '10', '11', '12'],
                       [ '13', '14', '15', '16', '17', '18'],
                       ['19', '20', '21', '23', '24'] ]
    update.message.reply_text("Setze die Uhrzeit für die Benachrichtigung", reply_markup=ReplyKeyboardMarkup(replay_keyboard, one_time_keyboard=True))

    return ConversationHandler.END 

def get_current_angebote(update: Update, context: CallbackContext) -> None:
    data : AuerData = AuerData.instance()
    update.message.reply_text(data.text_table_of_current_data(), parse_mode=ParseMode.HTML)




def main() -> None:
    """Run bot."""
    # Create the Updater and pass it your bot's token.
    updater = Updater(settings.BOT_TOKEN)

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    updater.job_queue.run_once( when=0, callback= auer_scraper.scrape_site )
    updater.job_queue.run_repeating( callback= auer_scraper.scrape_site, interval=int(settings.AUER_SCRAPE_INTERVAL), job_kwargs=[])

    conv_hanlder = ConversationHandler([CommandHandler('set_update_times',start_update_times)],
                                        states= {
                                            DAY: [MessageHandler(Filters.regex(r"\w\w"),set_times_for_update )]
                                        },
                                        fallbacks=[])

    # on different commands - answer in Telegram
    dispatcher.add_handler(conv_hanlder)
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("angebote", get_current_angebote))
    # Start the Bot
    updater.start_polling()

    # Block until you press Ctrl-C or the process receives SIGINT, SIGTERM or
    # SIGABRT. This should be used most of the time, since start_polling() is
    # non-blocking and will stop the bot gracefully.
    updater.idle()


