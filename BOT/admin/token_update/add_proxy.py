from pyrogram import Client, filters
from FUNC.usersdb_func import *
from FUNC.admin_auth import is_admin_or_owner

@Client.on_message(filters.command("addproxy", [".", "/"]))
async def addbrod(Client, message):
    try:
        user_id     = str(message.from_user.id)
        if not await is_admin_or_owner(user_id):
            resp = "<b>⛔ Access Denied — Admin only.</b>"
            await message.reply_text(resp, message.id)
            return

        proxy      = str(message.reply_to_message.text)
        clear_file = open('FILES/proxy.txt', 'w',encoding="UTF-8").close()
        with open("FILES/proxy.txt", "a",encoding="UTF-8") as f:
            f.write(proxy)

        resp = f"""<b>
Proxy Successfully Added ✅
━━━━━━━━━━━━━━
{proxy}

Total Proxy Count: {len(proxy.splitlines())}
    </b>"""
        await message.reply_text(resp, message.id)
        
    except:
        await log_cmd_error(message)
