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
import requests
import subprocess
import time
import json
import re

rs = requests.Session()

# the secret configuration specific things
if bool(os.environ.get("WEBHOOK", False)):
    from sample_config import Config
else:
    from config import Config

# the Strings used for this "thing"
from translation import Translation

import pyrogram
logging.getLogger("pyrogram").setLevel(logging.WARNING)

from helper_funcs.display_progress import progress_for_pyrogram
from pydrive.drive import GoogleDrive


@pyrogram.Client.on_message(pyrogram.filters.command(["verystream"]))
def get_link(bot, update):
    if str(update.from_user.id) in Config.BANNED_USERS:
        bot.send_message(
            chat_id=update.chat.id,
            text=Translation.ABUSIVE_USERS,
            reply_to_message_id=update.message_id,
            disable_web_page_preview=True,
            parse_mode=pyrogram.ParseMode.HTML
        )
        return
    logger.info(update.from_user)
    if update.reply_to_message is not None:
        reply_message = update.reply_to_message
        download_location = Config.DOWNLOAD_LOCATION + "/"
        start = datetime.now()
        a = bot.send_message(
            chat_id=update.chat.id,
            text=Translation.DOWNLOAD_START,
            reply_to_message_id=update.message_id
        )
        c_time = time.time()
        after_download_file_name = bot.download_media(
            message=reply_message,
            file_name=download_location,
            progress=progress_for_pyrogram,
            progress_args=(Translation.DOWNLOAD_START, a.message_id, update.chat.id, c_time)
        )
        download_extension = after_download_file_name.rsplit(".", 1)[-1]
        bot.edit_message_text(
            text=Translation.SAVED_RECVD_DOC_FILE,
            chat_id=update.chat.id,
            message_id=a.message_id
        )
        end_one = datetime.now()
        if str(update.from_user.id) in Config.G_DRIVE_AUTH_DRQ:
            gauth = Config.G_DRIVE_AUTH_DRQ[str(update.from_user.id)]
            # Create GoogleDrive instance with authenticated GoogleAuth instance.
            drive = GoogleDrive(gauth)
            file_inance = drive.CreateFile()
            # Read file and set it as a content of this instance.
            file_inance.SetContentFile(after_download_file_name)
            file_inance.Upload() # Upload the file.
            end_two = datetime.now()
            time_taken_for_upload = (end_two - end_one).seconds
            logger.info(file_inance)
            adfulurl = file_inance.webContentLink
            max_days = 0
        else:
            max_days = 5
            verystreamLOGIN = '1789e745b8561c5548b0'
            verystreamKEY = 'JcGF53rcBri'
            
            # check video extension
            if not after_download_file_name.lower().endswith(('.mp4', '.mkv', '.avi', '.webm', '.vob', '.mpg')):
                bot.edit_message_text(
                    chat_id=update.chat.id,
                    text="This is not a video.",
                    message_id=a.message_id
                )
                return False
            
            
            rget = rs.get("https://api.verystream.com/file/ul?login=" + verystreamLOGIN + "&key=" + verystreamKEY)
            rjson = json.loads(rget.text)

            if rjson['status'] == 200:
                url = rjson['result']['url']
            else:
                bot.edit_message_text(
                    chat_id=update.chat.id,
                    text="Failed to initiate the upload process.",
                    message_id=a.message_id
                )
                return False

            command_to_exec = [
                "curl",
                "-F","file1=@"+after_download_file_name,
                "-H","Transfer-Encoding: chunked",
                url
            ]

            # {"status":200,"msg":"OK","result":{"name":"small.mp4","size":"383631","sha1":"5c5a07267317b166a218e5edb7667ccd2b5351be","content_type":"video\\/mp4","id":"h2qdQpteEk9","url":"https:\\/\\/verystream.com\\/stream\\/h2qdQpteEk9\\/small.mp4"}}
                
            bot.edit_message_text(
                text=Translation.UPLOAD_START,
                chat_id=update.chat.id,
                message_id=a.message_id
            )
            try:
                logger.info(command_to_exec)
                t_response = subprocess.check_output(command_to_exec, stderr=subprocess.STDOUT)
            except subprocess.CalledProcessError as exc:
                logger.info("Status : FAIL", exc.returncode, exc.output)
                bot.edit_message_text(
                    chat_id=update.chat.id,
                    text=exc.output.decode("UTF-8"),
                    message_id=a.message_id
                )
                return False
            else:
                logger.info(t_response)
                print ( t_response )

                t_response_arry = json.loads(t_response.decode("UTF-8").split("\n")[-2].strip())['result']['url']


        bot.edit_message_text(
            chat_id=update.chat.id,
            text=Translation.AFTER_GET_DL_LINK.format(t_response_arry, max_days),
            parse_mode=pyrogram.ParseMode.HTML,
            message_id=a.message_id,
            disable_web_page_preview=True
        )
        try:
            os.remove(after_download_file_name)
        except:
            pass
    else:
        bot.send_message(
            chat_id=update.chat.id,
            text=Translation.REPLY_TO_DOC_GET_LINK,
            reply_to_message_id=update.message_id
        )
