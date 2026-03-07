from pyrogram import Client, filters
from FUNC.usersdb_func import *
from FUNC.defs import *
from FUNC.admin_auth import is_admin_or_owner


@Client.on_message(filters.command("viewsk", [".", "/"]))
async def viewsk(Client, message):
    try:
        user_id     = str(message.from_user.id)
        if not await is_admin_or_owner(user_id):
            resp = "<b>⛔ Access Denied — Admin only.</b>"
            await message.reply_text(resp, message.id)
            return

        sks     = await getallsk()
        amt_sk  = 0
        sk_text = ""

        for sk in sks:
            amt_sk += 1
            sk_text += f"{amt_sk}.{sk}\n"
        resp = f"""<b>
Current SK Keys Retrieved Successfully ✅
━━━━━━━━━━━━━━ 
{sk_text}

Total SK Amount : {len(sks)}
        </b>"""

        await message.reply_text(resp, message.id)

    except Exception as e:
        await log_cmd_error(message)
