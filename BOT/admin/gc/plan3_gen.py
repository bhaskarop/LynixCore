from .func import *
from pyrogram import Client, filters
from FUNC.defs import error_log
from FUNC.admin_auth import is_admin_or_owner


@Client.on_message(filters.command("getplan3", [".", "/"]))
async def cmd_getplan3(Client, message):
    try:
        user_id     = str(message.from_user.id)
        if not await is_admin_or_owner(user_id):
            resp = "<b>⛔ Access Denied — Admin only.</b>"
            await message.reply_text(resp, message.id)
            return

        try:
            amt = int(message.text.split(" ")[1])
        except:
            amt = 10

        text = f"""<b>Giftcode Genarated ✅
Amount: {amt}\n</b>"""

        for _ in range(amt):
            GC = f"XCC-{gcgenfunc()}-{gcgenfunc()}-{gcgenfunc()}"
            await insert_plan3(GC)
            text += f"""
➔ <code>{GC}</code>
<b>Value : Gold Plan 30 Days</b>\n"""

        text += f"""
<b>For Redeemtion 
Type /redeem XCC-XXXX-XXXX-XXXX</b>"""

        await message.reply_text(text, message.id)

    except:
        await log_cmd_error(message)
