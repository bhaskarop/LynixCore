from pyrogram import Client, filters
from FUNC.defs import *
from FUNC.admin_auth import is_admin_or_owner

async def update_api_token(TOKEN_NAME , TOKEN):
    TOKEN_DB.update_one({"id": TOKEN_NAME}, {"$set": {"api_key": TOKEN}})


@Client.on_message(filters.command("addauthtoken", [".", "/"]))
async def addauthtoken(Client, message):
    try:
        user_id     = str(message.from_user.id)
        if not await is_admin_or_owner(user_id):
            resp = "<b>⛔ Access Denied — Admin only.</b>"
            await message.reply_text(resp, message.id)
            return

        AUTH_TOKEN = str(message.reply_to_message.text)
        await update_api_token("AUTH_TOKEN", AUTH_TOKEN)

        resp = f"""<b>
Auth API Token Successfully Added ✅
━━━━━━━━━━━━━━
{AUTH_TOKEN}

Status: Successfull
    </b>"""
        await message.reply_text(resp, message.id)

    except:
        await log_cmd_error(message)
