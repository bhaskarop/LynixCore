import json
from pyrogram import Client, filters
from FUNC.usersdb_func import *
from FUNC.defs import *
from FUNC.admin_auth import is_admin_or_owner


@Client.on_message(filters.command("skadd", [".", "/"]))
async def addbrod(Client, message):
    try:
        user_id     = str(message.from_user.id)
        if not await is_admin_or_owner(user_id):
            resp = "<b>⛔ Access Denied — Admin only.</b>"
            await message.reply_text(resp, message.id)
            return
        
        await addsk(message.reply_to_message.text)
        resp = f"""<b>
SK Key ( Stripe Key ) Successfully Added ✅
━━━━━━━━━━━━━━
{message.reply_to_message.text}

Status: Successfull
    </b>"""
        await message.reply_text(resp, message.id)

    except:
        await log_cmd_error(message)



@Client.on_message(filters.command("addsk", [".", "/"]))
async def update_live_sk_key(Client, message):
    try:
        user_id = str(message.from_user.id)
        if not await is_admin_or_owner(user_id):
            resp = "<b>⛔ Access Denied — Admin only.</b>"
            await message.reply_text(resp)
            return

        new_sk_key = str(message.reply_to_message.text)

        with open("FILES/deadsk.json", "r", encoding="UTF-8") as f:
            data = json.load(f)

        data["LIVE_SK"] = new_sk_key

        with open("FILES/deadsk.json", "w", encoding="UTF-8") as f:
            json.dump(data, f, indent=4)

        resp = f"""<b>
SK Key ( Stripe Key ) Successfully Added ✅
━━━━━━━━━━━━━━
{message.reply_to_message.text}

Status: Successfull
    </b>"""
        await message.reply_text(resp)

    except Exception as e:
        await log_cmd_error(message)


