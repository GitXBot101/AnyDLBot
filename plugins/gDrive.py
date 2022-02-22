#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# (c) Shrimadhav U K

# the logging things
import logging
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

from datetime import datetime
import os

# the secret configuration specific things
if bool(os.environ.get("WEBHOOK", False)):
    from sample_config import Config
else:
    from config import Config

# the Strings used for this "thing"
from translation import Translation

from pyrogram import Client as AnyDL, filters
logging.getLogger("pyrogram").setLevel(logging.WARNING)

from helper_funcs.display_progress import humanbytes


from pydrive.auth import GoogleAuth


@AnyDL.on_message(filters.command(["gauth"]))
def g_auth(bot, update):
    Config.G_DRIVE_AUTH_DRQ[str(update.from_user.id)] = GoogleAuth()
    auth_url = Config.G_DRIVE_AUTH_DRQ[str(update.from_user.id)].GetAuthUrl()
    # Create authentication url user needs to visit
    bot.send_message(
        chat_id=update.chat.id,
        text=Translation.G_DRIVE_GIVE_URL_TO_LOGIN.format(auth_url),
        reply_to_message_id=update.message_id
    )


@AnyDL.on_message(filters.command(["gsetup"]))
def g_setup(bot, update):
    recvd_commands = update.command
    if len(recvd_commands) == 2:
        cmnd, auth_code = recvd_commands
        Config.G_DRIVE_AUTH_DRQ[str(update.from_user.id)].Auth(auth_code)
        # Authorize and build service from the code
        bot.send_message(
            chat_id=update.chat.id,
            text=Translation.G_DRIVE_SETUP_COMPLETE,
            reply_to_message_id=update.message_id
        )
    else:
        bot.send_message(
            chat_id=update.chat.id,
            text=Translation.G_DRIVE_SETUP_IN_VALID_FORMAT,
            reply_to_message_id=update.message_id
        )
