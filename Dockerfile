FROM python:latest

RUN pip install python-telegram-bot
RUN pip install python-jenkins

VOLUME /app
WORKDIR /app
CMD [ "python", "jenkinsbot.py" ]