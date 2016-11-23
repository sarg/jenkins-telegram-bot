#!/usr/bin/env python
# -*- coding: utf-8 -*-

from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackQueryHandler
from telegram import (InlineKeyboardMarkup, ReplyKeyboardHide,InlineKeyboardButton)
import logging
import jenkins
from settings import *

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

server = jenkins.Jenkins(JENKINS_URL, username=JENKINS_USER, password=JENKINS_PASS)

def _match(item, cond):
    item = item.lower()
    cond = cond.lower()
    condIdx = 0
    itemIdx = -1
    for condIdx in range(len(cond)):
        itemIdx = item.find(cond[condIdx], itemIdx+1)
        if itemIdx == -1:
            return False

    return True

# Define a few command handlers. These usually take the two arguments bot and
# update. Error handlers also receive the raised TelegramError object in error.
def build(bot, update):
    bname = update.message.text[7:]
    if not bname:
        bname = DEFAULT_JENKINS_QUERY
    jobs = [ [ InlineKeyboardButton(x['fullname'], callback_data=x['fullname'])] for x in server.get_jobs() if _match(x['fullname'], bname) ]
    if len(jobs) == 1:
        update.message.reply_text("Building only job: %s %s" % _build(jobs[0][0].text))
    else:
        update.message.reply_text('Which job?' + (' Shown only 5' if len(jobs)>5 else ''), reply_markup=InlineKeyboardMarkup(jobs[:5]))

def builds(bot, update):
    update.message.reply_text(server.get_running_builds())

def _build(job):
    params = [ p['parameterDefinitions'] for p in server.get_job_info(job)['actions'] if p.get('_class')=='hudson.model.ParametersDefinitionProperty' ]
    if params:
        params = { p['name']: p['defaultParameterValue']['value'] for p in params[0] if not p['type']=='PasswordParameterDefinition' }
    else:
        params = {}

    server.build_job(job, params)
    return (job, params)

def button(bot, update):
    query = update.callback_query
    job, params = _build(query.data)

    bot.editMessageText(text="Building: %s %s" % (job, params),
                        chat_id=query.message.chat_id,
                        message_id=query.message.message_id)

def error(bot, update, error):
    logger.warn('Update "%s" caused error "%s"' % (update, error))

def main():
    # Create the EventHandler and pass it your bot's token.
    updater = Updater(BOT_TOKEN)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("build", build))
    dp.add_handler(CommandHandler("builds", builds))
    dp.add_handler(CallbackQueryHandler(button))

    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    # Run the bot until the you presses Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()
