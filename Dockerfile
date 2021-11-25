from python:3.10.0-buster



RUN apt-get update

RUN apt-get install postgresql-client -y 

ENV PYTHONPATH /


RUN  python -m venv venv
RUN  chmod a+x ./venv/bin/activate
RUN  ./venv/bin/activate

COPY requerments.txt requerments.txt
RUN  python -m pip install -r requerments.txt

COPY logging.yml /logging.yml
COPY start.sh start.sh
RUN  chmod a+x ./start.sh

COPY auer_b_telegram_bot auer_b_telegram_bot 
RUN chmod a+x ./auer_b_telegram_bot/database_migrations/db_init.sh

CMD ./start.sh