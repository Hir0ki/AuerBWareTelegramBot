
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext
from config import settings



# Define a few command handlers. These usually take the two arguments update and
# context. Error handlers also receive the raised TelegramError object in error.
def start(update: Update, _: CallbackContext) -> None:
    update.message.reply_text('Hi! Use /set <seconds> to set a timer')

def set_notification(update: Update, context: CallbackContext) -> None:
    chat_id = update.ch




def main() -> None:
    """Run bot."""
    # Create the Updater and pass it your bot's token.
    updater = Updater(settings.BOT_TOKEN)

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    # on different commands - answer in Telegram
    dispatcher.add_handler(CommandHandler("start", start))

    # Start the Bot
    updater.start_polling()

    # Block until you press Ctrl-C or the process receives SIGINT, SIGTERM or
    # SIGABRT. This should be used most of the time, since start_polling() is
    # non-blocking and will stop the bot gracefully.
    updater.idle()


