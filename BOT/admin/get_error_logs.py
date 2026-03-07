import os
from pyrogram import Client, filters
from FUNC.defs import *
from FUNC.admin_auth import is_admin_or_owner


@Client.on_message(filters.command("geterror", [".", "/"]))
async def cmd_geterror(Client, message):
    try:
        user_id     = str(message.from_user.id)
        if not await is_admin_or_owner(user_id):
            resp = "<b>⛔ Access Denied — Admin only.</b>"
            await message.reply_text(resp, message.id)
            return

        delete         = await message.reply_text("<b>Getting Error Logs...</b>", message.id)

        document = "error_logs.txt"
        await message.reply_document(document = document,  reply_to_message_id = message.id)
        os.remove(document)

        document = "result_logs.txt"
        await message.reply_document(document=document, reply_to_message_id=message.id)
        os.remove(document)

        await Client.delete_messages(message.chat.id, delete.id)

    except:
        await log_cmd_error(message)
