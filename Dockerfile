from python:3.8



RUN apt-get update


ENV PYTHONPATH /
COPY logging.yml /logging.yml



RUN  python -m venv venv
RUN  chmod a+x ./venv/bin/activate
RUN  ./venv/bin/activate

COPY requerments.txt requerments.txt
RUN  python -m pip install -r requerments.txt

COPY auer_b_telegram_bot auer_b_telegram_bot 

COPY start.sh start.sh
RUN  chmod a+x ./start.sh
CMD ./start.sh