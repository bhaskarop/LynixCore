from pyrogram import Client, filters
from FUNC.defs import *
from FUNC.admin_auth import is_admin_or_owner



@Client.on_message(filters.command("addvbvtoken", [".", "/"]))
async def addbrod(Client, message):
    try:
        user_id     = str(message.from_user.id)
        if not await is_admin_or_owner(user_id):
            resp = "<b>⛔ Access Denied — Admin only.</b>"
            await message.reply_text(resp, message.id)
            return

        VBV_TOKEN = str(message.reply_to_message.text).split('"dfReferenceId":"')[1].split('"')[0]
        await update_token("VBV_TOKEN", VBV_TOKEN)

        resp = f"""<b>
VBV_TOKEN Successfully Added ✅
━━━━━━━━━━━━━━
{VBV_TOKEN}

Status: Successfull
    </b>"""
        await message.reply_text(resp, message.id)

    except:
        await log_cmd_error(message)
