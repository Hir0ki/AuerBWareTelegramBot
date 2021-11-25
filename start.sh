#! /usr/bin/env sh
set -e

#In this script you can add all things that have to be done, before you programm starts

# database migration script is run.
sh ./auer_b_telegram_bot/database_migrations/db_init.sh

# bot is started
exec python ./auer_b_telegram_bot/main.py