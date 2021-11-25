#/bin/bash

echo "Start database init script!"

export PGPASSWORD=$POSTGRES_PASSWORD

psql -h $POSTGRES_HOSTNAME -d $POSTGRES_DBNAME -U $POSTGRES_USERNAME -a -f ./auer_b_telegram_bot/database_migrations/init.sql

echo "Done with database init script"
